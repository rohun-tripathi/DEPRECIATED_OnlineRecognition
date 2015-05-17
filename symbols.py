#This code produces the output in the set acquired which is all the
#symbols that have been tagged in the ground truth file

import xlrd

def checksymbol():
	#Standard
	workbook = xlrd.open_workbook('ground_truth.xls')
	worksheet = workbook.sheet_by_name('Sheet1')
	num_rows = worksheet.nrows - 1
	curr_row = -1

	#Mycode
	acquired = set()
	default = set()
	for i in range(153):
		default.add(i)


	while curr_row < num_rows:
		curr_row += 1
		row = worksheet.row(curr_row)
		if curr_row < 2:
			continue	
		#code for checking the number entries in the ground truth
		for index,k  in enumerate(row):
			if index > 1:
				k = str(k)

				term = k.split("number:")
				print term
				val = int(float(term[1]))
				print val
				acquired.add(str(val))

	print "The set of symbols in the ground truth: ", acquired

	print "Is the acquire set having atleast one instance of all the symbols: ", acquired == default

def converttotext():
	#Standard
	workbook = xlrd.open_workbook('ground_truth.xls')
	worksheet = workbook.sheet_by_name('Sheet1')
	num_rows = worksheet.nrows - 1
	curr_row = -1
	
	grnd_trth = open("grnd_trth.txt","w")


	while curr_row < num_rows:
		curr_row += 1
		row = worksheet.row(curr_row)
		if curr_row < 2:
			continue	
		#code for tranfering each line to the txt
		word = ''
		for k in row[2:]:
			k = str(k)
			term = k.split("number:")
			
			val = int(float(term[1]))
			if val > 0:
				word += str(val) + " "
		print >> grnd_trth, word

#checksymbol()
converttotext()