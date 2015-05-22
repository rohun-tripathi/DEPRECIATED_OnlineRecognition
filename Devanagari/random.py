from os import walk

path = "usr106/"
holder = []
for (dirpath, dirnames, files) in walk(path):
	holder.extend(files)

out = open("output.txt","w")

out2 = open("output2.txt","w")

#print holder
for file1 in holder:
		firstlinechk = 0
		k = open(path + "059t01.new").readlines()
		segmentline = []
		strokeline = []
		for line in k:
			if line == "\n": continue
			line = line.strip()
			parts = line.split()
			if parts[0] == ".SEGMENT":
				segmentline.append(line)

			if firstlinechk == 0 and line != ".PEN_DOWN":
				continue
			elif line == ".PEN_DOWN":
				firstlinechk = 1
				start = []
				thirdval = 1.0
			elif line == ".PEN_UP":
				strokeline.append(start)
				continue
			else:
				coor = line.split();
				start.append([float(coor[0]), float(coor[1]), thirdval])
				thirdval = 0.0

		
		#Now manipulate the segment line
		final = []
		tally = []
		print segmentline
		for index, line in enumerate(segmentline):
			parts = line.strip().split()
			if index == 0:
				word = parts[4].lstrip("\"").strip("\"")
				continue

			numbers = parts[4].strip("\"").split("_")
			strokes = parts[2].split(",")
			
			if len(numbers) > 1:							#If more than one symbol in a line
				for i in range(len(numbers) - 1):			#I map the last of the symbols to the last of the strokes.
					if len(strokes) == 1:
						break
					final.append([ strokes[-1], numbers[-1] ])
					tally.append([ strokes[-1], 2 ])
					strokes.pop()							#Then I pop the corresponding stroke and symbol and use the rest of the strokes for the lead symbol
					numbers.pop()
			#By now the numbers should have just one item.
			#Now the strokes left have to be concatenated for the symbol left in numbers
			tally.append( [strokes[0], len(strokes)] )
			strokes.extend(numbers)							#The final state of each append to final has 
			final.append( strokes )							#atleast one stroke and the symbols for the number of strokes at the end
			final.sort(key=lambda x: x[0])					#We arrange according order of strokes. This is a real problematic part
			tally.sort(key=lambda x: x[0])
		
		print >>out2, "Final == ", final
		print >>out2, "Tally == ", tally
		print >>out2, strokeline
		wordtargetstr = ""							#Initially the sequence of characters to be fed
		for symbol,tal in zip(final, tally):
			for term in symbol[ tal[1]:]
				wordtargetstr += term + " "		#For each symbol entry in final the last entry in symbol is the symbol no.
			if len(symbol) == 2:
				inputs.append( strokeline[ int(symbol[0]) ] )	
			elif tal[1] == 1:
				inputs.append( strokeline[ int(symbol[0]) ] )
			if len(symbol) != 2:
				for term in symbol[1:-1]:			#The earlier entries are strokes for that symbol and need to be stuck together and pass ahead
					strokeline[ int(term) ][0][2] = 0.0
					strokeline[ int(symbol[0]) ].extend(strokeline[ int(term) ])
		print >> out, strokeline
		break