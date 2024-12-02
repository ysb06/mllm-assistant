import logging
import socket
import struct
from typing import Dict, List, Optional, Tuple
import threading
import time
from collections import deque

from sensor_server.server import SERVER_IP
from .server import SensorServer

SCANER_SERVER_IP = "192.168.0.100"
SCANER_SERVER_PORT = 46012
DATA_VALUE_SIZE = 8  # 32-bit float

logger = logging.getLogger(__name__)


class ScanerFilterServer(SensorServer):
    def __init__(
        self,
        filter_ip: str = SCANER_SERVER_IP,
        filter_port: int = SCANER_SERVER_PORT,
        data_size: int = DATA_VALUE_SIZE,
        timeout: float = 3,
    ) -> None:
        super().__init__()
        print(f"ScanerFilterServer: {filter_ip}:{filter_port}")
        self.data_size = data_size

        self.filter_thread: Optional[threading.Thread] = None
        self.filter_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.filter_address = (filter_ip, filter_port)
        self.timeout = timeout
        
        self._scaner_steering_angles = deque([0.0] * 20, maxlen=20)
        self._scaner_speeds = deque([0.0] * 20, maxlen=20)

    def _update_scaner_data(self) -> None:
        print("Updating scaner data...")
        while self.is_active:
            try:
                data, _ = self.filter_udp_socket.recvfrom(self.buffer_size)
                values = struct.unpack("<" + "d" * (len(data) // self.data_size), data)
                results = {}
                key = -1
                for idx, value in enumerate(values):
                    if idx % 2 == 0:
                        key = int(value)
                    else:
                        results[key] = value
                self._process_scaner_data(results)
            except socket.timeout:
                print("(Timeout) Waiting for messages...")
                continue
            except OSError as e:
                print(f"The socket may be forcibly closed: {e}")

    def _process_client_request(self, _: bytes) -> bytes:
        result = ""
        result += f"[Steering Angles]:{list(self._scaner_steering_angles)}\n"
        result += f"[Velocities]:{list(self._scaner_speeds)}\n"
        
        return result.encode()
    
    def _process_scaner_data(self, data: Dict[int, float]) -> bytes:
        self._scaner_steering_angles.append(data[167])  # 167: Steering Angle
        self._scaner_speeds.append(data[120])           # 120: Speed
    
    def activate(self):
        super().activate()
        self.filter_udp_socket.bind(self.filter_address)
        self.filter_udp_socket.settimeout(self.timeout)
        self.filter_thread = threading.Thread(target=self._update_scaner_data)
        self.filter_thread.start()
        

    def deactivate(self):
        super().deactivate()
        self.filter_udp_socket.close()
        self.filter_thread.join()


class UdpFilterServer:
    def __init__(
        self,
        ip_address: str = SCANER_SERVER_IP,
        port: int = 65002,
        buffer_size=1024,
        timeout=3,
        update_interval=0.25,
    ) -> None:
        self.udp_socket: Optional[socket.socket] = None
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.buffer_size = buffer_size

        self.udp_thread: Optional[threading.Thread] = None
        self.is_active = False
        self.update_interval = update_interval

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.deactivate()

    def _receive_message(self) -> None:
        print("Receiving messages...")
        while self.is_active:
            try:
                data, _ = self.udp_socket.recvfrom(self.buffer_size)
                results = self._parse_data(data)
                self._update(list(results))
            except socket.timeout:
                print("(Timeout) Waiting for messages...")
                continue
            except OSError as e:
                print(f"The socket may be forcibly closed: {e}")
            time.sleep(self.update_interval)
        print("Receiving messages stopped")

    def _parse_data(self, data: bytes) -> Optional[Tuple]:
        data_len = len(data)
        if data_len % 8 != 0:
            print("Wrong data format")
            return None

        num_doubles = data_len // 8
        results = struct.unpack("<" + "d" * num_doubles, data)

        return results

    def _send_message(self, message: bytes) -> None:
        self.udp_socket.sendto(message, (self.ip_address, self.port))

    def _update(self, messages: List):
        raise NotImplementedError("This method should be implemented in a subclass.")

    def activate(self):
        print(f"Activating client for server[{self.ip_address}:{self.port}]...")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.ip_address, self.port))
        self.udp_socket.settimeout(self.timeout)
        self.is_active = True
        self.udp_thread = threading.Thread(target=self._receive_message)
        self.udp_thread.start()
        print("Activating complete!")

    def deactivate(self):
        self.is_active = False
        self.udp_socket.close()
        self.udp_thread.join()
        print("Deactivating complete!")


def activate_server():
    with ScanerFilterServer() as server:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt: Stopping the server...")


if __name__ == "__main__":
    activate_server()
