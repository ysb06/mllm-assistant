import socket
import struct
from typing import List, Optional, Tuple
import threading
import time

from sensor_server.server import SERVER_IP
from .server import SensorServer

SCANER_SERVER_IP = "192.168.0.100"
SCANER_SERVER_PORT = 65002
DATA_VALUE_SIZE = 8  # 32-bit float


class ScanerFilterServer(SensorServer):
    def __init__(
        self,
        filter_ip: str = SCANER_SERVER_IP,
        filter_port: int = SCANER_SERVER_PORT,
        data_size: int = DATA_VALUE_SIZE,
    ) -> None:
        super().__init__()
        self.filter_address = (filter_ip, filter_port)
        self.data_size = data_size

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


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
