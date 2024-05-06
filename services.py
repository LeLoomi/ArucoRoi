import cv2 as cv
import numpy as np
import json
import time

# read json from config and return data
def load_config_data(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

# helper to calculate if point is inside circle area
def is_inside_circle(area_x, area_y, area_radius, culprit_x, culprit_y) -> bool:
    return(
        ( pow(culprit_x - area_x, 2) + pow(culprit_y - area_y, 2) )
        < pow(area_radius, 2)
    )

# draw marker axes and id onto provided image
def drawInfos(frame, markerCorner, markerId):
    corners = markerCorner.reshape((4, 2))
    (topLeft, topRight, botRight, botLeft) = corners
    
    # convert each of the (x, y) pairs to int
    topRight = (int(topRight[0]), int(topRight[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))
    botRight = (int(botRight[0]), int(botRight[1]))
    botLeft = (int(botLeft[0]), int(botLeft[1]))
    
    # draw axes (z missing as of now)
    axisX = np.subtract(botRight, botLeft)
    axisY = np.subtract(topLeft, botLeft)
    
    cv.arrowedLine(frame,
        botLeft,
        np.add(botLeft, axisY),
        (255, 175, 5),
        2
    )
    cv.arrowedLine(frame,
        botLeft,
        np.add(botLeft, axisX),
        (100, 5, 255),
        2
    )
    # draw marker IDs
    cv.putText(frame, str(markerId),
        (topLeft[0], topLeft[1] - 15),
        cv.FONT_HERSHEY_SIMPLEX,
        1, (0, 0, 255), 2
    )
    
    return frame

# function that detects markers and MUTATES the passed in dicts
def detect_and_write(frame, config_data, detector, onscreen_markers, region_markers, calculated_rois, correct_markers):
    calculated_rois.clear()
    correct_markers.clear()
    
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
                if is_inside_circle(
                    calculated_rois[roi_name]['coords'][0],
                    calculated_rois[roi_name]['coords'][1],
                    calculated_rois[roi_name]['radius'],
                    onscreen_markers[culprit_id]['marker_center'][0],
                    onscreen_markers[culprit_id]['marker_center'][1]
                ):
                    correct_markers[culprit_id] = {'roi_name': roi_name}