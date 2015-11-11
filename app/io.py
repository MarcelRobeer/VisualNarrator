import os.path
import csv

class Reader:
	def parse(open_file):
		with open_file:
			lines = []
			for line in open_file:
				if not line.isspace():  # Don't parse empty lines...
					lines.append(line)
			return lines

class Writer:
	def make_file(dirname, filename, filetype, text):
		if not os.path.exists(dirname):
	    		os.makedirs(dirname)
	
		outputname = ""
		filetype = "." + str(filetype)
		potential_outp = dirname + "/" + filename
		
		i = 0		
		while outputname == "":
			if not os.path.exists(potential_outp + str(i) + filetype):
				outputname = potential_outp + str(i) + filetype
			i += 1

		if filetype == ".csv":			
			Writer.writecsv(outputname, text)
		else:
			Writer.write(outputname, text)			

		return outputname

	def write(outputname, text):
		with open(outputname, 'w') as f:
			f.write(text)
			f.close()

	def writecsv(outputname, list):
		with open(outputname, 'wt') as f:
			writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
			writer.writerows(list)
