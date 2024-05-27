import cv2 # type: ignore
import time
import chime
import argparse
from helpers.helperFunctions import get_annotation_from
from helpers.vectors import Palm
import config

parser = argparse.ArgumentParser(description='Script for hand/gesture detection and PC interaction')
parser.add_argument("-f", "--FrameRate", help = "milliseconds for script to wait between analysis",
                   nargs='?',
                   type = float, 
                   default = "0.01")
parser.add_argument("-l", "--FrameLag", help = "frames without gesture to store last gesture in memory, default = 5",
                   nargs='?',
                   type = float, 
                   default = "5")
parser.add_argument("-mf", "--MasterModeFrames", help = "number of frames to keep stored gesture to enter SECRET COMMAND MODE, default = 30, lagging included",
                   nargs='?',
                   type = float, 
                   default = "20")
args = parser.parse_args()

vid = cv2.VideoCapture(0) 
caughtGesture = None

#Basic lagging logic, to store gestures for N frames
def storeLagging(caughtGesture, currentGesture, lag):
    config.recognitionCounter
    if config.caughtGesture == None:
        if currentGesture:
            print(f'first time caught gesture {currentGesture}, stored in memory due to lag rules')
            config.caughtGesture = currentGesture
            config.recognitionCounter += 1
            return caughtGesture
    else:
        if currentGesture != config.caughtGesture:
            config.recognitionCounter += 1
            print(f'gesture {config.caughtGesture} stored due to lag rules for {config.recognitionCounter}/{lag} frames')
            if config.recognitionCounter >= float(lag):
                print(f'no more gesture caught for {lag} frames, gesture {config.caughtGesture} no longer stored')
                config.caughtGesture = None
                config.masterCommandCounter = 0 
                config.recognitionCounter = 0
            return config.caughtGesture
        else:
            config.recognitionCounter = 0 
            print(f'gesture {currentGesture} still on screen, counter set to 0')
            return config.caughtGesture
        
#Entering master mode
def enterMasterMode(caughtGesture, masterFrames): 
    if config.masterCommandCounter >= masterFrames:
        config.masterCommandCounter = 0
        if config.mode == 'r':
            config.mode = 'mm'
            chime.success()
            return print('entering control mode')
        else:
            config.mode = 'r'
            chime.info()
            return print('entering recognition mode')
    elif caughtGesture == config.commandGestures[config.mode]:
        config.masterCommandCounter += 1
        print(f'hold your hand, {config.masterCommandCounter}/{masterFrames}')
        
while True:

    ret, frame = vid.read()
    
    if ret:
        detection_result, annotation, currentGesture = get_annotation_from(cv2.flip(frame, 1), config.mode)
        if detection_result.handedness:
            hand = Palm(detection_result.hand_landmarks[0])
            hand.findCenter()
        command = storeLagging(caughtGesture, currentGesture, args.FrameLag)
        if command:
            enterMasterMode(command, args.MasterModeFrames)
        cv2.imshow('', annotation)  
    else:
        print("! No frame")

    time.sleep(float(args.FrameRate))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release() 
cv2.destroyAllWindows() 