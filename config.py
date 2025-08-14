caughtGesture = None
recognitionCounter = 0
masterCommandCounter = 0
pressCounter = 0
mode = "r"
mousePressed = False

# Exponential smoothing for cursor
emaX = None
emaY = None
alpha = 0.35

# Click hysteresis thresholds (normalized by hand scale)
clickPressThreshold = 0.22
clickReleaseThreshold = 0.28
clickPressStableCount = 0
clickReleaseStableCount = 0

# Double click gating (normalized by hand scale)
doubleClickThresholdNormalized = 0.26
doubleClickStableCount = 0
doubleClickStableNeeded = 3
doubleClickCooldownFrames = 12
doubleClickCooldownRemaining = 0

commandGestures = {
    'mm': 'Pointing_Up', 
    'r': 'Open_Palm'
}