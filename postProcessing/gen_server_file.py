'''
Generate a similar server output to face recognizer
'''

from BeautifulSoup import BeautifulSoup
import numpy as np
import cv2
import sys

def overlapPercent(rect_a, rect_b):
	a_x1 = rect_a[0]
	a_y1 = rect_a[1]
	a_x2 = rect_a[0] + rect_a[2]
	a_y2 = rect_a[1] + rect_a[3]
	
	b_x1 = rect_b[0]
	b_y1 = rect_b[1]
	b_x2 = rect_b[0] + rect_b[2]
	b_y2 = rect_b[1] + rect_b[3]
	w = max(0, min(b_x2,a_x2) - max(a_x1, b_x1))
	h = max(0, min(a_y2,b_y2) - max(a_y1, b_y1))
	si = w * h
	area_a = rect_a[2] * rect_a[3]
	area_b = rect_b[2] * rect_b[3]
	su = area_a + area_b - si
	return (si/((area_a +area_b - si) * 1.0)) * 100

def getAllRects(l):
	num = int(l.split(';')[0])
	rects = []
	for i in xrange(num):
		label = int(l.split(';')[i+1].split(':')[0])
		rect = [int(x) for x in (l.split(';')[i+1].split(':')[1].split(','))]
		rects += [[label, rect]]
	
	return rects


def convertToOutputString(rects):
	out_str = str(len(rects))+ ';'
	rect_str = ''
	for rect in rects:
		print rect
		if len(rect_str) == 0:
			rect_str += str(rect[0]) + ':' + str(rect[1][0]) + ','	 + str(rect[1][1]) + ',' + str(rect[1][2]) + ',' + str(rect[1][3])
		else:
			rect_str += ';' + str(rect[0]) + ':' + str(rect[1][0]) + ','	 + str(rect[1][1]) + ',' + str(rect[1][2]) + ',' + str(rect[1][3])

	out_str += rect_str
	return out_str


if __name__ == "__main__":
	if (len(sys.argv)) != 5:				
		print 'Usage:', sys.argv[0], 'tmp_groundtruth_file framenum server_output_path collection'
		exit(-1)
		
	input_file = sys.argv[1]
	frame_num = int(sys.argv[2])
	output_path = sys.argv[3]
	collection = sys.argv[4]

	annos = {}
	## assign labels
	for line in open(input_file).readlines():
		key = int(line.strip().split('.')[0])
		annos[key] = ';'.join(line.strip().split(';')[1:])
		
	## extract features
	counter = 0
	prev_rects = []
	for i in xrange(frame_num):
		
		if annos.has_key(i):
			rects = getAllRects(annos[i])			
			
			if len(prev_rects) == 0:
				prev_rects = rects
				for rect in rects:
					rect[0] = counter
					counter += 1

			else: ## propagate labels
				for cur_rect in rects:
					hasMatch = False
					for prev_rect in prev_rects:
						if overlapPercent(cur_rect[1], prev_rect[1]) >= 5:
							cur_rect[0] = prev_rect[0]	
							hasMatch = True
							break
					if not hasMatch:
						cur_rect[0] = counter
						counter += 1
				
			out_str = convertToOutputString(rects)
			
			annos[i] = out_str
			prev_rects = rects	
	
		else:
			annos[i] = '0;'
			prev_rects = []

	## tracking/cleaning
		

	## extract features 
	frame_folder = '/home/yuhan/traffic-sign-detection/videos/frames/' + collection  + '/'
	for i in xrange(frame_num): 
		rects = getAllRects(annos[i])
		im = cv2.imread(frame_folder + str(i) + '.jpg')
		
		frame_str = str(len(rects))+ ';'
		rect_str = ''
		#print i, rects
		for rect in rects:
			bbx = rect[1]
			roi = im[int(bbx[1]):(int(bbx[1]) + int(bbx[3])), int(bbx[0]):(int(bbx[0]) + int(bbx[2]))]		
			#print roi.shape
			surf = cv2.SIFT(nfeatures=26, edgeThreshold=100, contrastThreshold=0.01)
			kp, des = surf.detectAndCompute(roi, None)
			fps = []
			feature_str = ''
			for p in kp:
				l_p = list(p.pt)
				l_p[0] += bbx[0]
				l_p[1] += bbx[1]
				l_p[0] = int(l_p[0])
				l_p[1] = int(l_p[1])
				if len(feature_str) == 0:
					feature_str += str(l_p[0]) + '_' + str(l_p[1])
				else:
					feature_str += ',' + str(l_p[0]) + '_' + str(l_p[1])
			
				fps += [l_p]
			if len(rect_str) == 0:
				rect_str += str(rect[0]) + ':' + str(rect[1][0]) + ','	 + str(rect[1][1]) + ',' + str(rect[1][2]) + ',' + str(rect[1][3]) + ';' + feature_str
			else:
				rect_str += ';' + str(rect[0]) + ':' + str(rect[1][0]) + ','	 + str(rect[1][1]) + ',' + str(rect[1][2]) + ',' + str(rect[1][3]) + ';' + feature_str
	
		frame_str += rect_str
		annos[i] = frame_str
		'''	
		cv2.namedWindow(str(i))
		cv2.moveWindow(str(i), 10, 50)
		cv2.imshow( str(i),im)
		cv2.waitKey(500)
		cv2.destroyWindow(str(i))
		'''
	fh_out = open(output_path, 'w')
	for i in xrange(frame_num):
		fh_out.write(str(i) + '.jpg;' + annos[i] + '\n')

	fh_out.close()
