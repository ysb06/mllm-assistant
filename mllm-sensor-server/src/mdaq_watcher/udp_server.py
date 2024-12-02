import socket
import struct
from typing import Optional
import threading
import time
import mdaq_watcher.mdaq as mdaq

MDAQ_SERVER_IP = "192.168.1.2"
MDAQ_SERVER_PORT = 3232
REQUEST_MESSAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00"
DATA_VALUE_SIZE = 4  # 32-bit float
FLOAT_SIZE = 9


def open_server():
    with mdaq.MdaqClient() as mdaq_client:
        while True:
            try:
                time.sleep(0.25)
            except KeyboardInterrupt:
                print("Exiting...")
                break


if __name__ == "__main__":
    open_server()
