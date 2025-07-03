import cv2
import base64

# 웹캠 캡처 객체 생성
cap = cv2.VideoCapture(0)

def capture_webcam_image():
    # 프레임 읽기
    _, frame = cap.read()
    _, buffer = cv2.imencode('.jpg', frame)
    base64_jpg = base64.b64encode(buffer)

    return base64_jpg