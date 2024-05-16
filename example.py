from detector import Detector
from cv2 import imread

detector = Detector(config_path='./config.json')
img = imread('./images/test1.png')
detector.image_detect(img)