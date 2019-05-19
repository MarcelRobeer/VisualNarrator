"""Utility module for `vn.miner`"""

from .utility import is_sublist
from .nlputility import get_idx, is_noun, is_compound, is_verb
from lang.en.indicators import TYPE_II_PARTICLES, TYPE_II_PARTICLES_MARGINAL


# Fixes that a real lower string is used, instead of a reference
def lower(str):
	return str.lower()


# Fixes that spaCy dependencies are not spans, but temporary objects that get deleted when loaded into memory
def get_span(story, li, part='data'):
	ret = []
	for i in get_idx(li):
		ret.append(eval('story.' + str(part))[i])
	return ret


# Obtain Type I, II and III phrasal verbs
def get_phrasal_verb(story, head, part='data'):
	particles = TYPE_II_PARTICLES + TYPE_II_PARTICLES_MARGINAL
	phrasal_verb = head
	phrase = []
	mobj_i = 1000
	vtype = ""

	if part == 'means.text' or part == 'ends.text':
		for token in eval('story.' + str(part)):
			if token.dep_ == 'dobj':
				mobj_i = token.i
				break

	if str.lower(phrasal_verb.right_edge.text) in particles and phrasal_verb.right_edge.i < mobj_i:
		phrasal_verb = phrasal_verb.right_edge
		phrase.append(phrasal_verb)
		vtype = "II"
	else:
		for chunk in eval('story.' + str(part) + '.noun_chunks'):
			for c in phrasal_verb.children:
				if c == chunk.root.head and c.i < mobj_i:
					if c.pos_ == 'PART':
						phrase.append(c)
						vtype = "I"
						break
					if c.pos_ == 'ADP':
						phrase.append(c)
						vtype = "III"
						break

	if phrase:
		phrase.insert(0, head)

	return phrase, vtype


def _get(story, span, f_func):
	return get_span(story, list(filter(f_func, span)))


def get_subj(story, span):
	return _get(story, span, lambda x: x.dep_ == "subj")


def get_dobj(story, span):
	return _get(story, span, lambda x: x.dep_ == "dobj")


def get_nouns(story, span):
	return _get(story, span, lambda x: is_noun(x))


def get_proper_nouns(story, nouns):
	return _get(story, nouns, lambda x: x.tag_ == "NNP" or x.tag_ == "NNPS")


def get_compound_nouns(story, span):
	compounds = []
	nouns = get_nouns(story, span)

	for token in nouns:
		for child in token.children:
			if is_compound(child):
				# Replace to take rightmost child
				if child.idx < token.idx:
					for compound in compounds:
						if child in compound or token in compound:
							compounds.remove(compound)
				compounds.append([child, token])
	
	compounds = list(map(lambda c: get_span(story, c), compounds))

	if compounds and len(compounds) == 0 and type(compounds[0]) is list:
		compounds = compounds[0]

	return compounds


def get_noun_phrases(story, span, part='data'):
	phrases = []
	
	for chunk in eval('story.' + str(part) + '.noun_chunks'):
		chunk = get_span(story, chunk)
		if is_sublist(chunk, span):
			phrases.append(get_span(story, chunk))

	return phrases


def get_verbs(story, span):
	return _get(story, span, lambda x: is_verb(x) and str.lower(x.text) != 'can')


def get_phrasal_verbs(story, verbs):
	return [get_phrasal_verb(story, verb) for verb in verbs]
