import socket
import threading
import time
from typing import List, Optional

SERVER_IP = "localhost"
DATA_VALUE_SIZE = 8  # 32-bit float

class SensorServer:
    def __init__(
        self,
        ip_address: str = SERVER_IP,
        port: int = 46011,
        buffer_size=1024,
        update_interval=0.25,
    ) -> None:
        self.tcp_socket: Optional[socket.socket] = None
        self.ip_address = ip_address
        self.port = port
        self.buffer_size = buffer_size

        self.is_active = False
        self.update_interval = update_interval
        self.client_threads: List[threading.Thread] = []  # 클라이언트 스레드 목록

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.deactivate()

    def _handle_client(self, client_socket: socket.socket, client_address: tuple) -> None:
        print(f"클라이언트 연결 수락: {client_address}")
        client_socket.settimeout(5.0)  # 클라이언트 소켓 타임아웃 설정
        while self.is_active:
            try:
                data = client_socket.recv(self.buffer_size)
                if not data:
                    print(f"클라이언트 {client_address} 연결 종료")
                    break
                result = self._process_client_request(data)
                self._send_message(result, client_socket)
            except socket.timeout:
                continue
            except ConnectionResetError:
                print(f"클라이언트 {client_address} 연결이 리셋되었습니다.")
                break
            except Exception as e:
                print(f"클라이언트 {client_address} 처리 중 오류 발생: {e}")
                break
            time.sleep(self.update_interval)
        client_socket.close()

    def _send_message(self, results: bytes, client_socket: socket.socket) -> None:
        client_socket.sendall(results)

    def _process_client_request(self, data: bytes) -> bytes:
        raise NotImplementedError("Client request should be processed in a subclass")

    def activate(self):
        print(f"서버 활성화 중 [{self.ip_address}:{self.port}]...")
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.ip_address, self.port))
        self.tcp_socket.listen()
        self.is_active = True
        self.accept_thread = threading.Thread(target=self._accept_clients)
        self.accept_thread.start()
        print("서버가 활성화되었습니다!")

    def _accept_clients(self):
        print("클라이언트 연결 대기 중...")
        while self.is_active:
            try:
                client_socket, client_address = self.tcp_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client, args=(client_socket, client_address)
                )
                client_thread.start()
                self.client_threads.append(client_thread)
            except OSError as e:
                print(f"소켓 에러 발생: {e}")
                break

    def deactivate(self):
        self.is_active = False
        print("서버 종료 중...")
        # 모든 클라이언트 소켓 닫기
        for thread in self.client_threads:
            thread.join()
        self.tcp_socket.close()
        self.accept_thread.join()
        print("서버가 종료되었습니다!")