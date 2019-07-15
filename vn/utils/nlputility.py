"""Utility module for `spacy` natural language processing (NLP)"""

import string
from .utility import text
from spacy.tokens.token import Token


def is_us(cl):
	if cl.name.startswith("US") or cl.name == 'UserStory':
		return True
	elif cl.parent.startswith("US"):
		return True
	return False

def t(li):
	if type(li) is list:
		return text(get_tokens(li))
	return li.text if li is not None else ''

def is_i(li):
	if str.lower(t(li)) == 'i':
		return True
	return False

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
		if t == t.head:
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