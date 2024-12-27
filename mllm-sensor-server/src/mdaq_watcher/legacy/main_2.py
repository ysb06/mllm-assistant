import serial
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import seaborn as sns  # seaborn 임포트

# 시리얼 포트 설정 (포트 이름은 환경에 맞게 수정하세요)
SERIAL_PORT = 'COM4'  # 또는 '/dev/ttyUSB0' 등
BAUD_RATE = 115200

# 그래프 설정
PLOT_WINDOW_SIZE = 100  # 그래프에 표시할 데이터 포인트 수

# 대상 Message ID 설정
target_id = 0x53  # 원하는 Message ID로 변경하세요
# [45 = Digital, 42 = Analogue, 53]


# seaborn 스타일 적용
sns.set()

# 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows인 경우
# plt.rcParams['font.family'] = 'AppleGothic'   # macOS인 경우
# plt.rcParams['font.family'] = 'NanumGothic'   # Linux 또는 해당 폰트가 설치된 경우
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 부호 깨짐 방지

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

    # 데이터 저장을 위한 딕셔너리
    buffers = {}

    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle('실시간 데이터 시각화')

    # 애니메이션 업데이트 함수
    def update(frame):
        # 시리얼로부터 데이터 읽기
        while ser.in_waiting:
            data = ser.read(1)
            if not data:
                continue

            # 패킷을 저장할 버퍼
            buffer = bytearray()
            buffer += data

            # 시작 바이트 확인
            if buffer[0] != 0x23:
                continue

            # 나머지 패킷 데이터 읽기
            buffer += ser.read(4)
            if len(buffer) < 5:
                continue

            result = parse_packet(buffer)
            if result:
                msg_id = result['msg_id']
                sub_id = result['sub_id']
                data_int = result['data_int']
                data_fp16 = result['data_fp16']

                # target_id와 Message ID가 일치하는 경우에만 처리
                if msg_id == target_id:
                    key = (msg_id, sub_id)
                    if key not in buffers:
                        buffers[key] = {
                            'int': deque(maxlen=PLOT_WINDOW_SIZE),
                            'fp16': deque(maxlen=PLOT_WINDOW_SIZE)
                        }

                    buffers[key]['int'].append(data_int)
                    buffers[key]['fp16'].append(data_fp16)

        # 그래프 초기화
        axs[0].cla()
        axs[1].cla()

        # 대상 Message ID의 데이터만 그래프 그리기
        for key, data in buffers.items():
            msg_id, sub_id = key
            label = f"Sub ID:{sub_id:02X}"

            # 정수형 데이터 그래프
            axs[0].plot(data['int'], label=label)
            # 부동소수점 데이터 그래프
            axs[1].plot(data['fp16'], label=label)

        axs[0].set_title(f'16비트 정수 데이터 (Message ID: {target_id:02X})')
        axs[0].set_ylabel('값')
        axs[0].legend(loc='upper left')

        axs[1].set_title(f'16비트 부동소수점 데이터 (Message ID: {target_id:02X})')
        axs[1].set_ylabel('값')
        axs[1].legend(loc='upper left')

        plt.tight_layout()

    ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)

    try:
        plt.show()
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
