'''
Copyrighted 2014
@Author: FinaDevil
'''

import sys, os
import mpo
import cv2
import numpy as np
from numpy import ma
from matplotlib import pyplot as plt
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
from tkFileDialog import askopenfilename

# cross_talk = np.matrix('0.03 0.03 0.03 0.03; 0.04 0.04 0.04 0.04; 0.03 0.03 0.03 0.03')
cross_talk = np.matrix('0.11 0.11 0.11 0.11; 0.17 0.17 0.17 0.17; 0.11 0.11 0.11 0.11')

def detach_stereo_image(file, filename):
	image = cv2.imread(file)
	size = image.shape[:2]
	width = int(size[1]/2)
	height = size[0]
	left = image[0:height, 0:width]
	right = image[0:height, width:2*width]
	cv2.imwrite(filename[:-4] + '_L.jpg', left)
	cv2.imwrite(filename[:-4] + '_R.jpg', right)
	return [left, right]

class App(Tkinter.Frame):
	def __init__(self, root):

		self.file = None
		self.filename = None
		self.left = None
		self.right = None
		self.matches = None
		self.kp1 = None
		self.kp2 = None
		self.size = None
		self.shift = 0

		f = Tkinter.Frame.__init__(self, root)

		#Tkinter.Entry(f, width = 60).pack(side= TOP,padx=12,pady=12)
		Tkinter.Label(self, text = "Browse image file").pack(padx=5, pady=5)

		button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

		Tkinter.Button(self, text='Choose file', command = self.getname).pack(**button_opt)

		# define options for opening or saving a file
		self.file_opt = options = {}
		options['defaultextension'] = '.MPO'
		options['filetypes'] = [('All file', '.*'), ('MPO file', '.MPO'), ('JPEG file', '.jpg')]
		options['initialdir'] = '/media/STUDY/Dopbox/3d-image-processing/'
		options['initialfile'] = 'demo.MPO'
		options['parent'] = root
		options['title'] = 'Select an image file'

		Tkinter.Button(self, text="Exit", command = self.quit).pack(side = BOTTOM)

	def getname(self):
		self.file = askopenfilename(**self.file_opt)
		print self.file
		self.filename = os.path.split(self.file)[1]
		print self.filename
		Tkinter.Label(self, text = self.file).pack(padx=5, pady=5)		
		Tkinter.Button(self, text='Start process', command = self.run).pack(padx=5, pady=5)

	def pre_proc(self):
		images = None
		if self.filename.split('.')[1].upper() == 'MPO':
			images = mpo.extractImagePair(self.file, self.filename[:-4], False)
			self.left = cv2.resize(cv2.imread(images[0], 1), (600, 800))
			self.right = cv2.resize(cv2.imread(images[1], 1), (600, 800))
		else:
			images = detach_stereo_image(self.file, self.filename)
			self.left = images[0]
			self.right = images[1]
		self.size = self.left.shape[:2]
		# print self.size
		vis = np.concatenate((self.left, self.right), axis=1)
		cv2.imwrite('1_origin_' + self.filename[:-3] + 'jpg', vis)
		return self

	def calculate_matches(self):
		orb = cv2.ORB()
		self.kp1, des1 = orb.detectAndCompute(self.left, None)
		self.kp2, des2 = orb.detectAndCompute(self.right, None)
		# BFMatcher with default params
		bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		# Match descriptors.
		self.matches = bf.match(des1,des2)
		return self

	def calculate_shift(self):
		sum = 0
		threshold_matches = []
		half_size = int(self.size[1]/2)
		threshold = int(self.size[1]/6)
		for match in self.matches:
			img1_idx = match.queryIdx
			(x1,y1) = self.kp1[img1_idx].pt
			if abs(x1 - half_size) < threshold:
				threshold_matches.append(match)
		threshold_matches = sorted(threshold_matches, key = lambda x:x.distance)
		img1_idx = threshold_matches[int(len(threshold_matches)/2)].queryIdx
		img2_idx = threshold_matches[int(len(threshold_matches)/2)].trainIdx
		(x1, y1) = self.kp1[img1_idx].pt
		(x2, y2) = self.kp2[img2_idx].pt
		self.shift = int(abs(x1 - x2))

	def pos_proc(self):
		self.left = self.left[0:self.size[0], self.shift:self.size[1]]
		self.right = self.right[0:self.size[0], 0:self.size[1] - self.shift]
		self.size = self.left.shape[:2]
		return self

	def reduce_ghost(self, cross_talk):
		row = cross_talk.shape[0]
		col = cross_talk.shape[1]
		step_x = self.size[0]/row
		step_y = self.size[1]/col

		for i in range(row):
			for j in range(col):
				a = i * step_x
				a1 = (i + 1) * step_x
				b = j * step_y
				b1 = (j + 1) * step_y
				temp_left = self.left[a:a1, b:b1]
				temp_right = self.right[a:a1, b:b1]
				cross_talk_val = cross_talk.item((i, j))
				inverse_reduce = 1 / (1 - cross_talk_val)
				l = inverse_reduce * (temp_left - cross_talk_val * temp_right)
				r = inverse_reduce * (temp_right - cross_talk_val * temp_left)
				
				l = np.int_(l)
				r = np.int_(r)

				l = np.asarray(l)
				r = np.asarray(r)

				# Set value < 0 to 0
				low_indexes_l = l < 0
				l[low_indexes_l] = 0
				low_indexes_r = r < 0
				r[low_indexes_r] = 0

				# Set value > 255 to 255
				hight_indexes_l = l > 255
				l[hight_indexes_l] = 255
				hight_indexes_r = r > 255
				r[hight_indexes_r] = 255

				self.left[a:a1, b:b1] = l
				self.right[a:a1, b:b1] = r

	def run(self):
		self.pre_proc()
		self.calculate_matches()
		self.calculate_shift()
		self.pos_proc()
		self.reduce_ghost(cross_talk)

		vis = np.concatenate((self.left, self.right), axis=1)
		cv2.imwrite('final_' + self.filename[:-3] + 'jpg', vis)

		Tkinter.Label(self, text = 'Done').pack(padx=5, pady=5)		
		cv2.imshow("Concated", vis)
		cv2.waitKey(0)

root = Tkinter.Tk()
root.title('3D image processing')
app = App(root).pack(padx = 100, pady = 50)
root.mainloop()
