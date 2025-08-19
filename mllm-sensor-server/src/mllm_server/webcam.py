import cv2
import base64
import logging

logger = logging.getLogger(__name__)

# 웹캠 캡처 객체 생성
cap = cv2.VideoCapture(0)
logger.info("Webcam initialized")

def capture_webcam_image():
    # 프레임 읽기
    _, frame = cap.read()

    cv2.imshow('Webcam', frame)
    cv2.waitKey()
    cv2.destroyAllWindows()
    
    _, buffer = cv2.imencode('.jpg', frame)
    base64_jpg = base64.b64encode(buffer)

    return base64_jpg