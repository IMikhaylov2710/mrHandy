import numpy as np

def calculateGradient(fingerArray):
    y = np.array([fingerArray], dtype=np.float)
    diff = np.gradient(y)
    return diff