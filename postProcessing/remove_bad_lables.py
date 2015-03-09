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
SIZE_THRESH = 5000

def getObjects(xml_path):
	xml = BeautifulSoup(open(xml_path).read())
	objs = []
	for obj in  xml.annotation.findAll('object'): # for each object labeled

		names = [name.contents[0] for name in obj.findAll('name')]
		assert(len(names) == 1)
		obj_name =  names[0]
			
		poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
		pts = np.array(poly_pts, np.int32)
		pts = pts.reshape((-1 , 1, 2))
		objs += [pts]

	return objs

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

def hasObj(obj_key, objs): # true if obj_key is in objs
	rect_key = cv2.boundingRect(obj_key)
	for obj in objs:
		rect = cv2.boundingRect(obj)
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
	files = [os.path.join(anno_folder, collection, f) for f in files]
		
	## load all xml files into memory (path: xml)
	file_idx = []
	xmls = {}
	file_dicts = {}
	for f in files:
		xmls[getFileKeyFromPath(f)] = BeautifulSoup(open(f).read())
		file_idx += [getFileKeyFromPath(f)]
		file_dicts[getFileKeyFromPath(f)] = f

	# First pass: remove labels with wrong sizes
	areas = []
	for t in files:
		tag_path = t
		im_path = os.path.join(img_folder, collection, (t.split('.')[-2].split('/')[-1] + '.jpg'))

		xml = xmls[getFileKeyFromPath(t)]
		for obj in xml.annotation.findAll('object'): # for each object labeled

			names = [name.contents[0] for name in obj.findAll('name')]
			assert(len(names) == 1)
			obj_name =  names[0]
			
			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1 , 1, 2))
			area = cv2.contourArea(pts)
			
			if area > SIZE_THRESH:
				obj.find('deleted').replaceWith('<deleted>1</deleted>')

		
	# Second pass: look at previous/next labels
	'''
	for i in xrange(1, len(file_idx)-1):	
		ind = file_idx[i]			
			
		objs = getObjects(file_dicts[ind])
		# for each object in xml[idx]
		for obj in objs:
			deleted = True
			# check if it's in the prev or nxt frame, keep it if yes
			if file_dicts.has_key(ind - 1):
				if (hasObj(obj, getObjects(file_dicts[ind-1]))):
					deleted = False
			if file_dicts.has_key(ind + 1):
				if (hasObj(obj, getObjects(file_dicts[ind + 1]))):
					deleted = False
			
			if deleted:
					if xmls[ind].find('deleted') >= 0:
						xmls[ind].find('deleted').replaceWith('<deleted>1</deleted>')
					else:
						print xmls[ind]
	'''
	
	for t in files:
		fh_out = open('/var/www/LabelMeAnnotationTool/Annotations/biking_1_test/' + t.split('/')[-1], 'w')	
		fh_out.write(xmls[getFileKeyFromPath(t)].prettify()+'\n')		
		fh_out.close()

	# Third pass: smoothing	

	
