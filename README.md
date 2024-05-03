# AruCo tracker

Util to track [AruCo Marker](https://www.uco.es/investiga/grupos/ava/portfolio/aruco/) positions and identities in camera space in relation to predefined <b>regions of interest</b>.

<p> Meant to be used on live video but trivially easy to adapt for still images.
<br> <sup><i>might directly implement support in future idk</i></sup>

### How to use `config.json`:

```` JSON
{
  "region_marker": [
    {
      "align_id": 620,              // if of marker that ROIs will be in delta to
      "align_name": "torso-center", // purely for your information
      "rois": [                     // all ROIs attached to the marker
        {
          "reg_name": "V1",         // ROI display name and internal dict key
          "reg_dX": 250,            // ROI center coords in delta
          "reg_dY": 200,            // to align marker camera space position
          "reg_radius": 100,        // ROI radius (they're all circles rn)
          "desired_marker_id": 601  // id of marker that should be inside the ROI
        }
      ]
    },
    {
      "align_id": 630,
      "align_name": "left-hand",
      "rois": [
        {
          "reg_name": "V2",
          "reg_dX": -30,
          "reg_dY": -200,
          "reg_radius": 100,
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
- imutils