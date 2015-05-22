#!/usr/bin/env python

import netcdf_helpers
from scipy import *
from optparse import OptionParser
import sys, time
import os
from xml.dom.minidom import parse

from os import walk

def unnecessaryfunc(d, function):		#Seapration of files for the train/test/val so on
	if function == "train":
		return 0,90
	elif function == "test":
		return 90,110

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
path = "/home/riot/Videos/Devanagari/hpl-dvng-iso-word-online-1.0/Data/"


topdir = []
for (dirpath, dirnames, filenames) in walk(path):
	topdir.extend(dirnames)
	break
print "topdir = \n", topdir

#later
# inputMeans = array([1054.11664783, 1455.79299719, 0.0196859027344])
# inputStds = array([413.688579765, 643.506710495, 0.138918565959])

labels =  ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '109', '110']

seqDims = []
seqLengths = []
targetStrings = []
wordTargetStrings = []
seqTags = []
inputs = []

#Now for inside each folder

#For now I have two sets. The first-> function = train and second function  = test. Later we can add more for val and so on
start,end = unnecessaryfunc(topdir,function)

skip_strokes_more_nums = 0

for iter1, k in enumerate(topdir[start:end]):
	print "Directory == ", iter1, k
	pathname = path.rstrip("/") + "/" + k + "/"
	
	# using t for the new directory
	f = []
	for (dirpath, dirnames,filenames) in walk(pathname):	
		f.extend(filenames)
		break#only one iteraion cause all lines are same
	print f
	for onefile in f:				#Running for each data file
		try:
			if ".txt" in onefile: continue
			
			firstlinechk = 0 			# To make sure that the lines of code before the data lines are avoided when necessary
			segmentline = []			#Will store the lines that store with ground truth (They start with the text .SEGMENT)
			strokeline = []				#Will store the strokes in the data
			oldlen = len(inputs)
			thirdval = 0.0

			k = open(pathname + onefile).readlines()
			for line in k:
				line = line.strip()
				parts = line.split()
				if len(parts) == 0: continue
				if parts[0] == ".SEGMENT":
					if parts[3] == "?":
						continue
					segmentline.append(line)

				if firstlinechk == 0 and line != ".PEN_DOWN":		#Skip these lines as they donot have needed info
					continue
				elif line == ".PEN_DOWN":
					firstlinechk = 1 			#Nolonger the firstlines part, now all the information is relevant
					start = []					#Will store the individual points of this stroke
					thirdval = 1.0 				#Stores the value for the third column of the first point in the stroke to signify "PENDOWN"
				elif line == ".PEN_UP":
					strokeline.append(start)	#The stroke is complete so append to the list of strokes
					continue
				else:
					coor = line.split();
					start.append([float(coor[0]), float(coor[1]), thirdval])	#append the point to the others of this stroke
					thirdval = 0.0

			#Now manipulate the segment line
			final = []							#Final will store the strokes to symbol mappings
			for index, line in enumerate(segmentline):
				parts = line.strip().split()
				if index == 0:									#The first line has the word mappings and the others symbol mappings
					word = parts[4].lstrip("\"").strip("\"")	#Extract the word number from the first of the segment lines
					continue

				numbers = parts[4].strip("\"").strip("-").split("_")		#The symbol numbers in a line
				

				strokes = parts[2].split(",")					#The stroke numbers in a line
				
				if len(numbers) > len(strokes):						#For now, Can't work with them
					skip_strokes_more_nums += 1
					print "Raising exceptionn nums and strokes == ", numbers, strokes
					raise StopIteration


				if len(numbers) > 1:							#If more than one symbol in a line
					for i in range(len(numbers) - 1):			#I map the last of the symbols to the last of the strokes.
						final.append([ strokes[-1], numbers[-1] ])	
						strokes.pop()							#Then I pop the corresponding stroke and symbol and use the rest of the strokes for the lead symbol
						numbers.pop()
				#By now the numbers should have just one item.
				#Now the strokes left have to be concatenated for the symbol left in numbers
				strokes.append(numbers[0])						#The final state of each append to final has 
				final.append( strokes )							#atleast one stroke and the symbol for the number of strokes at the end
				final.sort(key=lambda x: x[0])					#We arrange according order of strokes. This is a real problematic part

			wordtargetstr = ""							#Initially the sequence of characters to be fed
			for symbol in final:
				wordtargetstr += symbol[-1] + " "		#For each symbol entry in final the last entry in symbol is the symbol no.
				

				if len(symbol) != 2:
					for term in symbol[1:-1]:			#The earlier entries are strokes for that symbol and need to be stuck together and pass ahead
						strokeline[ int(term) ][0][2] = 0.0
						strokeline[ int(symbol[0]) ].extend(strokeline[ int(term) ])
				inputs.extend( strokeline[ int(symbol[0]) ] )	

			print onefile
			if wordtargetstr == '':
				raise StopIteration
			
			seqTags.append(onefile)		#appending to seqtags
			
			wordtargetstr = wordtargetstr.rstrip()

			wordTargetStrings.append(wordtargetstr)	#I have to append the wordtargetatr as I don't have a mapping for the word for the text, even tho I knwo the exact number it is
			targetStrings.append(wordtargetstr)
			
			seqLengths.append(len(inputs) - oldlen)
			seqDims.append([seqLengths[-1]])
			print "Sequence lengths ", [seqLengths[-1]], "\n"
		except StopIteration:
			continue
		##here the Loop for the respective folder shud stop

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
input_put = open("input_out.txt","w")
print >> input_put, wordTargetStrings
netcdf_helpers.createNcVar(file,'inputs',inputs,'f',('numTimesteps','inputPattSize'),'input patterns')

#write the data to disk
print "closing file", ncFilename
file.close()
