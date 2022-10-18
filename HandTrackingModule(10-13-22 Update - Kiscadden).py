import cv2 #To install in terminal:  pip install opencv-python 
import mediapipe as mp #To ins pip install mediapipe
import time
import math
import random

'''Resource: Countdown code in the main function was acquired by
https://www.geeksforgeeks.org/set-countdown-timer-to-capture-image-using-python-opencv/

Resource: initial Hand recognition program
https://google.github.io/mediapipe/solutions/hands.html
'''

#Version 10-13-22
# Included with class documentation
class handDetector():
    def __init__(self, mode=False, maxHands = 2, modelComplex=1, detectionConf = 0.5, trackConf = 0.5):

        #Initializing instance variables
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplex
        self.detectionConf = detectionConf
        self.trackConf = trackConf

        #setting up hands stuff for mediapipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionConf, self.trackConf)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4,8,12,16,20] #ids of the fingertips

    # Included with class documentation
    def findHands(self, img, draw = True): # Initializes the hand tracking
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Converts image so that cv2 can read it properly
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks: #If it sees a hand, and draw is true, it will draw landmarks on the hand
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    # Included with class documentation
    def findPosition(self, img, handNum=0, draw = True):
        xList = []
        yList = []
        #zList = []
        bbox = []
        self.lmList = [] # Important list which holds the ID, x-coor, y-coor, z-coor of each data point on the hand
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNum] #Defines which hand you're talking about, 
                                                                #within that hand it will put the landmarks in a list below
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x*w), int(lm.y*h), int(lm.z*1000)
                xList.append(cx)
                yList.append(cy)
                #zList.append(cz) #Currently don't need depth
                self.lmList.append([id, cx, cy, cz]) #Adding landmark position to lmList
                if draw:
                     cv2.circle(img, (cx,cy), 5, (0, 215, 255), cv2.FILLED)
            xMin, xMax = min(xList), max(xList) # min and max vals of hand for bounding box
            yMin, yMax = min(yList), max(yList)
            bbox = xMin, yMin, xMax, yMax # Bounding box
            if (draw):
                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0,255,0), 2) # Bounding box rectangle

        return self.lmList, bbox

    #Method returns a tuple of length 5 with the fingers that are currently up. 0 in the tuple stands for down, 1 stands for up.
    def getFingers(self):
        fingers = []
        # Thumb
        fingers.append(0) # decided not to check the thumb for identification of the rock, paper, or scissor
        
        # 4 Fingers
        #Checks the distance between the bottom of the palm and the tip of each finger in comparison to the bottom of palm and top of palm. If the tip of the finger is over the palm it is considered down
        for id in range(2,6):
            if self.findDist(self.lmList[0][1], self.lmList[0][2],  self.lmList[id*4][1],  self.lmList[id*4][2]) > self.findDist(self.lmList[0][1], self.lmList[0][2],  self.lmList[9][1],  self.lmList[9][2]):
                fingers.append(1)
            else:
                fingers.append(0)
        
        
        return fingers
        #Return example [1,1,1,1,1] all five fingers are up
        #               [0,0,0,0,0] all five fingers are down
        #               [0,1,1,0,0] Pointer finger and middle finger up
        #               [0,1,0,0,1] Pointer and pinky finger are up
        
    #Created methods
    def allFingersUp(self):
        fingers = self.getFingers()
        # Thumb
        print(fingers) # for debugging purposes to see th tuple output in the console
        if ((fingers[1] and fingers[2] and fingers[3] and fingers[4])):
            return True
        return False

    def isFist(self):
        fingers = self.getFingers()
        print(fingers) # for debugging purposes to see th tuple output in the console
        if (not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]):
            return True
        return False
    
    def isScissor(self):
        fingers = self.getFingers()
        print(fingers) # for debugging purposes to see th tuple output in the console
        if (fingers[1] and fingers[2] and not fingers[3] and not fingers[4]):
            return True
        return False
    
    def findDist(self, x1, y1, x2, y2):
        dist = math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
        return dist


def main():
    prevTime = 0
    currTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    TIMER = int(3)

    cont = True
    while cont:
	
	# Read and display each frame
            ret, img = cap.read()
            cv2.imshow('Image', img)

	# check for the key pressed
            k = cv2.waitKey(125)

	# set the key for the countdown
	# to begin. Here we set q
	# if key pressed is q
            if k == ord('q'):
                    prev = time.time()

                    while TIMER >= 1:
                            ret, img = cap.read()

			# Display countdown on each frame
			# specify the font and draw the
			# countdown using puttext
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(img, str(TIMER),
                                                    (200, 250), font,
                                                    7, (0, 255, 255),
                                                    4, cv2.LINE_AA)
                            cv2.imshow('Image', img)
                            cv2.waitKey(125)

			# current time
                            cur = time.time()

			# Update and keep track of Countdown
			# if time elapsed is one second
			# than decrease the counter
                            if cur-prev >= 1:
                                    prev = cur
                                    TIMER = TIMER-1

                    else:
                            ret, img = cap.read()

                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(img, "PLAY",
                                        (130, 200), font,
                                        4, (0, 255, 255),
                                        4, cv2.LINE_AA)
			# Display the clicked frame for 2
			# sec.You can increase time in
			# waitKey also
                            cv2.imshow('Image', img)

			# time for which image displayed
                            cv2.waitKey(2000)

			# Save the frame
                            #cv2.imwrite('camera.jpg', img)
                            cont = False
			# HERE we can reset the Countdown timer
			# if we want more Capture without closing
			# the camera

    
    #TO DO:
    # Will need some sort of gesture or condition to end the while loop. An infinte loop will be fine for now.
    again = True
    while again:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime
        
        #Generate the CPU play
        hPlay = "None"
        cpu = random.randint(1,3)
        if cpu == 1:
            cPlay = "Paper"
        elif cpu == 2:
            cPlay = "Scissors"
        else:
            cPlay = "Rock"

        cv2.putText(img, cPlay, (300, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        if(len(detector.lmList) > 0):
            if (detector.allFingersUp()):
                hPlay = "Paper"
                cv2.putText(img, "Paper", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            elif (detector.isScissor()):
                hPlay = "Scissors"
                cv2.putText(img, "Scissors", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            elif (detector.isFist()):
                hPlay = "Rock"
                cv2.putText(img, "Rock", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            else:
                cv2.putText(img, "None", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

        

        #Declare a winner
        winner = ""
        if hPlay == cPlay:
            winner = "Tie"
        elif hPlay == "Paper":
            if cPlay == "Rock":
                winner = "Human"
            elif cPlay == "Scissors":
                winner = "Computer"
        elif hPlay == "Rock":
            if cPlay == "Paper":
                winner = "Computer"
            elif cPlay == "Scissors":
                winner = "Human"
        elif hPlay == "Scissors":
            if cPlay == "Paper":
                winner = "Human"
            elif cPlay == "Rock":
                winner = "Computer"
        winner += " wins!"
        cv2.putText(img, winner , (160, 140), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        
        cv2.imshow("Image", img)
        k = cv2.waitKey(125)
        if k == ord('a'):
            again = True
        else:
            again = False
            


if __name__ == "__main__":
    main()
