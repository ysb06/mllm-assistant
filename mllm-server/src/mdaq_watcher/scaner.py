import socket
import struct
from typing import List, Optional
import threading
import time

SCANER_SERVER_IP = "192.168.0.100"
DATA_VALUE_SIZE = 8  # 32-bit float


class ClusterGatewayFilter:
    def __init__(
        self, ip_address: str = SCANER_SERVER_IP, port: int = 65002, buffer_size=1024
    ) -> None:
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
            try:
                data, _ = self.udp_socket.recvfrom(self.buffer_size)
                (
                    rpm,
                    temp,
                    speed,
                    fuel,
                    incident,
                    sagat,
                    left_signal,
                    right_signal,
                    set_num,
                ) = self._parse_data(data)

                self.update(
                    rpm,
                    temp,
                    speed,
                    fuel,
                    incident,
                    sagat,
                    left_signal,
                    right_signal,
                    set_num,
                )
            except socket.timeout:
                print("(Timeout) Waiting for messages...")
                continue
            time.sleep(0.25)
        print("Socket closed")

    def _parse_data(self, data: bytes):
        data_len = len(data)
        if data_len % 8 != 0:
            print("Wrong data format")
            return None

        num_doubles = data_len // 8
        results = struct.unpack("<" + "d" * num_doubles, data)

        return results

    def _send_message(self, message: bytes) -> None:
        self.udp_socket.sendto(message, (self.ip_address, self.port))

    def activate(self):
        print(f"Activating client for server[{self.ip_address}:{self.port}]...")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.ip_address, self.port))
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

    def update(
        self,
        rpm,
        temp,
        speed,
        fuel,
        incident,
        sagat,
        left_signal,
        right_signal,
        set_num,
    ) -> None:
        # print(f"RPM: {rpm}")
        # print(f"Temp: {temp}")
        # print(f"Speed: {speed}")
        # print(f"Fuel: {fuel}")
        # print(f"Incident: {incident}")
        # print(f"Sagat: {sagat}")
        # print(f"Left Signal: {left_signal}")
        # print(f"Right Signal: {right_signal}")
        # print(f"Set Num: {set_num}")
        
        # ------- Example output:
        # RPM: 745.3675537109375
        # Temp: 50.0
        # Speed: 5.609803199768066
        # Fuel: 50.0
        # Incident: inf
        # Sagat: inf
        # Left Signal: 0.0
        # Right Signal: 0.0
        # Set Num: 1.0

        raise NotImplementedError("This method should be implemented in a subclass.")
