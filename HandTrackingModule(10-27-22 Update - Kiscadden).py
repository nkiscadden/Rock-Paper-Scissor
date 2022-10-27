import cv2 #To install in terminal:  pip install opencv-python 
import mediapipe as mp #To ins pip install mediapipe
import time
import math
import random

# Included with class documentation
class handDetector():
    def __init__(self, mode=False, maxHands = 1, modelComplex=1, detectionConf = 0.5, trackConf = 0.5 , color = 0): #Added a color field 

        #Initializing instance variables
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplex
        self.detectionConf = detectionConf
        self.trackConf = trackConf
        self.color = color

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
        if ((fingers[1] and fingers[2] and fingers[3] and fingers[4])):
            return True
        return False

    def isFist(self):
        fingers = self.getFingers()
        if (not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]):
            return True
        return False
    
    def isScissor(self):
        fingers = self.getFingers()
        if (fingers[1] and fingers[2] and not fingers[3] and not fingers[4]):
            return True
        return False
    
    def findDist(self, x1, y1, x2, y2):
        dist = math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
        return dist

    def onButton(self, x1, y1, x2, y2): #chechks if the tip of the pointer finger is within the boundaries of the button to push
        if(self.lmList[8][1] > x1 and self.lmList[8][1] < x2 and self.lmList[8][2] > y1 and self.lmList[8][2] < y2):
            return True

    def getColor(self):
        return self.color
    
    def setColor(self,colorIn):
        self.color = colorIn
        return self.color


def main():
    prevTime = 0
    currTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    #variables to keep track of number of wins & ties
    hCount = 0
    cCount = 0
    tCount = 0
    
    # Booleans to change pages
    titleScreen = True
    playScreen = False
     
    cont = True
    
    #TO DO:
    # Will need some sort of gesture or condition to end the while loop. An infinte loop will be fine for now.
    while True:
        success, img = cap.read()
        img = cv2.flip(img,1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        if(titleScreen):
            if(len(detector.lmList) > 0):
                if (detector.onButton(25, 250, 200, 300)):# Over the play button
                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + 10) #updates color
                        cv2.rectangle(img, (25,250), (200,300),(0,colorOfButton,0), -1) # Button
                        print(colorOfButton)
                    else: #Button is confirmed to be pushed, move to PLAY screen
                        playScreen = True
                        titleScreen = False
                elif (detector.onButton(25, 350, 200, 400)):# Over the tutorial button
                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + 10) #updates color
                        cv2.rectangle(img, (25,350), (200,400),(0,colorOfButton,0), -1) # Button
                    else: #Button is confirmed to be pushed, move to Tutorial screen
                        playScreen = False
                        titleScreen = False
                else:
                    cv2.rectangle(img, (25,350), (200,400),(125,125,125), -1) # Button
                    cv2.rectangle(img, (25,250), (200,300),(125,125,125), -1) # Button
                    detector.setColor(125)  
                         
            else:
                cv2.rectangle(img, (25,250), (200,300),(125,125,125), -1) # Button
                cv2.rectangle(img, (25,350), (200,400),(125,125,125), -1) # Button
                detector.setColor(125)

            cv2.putText(img, "Rock, Paper, Scissors", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            cv2.putText(img, "Hover over button to start", (200, 75), cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 0), 3)
            cv2.putText(img, "Lets Play", (25, 275), cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 0), 3)
            #Modified button to quit game and it shows a tally
            cv2.putText(img, "End Game", (25, 375), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            prev = time.time()

        #occurs when play button is pushed
        elif(playScreen):
            cur = int(time.time())
            goal = int(prev + 6)
            font = cv2.FONT_HERSHEY_SIMPLEX

            #place countdown on the screen until it reaches zero
            if goal > cur:
                
                if cur < goal -1: #displays the current time in seconds remaining , goal-1 is to allow 1 second for the word PLAY to appear
                    cv2.putText(img, str(int((goal-1) - cur)),(250, 300), font,5, (0, 255, 255),2, cv2.LINE_AA)
                    cv2.putText(img, "Make a selection now",(200, 320), font,.75, (0, 255, 255),2, cv2.LINE_AA)
                    cv2.imshow('Image', img)
                else: #displays PLAY with one second left
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, "PLAY",(200,320), font,4, (0, 255, 255),4, cv2.LINE_AA)
                    cv2.imshow('Image', img)

			    #updates the time
                cur = int(time.time())

                # Gives feedback to user about which hand position they are currently showing
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
            
            #TO DO:
            # Will need some sort of gesture or condition to end the while loop. An infinte loop will be fine for now.
            else:
                again = True
                while again:
                    #Generate the CPU play
                    hPlay = "None"
                    cpu = random.randint(1,3)
                    print("CPU: ", cpu)
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
                    
                    if winner == "Human wins!":
                        hCount += 1
                    elif winner == "Computer wins!":
                        cCount += 1
                    elif winner == "Tie wins!":
                        tCount += 1
                        
                    print("h ", hCount, "  c ", cCount, "   t ", tCount)
                    
                    cv2.imshow("Image", img)
                    #added code
                    delay = 110 #delay timer for showing the results to screen
                    while delay >= 0:
                        success, img = cap.read()
                        img = cv2.flip(img,1)
                        cv2.putText(img, hPlay, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
                        cv2.putText(img, cPlay, (300, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
                        #if the human does not have a valid play it displays "No winner"
                        if winner == " wins!":
                            cv2.putText(img, "No winner" , (160, 140), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
                        else:
                            if delay <= 50: #condition to add a delay to the winner display
                                cv2.putText(img, winner , (160, 140), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
                        cv2.imshow("Image", img)
                        cv2.waitKey(1)
                        delay -= 1
                        #print("Test ", delay)
                    #add a Quit button to the screen to return to home page
                    '''if(len(detector.lmList) > 0):
                        if (detector.onButton(25, 250, 200, 300)):# Over the play button
                            if(detector.getColor() < 255):
                                colorOfButton = detector.setColor(detector.getColor() + 10) #updates color
                                cv2.rectangle(img, (25,250), (200,300),(0,colorOfButton,0), -1) # Button
                                print(colorOfButton)
                            else: #Button is confirmed to be pushed, move to PLAY screen
                                playScreen = True
                                titleScreen = False
                        elif (detector.onButton(25, 350, 200, 400)):# Over the tutorial button
                            if(detector.getColor() < 255):
                                colorOfButton = detector.setColor(detector.getColor() + 10) #updates color
                                cv2.rectangle(img, (25,350), (200,400),(0,colorOfButton,0), -1) # Button
                            else: #Button is confirmed to be pushed, move to Tutorial screen
                                playScreen = False
                                titleScreen = False
                        else:
                            #cv2.rectangle(img, (25,350), (200,400),(125,125,125), -1) # Button
                            cv2.rectangle(img, (25,250), (200,300),(125,125,125), -1) # Button
                            detector.setColor(125)  
                         
                    else:
                        cv2.rectangle(img, (25,250), (200,300),(125,125,125), -1) # Button
                        #cv2.rectangle(img, (25,350), (200,400),(125,125,125), -1) # Button
                        detector.setColor(125)

                    cv2.putText(img, "Play Again", (25, 275), cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 0), 3)
                    
                    prev = time.time()'''



                    #end of added code   
                    titleScreen = True
                    playScreen = False
                    again = False #end of added code
               
                #prevTime = 0
                #currTime = 0
                                            
        #Altered Tutorial button to Quit button, shows a tally for the human, computer, and ties   
        else:
            cv2.putText(img, "Human " + str(hCount), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            cv2.putText(img, "Computer " + str(cCount), (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            cv2.putText(img, "Tie " + str(tCount), (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            #cv2.putText(img, "Tutorial Page", (100, 700), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

       
        
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
