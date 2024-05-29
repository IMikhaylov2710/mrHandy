import cv2 # type: ignore
import time
import chime
import macmouse
import argparse
from helpers.helperFunctions import get_annotation_from
from helpers.control import moveMouse, clickMouse, releaseMouse
from helpers.vectors import Palm
from screeninfo import get_monitors
from datetime import datetime
import config

parser = argparse.ArgumentParser(description='Script for hand/gesture detection and PC interaction')
parser.add_argument("-f", "--FrameRate", help = "milliseconds for script to wait between analysis",
                   nargs = '?',
                   type = float, 
                   default = "0.01")
parser.add_argument("-l", "--FrameLag", help = "frames without gesture to store last gesture in memory, default = 5",
                   nargs = '?',
                   type = float, 
                   default = "5")
parser.add_argument("-mFrames", "--MasterModeFrames", help = "number of frames to keep stored gesture to enter master mode, default = 20, lagging included",
                   nargs = '?',
                   type = float, 
                   default = "20")
parser.add_argument("-cFrames", "--clickFrames", help = "number of frames for detection during mouse click and mouse release events, default to 3",
                    nargs = '?', 
                    type = float, 
                    default = 3.0)
parser.add_argument("--muffle", action="store_true", help = "use this flag to turn sound notification off")
parser.add_argument("--log", action="store_true", help = "use this flag to log all actions")
args = parser.parse_args()

if __name__ == "__main__":
    vid = cv2.VideoCapture(0) 
    caughtGesture = None
    newMouse = macmouse

#Basic lagging logic, to store gestures for N frames
def storeLagging(currentGesture, lag, log):
    config.recognitionCounter
    if config.caughtGesture == None:
        if currentGesture:
            if log:
                print(f'first time caught gesture {currentGesture}, stored in memory due to lag rules at {datetime.now()}')
            config.caughtGesture = currentGesture
            config.recognitionCounter += 1
    elif currentGesture != config.caughtGesture:
        config.recognitionCounter += 1
        if log:
            print(f'gesture {config.caughtGesture} stored due to lag rules for {config.recognitionCounter}/{lag} frames at {datetime.now()}')
        if config.recognitionCounter >= float(lag):
            if log:
                print(f'no more gesture caught for {lag} frames, gesture {config.caughtGesture} no longer stored at {datetime.now()}')
            config.caughtGesture = None
            config.masterCommandCounter = 0 
            config.recognitionCounter = 0
    else:
        config.recognitionCounter = 0 
        if log:
            print(f'gesture {currentGesture} still on screen, counter set to 0 at {datetime.now()}')
        
#Entering master mode
def enterMasterMode(caughtGesture, masterFrames): 
    if config.masterCommandCounter >= masterFrames:
        config.masterCommandCounter = 0
        if config.mode == 'r':
            if not args.muffle:
                chime.success()
            config.mode = 'mm'
        else:
            if not args.muffle:
                chime.info()
            config.mode = 'r'
    elif caughtGesture == config.commandGestures[config.mode]:
        config.masterCommandCounter += 1
        print(f'hold your hand, {config.masterCommandCounter}/{masterFrames}')

#Looking for a click
def catchClick(gesture, open, mouse, frames):
    print(config.forClick)
    if open and gesture == 'Closed_Fist':
        config.forClick += 1
        if config.forClick >= frames:
            clickMouse(mouse)
            open = False
            config.forClick = 0 
            print('==========CLICKED MF!!!!============')
    elif gesture == 'Open_Palm':
        config.forClic += 1
        if config.forClick >= frames:
            releaseMouse(mouse)
            open = True
            config.forClick = 0
            print('==========RELEASED MF!!!!===========')
    else:
        config.forClick = 0

monitors = get_monitors()
width = monitors[0].width
height = monitors[0].height

while True:

    ret, frame = vid.read()
    
    if ret:
        detection_result, annotation, currentGesture = get_annotation_from(cv2.flip(frame, 1), config.mode)
        storeLagging(currentGesture, args.FrameLag, args.log)
        if detection_result.handedness:
            if config.mode == 'mm':
                hand = Palm(detection_result.hand_landmarks[0])
                X_centroid, Y_centroid = hand.findCenter()
                X_abs = width * X_centroid
                Y_abs = height * Y_centroid
                moveMouse(X_abs, Y_abs, newMouse)
                catchClick(config.caughtGesture, True, newMouse, args.clickFrames)
        if config.caughtGesture:
            enterMasterMode(config.caughtGesture, args.MasterModeFrames)
        cv2.imshow('', annotation)  
    else:
        print("! No frame")
        break

    time.sleep(float(args.FrameRate))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release() 
cv2.destroyAllWindows() 