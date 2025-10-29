import cv2 as cv
import time
import services

class Detector:
    onscreen_markers = dict()   # to store id and position, updated per frame with whats on screen
    region_markers = dict()     # loaded from config at start of run
    calculated_rois = dict()    # updated each frame, with ready to use coords now
    roi_statuses = dict()       # updated each frame, every target marker with its roi info (name, desc, fulfilled?). Key is target marker ID
    
    # initialize detector
    arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)    # impacts hamming distance and maybe accuracy?
    arucoParams = cv.aruco.DetectorParameters()
    # reduce expected marker size, to detect small markers
    arucoParams.minMarkerPerimeterRate *= 1/6
    arucoParams.minMarkerDistanceRate *= 1/6
    arucoParams.minCornerDistanceRate *= 1/6
    arucoParams.cornerRefinementMethod = cv.aruco.CORNER_REFINE_SUBPIX
    #arucoParams.useAruco3Detection = False     # It's supposedly worse at detecting small markers
    detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

    def __init__(self, config_path):
        self.load_config(config_path)
        
        # load all regions with their align ids for quick, streamlined access
        for culprit in self.config_data['region_marker']:
            self.region_markers[culprit['align_id']] = {
                'align_name:': culprit['align_name'],
                'rois': culprit['rois']
            }

    def reload_config(self):
        self.load_config(self.config_path)
        for culprit in self.config_data['region_marker']:
            self.region_markers[culprit['align_id']] = {
                'align_name:': culprit['align_name'],
                'rois': culprit['rois']
            }
    
    def load_config(self, config_path):
        self.config_path = config_path
        self.config_data = services.load_config_data(config_path)

    # use this to detect in still images; output frame will be saved in ./results (only if folder exists)
    # returns the frame with all annotations (rois, markers and if they're in the correct roi) as well as all correct markers in a a dict
    def image_detect(self, frame, *args):
        frametime = time.time_ns()
        
        # all of the detection happens here, mutating the result dicts in place over here
        services.detect_and_write_full(frame, self.detector, self.onscreen_markers, self.region_markers, self.calculated_rois, self.roi_statuses)
        
        # write frametime
        cv.putText(frame,
                    'ft: {} ms'.format(((time.time_ns() - frametime) / 1000000).__round__(1)),
                    (50, 50),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (100, 5, 255),
                    2
                )
        
        cv.imwrite('./results/{}.png'.format(time.time_ns()), frame)
        return frame, self.roi_statuses

    def grab_skeleton(self, frame: cv.typing.MatLike, line_color_bgra=(1, 5, 0, 255), line_thickness=3, put_frametime=False) -> cv.typing.MatLike:
        if(put_frametime):
            frametime = time.time_ns()
        
        result = services.create_bounds_and_id_overlay(frame, self.detector, line_color_bgra, line_thickness)
        
        if(put_frametime):
            cv.putText(result,
                    'ft: {} ms'.format(((time.time_ns() - frametime) / 1000000).__round__(1)), # pyright: ignore[reportPossiblyUnboundVariable]
                    (50, 50),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    line_color_bgra,
                    line_thickness
                )
        
        return result

    # use this to detect markers in leve video, with visual feedback
    # not returning anything right now
    def video_detect(self, camera_index):
        # warm up and make camera available
        stream = cv.VideoCapture(index=camera_index, apiPreference=cv.CAP_ANY)
        time.sleep(1.5)
        
        while True:
            frametime = time.time_ns()
            ret, frame = stream.read()
            self.reload_config()
            
            # all of the detection happens here, mutating the result dicts in place over here
            services.detect_and_write_full(frame, self.detector, self.onscreen_markers, self.region_markers, self.calculated_rois, self.roi_statuses)
            
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
        stream.release()