import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
def nothing(x):
    return None

cv.namedWindow('Parameter Tuning')

cv.createTrackbar('rho', 'Parameter Tuning', 1 , 30, nothing)
cv.createTrackbar('min_line_length', 'Parameter Tuning', 1 , 200, nothing)
cv.createTrackbar('max_line_gap', 'Parameter Tuning', 1 , 200, nothing)
cv.createTrackbar('threshold', 'Parameter Tuning', 1 , 50, nothing)

lanes = cv.imread('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/Suppli/test_images/whiteCarLaneSwitch.jpg')
print(lanes.shape)
grey = cv.cvtColor(lanes, cv.COLOR_BGR2GRAY)

while True:

    #rho = cv.getTrackbarPos('rho', 'Parameter Tuning')
    #min_line_length = cv.getTrackbarPos('min_line_length', 'Parameter Tuning')
    #max_line_gap = cv.getTrackbarPos('max_line_gap', 'Parameter Tuning')
    #threshold = cv.getTrackbarPos('threshold', 'Parameter Tuning')

    kernel = 1
    gaussBlur = cv.GaussianBlur(grey, (kernel,kernel), 0)
    
    lowerThreshold = 150
    upperThreshold = 300
    edges = cv.Canny(gaussBlur, lowerThreshold, upperThreshold)

    mask = np.zeros_like(edges)
    vertices = np.array([[(115,539),(450,325), (525,325), (940,539)]], np.int32)
    #cv.polylines(lanes, [quad], True, (0,255,0), thickness=3)
    cv.fillPoly(mask, vertices, 255)
    roi = cv.bitwise_and(mask, edges)
    
    rho = 1 
    theta = np.pi/180 
    threshold = 20   
    min_line_length = 0 
    max_line_gap = 95  
    lane_marked = lanes.copy()
    lines = cv.HoughLinesP(roi, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)

    for line in lines:
        for x1,y1,x2,y2 in line:
            cv.line(lane_marked,(x1,y1),(x2,y2),(255,0,0),10)

# Create a "color" binary image to combine with line image
    #color_edges = np.dstack((edges, edges, edges)) 
    original = lanes.copy()
# Draw the lines on the edge image
    lines_edges = cv.addWeighted(lane_marked, 0.5, original, 0.5, 0) 
    
    cv.imshow('edges', edges)
    cv.imshow('lane', lanes)
    cv.imshow('roi', roi)
    cv.imshow('Lanes Marked', lines_edges)

    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()