import cv2 as cv
import services
from imutils.video import VideoStream
import numpy as np
import time

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
            frame = services.drawInfos(frame, markerCorner, markerId)
    
    # render output
    cv.imshow("Output", frame)
    key = cv.waitKey(1)
    
    if key == ord('q'):
        break

cv.destroyAllWindows()
stream.stop()
