import cv2 as cv
import services
import numpy as np

arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)    # 1000 since we're using 60X as IDs for the 1..6 electrodes
arucoParams = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

image = cv.imread("images/raw1.png")

(corners, ids, rejected) = detector.detectMarkers(image)

if len(corners) > 0:    # check if we even found a code
    ids = ids.flatten()
    # loop over all corners
    for (markerCorner, markerId) in zip(corners, ids):
        image = services.drawInfos(image, markerCorner, markerId)

# render output
cv.imshow("Output", image)
cv.waitKey(0)
