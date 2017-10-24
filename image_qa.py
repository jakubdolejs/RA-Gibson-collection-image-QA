import os
import sys
import re
from exifpy import EXIF as exifread
filename = r'^(R|C)[0-9]{4}_[0-9]{2}\.'
resolution = 600
size = 1900
title = 'Gibson Photographic Collection'
creator = 'R A Gibson'
cright = 'Hackney Archives Copyright'
directory = '.'
if len(sys.argv) > 1:
	for arg in sys.argv:
		if arg[0:3] == '-r=':
			resolution = int(arg[3:])
		elif arg[0:3] == '-s=':
			size = int(arg[3:])
		elif arg[0:3] == '-t=':
			title = arg[3:]
		elif arg[0:3] == '-a=':
			creator = arg[3:]
		elif arg[0:3] == '-c=':
			cright = arg[3:]
		elif os.path.isdir(arg):
			directory = arg
files = os.listdir(directory)
resolutionUnits = {
	1: 'undefined',
	2: 'in',
	3: 'cm'
}
for item in files:
	if item.endswith('.tif') or item.endswith('.tiff'):
		f = open(directory+item, 'rb')
		fnmatch = re.match(filename, item)
		tags = exifread.process_file(f)
		samples = 0
		bits = 0
		resolutionX = 72
		resolutionY = 72
		resolutionUnit = 2
		namevalid = fnmatch
		if fnmatch:
			colour = fnmatch.group(1)
		else:
			colour = None
		sizevalid = 'Image ImageWidth' in tags.keys() and 'Image ImageLength' in tags.keys() and re.match(r'[0-9]+',str(tags['Image ImageWidth'])) and re.match(r'[0-9]+',str(tags['Image ImageLength']))
		depthvalid = 'Image BitsPerSample' in tags.keys()
		channelcountvalid = 'Image SamplesPerPixel' in tags.keys()
		titlevalid = 'Image ImageDescription' in tags.keys()
		creatorvalid = 'Image Artist' in tags.keys()
		copyrightvalid = 'Image Copyright' in tags.keys()
		for tag in tags.keys():
			if (tag == 'Image ImageWidth' or tag == 'Image ImageLength') and re.match(r'[0-9]+$',str(tags[tag])) and int(str(tags[tag])) < size:
				sizevalid = False
			elif tag == 'Image XResolution':
				match = re.match(r'([0-9]+)',str(tags[tag]))
				if match:
					resolutionX = int(match.group(1))
			elif tag == 'Image YResolution':
				match = re.match(r'([0-9]+)',str(tags[tag]))
				if match:
					resolutionY = int(match.group(1))
			elif tag == 'Image ResolutionUnit':
				match = re.match(r'([0-9]+)', str(tags[tag]))
				if match:
					resolutionUnit = int(match.group(1))
			elif tag == 'Image BitsPerSample':
				bits = str(tags[tag])[1:-1].split(', ')
			elif tag == 'Image SamplesPerPixel':
				samples = int(str(tags[tag]))
			elif tag == 'Image ImageDescription' and str(tags[tag]) != title:
				titlevalid = False
			elif tag == 'Image Artist' and str(tags[tag]) != creator:
				creatorvalid = False
			elif tag == 'Image Copyright' and str(tags[tag]) != cright:
				copyrightvalid = False
		if samples == 3 and colour == 'C':
			channelcountvalid = True
		elif samples == 1 and colour == 'R':
			channelcountvalid = True
		else:
			channelcountvalid = False
		for bit in bits:
			if bit != '8':
				depthvalid = False
				break
		resolutionvalid = resolutionUnit == 2 and resolutionX == resolution and resolutionY == resolution
		if namevalid and sizevalid and resolutionvalid and depthvalid and channelcountvalid and titlevalid and creatorvalid and copyrightvalid:
			print('PASS: '+item)
		else:
			print('FAIL: '+item)
			if not namevalid:
				print('\tInvalid file name: '+item)
			if not sizevalid:
				if 'Image ImageWidth' in tags.keys() and 'Image ImageLength' in tags.keys():
					print('\tInvalid size: '+str(tags['Image ImageWidth'])+' x '+str(tags['Image ImageLength']))
				else:
					print('\tMissing image size tags')
			if not resolutionvalid:
				if 'Image XResolution' in tags.keys() and 'Image YResolution' in tags.keys():
					print('\tInvalid resolution: '+str(resolutionX)+' x '+str(resolutionY)+', unit: '+resolutionUnits[resolutionUnit])
				else:
					print('\tMissing resolution tags')
			if samples != 3 and colour == 'C':
				print('\tInvalid channel count: '+str(samples))
			elif samples != 1 and colour == 'R':
				print('\tInvalid channel count: '+str(samples))
			if not depthvalid:
				print('\tInvalid bit depth: '+str(bits))
			if not titlevalid:
				if 'Image ImageDescription' in tags.keys():
					print('\tInvalid title: '+str(tags['Image ImageDescription']))
				else:
					print('\tMissing title')
			if not creatorvalid:
				if 'Image Artist' in tags.keys():
					print('\tInvalid title: '+str(tags['Image Artist']))
				else:
					print('\tMissing creator')
			if not copyrightvalid:
				if 'Image Copyright' in tags.keys():
					print('\tInvalid title: '+str(tags['Image Copyright']))
				else:
					print('\tMissing copyright')


# f = open('/Users/jakub/Documents/archive/Jakub\'s artwork/Untitled (Propeller show)/15093_01_DOLEJS.tif', 'rb')
# tags = exifread.process_file(f)

# for tag in tags.keys():
# 	# print(tag, tags[tag]);
# 	if (tag == 'Image ImageWidth' or tag == 'Image ImageLength') and int(str(tags[tag])) < size:
# 		print('Wrong size')
# 	if (tag == 'Image XResolution' or tag == 'Image YResolution') and int(str(tags[tag])) != resolution:
# 		print('Wrong resolution')