import cv2 # type: ignore
import time
import chime
import macmouse
import argparse
from helpers.helperFunctions import get_annotation_from
from helpers.control import moveMouse, releaseMouse, pressMouse
from helpers.vectors import Palm
from screeninfo import get_monitors
from datetime import datetime
import config
from PIL import ImageEnhance

parser = argparse.ArgumentParser(description='Script for hand/gesture detection and PC interaction')
parser.add_argument("-f", "--FrameRate", help = "milliseconds for script to wait between analysis",
                   nargs = '?',
                   type = float, 
                   default = "0.05")
parser.add_argument("-l", "--FrameLag", help = "frames without gesture to store last gesture in memory, default = 5",
                   nargs = '?',
                   type = float, 
                   default = "5")
parser.add_argument("-mf", "--MasterModeFrames", help = "number of frames to keep stored gesture to enter master mode, default = 20, lagging included",
                   nargs = '?',
                   type = float, 
                   default = "20")
parser.add_argument("-cf", "--clickFrames", help = "number of frames for detection during mouse click and mouse release events, default to 3",
                    nargs = '?', 
                    type = float, 
                    default = 2.0)
parser.add_argument("--muffle", action="store_true", help = "use this flag to turn sound notification off")
parser.add_argument("--centroid", action="store_true", help = "use this flag for mouse to follow center of your knuckles")
parser.add_argument("--contrast", action="store_true", help = "use this flag enhance contrast of image. WARNING! Still in beta")
parser.add_argument("--brightness", action="store_true", help = "use this flag to reduce brightness of image")
parser.add_argument("--noCorr", action="store_true", help = "use this flag to not perform correction of coordinates")
parser.add_argument("--log", action="store_true", help = "use this flag to log all actions")
args = parser.parse_args()

if __name__ == "__main__":
    vid = cv2.VideoCapture(0) 
    caughtGesture = None
    newMouse = macmouse

#Basic lagging logic, to store gestures for N frames
def storeLagging(currentGesture, lag, log):
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
                chime.success()
            config.mode = 'r'
    elif caughtGesture == config.commandGestures[config.mode]:
        config.masterCommandCounter += 1
        if args.log:
            print(f'hold your hand, {config.masterCommandCounter}/{masterFrames}')

#Lag mouse press/release
def lagPressStatus(mouse):
    if config.pressCounter >= 1:
        releaseMouse(mouse)
        config.mousePressed = False
        if not args.muffle:
            chime.info()
        config.pressCounter = 0
    else:
        config.pressCounter += 1

monitors = get_monitors()
width = monitors[0].width
height = monitors[0].height
factor = 0.5

while True:

    ret, frame = vid.read()
    
    if ret:
        if args.contrast:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit = 4.0, tileGridSize = (4,4))
            cl = clahe.apply(l_channel)
            limg = cv2.merge((cl,a,b))
            enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
            detection_result, annotation, currentGesture = get_annotation_from(cv2.flip(enhanced_img, 1), config.mode)
            cv2.imshow('', annotation)
        elif args.brightness:
            img_enhancer = ImageEnhance.Brightness(frame)
            enhanced_output = img_enhancer.enhance(factor) 
            detection_result, annotation, currentGesture = get_annotation_from(cv2.flip(enhanced_output, 1), config.mode)
        else:
            detection_result, annotation, currentGesture = get_annotation_from(cv2.flip(frame, 1), config.mode)
            storeLagging(currentGesture, args.FrameLag, args.log)
            if detection_result.handedness:
                if config.mode == 'mm':
                    hand = Palm(detection_result.hand_landmarks[0])
                    if args.centroid:
                        X_centroid, Y_centroid = hand.findCenter()
                        X_abs = width * X_centroid
                        Y_abs = height * Y_centroid
                    else:
                        if 0.2 < hand.bottom.x < 0.8 and 0.2 < hand.bottom.y < 0.8:
                            X_abs = hand.bottom.x - 0.2
                            Y_abs = hand.bottom.y - 0.2
                            X_corrected = X_abs * (float(width)**2 / (float(width) * 0.6))
                            Y_corrected = Y_abs * (float(height)**2 / (float(height) * 0.6))
                    moveMouse(X_corrected, Y_corrected, newMouse)
                    distance = hand.getIndexBigDistance()
                    if distance < 0.1:
                        if config.mousePressed:
                            config.pressCounter = 0
                        else:
                            pressMouse(newMouse)
                            config.mousePressed = True
                            if not args.muffle:
                                chime.info()
                    elif config.mousePressed:
                        lagPressStatus(newMouse)
            if config.caughtGesture:
                enterMasterMode(config.caughtGesture, args.MasterModeFrames)
            cv2.imshow('', annotation)  
    else:
        print("! No frame")
        break

    time.sleep(float(args.FrameRate))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        releaseMouse(newMouse)
        break

vid.release() 
cv2.destroyAllWindows() 