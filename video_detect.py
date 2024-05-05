import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import time
import services

# initialize detector
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)    # 1000 since we're using 60X as IDs for the 1..6 electrodes
arucoParams = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

data = services.load_config_data('./config.json')
onscreen_markers = dict()   # to store id and position, updated per frame with whats on screen
region_markers = dict()     # loaded from config at start of run
calculated_rois = dict()    # updated each frame, with ready to use coords now
correct_markers = dict()    # updated each frame, with the currently correnctly placed markers

# warm up and make camera available
stream = VideoStream(src=0).start()
time.sleep(1.5)

# load all regions with their align ids for quick, streamlined access
for culprit in data['region_marker']:
    rois = dict()
    
    region_markers[culprit['align_id']] = {
        'align_name:': culprit['align_name'],
        'rois': culprit['rois']
    }
print(region_markers)

while True:
    frametime = time.time_ns()
    
    calculated_rois.clear()
    correct_markers.clear()
    frame = stream.read()
    
    # we detect in grayscale in order to cope a bit with micro-light-differences
    (detected_corners, detected_ids, rejected) = detector.detectMarkers(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))

    if len(detected_corners) > 0:    # check if we even found a marker
        detected_ids = detected_ids.flatten()
        
        # remove all markers from dict that are not on screen anymore
        for suspect_id in list(onscreen_markers.keys()):
            if suspect_id not in detected_ids:
                del onscreen_markers[suspect_id]
        
        
        # store all markers on screen in the dict, key is marker id
        for (marker_corners, marker_id) in zip(detected_corners, detected_ids):
            (c_top_left, c_top_right, c_bot_right, c_bot_left) = marker_corners.reshape((4, 2))
            marker_center = (int((c_bot_left[0] + c_top_right[0]) / 2),
                            int((c_bot_left[1] + c_top_right[1]) / 2))
            # no we have a marker with its id and its center-point that we can save / update
            onscreen_markers[marker_id] = {'marker_center': marker_center}  # with internal key to ensure expandability
        
        # get rois and update their coords, draw circle
        for match_id in set(region_markers).intersection(set(onscreen_markers)):
            for roi in region_markers[match_id]['rois']:
                calculated_rois[roi['reg_name']] = {
                    'coords': np.add(
                        onscreen_markers[match_id]['marker_center'],
                        ( roi['reg_dX'], roi['reg_dY'] )
                    ).flatten(),
                    'radius': roi['reg_radius'],
                    'desired_marker_id': roi['desired_marker_id']
                }
        
        # loop rois on screen right now
        for roi_name in calculated_rois:
            # draw roi info onto frame
            frame = cv.circle(
                    frame,
                    calculated_rois[roi_name]['coords'],
                    calculated_rois[roi_name]['radius'],
                    (100, 5, 255),
                    3
                )
            frame = cv.putText(
                frame,
                roi_name,
                np.add(
                    calculated_rois[roi_name]['coords'],
                    (0, -calculated_rois[roi_name]['radius']),
                ),
                cv.FONT_HERSHEY_SIMPLEX,
                2,
                (100, 5, 255),
                3
            )
            
            # check if any desired markers are in their roi
            if calculated_rois[roi_name]['desired_marker_id'] in onscreen_markers:
                culprit_id = calculated_rois[roi_name]['desired_marker_id']
                if services.is_inside_circle(
                    calculated_rois[roi_name]['coords'][0],
                    calculated_rois[roi_name]['coords'][1],
                    calculated_rois[roi_name]['radius'],
                    onscreen_markers[culprit_id]['marker_center'][0],
                    onscreen_markers[culprit_id]['marker_center'][1]
                ):
                    correct_markers[culprit_id] = {'roi_name': roi_name}

    # put frametime text on frame
    cv.putText(frame,
            'ft: {} ms'.format(((time.time_ns() - frametime) / 1000000).__round__(1)),
            (50, 50),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (100, 5, 255),
            2
        )
    
    # render output
    cv.imshow("Output", frame)
    key = cv.waitKey(1)
    
    if key == ord('q'):
        break

cv.destroyAllWindows()
stream.stop()
