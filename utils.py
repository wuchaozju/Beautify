from PIL import Image
import os, random
import scipy.ndimage
from resizeimage import resizeimage
import math

FileFolder = "photo_sample"


def show_image(filename):
	with Image.open(filename) as img:
		img.show()


def show_random_image():
	filename = random.choice(os.listdir(FileFolder))
	path = os.path.join(FileFolder, filename)
	show_image(path)


def clean_images():
	allfiles = [f for f in os.listdir(FileFolder) if os.path.isfile(
		os.path.join(FileFolder,f))]

	for file in allfiles:
		path = os.path.join(FileFolder, file)

		size = os.stat(path).st_size
		if size < 10000:
			os.remove(path)
			continue
		
		channel = scipy.ndimage.imread(path).shape[2]
		if channel != 3:
			os.remove(path)


def stat_images():
	allfiles = [os.path.join(FileFolder, f) for f in os.listdir(FileFolder) if os.path.isfile(
		os.path.join(FileFolder + "",f))]

	allwidths = [scipy.ndimage.imread(f).shape[0] for f in allfiles]
	allheights = [scipy.ndimage.imread(f).shape[1] for f in allfiles]
	#allchannels = [scipy.ndimage.imread(f).shape[2] for f in allfiles]

	#print "Max Width: " + str(max(allwidths))
	#print "Min Width: " + str(min(allwidths))
	#print "Max Height: " + str(max(allheights))
	#print "Min Height: " + str(min(allheights))

	return min(allheights), min(allwidths)
	#print allchannels


def crop_and_resize(size):
	allfiles = [f for f in os.listdir(FileFolder) if os.path.isfile(
		os.path.join(FileFolder,f))]

	for filename in allfiles:
		path = os.path.join(FileFolder,filename)
		with open(path, 'r+b'):
			with Image.open(path) as img:
				img = resizeimage.resize_crop(img, [size, size])
				img.save(os.path.join(FileFolder + "/output",filename), img.format)


if __name__ == "__main__":
	print "...image utils..."

	clean_images()
	min_size = int(math.sqrt(min(stat_images())))
	crop_and_resize(min_size * min_size)
