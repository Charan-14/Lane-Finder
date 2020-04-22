import cv2 as cv
import numpy as np
from math import sqrt
import os

# Use to easily visualize the tuninng of paramters.

def parameterTuning():

    def nothing(x):
        return None

    cv.namedWindow('Parameter Tuning')

    cv.createTrackbar('rho', 'Parameter Tuning', 1 , 30, nothing)
    cv.createTrackbar('min_line_length', 'Parameter Tuning', 1 , 400, nothing)
    cv.createTrackbar('max_line_gap', 'Parameter Tuning', 1 , 400, nothing)
    cv.createTrackbar('threshold', 'Parameter Tuning', 1 , 200, nothing)
    
def trackbarPos():
    global rho
    global min_line_length
    global max_line_gap
    global threshold
    
    #Position of trackbar is stored
    rho = cv.getTrackbarPos('rho', 'Parameter Tuning')
    min_line_length = cv.getTrackbarPos('min_line_length', 'Parameter Tuning')
    max_line_gap = cv.getTrackbarPos('max_line_gap', 'Parameter Tuning')
    threshold = cv.getTrackbarPos('threshold', 'Parameter Tuning')
    
    #Creates ROI 
def ROI(image):
    mask = np.zeros_like(image) # creating a black image of size provided as argument
    vertices = np.array([[(100,539),(420,335), (540,335), (940,539)]], np.int32) # vertices of the polygon for roi
    #cv.polylines(edges, vertices, True, (0,255,0), thickness=3) # for visualization of polygon
    cv.fillPoly(mask, vertices, 255) # filling the roi with white pixels in efforts to extract the particular region
    global roi
    roi = cv.bitwise_and(mask, image) # AND operation with the canny edge image

#Draws single Lane Lines from bottom of roi to the top without any gaps on both sides 
def drawLines():
    rho = 15 # distance from..
    theta = np.pi/180 # angle..
    threshold = 80 # Number of intersecting lines in hough space, these lines are pts in original space that lie on the same line
    min_line_length = 200 # length in pixels required to be considered as a line 
    max_line_gap = 200 # maximum gap in pixels between subsequent line segments for them to be considered as one line
    global lane_marked
    lane_marked = lanes.copy() # copy of original image for creating lines
    lines = cv.HoughLinesP(roi, rho, theta, threshold, np.array([]), min_line_length, max_line_gap) # Houghline transform returns the lines 
    i = 0
    lengths_plus = []
    coordinates_plus =  []
    lengths_minus = []
    coordinates_minus =  []
    
    # Drawing the detected lines 
    for line in lines:

        for x1,y1,x2,y2 in line:
            length = sqrt(((x2-x1)**2 + (y2-y1)**2))
            slope = (y2-y1)/(x2-x1)
            if slope>0:
                lengths_plus.append(length)
                coordinates_plus.append([x1,y1,x2,y2])
            else:
                lengths_minus.append(length)
                coordinates_minus.append([x1,y1,x2,y2])
            
            #print('line', i,  " slope = ",  slope, ' length = ', length)
        i = i + 1    

    ind_plus = lengths_plus.index(max(lengths_plus))
    coor_plus = coordinates_plus[ind_plus]
    cv.line(lane_marked,(coor_plus[0],coor_plus[1]),(coor_plus[2],coor_plus[3]),(255,0,0),15)

    ind_minus = lengths_minus.index(max(lengths_minus))
    coor_minus = coordinates_minus[ind_minus]
    cv.line(lane_marked,(coor_minus[0],coor_minus[1]),(coor_minus[2],coor_minus[3]),(255,0,0),15)

# Adds original image and lane marked image to lower the intensity of the line marking
def reduceLineIntensity():
    original = lanes.copy()
    global lane_blended
    lane_blended = cv.addWeighted(lane_marked, 0.5, original, 0.5, 0) 

# Shows all significant results
def show():
    #cv.imshow('edges', edges)
    #cv.imshow('lane', lanes)
    #cv.imshow('roi', roi)
    cv.imshow('Lanes Marked', lane_blended)
    
 
# ___________________________________Main--Function___________________________________________

# Input of image or video file
path_folder = '/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/test_images'
for files in os.listdir(path_folder):
    
    lanes = cv.imread(path_folder + "/" + files)
    #print(lanes.shape)

    #parameterTuning()
    #Converting to grayscale for edge detection
    grey = cv.cvtColor(lanes, cv.COLOR_BGR2GRAY)

    while True:

        #trackbarPos()

        #Blurring image for better edge detection
        kernel = 1 # kernel size for blurring operation
        gaussBlur = cv.GaussianBlur(grey, (kernel,kernel), 0)
        
        #Best threshold values found after tuning on multiple test images.
        lowerThreshold = 100 # below which..
        upperThreshold = 200 # above which..
        cv.line(gaussBlur,(25,539),(225,539),(255,0,0),5)
        cv.line(gaussBlur,(900,539),(700,539),(255,0,0),5)
        edges = cv.Canny(gaussBlur, lowerThreshold, upperThreshold)

        ROI(edges)

        drawLines()

        reduceLineIntensity()

        show()

    #cv.imwrite('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/test_images_output/solidWhiteCurve_output.jpg', lane_blended)
    # Exiting the loop
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            break

    cv.destroyAllWindows()