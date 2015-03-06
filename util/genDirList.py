import os
import sys

if __name__ == "__main__":

	folder = sys.argv[1]
	segs = folder.split("/")
	folder_name = ""
	if len(segs[-1]) == 0:
		folder_name = segs[-2]
	else:
		folder_name = segs[-1]
		
	for f in os.listdir(folder):
		print folder_name + "," +f
