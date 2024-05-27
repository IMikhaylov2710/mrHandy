import pandas as pd

class Palm:

    def __init__(self, hand):
        self.hand = hand
        self.index = hand[8]
        self.middle = hand[12]
        self.ring = hand[16]
        self.little = hand[20]

        self.firstKnuckle = hand[5]
        self.secondKnuckle = hand[9]
        self.thirdKnuckle = hand[13]
        self.fourthKnuckle = hand[17]

        self.knuckles = [
            self.firstKnuckle, 
            self.secondKnuckle, 
            self.thirdKnuckle, 
            self.fourthKnuckle
        ]

    def findCenter(self):
        x = [knuckle.x for knuckle in self.knuckles]
        y = [knuckle.y for knuckle in self.knuckles]
        centroid = (sum(x) / 4, sum(y) / 4)
        print(centroid)
        return centroid

#Future steps for apple vision employment
def get_index_finger_coordinates(detection_result, gestureConditionMet):
    if gestureConditionMet:
        return print(detection_result.hand_landmarks[0])
    
#Emulate click

#Get positions of 