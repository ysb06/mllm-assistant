import { IChatElement, IEventElement } from './langgraph';

export interface StreamingOptions {
    url: string;
    messages: IChatElement[];
    session?: string;
    signal?: AbortSignal;
}

export interface StreamingCallbacks {
    onEvent?: (event: IEventElement) => void;
    onError?: (error: Error) => void;
    onComplete?: () => void;
}

export class StreamingClient {
    private decoder: TextDecoder;
    private buffer: string;

    constructor() {
        this.decoder = new TextDecoder("utf-8");
        this.buffer = "";
    }

    async streamChat(options: StreamingOptions, callbacks: StreamingCallbacks = {}) {
        const { url, messages, session, signal } = options;
        const { onEvent, onError, onComplete } = callbacks;

        const content: { messages: IChatElement[], session?: string } = {
            messages: messages,
        };

        if (session) {
            content.session = session;
        }

        const request: RequestInit = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(content),
            signal,
        };

        try {
            const response = await fetch(url, request);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            if (!response.body) {
                throw new Error("Response body is empty");
            }

            await this.processStream(response.body, onEvent, onError);
            onComplete?.();

        } catch (error) {
            if (error instanceof Error) {
                onError?.(error);
            } else {
                onError?.(new Error("Unknown streaming error"));
            }
        }
    }

    private async processStream(
        body: ReadableStream<Uint8Array>,
        onEvent?: (event: IEventElement) => void,
        onError?: (error: Error) => void
    ) {
        const reader = body.getReader();
        this.buffer = "";

        try {
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;

                this.buffer += this.decoder.decode(value, { stream: true });
                await this.processBuffer(onEvent, onError);
            }

            // Flush the TextDecoder to include any remaining bytes
            this.buffer += this.decoder.decode();

            // 마지막에 남은 버퍼 처리
            await this.processRemainingBuffer(onEvent, onError);

        } finally {
            reader.releaseLock();
        }
    }

    private async processBuffer(
        onEvent?: (event: IEventElement) => void,
        onError?: (error: Error) => void
    ) {
        const lines = this.buffer.split("\n");
        this.buffer = lines.pop() || "";

        for (const line of lines) {
            if (line.trim() !== "") {
                try {
                    const event: IEventElement = JSON.parse(line);
                    onEvent?.(event);
                } catch (parseError) {
                    console.warn("Failed to parse JSON line:", line);
                    onError?.(new Error(`JSON parse error: ${parseError}`));
                }
            }
        }
    }

    private async processRemainingBuffer(
        onEvent?: (event: IEventElement) => void,
        onError?: (error: Error) => void
    ) {
        if (this.buffer.trim() !== "") {
            try {
                const event: IEventElement = JSON.parse(this.buffer);
                onEvent?.(event);
            } catch (parseError) {
                console.warn("Failed to parse remaining buffer:", this.buffer);
                onError?.(new Error(`JSON parse error: ${parseError}`));
            }
        }
        this.buffer = "";
    }

    createAbortController(): AbortController {
        return new AbortController();
    }
}

// 싱글톤 인스턴스 제공
export const streamingClient = new StreamingClient();