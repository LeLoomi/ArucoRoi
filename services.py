import cv2 as cv
import numpy as np
import json
from types import SimpleNamespace

# read json from config and return data
def load_config_data(path: str):
    with open(path, 'r') as f:
        data = f.read()
    # convert json to object
    data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
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