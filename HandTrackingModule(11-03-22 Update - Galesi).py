import cv2 #To install in terminal:  pip install opencv-python 
import mediapipe as mp #To ins pip install mediapipe
import time
import math
import random
import numpy as np


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
    cap.set(3,1920) #change the resolution of the screen in order to account for more space on the screen.
    cap.set(4,1080)

    detector = handDetector()
    #variables to keep track of number of wins & ties
    hCount = 0
    cCount = 0
    tCount = 0
    
    # Booleans to change pages
    homeScreen = True
    playScreen = False
    rulesScreen = False
    playAgain = False
     

    while True:
        success, img = cap.read()
        img = cv2.flip(img,1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        touchIncrement = 7
        if (homeScreen):

            bottomBannerTopX = 0
            bottomBannerTopY = 600
            bottomBannerBotX = 1280
            bottomBannerBotY = 700
            # Bottom Banner -----Note:color is not rgb but bgr BACKWARDS!! :(
            cv2.rectangle(img, (bottomBannerTopX, bottomBannerTopY), (bottomBannerBotX, bottomBannerBotY),(0,0,0), -1) # Bottom banner outline
            cv2.rectangle(img, (bottomBannerTopX + 5, bottomBannerTopY + 5), (bottomBannerBotX - 5, bottomBannerBotY - 5),(246, 202, 196), -1) # Bottom banner foreground
            cv2.putText(img, "Welcome to the Rock, Paper, Scissors Game", (80, 650), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 2)
            cv2.putText(img, "Hover your hand over a button to start", (400, 685), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 2)
            
            #Button Foreground coordinates
            playTopX = 100
            playTopY = 5
            playBotX = 440
            playBotY = 115
            playButtonColor = (178,209,0)

            exitTopX = 800
            exitTopY = 5
            exitBotX = 1140
            exitBotY = 115
            exitButtonColor = (96,56,235)

            rulesTopX = 500
            rulesTopY = 5
            rulesBotX = 740
            rulesBotY = 115
            rulesButtonColor = (238,156,32)

            # Button Outlines
            cv2.rectangle(img, (playTopX - 5, playTopY - 5), (playBotX + 5 ,playBotY + 5), (0, 0, 0), -1) # PLAY outline
            cv2.rectangle(img, (exitTopX - 5, exitTopY - 5), (exitBotX + 5 ,exitBotY + 5), (0, 0, 0), -1) # EXIT outline
            cv2.rectangle(img, (rulesTopX - 5, rulesTopY - 5), (rulesBotX + 5 ,rulesBotY + 5), (0, 0, 0), -1) # RULES outline

            if(len(detector.lmList) > 0):

                if (detector.onButton(playTopX,playTopY,playBotX,playBotY)):# Over the PLAY button

                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + touchIncrement) #updates color
                        cv2.rectangle(img, (playTopX,playTopY),(playBotX,playBotY),(0,colorOfButton,0), -1) # PLAY BUTTON

                    else: #Button is confirmed to be pushed, move to PLAY screen
                        homeScreen = False
                        playScreen = True
                        prev = time.time()

                elif (detector.onButton(exitTopX, exitTopY, exitBotX, exitBotY)):# Over the EXIT button

                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + touchIncrement) #updates color
                        cv2.rectangle(img, (exitTopX,exitTopY), (exitBotX,exitBotY),(0,0,colorOfButton), -1) # EXIT Button

                    else: #Button is confirmed to be pushed, move to EXIT screen
                        homeScreen = False

                elif (detector.onButton(rulesTopX,rulesTopY,rulesBotX,rulesBotY)):# Over the RULES button

                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + touchIncrement) #updates color
                        cv2.rectangle(img, (rulesTopX,rulesTopY),(rulesBotX,rulesBotY),(colorOfButton,0,0), -1) # RULES BUTTON

                    else: #Button is confirmed to be pushed, move to RULES screen
                        homeScreen = False
                        rulesScreen = True
                else:
                    cv2.rectangle(img, (playTopX,playTopY),(playBotX,playBotY),playButtonColor, -1) # PLAY Button
                    cv2.rectangle(img, (exitTopX,exitTopY), (exitBotX,exitBotY),exitButtonColor, -1) # EXIT Button
                    cv2.rectangle(img, (rulesTopX,rulesTopY), (rulesBotX,rulesBotY),rulesButtonColor, -1) # RULES Button
                    detector.setColor(125)  
                         
            else:
                cv2.rectangle(img, (playTopX,playTopY),(playBotX,playBotY),playButtonColor, -1) # PLAY Button
                cv2.rectangle(img, (exitTopX,exitTopY), (exitBotX,exitBotY),exitButtonColor, -1) # EXIT Button
                cv2.rectangle(img, (rulesTopX,rulesTopY), (rulesBotX,rulesBotY),rulesButtonColor, -1) # RULES Button
                detector.setColor(125)

            #Button Text 
            cv2.putText(img, "PLAY", (playTopX+ 60, playTopY + 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 255, 255), 2)
            cv2.putText(img, "EXIT", (exitTopX+ 60, exitTopY + 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 255, 255), 2)
            cv2.putText(img, "RULES", (rulesTopX+ 10, rulesTopY + 75), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (255, 255, 255), 2)
            
        elif (rulesScreen):

            rulesBannerTopX = 95
            rulesBannerTopY = 130
            rulesBannerBotX = 1280
            rulesBannerBotY = 700
            # Bottom Banner -----Note:color is not rgb but bgr BACKWARDS!! :(
            cv2.rectangle(img, (rulesBannerTopX, rulesBannerTopY), (rulesBannerBotX, rulesBannerBotY),(0,0,0), -1) # Rules Bottom banner outline
            cv2.rectangle(img, (rulesBannerTopX + 5, rulesBannerTopY + 5), (rulesBannerBotX - 5, rulesBannerBotY - 5),(246, 202, 196), -1) # Rules Bottom banner foreground
            cv2.putText(img, "Rules coming soon!", (100, 200), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 2)
            
            #Button Foreground coordinates
            homeTopX = 100
            homeTopY = 5
            homeBotX = 440
            homeBotY = 115
            homeButtonColor = (178,209,0)

            # Button Outlines
            cv2.rectangle(img, (homeTopX - 5, homeTopY - 5), (homeBotX + 5 ,homeBotY + 5), (0, 0, 0), -1) # HOME outline

            if(len(detector.lmList) > 0):

                if (detector.onButton(homeTopX,homeTopY,homeBotX,homeBotY)):# Over the HOME button

                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + touchIncrement) #updates color
                        cv2.rectangle(img, (homeTopX,homeTopY),(homeBotX,homeBotY),(0,colorOfButton,0), -1) # HOME BUTTON

                    else: #Button is confirmed to be pushed, move to HOME screen
                        homeScreen = True
                        rulesScreen = False
                        print("Hit it")
                        detector.setColor(125)

                else:
                    cv2.rectangle(img, (homeTopX,homeTopY),(homeBotX,homeBotY),homeButtonColor, -1) # HOME Button
                    detector.setColor(125)  
                         
            else:
                cv2.rectangle(img, (homeTopX,homeTopY),(homeBotX,homeBotY),homeButtonColor, -1) # HOME Button
                detector.setColor(125)

            #Button Text 
            cv2.putText(img, "HOME", (homeTopX+ 40, homeTopY + 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 255, 255), 2)
           


        #occurs when play button is pushed
        elif(playScreen):
            cur = int(time.time())
            goal = int(prev + 6)
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL

            #place countdown on the screen until it reaches zero
            if goal > cur:
                
                if cur < goal -1: #displays the current time in seconds remaining , goal-1 is to allow 1 second for the word PLAY to appear
                    cv2.putText(img, str(int((goal-1) - cur)),(250, 300), font,5, (0, 255, 255),2, cv2.LINE_AA)
                    cv2.putText(img, "Make a selection now",(200, 320), font,.75, (0, 255, 255),2, cv2.LINE_AA)
                    cv2.imshow('Image', img)
                else: #displays PLAY with one second left
                    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
                    cv2.putText(img, "PLAY",(200,320), font,4, (0, 255, 255),4, cv2.LINE_AA)
                    cv2.imshow('Image', img)

			    #updates the time
                cur = int(time.time())

                # Gives feedback to user about which hand position they are currently showing
                if(len(detector.lmList) > 0):
                    if (detector.allFingersUp()):
                        hPlay = "Paper"
                        cv2.putText(img, "Paper", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                    elif (detector.isScissor()):
                        hPlay = "Scissors"
                        cv2.putText(img, "Scissors", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                    elif (detector.isFist()):
                        hPlay = "Rock"
                        cv2.putText(img, "Rock", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                    else:
                        cv2.putText(img, "None", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
            
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

                    cv2.putText(img, cPlay, (300, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 0, 0), 3)
                    if(len(detector.lmList) > 0):
                        if (detector.allFingersUp()):
                            hPlay = "Paper"
                            cv2.putText(img, "Paper", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                        elif (detector.isScissor()):
                            hPlay = "Scissors"
                            cv2.putText(img, "Scissors", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                        elif (detector.isFist()):
                            hPlay = "Rock"
                            cv2.putText(img, "Rock", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                        else:
                            cv2.putText(img, "None", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)

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
                        cv2.putText(img, hPlay, (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
                        cv2.putText(img, cPlay, (300, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 0, 0), 3)
                        #if the human does not have a valid play it displays "No winner"
                        if winner == " wins!":
                            cv2.putText(img, "No winner" , (160, 140), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 0, 0), 3)
                        else:
                            if delay <= 50: #condition to add a delay to the winner display
                                cv2.putText(img, winner , (150, 140), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 0, 0), 3)
                        cv2.imshow("Image", img)
                        cv2.waitKey(1)
                        delay -= 1
                        #print("Test ", delay)
                   
                    #attempting to at least add the button to the playScreen
                    delay = 20000
                    while delay > 0:
                        cv2.rectangle(img, (25,250), (200,300),(125,125,125), -1) # Button
                        cv2.putText(img, "Play Again", (25, 275), cv2.FONT_HERSHEY_COMPLEX_SMALL, .75, (0, 0, 0), 3)
                        detector.setColor(125)
                        delay -= 1
                    
                    #prev = time.time()



                    #end of added code   
                    playScreen = False
                    playAgain = True
                    again = False
               
                #prevTime = 0
                #currTime = 0
        elif (playAgain):

            bottomBannerTopX = 0
            bottomBannerTopY = 600
            bottomBannerBotX = 1280
            bottomBannerBotY = 700
            # Bottom Banner -----Note:color is not rgb but bgr BACKWARDS!! :(
            cv2.rectangle(img, (bottomBannerTopX, bottomBannerTopY), (bottomBannerBotX, bottomBannerBotY),(0,0,0), -1) # Bottom banner outline
            cv2.rectangle(img, (bottomBannerTopX + 5, bottomBannerTopY + 5), (bottomBannerBotX - 5, bottomBannerBotY - 5),(246, 202, 196), -1) # Bottom banner foreground
            cv2.putText(img, "Human: "+ str(hCount) +" Computer: "+ str(cCount) + " Tie: "+ str(tCount), (80, 650), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 2)
            
            
            #Button Foreground coordinates
            playTopX = 100
            playTopY = 5
            playBotX = 440
            playBotY = 115
            playButtonColor = (178,209,0)

            exitTopX = 800
            exitTopY = 5
            exitBotX = 1140
            exitBotY = 115
            exitButtonColor = (96,56,235)

            # Button Outlines
            cv2.rectangle(img, (playTopX - 5, playTopY - 5), (playBotX + 5 ,playBotY + 5), (0, 0, 0), -1) # PLAY outline
            cv2.rectangle(img, (exitTopX - 5, exitTopY - 5), (exitBotX + 5 ,exitBotY + 5), (0, 0, 0), -1) # EXIT outline

            if(len(detector.lmList) > 0):

                if (detector.onButton(playTopX,playTopY,playBotX,playBotY)):# Over the PLAY button

                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + touchIncrement) #updates color
                        cv2.rectangle(img, (playTopX,playTopY),(playBotX,playBotY),(0,colorOfButton,0), -1) # PLAY BUTTON

                    else: #Button is confirmed to be pushed, move to PLAY screen
                        playAgain = False
                        playScreen = True
                        prev = time.time()

                elif (detector.onButton(exitTopX, exitTopY, exitBotX, exitBotY)):# Over the EXIT button

                    if(detector.getColor() < 255):
                        colorOfButton = detector.setColor(detector.getColor() + touchIncrement) #updates color
                        cv2.rectangle(img, (exitTopX,exitTopY), (exitBotX,exitBotY),(0,0,colorOfButton), -1) # EXIT Button

                    else: #Button is confirmed to be pushed, move to EXIT screen
                        playAgain = False

                else:
                    cv2.rectangle(img, (playTopX,playTopY),(playBotX,playBotY),playButtonColor, -1) # PLAY Button
                    cv2.rectangle(img, (exitTopX,exitTopY), (exitBotX,exitBotY),exitButtonColor, -1) # EXIT Button
                    detector.setColor(125)  
                         
            else:
                cv2.rectangle(img, (playTopX,playTopY),(playBotX,playBotY),playButtonColor, -1) # PLAY Button
                cv2.rectangle(img, (exitTopX,exitTopY), (exitBotX,exitBotY),exitButtonColor, -1) # EXIT Button
                detector.setColor(125)

            #Button Text 
            cv2.putText(img, "PLAY", (playTopX+ 60, playTopY + 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 255, 255), 2)
            cv2.putText(img, "EXIT", (exitTopX+ 60, exitTopY + 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 255, 255), 2)
                                                
        #Altered Tutorial button to Quit button, shows a tally for the human, computer, and ties   
        else:
            cv2.rectangle(img, (0,0), (800,1000),(125,125,125), -1) # home screen ((xmin,ymin),(xmax,ymax),(color),outter line)
            #cv2.rectangle(img, (25,350), (200,400),(255,0,0), -1) # Button

            #final screen showing the game tally and declares an overall winner...topDog
            cv2.putText(img, "Human " + str(hCount), (100, 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 3)
            cv2.putText(img, "Computer " + str(cCount), (100, 140), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 3)
            cv2.putText(img, "Tie " + str(tCount), (100, 240), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 3)
            if hCount > cCount:
                topDog = "Human wins!"
            elif hCount < cCount:
                topDog = "Computer wins!"
            else:
                topDog = "No winner :("
            cv2.putText(img, topDog, (150, 365), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 3)

       
        
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()
