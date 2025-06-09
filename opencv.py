import cv2

cap = cv2.VideoCapture("rtsp://camview:camview123@10.150.4.13:554/cam/realmonitor?channel=1")
ret, frame = cap.read()
print("Capture opened:", cap.isOpened())
print("Got frame:", ret)
if ret:
    cv2.imwrite("frame.jpg", frame)
cap.release()
