'''
Author: Tiffany Chen
Parse tag files, and plot tagged polygons on images
Usage: process_xml.py collection 
'''
from BeautifulSoup import BeautifulSoup
import numpy as np
import cv2
import sys
import os
from random import randint
import time

anno_folder = "/var/www/LabelMeAnnotationTool/Annotations/"
img_folder = "/var/www/LabelMeAnnotationTool/Images/"

if __name__ == "__main__":
	
	if (len(sys.argv)) != 2:
		print "Usage:", sys.argv[0], "collection"
		exit(-1)
	
	count = 0
	collection = sys.argv[1]
	files = [os.path.join(anno_folder, collection, f) for f in os.listdir(os.path.join(anno_folder, collection))]
	files.sort(key=lambda x:os.path.getmtime(x), reverse=True)
	
	for t in files:
		if t.find('4293') < 0:
			continue
		print t
		tag_path = t
		im_path = os.path.join(img_folder, collection, (t.split('.')[-2].split('/')[-1] + '.jpg'))

		xml = BeautifulSoup(open(tag_path).read())
		print xml
		im = cv2.imread(im_path)	

		for obj in  xml.annotation.findAll('object'): # for each object labeled
			names = [name.contents[0] for name in obj.findAll('name')]
			assert(len(names) == 1)
			obj_name =  names[0]
			
			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1, 1, 2))
			cv2.polylines(im, [pts], True, (randint(0,255),randint(0,255),randint(0,255)), thickness=3)
			count += 1

		cv2.imshow('', im)

		cv2.waitKey(500)
	print count
