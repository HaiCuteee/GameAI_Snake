#pip install --upgrade cvzone
#pip install opencv-python
#pip install numpy




import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1) #Nhận diện bàn tay


class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # số điểm
        self.lengths = []  #độ dài con rắn
        self.currentLength = 0 #tổng độ dài con rắn
        self.allowedLength = 150  #độ dài tối đa con rắn
        self.previousHead = 0, 0 #xác định vị trí ban đầu của đầu rắn

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED) #lấy ảnh donut
        self.hFood, self.wFood, _ = self.imgFood.shape #chiều cao và chiều rộng donut
        self.foodPoint = 0, 0 #điểm donut hiện ra
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                               scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                               scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead #lấy tọa độ trước đó của đầu rắn
            cx, cy = currentHead #lấy tọa độ hiện tại của đầu rắn

            self.points.append([cx, cy]) #thêm mới vào dánh sách điểm của con rắn
            distance = math.hypot(cx - px, cy - py) #tính khoảng cách các điểm hiện tại và điểm trước đó
            self.lengths.append(distance) #tăng độ dài khi ăn 1 điểm
            self.currentLength += distance #cật nhật tổng chiều dài con rắn
            self.previousHead = cx, cy #cật nhật vị trí đầu trước đó

            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths): 
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            #random bánh donut và cộng điểm
            rx, ry = self.foodPoint 
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:   
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (0, 255, 0), cv2.FILLED)

            # Draw Food
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                               scale=3, thickness=3, offset=10)

            # Check var
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                print("Hit")
                self.gameOver = True
                self.points = []  
                self.lengths = []  
                self.currentLength = 0  
                self.allowedLength = 150  
                self.previousHead = 0, 0  
                self.randomFoodLocation()

        return imgMain #update cam


game = SnakeGameClass("Donut.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1) #để cam không ngược
    hands, img = detector.findHands(img, flipType=False) #đóng khung bàn tay

    if hands: 
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False
        game.score = 0
    if key == ord('q'):
        break