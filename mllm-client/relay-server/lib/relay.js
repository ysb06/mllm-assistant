import { WebSocketServer } from 'ws';
import { RealtimeClient } from '@openai/realtime-api-beta';
import net from 'net';

const SERVER_ADDRESS = "localhost"
const SERVER_PORT = 46011

export class RealtimeRelay {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.sockets = new WeakMap();
    this.wss = null;

    this.sensorSocket = new net.Socket();
    this.sensorSocket.connect(SERVER_PORT, SERVER_ADDRESS, () => {
      this.log('Connected to Sensor Server');
    });
    this.getSensorData = this.getSensorData.bind(this);
    this.getSensorDataInstructions = this.getSensorDataInstructions.bind(this);
  }

  getSensorData() {
    return new Promise((resolve, reject) => {
      console.log('GETTING SENSOR DATA');
      this.sensorSocket.write('GET\n');

      const onData = (data) => {
        console.log('DATA RECEIVED');
        resolve(data.toString());
      };

      const onError = (err) => {
        console.error('에러가 발생했습니다:', err);
        reject(err);
      };

      this.sensorSocket.once('data', onData);
      this.sensorSocket.once('error', onError);
    });
  }

  async getSensorDataInstructions(instructions) {
    let newInstructions = "";
    const lines = instructions.split('\n');
    for (const line of lines) {
      if (line.startsWith("- Please refer to the following current vehicle state when providing answers or questions:")) {
        newInstructions += "- Please refer to the following current vehicle state when providing answers or questions:";
        const sensorData = await this.getSensorData();
        newInstructions += sensorData + '\n';
      } else {
        newInstructions += line + '\n';
      }
    }

    return newInstructions;
  }

  listen(port) {
    this.wss = new WebSocketServer({ port });
    this.wss.on('connection', this.connectionHandler.bind(this));
    this.log(`Listening on ws://localhost:${port}`);
  }

  async connectionHandler(ws, req) {
    if (!req.url) {
      this.log('No URL provided, closing connection.');
      ws.close();
      return;
    }

    const url = new URL(req.url, `http://${req.headers.host}`);
    const pathname = url.pathname;

    if (pathname !== '/') {
      this.log(`Invalid pathname: "${pathname}"`);
      ws.close();
      return;
    }

    // Instantiate new client
    this.log(`Connecting with key "${this.apiKey.slice(0, 3)}..."`);
    const client = new RealtimeClient({ apiKey: this.apiKey });

    // Relay: OpenAI Realtime API Event -> Browser Event
    client.realtime.on('server.*', (event) => {
      this.log(`Relaying "${event.type}" to Client`);
      if (event.type.includes(".delta") == false)
        console.log(event);
      ws.send(JSON.stringify(event));
    });
    client.realtime.on('close', () => ws.close());

    // Relay: Browser Event -> OpenAI Realtime API Event
    // We need to queue data waiting for the OpenAI connection
    const messageQueue = [];
    const messageHandler = async (data) => {
      try {
        const event = JSON.parse(data);
        this.log(`Relaying "${event.type}" to OpenAI`);
        if (event.type === 'session.update') {
          client.updateSession(event.session);
        }
        // else if (event.type === 'input_audio_buffer.append' || event.type === 'conversation.item.create') {
        //   await client.waitForSessionCreated();
        //   const instructions = await this.getSensorDataInstructions(client.sessionConfig.instructions);
        //   client.updateSession({ instructions: instructions });
        // }


        // if (Object.keys(event).includes('item')) {
        //   if (event.item.role === 'user') {
        //     event.item.content[0].text += "\n- Current vehicle state:\n" + result;
        //   }
        // }

        client.realtime.send(event.type, event);
      } catch (e) {
        console.error(e.message);
        this.log(`Error parsing event from client: ${data}`);
      }
    };
    ws.on('message', (data) => {
      if (!client.isConnected()) {
        messageQueue.push(data);
      } else {
        messageHandler(data);
      }
    });
    ws.on('close', () => client.disconnect());

    // Connect to OpenAI Realtime API
    try {
      this.log(`Connecting to OpenAI...`);
      await client.connect();
    } catch (e) {
      this.log(`Error connecting to OpenAI: ${e.message}`);
      ws.close();
      return;
    }
    this.log(`Connected to OpenAI successfully!`);
    while (messageQueue.length) {
      messageHandler(messageQueue.shift());
    }
  }

  log(...args) {
    console.log(`[RealtimeRelay]`, ...args);
  }
}
