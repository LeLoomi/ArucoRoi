import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import time
import services
import os

# initialize detector
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)    # 1000 since we're using 60X as IDs for the 1..6 electrodes
arucoParams = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

data = services.load_config_data('./config.json')
current_corrects = []

# warm up and make camera available
stream = VideoStream(src=0).start()
time.sleep(1.5)

framei = 0
while True:
    current_corrects = []
    frame = stream.read()
    time.sleep(0.1)    # to give us breathing room for our unoptimized calcs
    (corners, ids, rejected) = detector.detectMarkers(frame)

    if len(corners) > 0:    # check if we even found a marker
        ids = ids.flatten()
        # loop over all corners
        for (markerCorner, markerId) in zip(corners, ids):
            m_corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, botRight, botLeft) = m_corners
        
            # convert each of the (x, y) pairs to int
            topRight = (int(topRight[0]), int(topRight[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            botRight = (int(botRight[0]), int(botRight[1]))
            botLeft = (int(botLeft[0]), int(botLeft[1]))
        
            markerCentre = (int((botLeft[0] + topRight[0]) / 2),
                            int((botLeft[1] + topRight[1]) / 2))
        
            for region_marker in data.region_marker:    # loop all markers
                for roi in region_marker.rois:  # loop their rois
                    if region_marker.align_id in ids: 
                        # if we have a region marker
                        if region_marker.align_id == markerId:
                            roiCentre = np.add(markerCentre, (roi.reg_dX, roi.reg_dY))
                            frame = cv.circle(
                                frame,
                                roiCentre,
                                roi.reg_radius,
                                (100, 5, 255),
                                3
                            )
                            cv.putText(frame,
                                roi.reg_name,
                                np.add(roiCentre, (0, roi.reg_radius - 30)),
                                cv.FONT_HERSHEY_SIMPLEX,
                                2,
                                (100, 5, 255),
                                3
                            )
                        
                        # if we have a desired marker
                        if roi.desired_marker_id == markerId:
                            if services.is_inside_circle(
                                roiCentre[0], roiCentre[1], roi.reg_radius,
                                markerCentre[0], markerCentre[1]):
                                current_corrects.append(markerId)
            
            frame = services.drawInfos(frame, markerCorner, markerId)
    os.system('clear')
    print("Currently correct: ", current_corrects)

    # render output
    cv.imshow("Output", frame)
    key = cv.waitKey(1)
    
    if key == ord('q'):
        break

cv.destroyAllWindows()
stream.stop()
