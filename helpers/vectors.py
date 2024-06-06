import numpy as np

class Palm:

    def __init__(self, hand):
        self.hand = hand

        self.big = hand[4]
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
        self.bottom = hand[0]

    def findCenter(self):
        x = [knuckle.x for knuckle in self.knuckles]
        y = [knuckle.y for knuckle in self.knuckles]
        centroid = (sum(x) / 4, sum(y) / 4)
        return centroid
    
    def getIndexBigDistance(self):

        p1 = np.array([self.big.x, self.big.y, self.big.z])
        p2 = np.array([self.index.x, self.index.y, self.index.z])
        squared_dist = np.sum((p1-p2)**2, axis=0)
        distance= np.sqrt(squared_dist)
        
        return distance


    def getY(self):
        return [self.index.y, self.middle.y, self.ring.y, self.little.y]
        

#Future steps for apple vision employment
def get_index_finger_coordinates(detection_result, gestureConditionMet):
    if gestureConditionMet:
        return print(detection_result.hand_landmarks[0])