import cv2 # type: ignore
import time
import chime
import argparse
from helpers.helperFunctions import get_annotation_from, infer_gesture_from_landmarks
from helpers.control import moveMouse, releaseMouse, pressMouse, doubleClickMouse
from helpers.vectors import Palm
from helpers.mouse_adapters import get_mouse_adapter
from screeninfo import get_monitors
from datetime import datetime
import config
from PIL import ImageEnhance

parser = argparse.ArgumentParser(description='Script for hand/gesture detection and PC interaction')
parser.add_argument("-f", "--FrameRate", help = "seconds for script to wait between frames (sleep)",
                   nargs = '?',
                   type = float, 
                   default = 0.0)
parser.add_argument("-l", "--FrameLag", help = "frames without gesture to store last gesture in memory, default = 5",
                   nargs = '?',
                   type = float, 
                   default = 5.0)
parser.add_argument("-mf", "--MasterModeFrames", help = "number of frames to keep stored gesture to enter master mode, default = 20, lagging included",
                   nargs = '?',
                   type = float, 
                   default = 20.0)
parser.add_argument("-cf", "--clickFrames", help = "number of stable frames for press/release/double-click gating, default = 3",
                    nargs = '?', 
                    type = int, 
                    default = 3)
parser.add_argument("--muffle", action="store_true", help = "use this flag to turn sound notification off")
parser.add_argument("--centroid", action="store_true", help = "use this flag for mouse to follow center of your knuckles")
parser.add_argument("--contrast", action="store_true", help = "use this flag enhance contrast of image. WARNING! Still in beta")
parser.add_argument("--brightness", action="store_true", help = "use this flag to reduce brightness of image")
parser.add_argument("--noCorr", action="store_true", help = "use this flag to not perform correction of coordinates")
parser.add_argument("--log", action="store_true", help = "use this flag to log all actions")
parser.add_argument("--heuristic", action="store_true", help = "use lightweight heuristic for gesture detection instead of model (faster)")
args = parser.parse_args()

if __name__ == "__main__":
    vid = cv2.VideoCapture(0)
    # Attempt to reduce latency and set a reasonable resolution
    try:
        vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        vid.set(cv2.CAP_PROP_FPS, 30)
        vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    caughtGesture = None
    newMouse = get_mouse_adapter()

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

start_time = time.perf_counter()

def smooth_to(x, y):
    if config.emaX is None or config.emaY is None:
        config.emaX = x
        config.emaY = y
    else:
        config.emaX = config.alpha * x + (1.0 - config.alpha) * config.emaX
        config.emaY = config.alpha * y + (1.0 - config.alpha) * config.emaY
    return config.emaX, config.emaY

while True:

    ret, frame = vid.read()
    
    if ret:
        # Timestamp for MediaPipe VIDEO mode
        timestamp_ms = int((time.perf_counter() - start_time) * 1000)
        working_frame = frame
        if args.contrast:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit = 4.0, tileGridSize = (4,4))
            cl = clahe.apply(l_channel)
            limg = cv2.merge((cl,a,b))
            enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
            working_frame = enhanced_img
        elif args.brightness:
            img_enhancer = ImageEnhance.Brightness(frame)
            enhanced_output = img_enhancer.enhance(factor) 
            working_frame = enhanced_output
        # Flip for mirror-like experience
        working_frame = cv2.flip(working_frame, 1)
        # Skip gesture recognition while in master mode to save compute
        do_gesture = config.mode != 'mm'
        detection_result, annotation, currentGesture = get_annotation_from(working_frame, config.mode, timestamp_ms, do_gesture=(do_gesture and not args.heuristic))
        
        # If heuristic mode, derive gesture from landmarks
        if args.heuristic and do_gesture:
            currentGesture = infer_gesture_from_landmarks(detection_result)
        
        # Store and possibly switch modes
        if do_gesture:
            storeLagging(currentGesture, args.FrameLag, args.log)
        if config.caughtGesture:
            enterMasterMode(config.caughtGesture, args.MasterModeFrames)

        if detection_result and detection_result.handedness:
            hand = Palm(detection_result.hand_landmarks[0])
            # Choose pointer reference
            if args.centroid:
                X_norm, Y_norm = hand.findCenter()
            else:
                X_norm, Y_norm = hand.bottom.x, hand.bottom.y

            # Optional linear correction to stretch central 60% to full screen
            if args.noCorr:
                X_abs = max(0.0, min(1.0, X_norm)) * width
                Y_abs = max(0.0, min(1.0, Y_norm)) * height
            else:
                # Map [0.2,0.8] -> [0,1] and clamp
                X_corrected = (X_norm - 0.2) / 0.6
                Y_corrected = (Y_norm - 0.2) / 0.6
                X_abs = max(0.0, min(1.0, X_corrected)) * width
                Y_abs = max(0.0, min(1.0, Y_corrected)) * height

            # Smooth cursor to reduce jitter
            X_smooth, Y_smooth = smooth_to(X_abs, Y_abs)
            moveMouse(X_smooth, Y_smooth, newMouse)

            # Normalized distances for robust thresholds
            leftDistanceN = hand.getIndexBigDistanceNormalized()
            middleDistanceN = hand.getMiddleBigDistanceNormalized()

            # Click press/release with hysteresis and stability gating
            if not config.mousePressed:
                if leftDistanceN < config.clickPressThreshold:
                    config.clickPressStableCount += 1
                else:
                    config.clickPressStableCount = 0
                if config.clickPressStableCount >= int(args.clickFrames):
                    pressMouse(newMouse)
                    config.mousePressed = True
                    config.clickPressStableCount = 0
                    if not args.muffle:
                        chime.info()
            else:
                if leftDistanceN > config.clickReleaseThreshold:
                    config.clickReleaseStableCount += 1
                else:
                    config.clickReleaseStableCount = 0
                if config.clickReleaseStableCount >= int(args.clickFrames):
                    releaseMouse(newMouse)
                    config.mousePressed = False
                    config.clickReleaseStableCount = 0
                    if not args.muffle:
                        chime.info()

            # Double click detection with cooldown
            if config.doubleClickCooldownRemaining > 0:
                config.doubleClickCooldownRemaining -= 1
            if (not config.mousePressed and config.doubleClickCooldownRemaining == 0):
                if middleDistanceN < config.doubleClickThresholdNormalized:
                    config.doubleClickStableCount += 1
                else:
                    config.doubleClickStableCount = 0
                if config.doubleClickStableCount >= int(args.clickFrames):
                    doubleClickMouse(newMouse)
                    config.doubleClickStableCount = 0
                    config.doubleClickCooldownRemaining = config.doubleClickCooldownFrames
        
        cv2.imshow('', annotation)  
    else:
        print("! No frame")
        break

    if args.FrameRate and args.FrameRate > 0:
        time.sleep(float(args.FrameRate))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        releaseMouse(newMouse)
        break

vid.release() 
cv2.destroyAllWindows() 