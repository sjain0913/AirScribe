import numpy as np
import cv2
from collections import deque

# Upper and lower bounds for finding blue pen
blueLower = np.array([100, 60, 60])
blueUpper = np.array([140, 255, 255])

kernel = np.ones((5, 5), np.uint8)

# Deques to store our colored pixel points
bluePoints = [deque(maxlen=512)]
greenPoints = [deque(maxlen=512)]
redPoints = [deque(maxlen=512)]
yellowPoints = [deque(maxlen=512)]

blueIndex, greenIndex, redIndex, yellowIndex, colorIndex = 0, 0, 0, 0, 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]

# Interface for the app
ourWindow = np.zeros((471,636,3)) + 255
ourWindow = cv2.rectangle(ourWindow, (40,1), (140,65), (0,0,0), 2)
ourWindow = cv2.rectangle(ourWindow, (160,1), (255,65), colors[0], -1)
ourWindow = cv2.rectangle(ourWindow, (275,1), (370,65), colors[1], -1)
ourWindow = cv2.rectangle(ourWindow, (390,1), (485,65), colors[2], -1)
ourWindow = cv2.rectangle(ourWindow, (505,1), (600,65), colors[3], -1)
cv2.putText(ourWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(ourWindow, "BLUE", (185, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(ourWindow, "GREEN", (298, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(ourWindow, "RED", (420, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(ourWindow, "YELLOW", (520, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (150,150,150), 2, cv2.LINE_AA)
cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

videoFeed = cv2.VideoCapture(0)
writing = True

while True:
    (grabbed, frame) = videoFeed.read()
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # adding the colors to window
    frame = cv2.rectangle(frame, (40,1), (140,65), (122,122,122), -1)
    frame = cv2.rectangle(frame, (160,1), (255,65), colors[0], -1)
    frame = cv2.rectangle(frame, (275,1), (370,65), colors[1], -1)
    frame = cv2.rectangle(frame, (390,1), (485,65), colors[2], -1)
    frame = cv2.rectangle(frame, (505,1), (600,65), colors[3], -1)
    cv2.putText(frame, "CLEAR", (49, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "BLUE", (185, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "GREEN", (298, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "RED", (420, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "YELLOW", (520, 33), cv2.FONT_HERSHEY_DUPLEX, 0.5, (150,150,150), 2, cv2.LINE_AA)

    if not grabbed:
        break

    # detect writing pen
    maskBlue = cv2.inRange(hsv, blueLower, blueUpper)
    maskBlue = cv2.erode(maskBlue, kernel, iterations=2)
    maskBlue = cv2.morphologyEx(maskBlue, cv2.MORPH_OPEN, kernel)
    maskBlue = cv2.dilate(maskBlue, kernel, iterations=1)

    (cnts, __) = cv2.findContours(maskBlue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    # in the case when contours are found
    if len(cnts) > 0:

        cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

        ((x, y), radius) = cv2.minEnclosingCircle(cnt)

        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center[1] <= 65:
            if 40 <= center[0] <= 140: # Clear All
                bluePoints = [deque(maxlen=512)]
                greenPoints = [deque(maxlen=512)]
                redPoints = [deque(maxlen=512)]
                yellowPoints = [deque(maxlen=512)]

                blueIndex = 0
                greenIndex = 0
                redIndex = 0
                yellowIndex = 0
                ourWindow[67:,:,:] = 255

            elif 160 <= center[0] <= 255:
                    colorIndex = 0
            elif 275 <= center[0] <= 370:
                    colorIndex = 1
            elif 390 <= center[0] <= 485:
                    colorIndex = 2
            elif 505 <= center[0] <= 600:
                    colorIndex = 3

        else :
            if colorIndex == 0:
                bluePoints[blueIndex].appendleft(center)
            elif colorIndex == 1:
                greenPoints[greenIndex].appendleft(center)
            elif colorIndex == 2:
                redPoints[redIndex].appendleft(center)
            elif colorIndex == 3:
                yellowPoints[yellowIndex].appendleft(center)

    # no blue pen detected 
    else:
        bluePoints.append(deque(maxlen=512))
        blueIndex += 1
        greenPoints.append(deque(maxlen=512))
        greenIndex += 1
        redPoints.append(deque(maxlen=512))
        redIndex += 1
        yellowPoints.append(deque(maxlen=512))
        yellowIndex += 1

    # Drawing the lines
    points = [bluePoints, greenPoints, redPoints, yellowPoints]

    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                if writing:
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(ourWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

    cv2.imshow("Main", frame)
    cv2.imshow("Paint", ourWindow)

    # Key bindings
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('a') and writing:
        writing = False
    elif key == ord('a') and not writing:
        writing = True

camera.release()
cv2.destroyAllWindows()