import os.path
import csv
import pandas

class Reader:
	def parse(open_file):
		with open_file:
			lines = []
			for line in open_file:
				if not line.isspace():  # Don't parse empty lines...
					lines.append(line)
			return lines

class Writer:
	def __init__(self):
		self.number = 1

	def make_file(self, dirname, filename, filetype, text):
		if not os.path.exists(dirname):
	    		os.makedirs(dirname)
	
		outputname = ""
		filetype = "." + str(filetype)
		potential_outp = dirname + "/" + filename

		if self.number == 1:			
			while os.path.exists(potential_outp + str(self.number) + filetype):
					self.number += 1
		outputname = potential_outp + str(self.number) + filetype


		if filetype == ".csv":			
			self.writecsv(outputname, text)
		else:
			self.write(outputname, text)			

		return outputname

	def write(self, outputname, text):
		with open(outputname, 'w') as f:
			f.write(text)
			f.close()

	def writecsv(self, outputname, li):
		with open(outputname, 'wt') as f:
			if isinstance(li, pandas.core.frame.DataFrame):
				li.to_csv(path_or_buf=f, sep=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
			else:
				writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
				writer.writerows(li)
