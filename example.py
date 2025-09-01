from detector import Detector
import cv2 as cv
from time import sleep

detector = Detector(config_path='./roi-config-mockup.json')
#img = imread('./images/test1.png')

#frame, results = detector.image_detect(img)
#detector.video_detect(0)

cap = cv.VideoCapture(0)
sleep(1.5)

while True:
    ret, frame = cap.read()
    
    #result = detector.grab_skeleton(frame)
    result = detector.grab_skeleton(frame, line_color_bgr=(57, 255, 20), line_thickness=3) # pyright: ignore[reportArgumentType]
    
    cv.imshow("Output", result)
    key = cv.waitKey(1)
    
    if key == ord('q'):
        break
        
cv.destroyAllWindows()
cap.release()

#print(results)