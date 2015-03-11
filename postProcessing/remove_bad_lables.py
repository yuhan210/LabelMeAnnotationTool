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
from time import gmtime, strftime

anno_folder = "/var/www/LabelMeAnnotationTool/Annotations/"
img_folder = "/var/www/LabelMeAnnotationTool/Images/"
SIZE_THRESH = 3500

def convertToServerString(key, xml):
	rects = []
	out_str = ''
	
	for obj in xml.annotation.findAll('object'): # for each object labeled
		poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
		pts = np.array(poly_pts, np.int32)
		pts = pts.reshape((-1 , 1, 2))
		if obj.deleted.string.find('0') >= 0:
			rect = list(cv2.boundingRect(pts))	# (x,y,w,h)
			rect[0] = max(0, rect[0]) 
			rect[1] = max(0, rect[1]) 
			rects += [rect]
	rects.sort(key=lambda x: x[0])		
	if len(rects) > 0:
		out_str += str(key) + '.jpg;' + str(len(rects))+ ';'
		rect_str = ''
		for rect in rects:
			if len(rect_str) == 0:
				rect_str += '-1:' + str(rect[0]) + ','	 + str(rect[1]) + ',' + str(rect[2]) + ',' + str(rect[3])
			else:
				rect_str += ';-1:' + str(rect[0]) + ','	 + str(rect[1]) + ',' + str(rect[2]) + ',' + str(rect[3])
		out_str += rect_str
	return out_str

def mergeRects(rects):
	unionmap = range(len(rects))
	for i in xrange(len(rects)-1):
		rect_a = rects[i]
		for j in xrange(i+1, len(rects)):	
			rect_b = rects[j]
			percent = overlapPercent(rect_a, rect_b)
			if percent >= 20:
				unionmap[j] = unionmap[i]			
	
	merged_rects = []	
	# index merged_rect 	
	for i in xrange(len(rects)):
		# merge all i rects
		inds = [k for k,val in enumerate(unionmap) if val == i]
		if len(inds) > 0:
			merged_rect = rects[inds[0]]
			for j in xrange(1,len(inds)):
				merged_rect[0] += rects[inds[j]][0]				
				merged_rect[1] += rects[inds[j]][1]				
				merged_rect[2] += rects[inds[j]][2]				
				merged_rect[3] += rects[inds[j]][3]				
			
			merged_rect[0] /= len(inds)
			merged_rect[1] /= len(inds)
			merged_rect[2] /= len(inds)
			merged_rect[3] /= len(inds)

			merged_rects += [(inds, merged_rect)]


	return merged_rects

def getRects(xml_path):
	xml = BeautifulSoup(open(xml_path).read())
	rects = []
	for obj in  xml.annotation.findAll('object'): # for each object labeled

			
		poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
		pts = np.array(poly_pts, np.int32)
		pts = pts.reshape((-1 , 1, 2))
		if obj.deleted.string.find('0') >= 0:
			rect = list(cv2.boundingRect(pts))	# (x,y,w,h)
			rects += [rect]

	return rects

def getUndeletedRectsFromMem(xml):
	rects = []
	for obj in  xml.annotation.findAll('object'): # for each object labeled
		poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
		pts = np.array(poly_pts, np.int32)
		pts = pts.reshape((-1 , 1, 2))
		if obj.deleted.string.find('0') >= 0:
			rect = list(cv2.boundingRect(pts))	# (x,y,w,h)
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
	w = max(0, min(b_x2,a_x2) - max(a_x1, b_x1))
	h = max(0, min(a_y2,b_y2) - max(a_y1, b_y1))
	si = w * h
	area_a = rect_a[2] * rect_a[3]
	area_b = rect_b[2] * rect_b[3]
	su = area_a + area_b - si
	return (si/((area_a +area_b - si) * 1.0)) * 100

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
	
	if (len(sys.argv)) != 4:
		print "Usage:", sys.argv[0], "collection xml_outfolder server_file"
		exit(-1)
  	
	collection = sys.argv[1]
	files = os.listdir(os.path.join(anno_folder, collection))
	files.sort(key=lambda f: int(f.split('.xml')[0]))
	
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
			name = [name.contents[0] for name in obj.findAll('name')][0]
			poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in obj.polygon.findAll('pt')] # for each point in the polygon
			pts = np.array(poly_pts, np.int32)
			pts = pts.reshape((-1 , 1, 2))
			rect = list(cv2.boundingRect(pts))	# (x,y,w,h)
			area = cv2.contourArea(pts)
				
			if (area > SIZE_THRESH) or (area < 400):
				print 'Remove ', name, rect, ', size:', area, 'x-index:', rect[0],' in frame', getFileKeyFromPath(t)
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
			rect = list(cv2.boundingRect(pts))	# (x,y,w,h)
			
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
			pts = pts.reshape((-1, 1, 2))
			
			if obj.deleted.string.find('0') >= 0:
				rects += [list(cv2.boundingRect(pts))]
	
		merged_rects = mergeRects(rects)
		
		## delete objects with multiple rectangles
		counter = 0
		for obj in xml.annotation.findAll('object'):
			# should i delete the current rectangle
			if obj.deleted.string.find('0') >= 0:
				for pmr in merged_rects:
					if len(pmr[0]) > 1 and counter in pmr[0]:
						obj.deleted.string = unicode(1)	
				counter += 1			
	
		## add merged rectangles
		objs = xml.annotation.findAll('object')
		for mgr in merged_rects:
			if len(mgr[0]) > 1:
				obj = objs[mgr[0][0]]
				name = [name.contents[0] for name in obj.findAll('name')][0]
				rect = mgr[1]
				output_str = '<object><name>' + name + '</name><deleted>0</deleted><parts><hasparts/><ispartof/></parts><date>' + strftime('%d-%b-%Y %X',gmtime()) + '</date><id>' + str(len(obj.findAll('object'))) +  '</id><polygon><username>' + obj.polygon.username.string + '</username><pt><x>' + str(max(0,rect[0])) + "</x><y>" + str(max(rect[1], 0)) + '</y></pt><pt><x>' + str(rect[0] + rect[2])  + '</x><y>' + str(rect[1]) + '</y></pt><pt><x>' + str(rect[0]) + '</x><y>' + str(rect[1]+ rect[3]) + '</y></pt><pt><x>' + str(rect[0]+rect[2]) + '</x><y>' + str(rect[1]+rect[3]) + '</y></pt>' + '</polygon></object>'
				bstr = BeautifulSoup(output_str)
				xml.annotation.append(bstr)
				open('tmp','w').write(xml.prettify()+'\n')
				xml = BeautifulSoup(open('tmp').read()) 
				xmls[getFileKeyFromPath(f)] = xml
	
	print "Forth pass: smoothing"
	for i in xrange(1, len(file_idx)-1):	
		ind = file_idx[i]		# key	
		xml = xmls[ind]
		
		if file_dicts.has_key(ind - 1) and file_dicts.has_key(ind + 1):
			prev_objs = xmls[ind - 1].findAll('object')
			for prev_obj in prev_objs:
				if prev_obj.deleted.string.find('1') >= 0:
					continue
				
				poly_pts = [[int(pt.x.contents[0]), int(pt.y.contents[0])]  for pt in prev_obj.polygon.findAll('pt')] # for each point in the polygon
				pts = np.array(poly_pts, np.int32)
				pts = pts.reshape((-1, 1, 2))
				prev_rect = list(cv2.boundingRect(pts))	# (x,y,w,h)
				name = [name.contents[0] for name in prev_obj.findAll('name')][0]
				for nxt_rect in getUndeletedRectsFromMem(xmls[ind+1]):
					 
					#print prev_rect, nxt_rect, overlapPercent(prev_rect, nxt_rect)
					if overlapPercent(prev_rect, nxt_rect) >= 60:
						noMatch = True
						for cur_rect in getUndeletedRectsFromMem(xmls[ind]):
							if overlapPercent(cur_rect, prev_rect) >= 60 or overlapPercent(cur_rect, nxt_rect) >= 60:
								noMatch = False			
						if noMatch: # create a mean rectangle in this frame
							# merged
							for i in xrange(4):
								rect[i] = (prev_rect[i] + nxt_rect[i])/2

							print 'create a ', name, rect ,' in frame ', ind
							output_str = '<object><name>' + name + '</name><deleted>0</deleted><parts><hasparts/><ispartof/></parts><date>' + strftime('%d-%b-%Y %X',gmtime()) + '</date><id>-1</id><polygon><username>' + prev_obj.polygon.username.string + '</username><pt><x>' + str(max(0,rect[0])) + "</x><y>" + str(max(0,rect[1])) + '</y></pt><pt><x>' + str(rect[0] + rect[2])  + '</x><y>' + str(rect[1]) + '</y></pt><pt><x>' + str(rect[0]) + '</x><y>' + str(rect[1]+ rect[3]) + '</y></pt><pt><x>' + str(rect[0]+rect[2]) + '</x><y>' + str(rect[1]+rect[3]) + '</y></pt>' + '</polygon></object>'
							bstr = BeautifulSoup(output_str)
							xml.annotation.append(bstr)
							open('tmp','w').write(xml.prettify()+'\n')
							xml = BeautifulSoup(open('tmp').read()) 
							xmls[ind] = xml
	
	for t in files:
		fh_out = open('/var/www/LabelMeAnnotationTool/processedAnnotations/' + collection+ '/' + t.split('/')[-1], 'w')	
		fh_out.write(xmls[getFileKeyFromPath(t)].prettify()+'\n')		
		fh_out.close()

	fh_out = open(sys.argv[3], 'w')
	for t in files:
		out_str = convertToServerString(getFileKeyFromPath(t), xmls[getFileKeyFromPath(t)])
		if len(out_str) == 0:
			fh_out.write(str(getFileKeyFromPath(t)) + '.jpg;0;\n')
		else:
			fh_out.write(out_str + '\n')
	fh_out.close()
