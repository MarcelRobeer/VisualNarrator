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
	def make_file(filename, text):
		if not os.path.exists("ontologies"):
	    		os.makedirs("ontologies")
	
		outputname = "ontologies/" + filename + ".omn"
		f = open(outputname, 'w')
		f.write(text)
		f.close()
		return outputname
