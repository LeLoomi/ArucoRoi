import json
from types import SimpleNamespace

# helper to calculate if point is inside circle area
def is_inside(area_x, area_y, area_radius, culprit_x, culprit_y) -> bool:
    return(
        ( pow(culprit_x - area_x, 2) + pow(culprit_y - area_y, 2) )
        < pow(area_radius, 2)
    )

with open('./config.json', 'r') as f:
    data = f.read()
    # convert json to object
    data = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

testX = -20
testY = 9

for region_marker in data.region_marker:    # loop all markers
    for roi in region_marker.rois:               # loop their rois
        print("\n+++ {} +++ ".format(roi.reg_name))
        print(roi.desired_marker_id,
            is_inside(
            roi.reg_dX,
            roi.reg_dY,
            roi.reg_radius,
            testX,
            testY
        ))