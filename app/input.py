class Reader:
	def parse(open_file):
		with open_file:
			lines = []
			for line in open_file:
				if not line.isspace():  # Don't parse empty lines...
					lines.append(line)
			return lines
