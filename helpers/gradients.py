import numpy as np

#function for gradient calculation for smootheness, fututre steps
def calculateGradient(fingerArray):
    y = np.array([fingerArray], dtype=np.float)
    diff = np.gradient(y)
    return diff