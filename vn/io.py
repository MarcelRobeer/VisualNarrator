import os.path
import csv
import pandas
import datetime as d

from vn.utils.utility import get_tokens, get_case

class Reader:
	@staticmethod
	def parse(fname):
		"""Parses a previously open file

		:param fname: File name
		:returns: List of non-empty lines
		"""
		with open(fname, 'r') as open_file:
			lines = []
			for line in open_file:
				if not line.isspace():
					lines.append(line.rstrip('\n\r'))
			return lines

class Writer:
	@staticmethod
	def make_file(dirname, filename, filetype, content):
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

		f_unique = str(d.datetime.now().date()) + "_" + str(d.datetime.now().time()).replace(':', '.')
		outputname = potential_outp + f_unique + filetype


		if filetype == ".csv":			
			Writer.writecsv(outputname, content)
		else:
			Writer.write(outputname, content)			

		return outputname

	@staticmethod
	def write(outputname, text):
		"""Writes text to a file

		:param outputname: Name and location of the output file
		:param text: Text to write to the file
		"""
		with open(outputname, 'w') as f:
			f.write(text)
			f.close()

	@staticmethod
	def writecsv(outputname, li):
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

class Printer:
	@staticmethod
	def print_head(text):
		print("\n\n////////////////////////////////////////////////")
		print("/////", '{:^36}'.format(text) ,"/////")
		print("////////////////////////////////////////////////")

	@staticmethod
	def print_subhead(text):
		print("<----------", '{:^9}'.format(text) ,"---------->")

	@staticmethod
	def print_us_data(story):
		phrasetext = ""
		if story.means.main_verb.phrase:
			phrasetext = "( w/ Type " + story.means.main_verb.type + " phrase " + str(get_tokens(story.means.main_verb.phrase)) + " )"

		print("\n\n")
		Printer.print_subhead("BEGIN U S")
		print("User Story", story.number, ":", story.text)
		print(" >> INDICATORS\n  Role:", story.role.indicator, "\n    Means:", story.means.indicator, "\n    Ends:", story.ends.indicator)
		print(" >> ROLE\n  Functional role:", story.role.functional_role.main, "( w/ compound", get_tokens(story.role.functional_role.compound), ")")
		print(" >> MEANS\n  Main verb:", story.means.main_verb.main, phrasetext, "\n  Main object:", story.means.main_object.main, "( w/ noun phrase", get_tokens(story.means.main_object.phrase), "w/ compound", get_tokens(story.means.main_object.compound), ")")
		Printer.print_free_form(story, "means")
		Printer.print_free_form(story, "ends")

		Printer.print_subhead("END U S")

	@staticmethod
	def print_free_form(story, part):
		p = 'story.' + part + '.'
		if eval(p + 'free_form'):
			print("  Free form:", get_tokens(eval(p + 'free_form')))
			if eval(p + 'verbs'):
				print("    Verbs:", get_tokens(eval(p + 'verbs')))
				if eval(p + 'phrasal_verbs'):
					print("      Phrasal:", eval(p + 'phrasal_verbs'))
			if eval(p + 'noun_phrases'):
				print("    Noun phrases:", eval(p + 'noun_phrases'))
			if eval(p + 'compounds'):
				print("    Compound nouns:", eval(p + 'compounds'))
			if eval(p + 'nouns'):
				pnounstext = ""
				if eval(p + 'proper_nouns'):
					pnounstext = " ( Proper: " + str(get_tokens(eval(p + 'proper_nouns'))) + ")"
				print("    Nouns:", get_tokens(eval(p + 'nouns')), pnounstext)

	@staticmethod
	def print_details(fail, success, nlp_time, parse_time, matr_time, gen_time, stats_time):
		total = success + fail
		if success is not 0:
			frate = fail/(success + fail)
		else:
			frate = 1

		Printer.print_head("RUN DETAILS")
		print("User Stories:\n  # Total parsed:\t\t ", total,"\n    [+] Success:\t\t ", success, "\n    [-] Failed:\t\t\t ", fail, "\n  Failure rate:\t\t\t ", frate, "(", round(frate * 100, 2), "% )")
		print("Time elapsed:")
		print("  NLP instantiate:\t\t ", round(nlp_time, 5), "s")
		print("  Mining User Stories:\t\t ", round(parse_time, 5), "s")
		print("  Creating factor matrix:\t ", round(matr_time, 5), "s")
		print("  Generating Manchester Ontology:", round(gen_time, 5), "s")
		if stats_time > 0:
			print("  Generating statistics:\t ", round(stats_time, 5), "s")
		print("")

	@staticmethod
	def print_dependencies(story):
		print("---------- U S", story.number, "----------")
		for token in story.data:
			print(token.i, "-> ", token.text, " [", token.pos_, " (", token.tag_ ,")", "dep:", token.dep_, " at ", token.idx, "]")
			if token.is_stop:
				print("! PART OF STOP LIST")
			print("Left edge: ", token.left_edge)
			print("Right edge: ", token.right_edge)
			print("Children: ", get_tokens(token.children))
			print("Subtree: ", get_tokens(token.subtree))
			print("Head: ", token.head)
			if token is not story.data[0]:
				print("Left neighbor: ", token.nbor(-1))
			if token is not story.data[-1]:
				print("Right neighbor: ", token.nbor(1))
			print("Entity type: ", token.ent_type, "\n")

	@staticmethod
	def print_noun_phrases(story):
		print("NOUN PHRASES > US " + str(story.number) + ": " + str(story.text))
		for chunk in story.data.noun_chunks:
			print(chunk.root.head.text, " <-- ", chunk.text)
		print("")

	@staticmethod
	def print_stats(stats, detail):
		if detail:
			print("\n")
			Printer.print_subhead("DETAILS")
			for r in stats:
				outline = ""
				for s in r:
					outline += str(s) + "; "
				print(outline)

		print("\n")		
		Printer.print_subhead("SUMMARY")

	@staticmethod
	def print_gen_settings(matrix, base, threshold):
		Printer.print_head("ONTOLOGY GENERATOR SETTINGS")
		print("Threshold:\t\t\t", threshold)
		print("Absolute Weights ( base =", base ,"):")
		print("  Functional role:\t\t", matrix.VAL_FUNC_ROLE)
		print("  Main object:\t\t", matrix.VAL_MAIN_OBJ)
		print("  Noun in free form means:\t", matrix.VAL_MEANS_NOUN)
		print("  Noun in free form ends:\t", matrix.VAL_ENDS_NOUN)
		print("Relative Weights:")
		print("  Compound (compared to parent):", matrix.VAL_COMPOUND)

	@staticmethod
	def print_rel(rel):
		print(get_case(rel[1]), "--", rel[2], "->", get_case(rel[3]))