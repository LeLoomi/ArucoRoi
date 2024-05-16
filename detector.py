import cv2 as cv
from imutils.video import VideoStream
import time
import services

class Detector:
    # read config, init dicts
    config_data = services.load_config_data('./config.json')
    onscreen_markers = dict()   # to store id and position, updated per frame with whats on screen
    region_markers = dict()     # loaded from config at start of run
    calculated_rois = dict()    # updated each frame, with ready to use coords now
    correct_markers = dict()    # updated each frame, with the currently correnctly placed markers
    # initialize detector
    arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)    # 1000 since we're using 60X as IDs for the 1..6 electrodes
    arucoParams = cv.aruco.DetectorParameters()
    detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

    # initialize detector
    arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)    # 1000 since we're using 60X as IDs for the 1..6 electrodes
    arucoParams = cv.aruco.DetectorParameters()
    detector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

    def initialize(self):
        # load all regions with their align ids for quick, streamlined access
        for culprit in self.config_data['region_marker']:
            self.region_markers[culprit['align_id']] = {
                'align_name:': culprit['align_name'],
                'rois': culprit['rois']
            }
            

    # use this to detect in still images; output frame will be saved in ./results (only if folder exists)
    # returns the frame with all annotations (rois, markers and if they're in the correct roi) as well as all correct markers in a a dict
    def image_detect(self, frame, *args):
        self.initialize()
        
        # all of the detection happens here, mutating the result dicts in place over here
        services.detect_and_write(frame, self.config_data, self.detector, self.onscreen_markers, self.region_markers, self.calculated_rois, self.correct_markers)
        
        cv.imwrite('./results/{}.png'.format(time.time_ns()), frame)
        
        return frame, self.correct_markers


    # use this to detect markers in leve video, with visual feedback
    # not returning anything right now
    def video_detect(self, camera_index):
        self.init()
        
        # warm up and make camera available
        stream = VideoStream(src=camera_index).start()
        time.sleep(1.5)
        
        while True:
            frametime = time.time_ns()
            frame = stream.read()
            
            # all of the detection happens here, mutating the result dicts in place over here
            services.detect_and_write(frame, self.config_data, self.detector, self.onscreen_markers, self.region_markers, self.calculated_rois, self.correct_markers)
            
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