# **Finding Lane Lines on the Road** 

A crucial task for Self-Driving Car Assitance.

![solidWhiteRight](https://user-images.githubusercontent.com/58968984/80316245-36e92e00-881a-11ea-9885-722cfd3358f3.jpg)


## My pipeline

![normal](https://user-images.githubusercontent.com/58968984/80318501-3d7ea200-8828-11ea-9542-8984be67aec0.png)

First Things first converting the input video/image to grayscale for it be used for Canny edge detection. 

![grayscale](https://user-images.githubusercontent.com/58968984/80318554-9a7a5800-8828-11ea-924c-6025d28004ca.png)

Then using gaussian blur which reduces noise depending on the kernel size. After which Canny edge detector filter is applied which finds edges based on gradients. I have used a GUI tool called trackbars in openCV for easier tuning and visualization of threshold values of the Canny filter.

![canny](https://user-images.githubusercontent.com/58968984/80318647-33a96e80-8829-11ea-8393-d17efe118518.png)

Next We Find a suitable ROI to isolate the lanes for a better result from the Hough Line Transform.

![roi](https://user-images.githubusercontent.com/58968984/80318745-dc57ce00-8829-11ea-98f9-697b828b6c30.png)

Using Hough Line Transform Line transform the points in cartesian coordinate space are lines in hough space and the lines which intersect in hough space are the points in cartesian coordinate which lie on a single line. So the important parameter to be tuned was threshold and max_line_gap. Changing the rho value gave fluctuation in slope values. rho value of 1 was the most stable. Line segments are formed whhich best fit the line.

![line segments](https://user-images.githubusercontent.com/58968984/80319134-6012ba00-882c-11ea-9e3a-10c2500914d5.png)

Now to extrapolate the average slope and intercept value of line segment to form single lines from top to bottom of ROI. Intially I used a more of a logical approach by connecting the lines to the bottom of the frame by creating a dummy line at the bottom and selecting the longest line segment, but the results were not as good as expected. Then Using a more mathematical approach by using the line equation y = mx + c. As the line must extend from top to bottom of roi we know the y axis value. The slope value and the intercept are calculated and averaged. Using line equation the x values are found therefore having the line coordinates required to plot the line. Also Outliers were avoided by providing a range of for slope values which will only be considered. This was how the drawLine function was modified. Using addWeighted function of openCV the lane line color was blended with the original image.

![lane marked](https://user-images.githubusercontent.com/58968984/80319449-dcf26380-882d-11ea-9ad7-e93624495a4d.png)

## The Challenge video

This alone was not enough to crack the challenge video. Since the Challenge video had different dimensions it was easy to differentite with the main videos. By using the image width/height different conditions were added in the main code for the challenge video. ROI was changed and the Canny's Threshold values were also changed. The challenge video had more realistic scenarios such as Shadows and Sunlight which interfered with Canny edge detection. 

![canny_challenge](https://user-images.githubusercontent.com/58968984/80319652-373ff400-882f-11ea-9393-197c1532c22b.png)

To counter this problem the HSV color value of lanes was used to better isolate the lanes.

![hsv](https://user-images.githubusercontent.com/58968984/80319690-69515600-882f-11ea-8786-7911aa6c6ce6.png)

Since HSV alone cannot be relied on as it fails in cases of shadows and changes in lighthing. So, a combination of HSV and Canny was used.

![cannyandhsv](https://user-images.githubusercontent.com/58968984/80320048-9ef73e80-8831-11ea-8c6d-5313d230c02c.png)

The results turned out to be good, though improvement in stability still needs to be made.

![challenge](https://user-images.githubusercontent.com/58968984/80320073-d5cd5480-8831-11ea-9bf5-e5fe15998483.png)


## 2. Potential shortcomings with current pipeline

One potential shortcoming would be when such a lightning condition occurs where both HSV and Canny edge fail though less but there is still a possibility.

Another potential shortcoming which is also less occuring is when the slope of the road increases a lot but it is ignored since it is above normal and considered as an outlier.


## 3. Possible improvements to pipeline

A possible improvement would be to avoid spikes in slope change.

Another possible improvement would be using a more suitable color isolation than HSV.
