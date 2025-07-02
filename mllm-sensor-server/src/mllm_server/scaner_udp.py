import logging
import socket
import struct
import threading
import time
from collections import deque
from typing import Dict, List, Optional

SERVER_IP = "192.168.1.3"
SERVER_PORT = 46012
DATA_VALUE_SIZE = 8  # 64-bit double

logger = logging.getLogger(__name__)

class ScanerFilterServer:
    def __init__(
        self,
        filter_ip: str = SERVER_IP,
        filter_port: int = SERVER_PORT,
        data_size: int = DATA_VALUE_SIZE,
        timeout: float = 5,
        buffer_size: int = 2048,
    ) -> None:
        logger.info(f"SCANeR Server: {filter_ip}:{filter_port}")

        self.filter_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.filter_address = (filter_ip, filter_port)
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.data_size = data_size  # 센서 데이터 단위 크기 (8바이트)
        self.filter_udp_socket.settimeout(self.timeout)
        
        self._scaner_steering_angles = deque([0.0] * 20, maxlen=20)
        self._scaner_speeds = deque([0.0] * 20, maxlen=20)
        
        self.is_active = False
        self.filter_thread: Optional[threading.Thread] = None
    
    def _parse_scaner_data(self, values: tuple) -> Dict[int, float]:
        results = {}
        
        # 값들을 2개씩 묶어서 처리 (key, value 쌍)
        for i in range(0, len(values) - 1, 2):
            key_value = values[i]
            data_value = values[i + 1]
            
            # 무한대 값은 유효하지 않은 키로 간주하고 건너뛰기
            if key_value in (float('inf'), float('-inf')):
                continue
                
            key = int(key_value)
            results[key] = data_value
            
        return results

    def _update_scaner_data(self) -> None:
        logger.info("Updating SCANeR data via UDP...")
        data_received = False
        while self.is_active:
            try:
                data, _ = self.filter_udp_socket.recvfrom(self.buffer_size)
                # '<' : little-endian, "d" : 64-bit double
                values = struct.unpack("<" + "d" * (len(data) // self.data_size), data)
                
                results = self._parse_scaner_data(values)
                self._process_scaner_data(results)

                # logger.info(f"SCANeR data received: {results}")
                if not data_received:
                    data_received = True
                    logger.info(f"SCANeR is running...")
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received, stopping SCANeR data update...")
                self.is_active = False
                break
            except socket.timeout:
                logger.info(f"(Timeout) Waiting for messages from SCANeR...")
                data_received = False
                continue
            except OSError as e:
                logger.error(f"The socket may be closed: {e}")
                break

    def _process_scaner_data(self, data: Dict[int, float]) -> None:
        if 167 in data:
            self._scaner_steering_angles.append(data[167])

        if 120 in data:
            self._scaner_speeds.append(data[120])

    def activate(self):
        logger.info("Activating SCANeR server (UDP Receiver)...")

        try:
            self.filter_udp_socket.bind(self.filter_address)
            self.filter_thread = threading.Thread(target=self._update_scaner_data)
            self.filter_thread.start()
            self.is_active = True
        except OSError as e:
            logger.error(f"May failed to bind UDP socket: {e}")
            self.is_active = False
            return

    def deactivate(self):
        logger.info("Deactivating SCANeR server...")

        self.is_active = False
        self.filter_udp_socket.close()
        if self.filter_thread:
            self.filter_thread.join()

        logger.info("SCANeR server deactivated.")

    def get_sensor_data(self) -> Dict[str, List[float]]:
        """
        현재 센서 데이터(최근 스티어링 각도와 속도 목록)를 반환합니다.
        반환 예:
          {
            "steering": [0.0, 1.2, 3.4, ...],
            "speed": [0.0, 5.6, 7.8, ...]
          }
        """
        return {
            "steering": list(self._scaner_steering_angles),
            "speed": list(self._scaner_speeds),
        }