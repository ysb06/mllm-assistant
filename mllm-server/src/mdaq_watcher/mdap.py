import socket
import struct
from typing import List, Optional
import threading
import time

MDAQ_SERVER_IP = "192.168.1.2"
MDAQ_SERVER_PORT = 3232
REQUEST_MESSAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00"
DATA_VALUE_SIZE = 4  # 32-bit float
FLOAT_SIZE = 9


class MdaqClient:
    def __init__(self, ip_address: str, port: int, buffer_size=1024) -> None:
        self.ip_address = ip_address
        self.port = port
        self.buffer_size = buffer_size
        self.is_active = False
        self.udp_socket: Optional[socket.socket] = None
        self.udp_thread: Optional[threading.Thread] = None

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.deactivate()

    def _receive_message(self) -> None:
        print("Receiving messages...")
        while self.is_active:
            self._send_message(REQUEST_MESSAGE)
            try:
                data, _ = self.udp_socket.recvfrom(self.buffer_size)
                _, float_values, _, int_values = self._parse_data(data)
                self.update(float_values, int_values)
            except socket.timeout:
                print("(Timeout) Waiting for messages...")
                continue
            time.sleep(0.25)
        print("Socket closed")

    def _parse_data(self, data: bytes):
        result = struct.unpack("<i9f52i", data)
        start_byte = result[0]
        float_values = result[1:10]
        seperator = result[10]
        int_values = result[11:]

        return start_byte, float_values, seperator, int_values

    def _send_message(self, message: bytes) -> None:
        self.udp_socket.sendto(message, (self.ip_address, self.port))

    def activate(self):
        print(f"Activating client for server[{self.ip_address}:{self.port}]...")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(3)
        self.is_active = True
        self.udp_thread = threading.Thread(target=self._receive_message)
        self.udp_thread.start()
        print("Activating complete!")

    def deactivate(self):
        self.is_active = False
        self.udp_socket.close()
        self.udp_thread.join()
        print("Deactivating complete!")
    
    def update(self, float_values: List[float], int_values: List[int]) -> None:
        # print(f"Received data:")
        # for idx, dat in enumerate(float_values):
        #     print(f"Float [{idx}]:", dat)
        # for idx, dat in enumerate(int_values):
        #     print(f"Int [{idx}]:", dat)
        
        raise NotImplementedError("This method should be implemented in a subclass.")
        
