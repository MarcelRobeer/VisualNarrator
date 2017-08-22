import re
import string
from spacy.tokens.token import Token

### General
def flatten(l):
	return [item for sublist in l for item in sublist]

def is_sublist(subli, li):
	""" Sees if X is a sublist of Y

	:param subli: Sublist
	:param li: List in which the sublist should occur
	:returns: Boolean
	"""
	if subli == []: return True
	if li == []: return False
	return set(subli).issubset(set(li))

def is_exact_sublist(subli, li):
	""" Sees if X is a sublist of Y and takes the exact order into account

	:param subli: Sublist
	:param li: List in which the sublist should occur
	:returns: Index of first occurence of sublist in list
	"""
	for i in range(len(li)-len(subli)):
		if li[i:i+len(subli)] == subli:
			return i
	else:
		return -1

def remove_punct(str):
	return re.sub(r"[,!?\.]", '', str).strip()

def text(a_list):
	return " ".join(str(x) for x in a_list)

def t(li):
	if type(li) is list:
		return text(get_tokens(li))
	return li.text

def is_i(li):
	if str.lower(t(li)) == 'i':
		return True
	return False

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

def occurence_list(li):
	res = []
	for o in li:
		if str(o) not in res and o >= 0:
			res.append(str(o))
	if res:
		return ', '.join(res)
	return "Does not occur, deducted"

def is_us(cl):
	if cl.name.startswith("US") or cl.name == 'UserStory':
		return True
	elif cl.parent.startswith("US"):
		return True
	return False

### NLP
def get_case(t):
	if type(t) is Token:
		if 'd' in t.shape_ or 'x' not in t.shape_ or t.shape_[:2] == 'xX':			
			return t.text
		elif t.text[-1] == 's' and 'x' not in t.shape_[:-1]:
			return t.text[:-1]
		return string.capwords(t.lemma_)
	elif type(t) is WeightedToken:
		return t.case
	elif type(t) is list and len(t) > 0 and type(t[0]) is WeightedToken:
		return ' '.join([get_case(cc) for cc in t])
	return t

def get_tokens(tree):
	return [t.text for t in tree]

def get_lower_tokens(tree):
	return [str.lower(t.text) for t in tree]

def get_idx(tree):
	return [t.i for t in tree]

def text_lower_tokens(a_list):
	return text(get_lower_tokens(a_list))

def is_noun(token):
	if token.pos_ == "NOUN" or token.pos_ == "PROPN":
		return True
	return False

def is_verb(token):
	if token.pos_ == "VERB":
		return True
	return False

def is_compound(token):
	if token.dep_ == "compound" or (token.dep_ == "amod" and is_noun(token)): 
		return True
	return False

def is_subject(token):
	if token.dep_[:5] == 'nsubj':
		return True
	return False

def is_dobj(token):
	if token.dep_ == 'dobj':
		return True
	return False


class WeightedToken(object):
	def __init__(self, token, weight):
		self.token = token
		self.case = get_case(token)
		self.weight = weight


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
		print("  Main object:\t\t", matrix.VAL_MAIN_OBJ)
		print("  Noun in free form means:\t", matrix.VAL_MEANS_NOUN)
		print("  Noun in free form ends:\t", matrix.VAL_ENDS_NOUN)
		print("Relative Weights:")
		print("  Compound (compared to parent):", matrix.VAL_COMPOUND)

	def print_rel(rel):
		print(get_case(rel[1]), "--", rel[2], "->", get_case(rel[3]))