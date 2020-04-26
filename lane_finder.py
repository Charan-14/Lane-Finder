import cv2 as cv
import numpy as np
from math import sqrt
from statistics import mean
import os

right_slope_avg = 0
right_intercept_avg = 0
left_slope_avg = 0
left_intercept_avg = 0

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
    global roi
    global height_img
    global res_y
    global lanes
    height_img = image.shape[0]
    
    # Different ROI for the challenge video as it has different dimensions
    if height_img == 720:
        
        lower_y = np.array([0, 0, 220]) # Defining ranges in HSV to isolate yellow and white color
        upper_y = np.array([255, 255, 255])
        lanes_hsv = cv.cvtColor(lanes, cv.COLOR_BGR2HSV) # Converting BGR image to HSV
        mask_y = cv.inRange(lanes_hsv, lower_y, upper_y) # Forming a mask
        res_y = cv.bitwise_and(lanes, lanes, mask=mask_y) # ANDing the mask with the original image 
        res_gray = cv.cvtColor(res_y, cv.COLOR_BGR2GRAY)
        image = cv.bitwise_or(res_gray, image) # ORing Canny edge image and HSV image for better line detection
        
        mask = np.zeros_like(image) # creating a black image of size provided as argument
        vertices = np.array([[(150,719),(500,490), (820,490), (1160,719)]], np.int32) # vertices of the polygon for roi
        #cv.polylines(edges, vertices, True, (0,255,0), thickness=3) # for visualization of polygon
        cv.fillPoly(mask, vertices, 255) # filling the roi with white pixels in efforts to extract the particular region
        roi = cv.bitwise_and(mask, image) # AND operation with the canny edge image
    
    else:
        
        mask = np.zeros_like(image) # creating a black image of size provided as argument
        vertices = np.array([[(100,539),(420,335), (540,335), (940,539)]], np.int32) # vertices of the polygon for roi
        #cv.polylines(edges, vertices, True, (0,255,0), thickness=3) # for visualization of polygon
        cv.fillPoly(mask, vertices, 255) # filling the roi with white pixels in efforts to extract the particular region
        roi = cv.bitwise_and(mask, image) # AND operation with the canny edge image

#Draws single Lane Lines from bottom of roi to the top without any gaps on both sides 
def drawLines():
    rho = 1 # distance from the coordinate origin
    theta = np.pi/180 # angle in radians in the polar coordinate system
    threshold = 45 # Number of intersecting lines in hough space, these lines are pts in original space that lie on the same line
    min_line_length = 40 # length in pixels required to be considered as a line 
    max_line_gap = 120 # maximum gap in pixels between subsequent line segments for them to be considered as one line
    global lane_marked
    global right_slope_avg 
    global right_intercept_avg 
    global left_slope_avg 
    global left_intercept_avg
    lane_marked = lanes.copy() # copy of original image for creating lines
    lines = cv.HoughLinesP(roi, rho, theta, threshold, np.array([]), min_line_length, max_line_gap) # Houghline transform returns the line segments  
    right_slope = []
    right_intercept = []
    left_slope = []
    left_intercept = []
    
    #Lane line starting and ending pts(ROI top and bottom)
    if height_img==720:
        y_top = 490
        y_bottom = 719
    else:
        y_top = 335
        y_bottom = 539
    
    #Using line segments predicted by hough transform
    for line in lines:
        for x1,y1,x2,y2 in line:
            slope = (y2-y1)/(x2-x1) # calculating slope of all lines
            intercept = y1 - (slope*x1) # intercept
            
            # Getting rid of outliers
            if slope>=0 and (slope<=0.2 or slope>=0.89):
                continue
            elif slope<0 and (slope>-0.2 or slope<-0.89):
                continue
                
            # Differentiating between left and right lane slopes
            if slope>0:
                left_intercept.append(intercept)
                left_slope.append(slope)
            else:
                right_intercept.append(intercept)
                right_slope.append(slope)
            
    # For right lane
    
    # When no line segments detected using previous results
    while len(right_intercept)==0:
        right_intercept.append(right_intercept_avg)
    while len(right_slope)==0:
        right_slope.append(right_slope_avg)
    
    # Using Average values for smoother results
    right_intercept_avg = mean(right_intercept)
    right_slope_avg = mean(right_slope)
    
    # Using line equation to find the X axis values for the lines as y value is already set to roi top and bottom
    xtop_right = (y_top - right_intercept_avg)/right_slope_avg
    xbottom_right = (y_bottom - right_intercept_avg)/right_slope_avg

    # for left lane
    
    # When no line segments detected using previous results
    while len(left_intercept)==0:
        left_intercept.append(left_intercept_avg)
    while len(left_slope)==0:
        left_slope.append(left_slope_avg)
    
    # Using Average values for smoother results
    left_intercept_avg = mean(left_intercept)
    left_slope_avg = mean(left_slope)
    
    # Using line equation to find the X axis values for the lines as y value is already set to roi top and bottom
    xtop_left = (y_top - left_intercept_avg)/left_slope_avg
    xbottom_left = (y_bottom - left_intercept_avg)/left_slope_avg 
        
    # drawing lines
    cv.line(lane_marked, (int(xtop_left), y_top), (int(xbottom_left), y_bottom), (255,0,0), 10)
    cv.line(lane_marked, (int(xtop_right), y_top), (int(xbottom_right), y_bottom), (255,0,0), 10)    
    
# Adds original image and lane marked image to lower the intensity of the line marking
def reduceLineIntensity():
    original = lanes.copy()
    global lane_blended
    lane_blended = cv.addWeighted(lane_marked, 0.5, original, 0.5, 0) 

# Shows all significant results
def show():
    #cv.imshow('edges', edges)
    #cv.imshow('lane', lanes)
    cv.imshow('roi', roi)
    cv.imshow('Lanes Marked', lane_blended)
    
 
# ___________________________________Main--Function___________________________________________

# Input of image or video file
#path_folder = '/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/test_images'
#for files in os.listdir(path_folder):
    
#lanes = cv.imread(path_folder + "/" + files)
#print(lanes.shape)

#parameterTuning()
#Converting to grayscale for edge detection

vid = cv.VideoCapture('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/test_videos/challenge.mp4')

frame_width = int(vid.get(3))
frame_height = int(vid.get(4))
out = cv.VideoWriter('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/test_videos_output/challenge_output.avi', cv.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))

while (vid.isOpened()):
    
    ret, lanes = vid.read()
    #trackbarPos()
    if ret == True:
        grey = cv.cvtColor(lanes, cv.COLOR_BGR2GRAY)

        #Blurring image for better edge detection
        kernel = 1 # kernel size for blurring operation
        gaussBlur = cv.GaussianBlur(grey, (kernel,kernel), 0)
        
        #Best threshold values found after tuning on multiple test images.
        if gaussBlur.shape[0]==720:
            lowerThreshold = 200 # below which.. #200
            upperThreshold = 600 # above which.. #600
        else:
            lowerThreshold = 100 # below which..
            upperThreshold = 300 # above which..
        
        edges = cv.Canny(gaussBlur, lowerThreshold, upperThreshold)

        ROI(edges)

        drawLines()

        reduceLineIntensity()

        show()
        out.write(lane_blended)

    #cv.imwrite('/home/blackpanther/Desktop/Projects/sdr_projects/lane_finder/test_images_output/solidWhiteCurve_output.jpg', lane_blended)
    # Exiting the loop
        k = cv.waitKey(25) & 0xFF
        if k == 27:
            break
    else:
        break
vid.release()
cv.destroyAllWindows()
