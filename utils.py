from PIL import Image
import os, random

def show_image(filename):
	with img = Image.open(filename):
		img.show()


def show_random_image(filefolder):
	filename = random.choice(os.listdir(filefolder))

if __name__ == "__main__":
	print "...image utils..."
	show_random_image("photo_sample")