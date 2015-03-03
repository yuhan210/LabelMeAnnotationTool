from BeautifulSoup import BeautifulSoup
import numpy as np
import cv2
import sys
import os

anno_folder = "/var/www/LabelMeAnnotationTool/Annotations/"
img_folder = "/var/www/LabelMeAnnotationTool/Images/"

if __name__ == "__main__":
	
	if (len(sys.argv)) != 2:
		print "Usage:", sys.argv[0], "collection"
		exit(-1)

	collection = sys.argv[1]
	for t in  os.listdir(os.path.join(anno_folder, collection)):
		tag_path = os.path.join(anno_folder, collection, t)
		im_path = os.path.join(img_folder, collection, (t.split('.')[0] + '.jpg'))
		print tag_path, im_path

		xml = BeautifulSoup(open(tag_path).read())
		im = cv2.imread(im_path)	

		for obj in  xml.annotation.findAll('object'): # for each object labeled
						
			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1, 1, 2))
			cv2.polylines(im, [pts], True, (0,255,255), thickness=3)
			
	#print y.annotation.polygon.findAll('pt')

		cv2.imshow('', im)
		cv2.waitKey(-1)
