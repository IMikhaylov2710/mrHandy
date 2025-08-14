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
    
    def _distance3(self, a, b):
        p1 = np.array([a.x, a.y, a.z])
        p2 = np.array([b.x, b.y, b.z])
        squared_dist = np.sum((p1 - p2) ** 2, axis=0)
        return float(np.sqrt(squared_dist))

    def _distance2(self, a, b):
        p1 = np.array([a.x, a.y])
        p2 = np.array([b.x, b.y])
        squared_dist = np.sum((p1 - p2) ** 2, axis=0)
        return float(np.sqrt(squared_dist))
    
    def estimate_scale(self):
        # Use horizontal span across MCPs and wrist-to-middle MCP distance as robust scale
        span_knuckles = self._distance2(self.firstKnuckle, self.fourthKnuckle)
        wrist_to_middle = self._distance2(self.bottom, self.secondKnuckle)
        scale = max(span_knuckles, wrist_to_middle)
        if scale <= 1e-6:
            scale = 1e-3
        return scale
    
    def getIndexBigDistance(self):

        p1 = np.array([self.big.x, self.big.y, self.big.z])
        p2 = np.array([self.index.x, self.index.y, self.index.z])
        squared_dist = np.sum((p1-p2)**2, axis=0)
        distance = np.sqrt(squared_dist)
        
        return distance
    
    def getMiddleBigDistance(self):

        p1 = np.array([self.big.x, self.big.y, self.big.z])
        p2 = np.array([self.middle.x, self.middle.y, self.middle.z])
        squared_dist = np.sum((p1-p2)**2, axis=0)
        distance = np.sqrt(squared_dist)
        
        return distance

    def getIndexBigDistanceNormalized(self):
        return self.getIndexBigDistance() / self.estimate_scale()

    def getMiddleBigDistanceNormalized(self):
        return self.getMiddleBigDistance() / self.estimate_scale()


    def getY(self):
        return [self.index.y, self.middle.y, self.ring.y, self.little.y]
        

#Future steps for apple vision employment
def get_index_finger_coordinates(detection_result, gestureConditionMet):
    if gestureConditionMet:
        return print(detection_result.hand_landmarks[0])