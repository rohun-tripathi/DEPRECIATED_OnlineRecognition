#!/usr/bin/env python

import netcdf_helpers
from scipy import *
from optparse import OptionParser
import sys, time
import os
from xml.dom.minidom import parse

from os import walk

def unnecessaryfunc(d, function):
	if function == "train":
		return 1, len(d)
	elif function == "test":
		return 0,1

#command line options
parser = OptionParser()

#parse command line options
(options, args) = parser.parse_args()
if (len(args)<1):
	print "usage: test/train/val/edited"
	sys.exit(2)

function = args [0]
if not function in ["test",  "train", "val", "edited"]:
	print "usage: test/train/val/edited"
	sys.exit(2)


ncFilename = "combine" + function + ".nc"
path = "/home/riot/Videos/Tamil_Online/TamData/"

topdir = []
for (dirpath, dirnames, filenames) in walk(path):
	topdir.extend(dirnames)
	break
print "topdir = \n", topdir

#later
# inputMeans = array([1054.11664783, 1455.79299719, 0.0196859027344])
# inputStds = array([413.688579765, 643.506710495, 0.138918565959])

labels =  ['133', '137', '136', '135', '134', '139', '138', '24', '25', '26', '27', '20', '21', '22', '23', '28', '29', '4', '8', '120', '121', '122', '59', '51', '50', '53', '52', '88', '89', '111', '110', '113', '112', '82', '119', '118', '84', '3', '7', '108', '109', '102', '100', '106', '107', '104', '105', '38', '33', '32', '30', '36', '61', '63', '65', '66', '67', '68', '69', '2', '6', '99', '98', '91', '90', '93', '92', '95', '94', '97', '96', '11', '10', '13', '12', '15', '17', '16', '19', '18', '117', '151', '150', '152', '41', '48', '49', '46', '86', '44', '45', '42', '43', '40', '87', '1', '5', '9', '146', '147', '144', '145', '142', '143', '140', '141', '148', '149', '74', '72', '71', '70', '47']

seqDims = []
seqLengths = []
targetStrings = []
wordTargetStrings = []
seqTags = []
inputs = []



#Retrieving the ground truth from the text format of it
truths = []
for i in open("grnd_trth.txt").readlines():
	truths.append(i)
	

#Now for inside each folder

#For now I have two sets. The first-> function = train and second function  = test. Later we can add more for val and so on
for folder in topdir:
	pathtemp = path + str(folder) + "/"
	d = []
	for (dirpath, dirnames, filenames) in walk(pathtemp):
		d.extend(dirnames)
		break
	start,end = unnecessaryfunc(d,function)

	for k in d[start:end]:
		t = pathtemp + k + "/"
		
		# print t
		# using t for the new directory
		f = []
		for (dirpath, dirnames,filenames) in walk(t):	
			f.extend(filenames)
			break#only one iteraion cause all lines are same in the ascii
		
		for onefile in f:
			seqTags.append(onefile)#appending to seqtags
			print onefile

			names = onefile.split("t")
			
			# Same for now
			word = truths[ int(names[0]) -1 ].strip()
			wordmod = truths[ int(names[0]) -1 ].strip()


			#they are appended here as they have to be done for each stroke file
			wordTargetStrings.append(word)
			targetStrings.append(wordmod)
			
			firstlinechk = 0;
			#to make the first points have output 1.0 instead of 0.0
			oldlen = len(inputs)
			thirdval = 0.0
			for line in file(t + onefile).readlines():
				line= line.strip()
				if firstlinechk == 0 and line != ".PEN_DOWN":
					continue
				elif line == ".PEN_DOWN":
					firstlinechk = 1
					thirdval = 1.0
				elif line == ".PEN_UP":
					continue
				else:
					coor = line.split();

					inputs.append([float(coor[0]), float(coor[1]), thirdval])
					thirdval = 0.0
				
			# print "Input = " , inputs, "\n\n\n\n"
			
			seqLengths.append(len(inputs) - oldlen)
			seqDims.append([seqLengths[-1]])
			print "Sequence lengths ", [seqLengths[-1]], "\n"
			##and this is the point it shud stop inside the folder

			##here the loop for the respective folder shud stop

#Later
#inputs = ((array(inputs)-inputMeans)/inputStds).tolist()

#print inputs
# print len(labels), labels
# print labels

#create a new .nc file
file = netcdf_helpers.NetCDFFile(ncFilename, 'w')

#create the dimensions
netcdf_helpers.createNcDim(file,'numSeqs',len(seqLengths))
netcdf_helpers.createNcDim(file,'numTimesteps',len(inputs))
netcdf_helpers.createNcDim(file,'inputPattSize',len(inputs[0]))
netcdf_helpers.createNcDim(file,'numDims',1)
netcdf_helpers.createNcDim(file,'numLabels',len(labels))

#create the variables
netcdf_helpers.createNcStrings(file,'seqTags',seqTags,('numSeqs','maxSeqTagLength'),'sequence tags')
netcdf_helpers.createNcStrings(file,'labels',labels,('numLabels','maxLabelLength'),'labels')
netcdf_helpers.createNcStrings(file,'targetStrings',targetStrings,('numSeqs','maxTargStringLength'),'target strings')
netcdf_helpers.createNcStrings(file,'wordTargetStrings',wordTargetStrings,('numSeqs','maxWordTargStringLength'),'word target strings')
netcdf_helpers.createNcVar(file,'seqLengths',seqLengths,'i',('numSeqs',),'sequence lengths')
netcdf_helpers.createNcVar(file,'seqDims',seqDims,'i',('numSeqs','numDims'),'sequence dimensions')
print inputs
netcdf_helpers.createNcVar(file,'inputs',inputs,'f',('numTimesteps','inputPattSize'),'input patterns')

#write the data to disk
print "closing file", ncFilename
file.close()
