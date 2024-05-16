import cv2
import time
from helpers.helperFunctions import get_annotation_from

vid = cv2.VideoCapture(0) 

while True:

    ret, frame = vid.read()
    
    if ret:
        detection_result, annotation = get_annotation_from(cv2.flip(frame, 1))
        cv2.imshow('', annotation)  
    else:
        print("! No frame")

    time.sleep(0.02)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release() 
cv2.destroyAllWindows() 