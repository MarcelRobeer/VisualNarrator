import re
import string

class Utility:
	def split_list(a_list, nr): # Potentially obsolete
		return a_list[:nr], a_list[nr:]

	def is_sublist(list_a, list_b):
		if list_a == []: return True
		if list_b == []: return False
		return set(list_a).issubset(set(list_b))

	def remove_punct(str):
		return re.sub(r"[,!?\.]", '', str).strip()

	def text(a_list):
		return " ".join(str(x) for x in a_list)

	def t(li):
		if type(li) is list:
			return Utility.text(NLPUtility.get_tokens(li))
		return li.text

	def remove_duplicates(self, arr): # Potentially obsolete
		li = list()
		li_add = li.append
		return [ x for x in arr if not (x in li or li_add(x))]

	def multiline(string):
		return [l.split(" ") for l in string.splitlines()]

	def tab(string):
		if string.startswith("\t"):
			return True
		return False
	
	def is_comment(line):
		if line[0] == "#":
			return True
		return False	


class NLPUtility:
	def case(token):
		if 'd' in token.shape_ or 'x' not in token.shape_ or token.shape_[:2] == 'xX':			
			return token.text
		return string.capwords(token.lemma_)

	def get_case(concept):
		c = ""
		if type(concept) is list:
			c = ' '.join([cc.case for cc in concept])
		elif type(concept) is str:
			return concept
		else:			
			c = concept.case
		return c

	def get_tokens(tree):
		return [t.text for t in tree]

	def get_lower_tokens(tree):
		return [str.lower(t.text) for t in tree]

	def get_idx(tree):
		return [t.i for t in tree]

	def text_lower_tokens(a_list):
		return Utility.text(NLPUtility.get_lower_tokens(a_list))	


class Printer:
	def print_head(text):
		print("\n\n////////////////////////////////////////////////")
		print("/////", '{:^36}'.format(text) ,"/////")
		print("////////////////////////////////////////////////")

	def print_subhead(text):
		print("<----------", '{:^9}'.format(text) ,"---------->")

	def print_us_data(story):
		phrasetext = ""
		pnounstext = ""
		if story.means.main_verb.phrase:
			phrasetext = "( w/ Type " + story.means.main_verb.type + " phrase " + str(NLPUtility.get_tokens(story.means.main_verb.phrase)) + " )"

		print("\n\n")
		Printer.print_subhead("BEGIN U S")
		print("User Story", story.number, ":", story.text)
		print(" >> INDICATORS\n  All:", NLPUtility.get_tokens(story.indicators), "\n    Role:", NLPUtility.get_tokens(story.role.indicator), "\n    Means:", NLPUtility.get_tokens(story.means.indicator), "\n    Ends:", NLPUtility.get_tokens(story.ends.indicator))
		print(" >> ROLE\n  Functional role:", story.role.functional_role.main, "( w/ compound", NLPUtility.get_tokens(story.role.functional_role.compound), ")")
		print(" >> MEANS\n  Main verb:", story.means.main_verb.main, phrasetext, "\n  Direct object:", story.means.direct_object.main, "( w/ noun phrase", NLPUtility.get_tokens(story.means.direct_object.phrase), "w/ compound", NLPUtility.get_tokens(story.means.direct_object.compound), ")")
		Printer.print_free_form(story, "means")
		Printer.print_free_form(story, "ends")

		Printer.print_subhead("END U S")

	def print_free_form(story, part):
		p = 'story.' + part + '.'
		if eval(p + 'free_form'):
			print("  Free form:", NLPUtility.get_tokens(eval(p + 'free_form')))
			if eval(p + 'verbs'):
				print("    Verbs:", NLPUtility.get_tokens(eval(p + 'verbs')))
				if eval(p + 'phrasal_verbs'):
					print("      Phrasal:", eval(p + 'phrasal_verbs'))
			if eval(p + 'noun_phrases'):
				print("    Noun phrases:", eval(p + 'noun_phrases'))
			if eval(p + 'compounds'):
				print("    Compound nouns:", eval(p + 'compounds'))
			if eval(p + 'nouns'):
				pnounstext = ""
				if eval(p + 'proper_nouns'):
					pnounstext = " ( Proper: " + str(NLPUtility.get_tokens(eval(p + 'proper_nouns'))) + ")"
				print("    Nouns:", NLPUtility.get_tokens(eval(p + 'nouns')), pnounstext)

	def print_details(fail, success, nlp_time, parse_time, matr_time, gen_time, stats_time):
		total = success + fail
		if success is not 0:
			frate = fail/success
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

	def print_dependencies(story):
		print("---------- U S", story.number, "----------")
		for token in story.data:
			print(token.i, "-> ", token.text, " [", token.pos_, " (", token.tag_ ,")", "dep:", token.dep_, " at ", token.idx, "]")
			if token.is_stop:
				print("! PART OF STOP LIST")
			print("Left edge: ", token.left_edge)
			print("Right edge: ", token.right_edge)
			print("Children: ", NLPUtility.get_tokens(token.children))
			print("Subtree: ", NLPUtility.get_tokens(token.subtree))
			print("Head: ", token.head)
			if token is not story.data[0]:
				print("Left neighbor: ", token.nbor(-1))
			if token is not story.data[-1]:
				print("Right neighbor: ", token.nbor(1))
			print("Entity type: ", token.ent_type, "\n")

	def print_noun_phrases(story):
		print("NOUN PHRASES > US " + str(story.number) + ": " + str(story.text))
		for chunk in story.data.noun_chunks:
			print(chunk.root.head.text, " <-- ", chunk.text)
		print("")

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

	def print_gen_settings(matrix, base, threshold):
		Printer.print_head("ONTOLOGY GENERATOR SETTINGS")
		print("Threshold:\t\t\t", threshold)
		print("Absolute Weights ( base =", base ,"):")
		print("  Functional role:\t\t", matrix.VAL_FUNC_ROLE)
		print("  Direct object:\t\t", matrix.VAL_DIRECT_OBJ)
		print("  Noun in free form means:\t", matrix.VAL_MEANS_NOUN)
		print("  Noun in free form ends:\t", matrix.VAL_ENDS_NOUN)
		print("Relative Weights:")
		print("  Compound (compared to parent):", matrix.VAL_COMPOUND)

	def print_rel(rel):
		print(NLPUtility.get_case(rel[1]), "--", rel[2], "->", NLPUtility.get_case(rel[3]))
