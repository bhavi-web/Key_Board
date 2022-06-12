import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm
import cvzone
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
from time import sleep
import webbrowser


def virtual_Painter():
    # print("started")
    brushThickness = 5
    eraserThickness = 150
    isPaint = False
    isGame = False
    folderPath = "Header"
    myList = os.listdir(folderPath)
    # print(myList)
    overlayList = []
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overlayList.append(image)
    # print(len(overlayList))
    header = overlayList[0]
    drawColor = (255, 0, 255)
    shape = 'freestyle'
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    imgBackground = cv2.imread("Resourses/Background.png")
    imgGameOver = cv2.imread("Resourses/gameOver.png")
    imgBall = cv2.imread("Resourses/Ball.png", cv2.IMREAD_UNCHANGED)
    imgBat1 = cv2.imread("Resourses/bat1.png", cv2.IMREAD_UNCHANGED)
    imgBat2 = cv2.imread("Resourses/bat2.png", cv2.IMREAD_UNCHANGED)

    # Hand Detector
    #detector = HandDetector(detectionCon=0.8, maxHands=2)

    # Variables
    ballPos = [100, 100]
    speedX = 15
    speedY = 15
    gameOver = False
    score = [0, 0]

    detector = htm.handDetector(detectionCon=0.85, maxHands=1)
    xp, yp = 0, 0
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)
    keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", "*", ".", "<"]]
    finalText = ""

    keyboard = Controller()

    def drawAll(img, buttonList):
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                              20, rt=0)
            cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 65),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return img

    class Button():
        def __init__(self, pos, text, size=[85, 85]):
            self.pos = pos
            self.size = size
            self.text = text

    buttonList = []
    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))
    gamedetector = HandDetector(detectionCon=0.8, maxHands=2)
    while True:
        if not isPaint and not isGame:
        # 1. Import image
            success, img = cap.read()
            # img = cv2.flip(img, 1)

            # 2. Find Hand Landmarks
            img = detector.findHands(img)
            lmList, bboxInfo = detector.findKeyboardPosition(img)
            img = drawAll(img, buttonList)
            if lmList:
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size
                    if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                        cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        l, _, _ = detector.findKeyboardDistance(8, 12, img, draw=False)
                        print(l)

                        ## when clicked
                        if l < 30:
                            keyboard.press(button.text)
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            if button.text == "<":

                                finalText = finalText[:-1]
                            elif button.text == "*":
                                finalText = " "
                            else:
                                finalText += button.text
                            if finalText == "P":
                                isPaint = True
                            elif finalText == "G":
                                isGame = True
                            elif ".COM" in finalText:
                                webbrowser.open(finalText)

                            sleep(1)

            cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
            cv2.putText(img, finalText, (60, 430),
                        cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

            cv2.imshow("Image", img)
            cv2.waitKey(1)
        elif isPaint:
            success, img = cap.read()
            # img = cv2.flip(img, 1)

            # 2. Find Hand Landmarks
            img = detector.findHands(img)
            lmList = detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                # print(lmList)

                # tip of index and middle fingers
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]
                x0, y0 = lmList[4][1:]
                # 3. Check which fingers are up
                fingers = detector.fingersUp()
                # print(fingers)

                # 4. If Selection Mode - Two finger are up
                if fingers[1] and fingers[2]:
                    xp, yp = 0, 0
                    # print("Selection Mode")
                    # # Checking for the click
                    if y1 < 120:
                        if 250 < x1 < 450:
                            header = overlayList[0]
                            drawColor = (255, 0, 255)
                        elif 550 < x1 < 750:
                            header = overlayList[1]
                            drawColor = (255, 0, 0)
                        elif 800 < x1 < 950:
                            header = overlayList[10]
                            drawColor = (0, 255, 0)
                        elif 1050 < x1 < 1200:
                            header = overlayList[5]
                            drawColor = (0, 0, 0)
                    if y1 > 120 and y1 < 210:
                        if x1 < 250:
                            header = overlayList[9]

                        elif 250 < x1 < 450 and drawColor == (255, 0, 255):
                            header = overlayList[0]
                            shape = 'freestyle'
                        elif 550 < x1 < 750 and drawColor == (255, 0, 255):
                            header = overlayList[6]
                            shape = 'circle'
                        elif 800 < x1 < 950 and drawColor == (255, 0, 255):
                            header = overlayList[7]
                            shape = 'rectangle'
                        elif 1050 < x1 < 1200 and drawColor == (255, 0, 255):
                            header = overlayList[8]
                            shape = 'elipse'
                        elif 250 < x1 < 450 and drawColor == (255, 0, 0):
                            header = overlayList[10]
                            shape = 'freestyle'
                        elif 550 < x1 < 750 and drawColor == (255, 0, 0):
                            header = overlayList[11]
                            shape = 'circle'
                        elif 800 < x1 < 950 and drawColor == (255, 0, 0):
                            header = overlayList[12]
                            shape = 'rectangle'
                        elif 1050 < x1 < 1200 and drawColor == (255, 0, 0):
                            header = overlayList[13]
                            shape = 'elipse'
                        if 250 < x1 < 450 and drawColor == (0, 255, 0):
                            header = overlayList[1]
                            shape = 'freestyle'
                        elif 550 < x1 < 750 and drawColor == (0, 255, 0):
                            header = overlayList[2]
                            shape = 'circle'
                        elif 800 < x1 < 950 and drawColor == (0, 255, 0):
                            header = overlayList[3]
                            shape = 'rectangle'
                        elif 1050 < x1 < 1200 and drawColor == (0, 255, 0):
                            header = overlayList[4]
                            shape = 'elipse'
                    cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
                if fingers[1] and fingers[2] == False:
                    cv2.circle(img, (x1, y1), 15, drawColor)
                    # print("Drawing Mode")
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)

                    if drawColor == (0, 0, 0):
                        eraserThickness = 50
                        z1, z2 = lmList[4][1:]
                        # print(z1,z2)
                        result = int(((((z1 - x1) ** 2) + ((z2 - y1) ** 2)) ** 0.5))
                        # print(result)
                        if result < 0:
                            result = -1 * result
                        u = result
                        if fingers[1] and fingers[4]:
                            eraserThickness = u
                        # print(eraserThickness)
                        cv2.putText(img, str("eraserThickness="), (0, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                        cv2.putText(img, str(int(eraserThickness)), (450, 700), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (255, 0, 255), 3)
                        cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)

                    else:
                        brushThickness = 5
                        # z1, z2 = lmList[4][1:]
                        # print(z1,z2)
                        # result = int(((((z1 - x1) ** 2) + ((z2 - y1) ** 2)) ** 0.5))
                        # print(result)
                        # if result < 0:
                        #     result = -1 * result
                        # u = result
                        # brushThickness = int(u)
                        # print(eraserThickness)

                        # draw
                        if shape == 'freestyle':
                            z1, z2 = lmList[4][1:]
                            # print(z1,z2)
                            result = int(((((z1 - x1) ** 2) + ((z2 - y1) ** 2)) ** 0.5))
                            print(result)
                            if result < 0:
                                result = -1 * result
                            u = result
                            cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                            if u >= 25:
                                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                            cv2.putText(img, str(u), (600, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                            cv2.putText(img, str("brushThickness="), (0, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255),
                                        3)
                            cv2.putText(img, str(int(brushThickness)), (450, 700), cv2.FONT_HERSHEY_PLAIN, 3,
                                        (255, 0, 255),
                                        3)

                        # Rectangle
                        if shape == 'rectangle':
                            z1, z2 = lmList[4][1:]
                            # print(z1,z2)
                            result = int(((((z1 - x1) ** 2) + ((z2 - y1) ** 2)) ** 0.5))
                            # print(result)
                            if result < 0:
                                result = -1 * result
                            u = result
                            cv2.rectangle(img, (x0, y0), (x1, y1), drawColor)
                            cv2.putText(img, "Length of Diagonal = ", (0, 700), cv2.FONT_HERSHEY_PLAIN, 3,
                                        (255, 0, 255), 3)
                            cv2.putText(img, str(u), (530, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                            if fingers[4]:
                                cv2.rectangle(imgCanvas, (x0, y0), (x1, y1), drawColor)
                                cv2.circle

                        # Circle
                        if shape == 'circle':
                            z1, z2 = lmList[4][1:]
                            # print(z1,z2)
                            result = int(((((z1 - x1) ** 2) + ((z2 - y1) ** 2)) ** 0.5))
                            # print(result)
                            if result < 0:
                                result = -1 * result
                            u = result
                            cv2.putText(img, "Radius Of Circe = ", (0, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255),
                                        3)
                            cv2.putText(img, str(u), (450, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                            cv2.circle(img, (x0, y0), u, drawColor)
                            if fingers[4]:
                                cv2.circle(imgCanvas, (x0, y0), u, drawColor)

                        # Ellipse
                        if shape == 'elipse':
                            z1, z2 = lmList[4][1:]
                            # cv2.ellipse(img,(x1,y1),(int(z1/2),int(z2/2)),0,0,360,255,0)
                            a = z1 - x1
                            b = (z2 - x2)
                            if x1 > 250:
                                b = int(b / 2)
                            if a < 0:
                                a = -1 * a
                            if b < 0:
                                b = -1 * b
                            cv2.ellipse(img, (x1, y1), (a, b), 0, 0, 360, 255, 0)
                            cv2.putText(img, "Major AL, Minor AL = ", (0, 700), cv2.FONT_HERSHEY_PLAIN, 3,
                                        (255, 0, 255), 3)
                            cv2.putText(img, str(a), (550, 700), cv2.FONT_HERSHEY_PLAIN, 3, (123, 20, 255), 3)
                            cv2.putText(img, str(b), (700, 700), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                            if fingers[4]:
                                cv2.ellipse(imgCanvas, (x1, y1), (a, b), 0, 0, 360, 255, 0)

                    xp, yp = x1, y1

                # Clear Canvas when 2 fingers are up
                if fingers[2] and fingers[3] and fingers[0] == 0 and fingers[1] == 0 and fingers[4] == 0:
                    imgCanvas = np.zeros((720, 1280, 3), np.uint8)

            imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
            img = cv2.bitwise_and(img, imgInv)
            img = cv2.bitwise_or(img, imgCanvas)

            # Setting the header image
            img[0:210, 0:1280] = header
            # img = cv2.addWeighted(img,0.5,imgCanvas,0.5,0)

            cv2.imshow("Image", img)
            # cv2.imshow("Canvas", imgCanvas)
            # cv2.imshow("Inv", imgInv)
            cv2.waitKey(1)
        elif isGame:

            _, img = cap.read()
            img = cv2.flip(img, 1)
            imgRaw = img.copy()

            # Find the hand and its landmarks
            hands, img = gamedetector.findHands(img, flipType=False)  # with draw

            # Overlaying the background image
            img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

            # Check for hands
            if hands:
                for hand in hands:
                    x, y, w, h = hand['bbox']
                    h1, w1, _ = imgBat1.shape
                    y1 = y - h1 // 2
                    y1 = np.clip(y1, 20, 415)

                    if hand['type'] == "Left":
                        img = cvzone.overlayPNG(img, imgBat1, (59, y1))
                        if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:
                            speedX = -speedX
                            ballPos[0] += 30
                            score[0] += 1

                    if hand['type'] == "Right":
                        img = cvzone.overlayPNG(img, imgBat2, (1195, y1))
                        if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                            speedX = -speedX
                            ballPos[0] -= 30
                            score[1] += 1

            # Game Over
            if ballPos[0] < 40 or ballPos[0] > 1200:
                gameOver = True

            if gameOver:
                img = imgGameOver
                cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX,
                            2.5, (200, 0, 200), 5)

            # If game not over move the ball
            else:

                # Move the Ball
                if ballPos[1] >= 500 or ballPos[1] <= 10:
                    speedY = -speedY

                ballPos[0] += speedX
                ballPos[1] += speedY

                # Draw the ball
                img = cvzone.overlayPNG(img, imgBall, ballPos)

                cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
                cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

            img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == ord('r'):
                ballPos = [100, 100]
                speedX = 15
                speedY = 15
                gameOver = False
                score = [0, 0]
                imgGameOver = cv2.imread("Resourses/gameOver.png")

virtual_Painter()
