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
		if str.lower(t.text) == "i":  # quickfix for https://github.com/explosion/spaCy/issues/962
			return "I"
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

def get_head(tree):
	for t in tree:
		if t is t.head:
			return t

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
