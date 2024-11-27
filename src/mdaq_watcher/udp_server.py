import socket
import struct
from typing import Optional
import threading
import time

MDAQ_SERVER_IP = "192.168.1.2"
MDAQ_SERVER_PORT = 3232
REQUEST_MESSAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00"
DATA_VALUE_SIZE = 4  # 32-bit float
FLOAT_SIZE = 9


def open_server():
    pass


if __name__ == "__main__":
    open_server()
