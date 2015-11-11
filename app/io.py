import os.path

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

		Writer.write(outputname, text)			

		return outputname

	def write(outputname, text):
		f = open(outputname, 'w')
		f.write(text)
		f.close()
