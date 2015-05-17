#!/usr/bin/env python

#this file was a stepping stone to the creation of the combine.py for the bengally text
#It requires two diff testing files, test1 has the strokes and test2 has the ascii mapping

import netcdf_helpers
from scipy import *
from optparse import OptionParser
import sys
import os
from xml.dom.minidom import parse

#what are these?
inputMeans = array([1115.96, 389.53, 0.015396])
inputStds = array([444.9145, 18.0568, 0.1231])

labels =  ['AU', 'AK', 'MA', 'JA', 'KA', 'LA']


#command line options
parser = OptionParser()

#parse command line options
(options, args) = parser.parse_args()
#if (len(args)<2):
#	print "usage: -options input_filename output_filename"
#	print options
#	sys.exit(2)

#inputFilename = args [0]
inputFilename = "test1"
#ncFilename = args[1]
ncFilename = "output.nc"

##rohun addition
inputFilename2 = "test2"
#if test2 == "ascii.txt":

print options
print "input filename", inputFilename
print "data filename", ncFilename

seqDims = []
seqLengths = []
targetStrings = []
wordTargetStrings = []
seqTags = []
inputs = []

print "reading data file test1"

#reading the ascii first(easier) TEST2
#here the loop shud begin for each folder
for l in file(inputFilename2).readlines():
	firstline = l.strip()
	terms = firstline.split()
	lenterms  = len(terms)
	word = ""
	wordspace = ""
	for x in range(1, lenterms):#skipping the first term as that is useless
		word += terms[x]
		wordspace += terms[x] + ' '
	wordmod = wordspace.strip()
	print wordspace
	print word
	wordTargetStrings.append(word)
	targetStrings.append(wordspace)

	##this the point the loop shud begin inside each folder
	firstlinechk = 0;
	oldlen = len(inputs)
	seqTags.append(inputFilename)
	for line in file(inputFilename).readlines():
		coor = line.split();
		##do the thing withe seq tags
		if(coor[2] == "0"):
			if firstlinechk == 1:
				inputs[-1][-1] = 1
			inputs.append([float(coor[0]), float(coor[1]), 0.0])
		else:
			firstlinechk = 1
			inputs.append([float(coor[0]), float(coor[1]), 0.0])
	inputs[-1][-1] = 1
	print inputs
	seqLengths.append(len(inputs) - oldlen)
	seqDims.append([seqLengths[-1]])
	print [seqLengths[-1]]
	####################################SKIPPING THE MEAN AND DEVIATION STEP###################################

	##and this is the point it shud stop inside the folder

	break#only one iteraion cause all lines are same in the ascii
	#here the loop for the respective folder shud stop

#sys.exit()#change this

#inputs = ((array(inputs)-inputMeans)/inputStds).tolist()
print len(labels), labels
print labels

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
netcdf_helpers.createNcVar(file,'inputs',inputs,'f',('numTimesteps','inputPattSize'),'input patterns')

#write the data to disk
print "closing file", ncFilename
file.close()
