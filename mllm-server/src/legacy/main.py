import serial
import struct
import numpy as np

# 시리얼 포트 설정 (포트 이름은 환경에 맞게 수정하세요)
SERIAL_PORT = 'COM4'  # 또는 '/dev/ttyUSB0' 등
BAUD_RATE = 115200

def parse_packet(packet):
    # 패킷 구조: [0x23][메시지 ID][서브 ID][데이터 바이트 2바이트]
    if len(packet) != 5:
        return None

    start_byte, msg_id, sub_id, data_high, data_low = packet
    if start_byte != 0x23:
        return None

    data_hex = '{:02X} {:02X}'.format(data_high, data_low)

    # 16비트 정수 (Big-endian)
    data_int = struct.unpack('>h', bytes([data_high, data_low]))[0]

    # 16비트 부동소수점 (FP16)
    # FP16은 numpy의 float16 사용
    data_bytes = bytes([data_high, data_low])
    data_fp16 = np.frombuffer(data_bytes, dtype='>f2')[0]

    # 결과 반환
    return {
        'msg_id': msg_id,
        'sub_id': sub_id,
        'data_hex': data_hex,
        'data_int': data_int,
        'data_fp16': data_fp16
    }

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    # 패킷을 저장할 버퍼
    buffer = bytearray()

    try:
        while True:
            # 시리얼로부터 데이터 읽기
            data = ser.read(1)
            if not data:
                continue

            buffer += data

            # 패킷의 시작 바이트(0x23)를 찾음
            if buffer[0] != 0x23:
                buffer = buffer[1:]  # 시작 바이트까지 버퍼를 이동
                continue

            # 패킷이 완전한지 확인
            if len(buffer) >= 5:
                packet = buffer[:5]
                buffer = buffer[5:]  # 처리한 패킷은 버퍼에서 제거

                result = parse_packet(packet)
                if result:
                    msg_id = result['msg_id']
                    sub_id = result['sub_id']
                    data_hex = result['data_hex']
                    data_int = result['data_int']
                    data_fp16 = result['data_fp16']

                    print(f"{msg_id:02X}-{sub_id:02X}: {data_hex}, {data_int}, {data_fp16}")
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
