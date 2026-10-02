import cv2
import numpy as np

def decode_qr(data: bytes):
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None: return []
    detector = cv2.QRCodeDetector()
    value, points, _ = detector.detectAndDecode(image)
    return [value] if value else []
