import cv2
import mediapipe as mp
import numpy as np
import os
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from helpers.helperFunctions import draw_landmarks_on_image, get_annotation_from

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