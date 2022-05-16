from __future__ import print_function
import cv2 as cv
import numpy as np
import random
from os import listdir

def filtruj(elipsy, src):

    for i in range(len(elipsy)-1,0,-1):
        if (elipsy[i] == None or 3.14*elipsy[i][1][0]*elipsy[i][1][1] < 150):
            elipsy.pop(i)
        
    indexes = []

    for i in range(len(elipsy)-1):
        for j in range(i,len(elipsy)):
            if (abs(elipsy[i][0][0] - elipsy[j][0][0]) < 2.5 and abs(elipsy[i][0][1] - elipsy[j][0][1]) < 2.5):
                if(j not in indexes and j != i):
                    indexes.append(j)

    indexes.sort(reverse = True)
    for i in indexes:
        elipsy.pop(i)

    params = cv.SimpleBlobDetector_Params()
    
    params.filterByArea = True
    params.minArea = src.size/9000
    params.filterByConvexity = True
    params.minConvexity = 0.90
    params.filterByInertia = True
    params.minInertiaRatio = 0.02
    params.filterByCircularity = True
    params.minCircularity = 0.25
    
    detector = cv.SimpleBlobDetector_create(params)
    keypoints = detector.detect(src)
    # blank = np.zeros((1, 1))
    # blobs = cv.drawKeypoints(src, keypoints, blank, (0, 0, 255),
    #                         cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # cv.imshow("Blobs", blobs)

    points = []
    for i in keypoints:
        points.append(i.pt)

    filtered = []
    
    for i in range(len(elipsy)):
        for j in range(len(points)):
            if (abs(elipsy[i][0][0] - points[j][0]) < 3.5 and abs(elipsy[i][0][1] - points[j][1]) < 3.5):
                filtered.append(elipsy[i])

    return filtered

def countDots(src, imname):

    # Convert image to gray and blur it
    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    gray = cv.blur(gray, (3,3))

    # source_window = 'Source'
    # cv.namedWindow(source_window)
    # cv.imshow(source_window, src)
    max_thresh = 255
    thresh = 100 # initial threshold

    canny_output = cv.Canny(gray, thresh, thresh * 2)

    contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    minRect = [None]*len(contours)
    minEllipse = [None]*len(contours)
    for i, c in enumerate(contours):
        minRect[i] = cv.minAreaRect(c)
        if c.shape[0] > 5:
            minEllipse[i] = cv.fitEllipse(c)

    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    drawing = src.copy()

    # canny_output = cv.cvtColor(canny_output, cv.COLOR_GRAY2BGR)
    # cv.drawContours(canny_output,contours,-1,(255,0,0))

    # for i in range(len(minEllipse)):
    #     cv.ellipse(canny_output, minEllipse[i], (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)), thickness = -1)

    # cv.imshow('Canny', canny_output)

    minEllipse = filtruj(minEllipse, src)

    sciany = []

    for i in range(len(minEllipse)):
        flag = 0
        if(len(sciany)==0):
            sciany.append([minEllipse[i]])
            continue
        for s in sciany:
            if(abs(s[0][2]-minEllipse[i][2]) < 10 and abs(s[0][1][0]-minEllipse[i][1][0]) < 15 and abs(s[0][1][1]-minEllipse[i][1][1]) < 15):
                s.append(minEllipse[i])
                flag = 1
                continue
        if(flag == 0):
            sciany.append([minEllipse[i]])

    for i in range(len(minEllipse)):
        if(minEllipse[i] in sciany[0]):
            color = (0,0,255)
        elif(minEllipse[i] in sciany[1]):
            color = (0,255,0)
        elif(minEllipse[i] in sciany[2]):
            color = (255,0,0)
        else:
            color = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))

        cv.ellipse(drawing, minEllipse[i], color, thickness = -1)

    cv.waitKey()

    top = []
    max = -1
    for i in sciany:
        avg = 0
        for j in i:
            avg += j[0][1]
        avg = avg/len(i)
        if(avg < max) or (max < 0):
            max = avg
            top = i

    print(len(top))
    cv.putText(drawing, str(len(top)),(10,50), cv.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv.LINE_AA)
    # cv.imshow('elipsy', drawing)
    cv.imwrite('output/'+imname, drawing)

for i in listdir('input/'):
    if(i == 'Thumbs.db'):
        continue
    img = cv.imread('input/'+i)
    countDots(img, i)