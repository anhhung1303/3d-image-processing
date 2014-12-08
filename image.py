'''
Copyrighted 2014
@Author: FinaDevil
'''

import sys, os
import mpo
import cv2
import numpy as np
from matplotlib import pyplot as plt

def calculate_shift(matches, kp1, kp2):
	sum = 0
	for match in matches:
		img1_idx = match.queryIdx
		img2_idx = match.trainIdx
		(x1,y1) = kp1[img1_idx].pt
		(x2,y2) = kp2[img2_idx].pt
		sum += abs((x1 - x2))
	return int(sum/len(matches))

def pre_proc():
	images = mpo.extractImagePair(sys.argv[1], sys.argv[1][:-4], False)
	left = cv2.imread(images[0], 1)
	right = cv2.imread(images[1], 1)
	left = cv2.resize(left, (0,0), fx = 0.2, fy = 0.2)
	right = cv2.resize(right, (0,0), fx = 0.2, fy = 0.2)
	size = left.shape[:2]
	return left, right, size

def calculate_matches(left, right):
	orb = cv2.ORB()
	kp1, des1 = orb.detectAndCompute(left,None)
	kp2, des2 = orb.detectAndCompute(right,None)
	# BFMatcher with default params
	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
	# Match descriptors.
	matches = bf.match(des1,des2)
	return matches, kp1, kp2

def pos_proc(left, right, shift, size):
	left = left[0:size[0], shift:size[1]]
	right = right[0:size[0], 0:size[1] - shift]
	size = left.shape[:2]
	return left, right, size

# left, right, size = pre_proc()
# matches, kp1, kp2 = calculate_matches(left, right)
# shift = calculate_shift(matches, kp1, kp2)
# left, right, size = pos_proc(left, right, shift, size)

# vis = np.concatenate((left, right), axis=1)
# cv2.imwrite(sys.argv[1][:-3] + 'jpg', vis)
# cv2.imshow("Concated", vis)
# cv2.waitKey(0)

def detach_stereo_image(filename):
	image = cv2.imread(filename)
	cv2.imshow('Origin', image)
	size = image.shape[:2]
	width = int(size[1]/2)
	height = size[0]
	left = image[0:height, 0:width]
	right = image[0:height, width:2*width]
	cv2.imwrite(filename[:-4] + '_L.jpg', left)
	cv2.imwrite(filename[:-4] + '_R.jpg', right)
	cv2.imshow('Left', left)
	cv2.imshow('Right', right)
	cv2.waitKey(0)

detach_stereo_image('stereo.jpg')