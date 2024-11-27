import socket

# INNO MDAQ 데이터 수신 프로그램
# 실행 시, 현재 센서들의 값들을 모두 

def send_and_receive_udp_message(message: bytes, server_ip: str = 'localhost', port: int = 3232, buffer_size: int = 1024) -> None:
    # UDP 소켓 생성
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        server_address = (server_ip, port)
        
        # 메시지 전송
        print(f"Sending message to {server_ip}:{port}")
        udp_socket.sendto(message, server_address)
        
        # 서버로부터 응답 대기
        try:
            # 응답 수신
            data, addr = udp_socket.recvfrom(buffer_size)
            print(f"Received response from {addr}: {data}")
            print("-"*12)
            print(data.hex(sep=" "))
        except socket.timeout:
            print("No response received within the timeout period.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 송신할 메시지: b'\x00\x00\x00\x00\x00\x00\x00\x00'
    message = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    # Note: 메시지 값에 따라 다르게 반환하는 것 같지만 어떻게 달라지는지는 모르겠음
    # Note: 통신 구조를 어떻게 알아냈는지는 잊어버렸지만 MDAQ 대신 가짜 서버를 만들어서 수신된 데이터를 분석했던 것 같음
    
    # UDP 메시지 전송 및 응답 수신
    send_and_receive_udp_message(message)
