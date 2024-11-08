# ArucoRoi

Util to track [AruCo Marker](https://www.uco.es/investiga/grupos/ava/portfolio/aruco/) positions and identities in camera space in relation to predefined <b>regions of interest</b>.

<p> You can use this to track / detect in still frames and live video.

> It is recommmended to use the still image detection. Use video detection for debugging your config.json since the display loop will thread-block. Video detection hot-reloads the config, making it a perfect tool to write your config with live feedback.
> - If you want to detect in video, simply call image_detect each frame
> - Currently, image_detect() reads the config file everytime, costing performance.
> <br><sup><i>This will be fixed in the future.</i></sup>

### How to use
- Import `Detector` from `ArucoRoi.detector`
- Instantiate a detector object
- Call `frame, roi_statuses = detector_object.image_detect(img)`
    - <i>img</i> is the opencv Image object you want to detect on
    - <i>frame</i> is img but processed, meaning annotated with marker ids, rois (+names), correctness markings
    - <i>roi_statuses</i> is a dict with
        <br>-> the target marker as key
        <br>-> a field <i>roi_name</i> containing the name of the markers target ROI
        <br>-> a field <i>roi_desc</i> containing the description of the target ROI
        <br>-> a field <i>fulfilled</i> which is True if the target marker is inside, False if outside of the ROI
        <br>-> a field <i>deviation_x</i> which is the desired markers X deviation from the center of the ROI
        <br>-> a field <i>deviation_y</i> which is the desired markers Y deviation from the center of the ROI
        'deviation_x': deviation_x,
                    'deviation_y': deviation_y

### How to setup `config.json`:
In here you define all of your ROIs and their desired markers. Identities and positions of markers not attached in the config will still be tracked and logged in the `onscreen_markers` dict.

```` JSON
{
  "region_marker": [
    {
      "align_id": 620,                // id of marker that ROIs will be in delta to
      "align_name": "torso-center",   // purely for your information
      "rois": [                       // all ROIs attached to the marker
        {
          "reg_name": "V1",           // ROI display name and internal dict key
          "reg_desc": "i'm a circle",
          "reg_shape": "circle",      // available: 'circle', 'rectangle' (rect see below)
          "reg_dX": 250,              // ROI center coords in delta (also in the center for rectangles!)
          "reg_dY": 200,              // to align marker camera space position
          "reg_radius": 100,          // ROI radius (specific to circle rois!)
          "desired_marker_id": 601    // id of marker that should be inside the ROI
        }
      ]
    },
    {
      "align_id": 630,
      "align_name": "left-hand",
      "rois": [
        {
          "reg_name": "V2",
          "reg_desc": "i'm a rectangle",
          "reg_shape": "rectangle",
          "reg_dX": 0,
          "reg_dY": 200,
          "reg_width": 200,           // roi width (specific for rect rois!)
          "reg_height": 150,          // roi height (specific for rect rois!)
          "desired_marker_id": 602
        }
      ]
    }
  ]
}
````

### Dependencies:
- OpenCV
- Numpy
