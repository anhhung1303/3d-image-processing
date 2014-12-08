#!/usr/bin/python
# Filename: mpo.py
# A python module that leverages exiftool to 

import os
from PIL import Image

def extractImagePair(mpoFile, image, exif=False):
	os.system('exiftool ' + mpoFile + ' -mpimage2 -b > ' + image + '_L.jpg')
	print 'Created ' + image + '_L.jpg'
	os.system('exiftool  -trailer:all= ' + mpoFile + ' -o ' + image + '_R.jpg')
	print 'Created ' + image + '_R.jpg'	
	if exif == True:
		print 'Writing EXIF data'
		os.system('exiftool ' + mpoFile + '> ' + image + '_EXIF.txt' )
	return [image + '_L.jpg', image + '_R.jpg']

def getExif(mpoFile):
	dict = {}
	fd = os.popen('exiftool ' + mpoFile)
	for line in fd:
		theSplit = line.split(' :')
		if len(theSplit) != 2:
			theSplit = line.split('t:')
		dict[theSplit[0].strip()] = theSplit[1].strip()
	fd.close()
	return dict

def sideBySide(im1, im2, type, output, show=False, JpgQuality=100):
	mpoPath = os.path.dirname(im1)
	imagePair = [im1,im2]
	im1 = Image.open(imagePair[1])
	im2 = Image.open(imagePair[0])
	size = im1.size
	im3 = im1.resize(((size[0]*2), size[1]), Image.NEAREST)
	im3.paste(im1, (0, 0))
	im3.paste(im2, (size[0], 0))
	
	print ('Saving image: ' + output)
	if type == 'jps': im3.save(output, 'JPEG', quality=JpgQuality)
	if type == 'pns': im3.save(output, 'PNG')
	if show == True: im3.show()
	print ('Save complete.')
	return output

def makeJPS(mpoFile, keepPair=False):
	mpoPath = os.path.dirname(mpoFile)
	jpsName = mpoFile.replace('.MPO','.JPS')
	imagePair = extractImagePair(mpoFile,jpsName.replace('.JPS',''))
	im1 = imagePair[1]
	im2 = imagePair[0]
	theFile = sideBySide(im1,im2,'jps',jpsName)
	if keepPair != True:
		for file in imagePair: os.remove(file)
	return theFile

def makePNS(mpoFile, keepPair=False):
	mpoPath = os.path.dirname(mpoFile)
	pnsName = mpoFile.replace('.MPO','.PNS')
	imagePair = extractImagePair(mpoFile,pnsName.replace('.PNS',''))
	im1 = imagePair[1]
	im2 = imagePair[0]
	theFile = sideBySide(im1,im2,'pns',pnsName)
	if keepPair != True:
		for file in imagePair: os.remove(file)
	return theFile

# out = sideBySide(images[0], images[1], 'jps', 'fuck_out', True, 100)

# exif = getExif('fuck.MPO')

# print exif["Convergence Angle"]

# print exif["Field Of View"]

# print exif["Focal Length"]
