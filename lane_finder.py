import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
def nothing(x):
    return None

cv.namedWindow('Parameter Tuning')
cv.createTrackbar('gaussBlur', 'Parameter Tuning', 1 , 29, nothing)
cv.createTrackbar('lowerThresh', 'Parameter Tuning', 150 , 500, nothing)
cv.createTrackbar('upperThresh', 'Parameter Tuning', 300 , 500, nothing)

lanes = cv.imread('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/Suppli/test_images/whiteCarLaneSwitch.jpg')
print(lanes.shape)
grey = cv.cvtColor(lanes, cv.COLOR_BGR2GRAY)

while True:

    gb = cv.getTrackbarPos('gaussBlur', 'Parameter Tuning')
    lt = cv.getTrackbarPos('lowerThresh', 'Parameter Tuning')
    ut = cv.getTrackbarPos('upperThresh', 'Parameter Tuning')

    gaussBlur = cv.GaussianBlur(grey, (1,1), 0)
    edges = cv.Canny(gaussBlur, 150, 300)

    quad = np.array([[[110,539],[450,325], [525,325] ,[940,539]]], np.int32)

    cv.polylines(lanes, [quad], True, (0,255,0), thickness=3)

    cv.imshow('edges', edges)
    cv.imshow('lane', lanes)

    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()