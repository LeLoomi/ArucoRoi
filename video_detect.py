import cv2 as cv
from imutils.video import VideoStream
import numpy as np
import time
import sys

# initialize detector
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)    # 1000 since we're using 60X as IDs for the 1..6 electrodes
arucoParams = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

# warm up and make camera available
stream = VideoStream(src=0).start()
time.sleep(1.0)

while True:
    frame = stream.read()
    # resize here for performance reasons?

    (corners, ids, rejected) = detector.detectMarkers(frame)

    if len(corners) > 0:    # check if we even found a code
        ids = ids.flatten()
        
        # loop over all corners
        for (markerCorner, markerId) in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, botRight, botLeft) = corners
            
            # convert each of the (x, y) pairs to int
            topRight = (int(topRight[0]), int(topRight[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            botRight = (int(botRight[0]), int(botRight[1]))
            botLeft = (int(botLeft[0]), int(botLeft[1]))
            
            # draw box around aruco marker
            cv.line(frame, topLeft, topRight, (0, 0, 255), 2)
            cv.line(frame, topRight, botRight, (0, 0, 255), 2)
            cv.line(frame, botRight, botLeft, (0, 0, 255), 2)
            cv.line(frame, botLeft, topLeft, (0, 0, 255), 2)
            
            # draw point into centre of marker, draw axes
            cX = int(( (topLeft[0] + botRight[0]) / 2.0))
            cY = int(( (topLeft[1] + botRight[1]) / 2.0))
            axisX = np.subtract(botRight, botLeft)
            axisY = np.subtract(topLeft, botLeft)
            
            cv.arrowedLine(frame,
                (cX, cY),
                np.add((cX, cY), axisY),
                (0, 255, 0),
                2
            )
            cv.arrowedLine(frame,
                (cX, cY),
                np.add((cX, cY), axisX),
                (0, 255, 0),
                2
            )
            cv.circle(frame, (cX, cY), 0, (0, 0, 255), 15)
            
            # draw marker IDs
            cv.putText(frame, str(markerId),
                (topLeft[0], topLeft[1] - 15),
                cv.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 255), 3
            )
    
    # render output
    cv.imshow("Output", frame)
    key = cv.waitKey(1)
    
    if key == ord('q'):
        break

cv.destroyAllWindows()
stream.stop()
