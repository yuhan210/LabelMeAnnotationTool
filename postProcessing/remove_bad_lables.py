'''
Remove crazy annotations from turkers
'''
from BeautifulSoup import BeautifulSoup
import numpy as np
import cv2
import sys
import os
from random import randint
import time
import matplotlib.pyplot as plt

anno_folder = "/var/www/LabelMeAnnotationTool/Annotations/"
img_folder = "/var/www/LabelMeAnnotationTool/Images/"
SIZE_THRESH = 4500


def mergeRects(rects):
	unionmap = range(len(rects))
	for rect in rects:	
		if overlapPercent()			
	return rects

def getRects(xml_path):
	xml = BeautifulSoup(open(xml_path).read())
	rects = []
	for obj in  xml.annotation.findAll('object'): # for each object labeled

			
		poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
		pts = np.array(poly_pts, np.int32)
		pts = pts.reshape((-1 , 1, 2))
		if obj.deleted.string.find('0') >= 0:
			rect = cv2.boundingRect(pts)	# (x,y,w,h)
			rects += [rect]

	return rects

def overlapPercent(rect_a, rect_b):
	a_x1 = rect_a[0]
	a_y1 = rect_a[1]
	a_x2 = rect_a[0] + rect_a[2]
	a_y2 = rect_a[1] + rect_a[3]
	
	b_x1 = rect_b[0]
	b_y1 = rect_b[1]
	b_x2 = rect_b[0] + rect_b[2]
	b_y2 = rect_b[1] + rect_b[3]
	si = max(0, max(a_x1, b_x1) - min(b_x2,a_x2)) * max(0, max(a_y1, b_y1) - min(a_y2, b_y2))
	area_a = rect_a[2] * rect_a[3]
	area_b = rect_b[2] * rect_b[3]
	return (area_a + area_b)/((area_a +area_b - si) * 1.0)

def isIntersect(rect_a, rect_b):# (x,y, w,h)
	a_x1 = rect_a[0]
	a_y1 = rect_a[1]
	a_x2 = rect_a[0] + rect_a[2]
	a_y2 = rect_a[1] + rect_a[3]
	
	b_x1 = rect_b[0]
	b_y1 = rect_b[1]
	b_x2 = rect_b[0] + rect_b[2]
	b_y2 = rect_b[1] + rect_b[3]

	noOverlap = a_x1 > b_x2 or b_x1 > a_x2 or a_y1 > b_y2 or b_y1 > a_y2
	return not noOverlap


def hasObj(rect_key, rects): # true if obj_key is in objs
	for rect_key in rects:
		if isIntersect(rect, rect_key):
			return True

	return False

def getFileKeyFromPath(p):
	return int(p.split('.')[-2].split('/')[-1])

if __name__ == "__main__":
	
	if (len(sys.argv)) != 2:
		print "Usage:", sys.argv[0], "folder"
		exit(-1)
  	
	collection = sys.argv[1]
	files = os.listdir(os.path.join(anno_folder, collection))
	files.sort(key=lambda f: f.split('.xml')[0])
	# sorted file paths
	files = [os.path.join(anno_folder, collection, f) for f in files]
			
	## load all xml files into memory (path: xml)
	file_idx = []
	xmls = {}
	file_dicts = {}
	for f in files:
		# key -> xml string 
		xmls[getFileKeyFromPath(f)] = BeautifulSoup(open(f).read())
		# list of keys
		file_idx += [getFileKeyFromPath(f)]
		# key to file path
		file_dicts[getFileKeyFromPath(f)] = f

	print "First pass: remove labels with wrong sizes.."
	areas = []
	for t in files:
		tag_path = t

		xml = xmls[getFileKeyFromPath(t)]
		for obj in xml.annotation.findAll('object'): # for each object labeled

			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1 , 1, 2))
			area = cv2.contourArea(pts)
			if area > SIZE_THRESH or area < 10:
				obj.deleted.string = unicode(1)
			
	print "Second pass: look at previous/next labels"
	for i in xrange(1, len(file_idx)-1):	
		ind = file_idx[i]		# key	
			
		# for each object in xml[idx]
		xml = xmls[ind]
		for obj in xml.annotation.findAll('object'):
			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1 , 1, 2))
			rect = cv2.boundingRect(pts)	# (x,y,w,h)
			
			deleted = True
			# check if it's in the prev or nxt frame, keep it if yes
			if file_dicts.has_key(ind - 1):
				if (hasObj(rect, getRects(file_dicts[ind-1]))):
					deleted = False
			if file_dicts.has_key(ind + 1):
				if (hasObj(rect, getRects(file_dicts[ind + 1]))):
					deleted = False
			
			if deleted:
					obj.deleted.string = unicode(1)
	
	print "Third pass: combining rects within each frame"
	for f in files:

		xml = xmls[getFileKeyFromPath(f)]
		rects = []		
		for obj in xml.annotation.findAll('object'): # for each object labeled

			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1 , 1, 2))
			rects += [cv2.boundingRect(pts)]
				
		sub_rects = mergeRects(rects)	
		
	# Forth pass: smoothing	
	
		
	for t in files:
		fh_out = open('/var/www/LabelMeAnnotationTool/tmp/biking_1/' + t.split('/')[-1], 'w')	
		fh_out.write(xmls[getFileKeyFromPath(t)].prettify()+'\n')		
		fh_out.close()


	
