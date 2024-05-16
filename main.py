from detector import Detector
from cv2 import imread

# run example main if not used as package
if __name__ == "__main__":
    detector = Detector()
    img = imread('./images/test1.png')
    detector.image_detect(img)