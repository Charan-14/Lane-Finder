import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

# Use to easily visualize the tuninng of paramters.

def parameterTuning():

    def nothing(x):
        return None

    cv.namedWindow('Parameter Tuning')

    cv.createTrackbar('rho', 'Parameter Tuning', 1 , 30, nothing)
    cv.createTrackbar('min_line_length', 'Parameter Tuning', 1 , 200, nothing)
    cv.createTrackbar('max_line_gap', 'Parameter Tuning', 1 , 200, nothing)
    cv.createTrackbar('threshold', 'Parameter Tuning', 1 , 50, nothing)

def trackbarPos():
    #Position of trackbar is stored
    rho = cv.getTrackbarPos('rho', 'Parameter Tuning')
    min_line_length = cv.getTrackbarPos('min_line_length', 'Parameter Tuning')
    max_line_gap = cv.getTrackbarPos('max_line_gap', 'Parameter Tuning')
    threshold = cv.getTrackbarPos('threshold', 'Parameter Tuning')

#Creates ROI 
def ROI(image):
    mask = np.zeros_like(image) # creating a black image of size provided as argument
    vertices = np.array([[(115,539),(450,325), (525,325), (940,539)]], np.int32) # vertices of the polygon for roi
    #cv.polylines(lanes, [quad], True, (0,255,0), thickness=3) # for visualization of polygon
    cv.fillPoly(mask, vertices, 255) # filling the roi with white pixels in efforts to extract the particular region
    global roi
    roi = cv.bitwise_and(mask, image) # AND operation with the canny edge image

#Draws single Lane Lines from bottom of roi to the top without any gaps on both sides 
def drawLines():
    rho = 1 # distance from  
    theta = np.pi/180 #angle
    threshold = 20 # Number of intersecting lines in hough space, these lines are pts in original space that lie on the same line
    min_line_length = 1 # number pixels required to be considered as a line 
    max_line_gap = 95 # maximum gap in pixels between subsequent line segments for them to be considered as one line
    global lane_marked
    lane_marked = lanes.copy() # copy of original image for creating lines
    lines = cv.HoughLinesP(roi, rho, theta, threshold, np.array([]), min_line_length, max_line_gap) # Houghline transform returns the lines 

    # Drawing the detected lines 
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv.line(lane_marked,(x1,y1),(x2,y2),(255,0,0),10)

# Adds original image and lane marked image to lower the intensity of the line marking
def lineIntensity():
    original = lanes.copy()
    global lines_edges
    lines_edges = cv.addWeighted(lane_marked, 0.5, original, 0.5, 0) 

# Shows all significant results
def show():
    cv.imshow('edges', edges)
    cv.imshow('lane', lanes)
    cv.imshow('roi', roi)
    cv.imshow('Lanes Marked', lines_edges)

# ___________________________________Main--Function___________________________________________

# Input of image or video file
lanes = cv.imread('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/Suppli/test_images/whiteCarLaneSwitch.jpg')
print(lanes.shape)

#Converting to grayscale for edge detection
grey = cv.cvtColor(lanes, cv.COLOR_BGR2GRAY)

while True:

    #Blurring image for better edge detection
    kernel = 1 # kernel size for blurring operation
    gaussBlur = cv.GaussianBlur(grey, (kernel,kernel), 0)
    
    #Best threshold values found after tuning on multiple test images.
    lowerThreshold = 150 # below which..
    upperThreshold = 300 # above which..
    edges = cv.Canny(gaussBlur, lowerThreshold, upperThreshold)

    ROI(edges)

    drawLines()

    lineIntensity()

    show()

    # Exiting the loop
    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()