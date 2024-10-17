from detector import Detector
from cv2 import imread

detector = Detector(config_path='./roi-config.json')
img = imread('./images/test1.png')

frame, results = detector.image_detect(img)
#detector.video_detect(0)

print(results)