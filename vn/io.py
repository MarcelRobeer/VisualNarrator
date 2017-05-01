import os.path
import csv
import pandas

class Reader:
	def parse(open_file):
		"""Parses a previously open file

		:param open_file: An open file
		:returns: List of non-empty lines
		"""
		with open_file:
			lines = []
			for line in open_file:
				if not line.isspace():
					lines.append(line)
			return lines

class Writer:
	def __init__(self):
		self.number = 1

	def make_file(self, dirname, filename, filetype, content):
		"""Makes a file and writes to it

		:param dirname: Name of the target directory
		:param filename: File name (without extension)
		:param filetype: Type of file
		:param content: Content to write to file
		:returns: Name and location of the file
		"""
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
			self.writecsv(outputname, content)
		else:
			self.write(outputname, content)			

		return outputname

	def write(self, outputname, text):
		"""Writes text to a file

		:param outputname: Name and location of the output file
		:param text: Text to write to the file
		"""
		with open(outputname, 'w') as f:
			f.write(text)
			f.close()

	def writecsv(self, outputname, li):
		"""Writes a list/array/Pandas DataFrame to a CSV file

		:param outputname: Name and location of the output file
		:param li: List/array/DataFrame
		"""
		with open(outputname, 'wt') as f:
			if isinstance(li, pandas.core.frame.DataFrame):
				li.to_csv(path_or_buf=f, sep=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
			else:
				writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
				writer.writerows(li)
