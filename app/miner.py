from app.utility import Utility, NLPUtility
from lang.en.indicators import *

class StoryMiner:
	def structure(self, story):
		story = self.get_indicators(story)

		if not story.role.indicator:
			raise ValueError('Could not find a role indicator', 0)
		if not story.means.indicator:
			raise ValueError('Could not find a means indicator', 1)

		story = self.get_I(story)

	def mine(self, story, nlp):
		story = self.get_part_text(story)
		story = self.nlp_part(story, nlp)

		story = self.get_functional_role(story)
		if not story.role.functional_role:
			raise ValueError('Could not find a functional role', 2)

		story = self.get_dobj_and_mv(story)
		if not story.means.main_object.main:
			raise ValueError('Could not find a main object', 3)
		if not story.means.main_verb.main:
			raise ValueError('Could not find a main verb', 4)	
		
		if story.has_ends:
			story = self.get_dobj_and_mv(story, 'ends')	

		story = self.get_free_form(story)

	# New method
	def get_indicators(self, story):
		indicator_types = ['Role', 'Means', 'Ends']
		returnlist = []

		for indicator_type in indicator_types:
			found_ind = []
			found_i = []

			l_sentence = str.lower(story.sentence)

			for indicator in eval(indicator_type.upper() + '_INDICATORS'):
				if indicator_type.lower() == 'role':
					i = str.lower(indicator) + " "
				else:
					i = " " + str.lower(indicator) + " "

				if i in l_sentence:
					found_ind.append([l_sentence.find(i), indicator])

			# Get the one(s) at the lowest index			
			places = [i[0] for i in found_ind]
			if places:
				p_min = min(places)
			else:
				p_min = -1

			for i in found_ind:
				if i[0] > p_min:
					found_ind.remove(i)
			for i in found_ind:
				found_i.append(i[1])

			# If multiple remain, get the longest match
			if found_i:
				if len(found_i) > 1:
					returnlist.append([max(found_i, key=len), p_min])
				else:
					returnlist.append([found_i[0], p_min])
			else:
				returnlist.append(['', p_min])
			
		story.role.indicator = returnlist[0][0]
		story.means.indicator = returnlist[1][0]
		story.ends.indicator = returnlist[2][0]

		story.role.indicator_i = returnlist[0][1]
		story.means.indicator_i = returnlist[1][1]
		story.ends.indicator_i = returnlist[2][1]

		if story.ends.indicator_i > -1 and story.ends.indicator != '':
			story.has_ends = True

		if story.means.indicator_i > story.ends.indicator_i and story.ends.indicator_i > -1:
			story.means.indicator_i = -1
			story.ends.indicator_i = -1
			story.means.indicator = ''
			story.ends.indicator = ''
			story.has_ends = False

		return story

	def get_I(self, story):
		for token in story.data:
			if token.text == 'I':
				story.iloc.append(token.i)

		return story

	def get_part_text(self, story):
		story.role.t = story.sentence[len(story.role.indicator) + 1 : story.means.indicator_i]

		if story.has_ends and story.ends.indicator_i > story.means.indicator_i:
			story.means.t = story.sentence[len(story.means.indicator) + story.means.indicator_i + 1: story.ends.indicator_i]
			story.ends.t = story.sentence[len(story.ends.indicator) + story.ends.indicator_i + 2:]
		else:
			story.means.t = story.sentence[len(story.means.indicator) + story.means.indicator_i + 1:]

		story.means.simplified = 'I' + story.means.t

		if story.has_ends and story.ends.indicator_i > story.means.indicator_i:
			if str.lower(story.ends.t[:1]) == 'i':
				if str.lower(story.ends.t[:5]) == 'i can':
					story.ends.simplified = 'I ' + story.ends.t[6:]
				elif str.lower(story.ends.t[:12]) == 'i am able to':
					story.ends.simplified = 'I ' + story.ends.t[13:]
				else:
					story.ends.simplified = story.ends.t
			else:
				story.ends.simplified = story.ends.t

		if story.has_ends and story.ends.indicator_i <= story.means.indicator_i:
			story.has_ends = False
			story.ends.indicator_i = -1
			story.ends.indicator = ""

		return story

	def nlp_part(self, story, nlp):
		story.role.text = nlp(story.role.t)
		story.means.text = nlp(story.means.simplified)
		if story.has_ends:
			story.ends.text = nlp(story.ends.simplified)

		return story

	def get_functional_role(self, story):
		potential_without_with = []

		with_i = -1
		for token in story.role.text:
			if MinerUtility.lower(token.text) == 'with' or MinerUtility.lower(token.text) == 'w/':
				with_i = token.i
		if with_i > 0:
			potential_without_with = story.role.text[0:with_i]
		else:
			potential_without_with = story.role.text
		
		# If there is just one word
		if len(story.role.text) == 1:
			story.role.functional_role.main = story.role.text[0]
		else:		
			compound = []
			for token in potential_without_with:
				if token.dep_ == 'compound':
					compound.append([token, token.head])

			if len(compound) > 0 and type(compound[0]) is list:
				compound = compound[0]

			story.role.functional_role.compound = compound

			# If it is a compound
			if story.role.functional_role.compound:
				story.role.functional_role.main = story.role.functional_role.compound[-1]

			# Get head of tree
			else:
				for token in story.role.text:
					if token is token.head:
						story.role.functional_role.main = token

		return story

	def get_dobj_and_mv(self, story, part='means'):
		has_subj = False
		simple = False
		found_verb = False
		found_obj = False
		subject = []
		main_verb = []
		main_object = []

		# Simple case if the subj and dobj are linked by a verb
		for token in eval('story.' + str(part) + '.text'):
			if token.dep_[:5] == 'nsubj':
				has_subj = True
				subject = token
				if token.head.pos_ == 'VERB':
					found_verb = True
					main_verb = token.head
					break

		if type(subject) is list:
			subject = eval('story.' + str(part) + '.text')[0]

		for token in eval('story.' + str(part) + '.text'):
			if token.dep_ == 'dobj':
				found_obj = True
				if token.head == main_verb:
					simple = True
				main_object = token
				break
	
		# If the root of the sentence is a verb
		if not simple:
			for token in eval('story.' + str(part) + '.text'):
				if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
					found_verb = True
					main_verb = token
					break
		
		# If no main verb could be found it is the second word (directly after 'I')
		# Possibly a NLP error...
		if not found_verb:
			main_verb = eval('story.' + str(part) + '.text')[1]


		# If the sentence contains no dobj it must be another obj
		if not found_obj:
			for token in eval('story.' + str(part) + '.text'):
				if token.dep_[1:] == 'obj':
					found_obj = True
					main_object = token
					break

		# If none is found it points to the unknown 'system part'
		# + get phrases for main_object and main_verb
		if not found_obj and part != 'means':
			main_object = story.system.main

		if part == 'means':
			story.means.main_verb.main = main_verb
			story.means.main_object.main = main_object
		else:
			story.ends.subject.main = subject
			story.ends.main_verb.main = main_verb
			story.ends.main_object.main = main_object

		if main_object == story.system.main:
			story = eval('self.get_' + str(part) + '_phrases(story, False)')
		else:
			story = eval('self.get_' + str(part) + '_phrases(story)')

		return story

	def get_means_phrases(self, story, assume=True):
		if assume:
			for np in story.means.text.noun_chunks:
				if story.means.main_object.main in np:
					story.means.main_object.phrase = np

			if story.means.main_object.phrase:
				for token in story.means.main_object.phrase:
					if token.dep_ == 'compound' and token.head == story.means.main_object.main:
						story.means.main_object.compound = [token, story.means.main_object.main]

		pv = MinerUtility.get_phrasal_verb(story, story.means.main_verb.main, 'means.text')
		story.means.main_verb.phrase = MinerUtility.get_span(story, pv[0], 'means.text')
		story.means.main_verb.type = pv[1]

		return story	

	def get_ends_phrases(self, story, assume=True):
		if assume:
			for np in story.ends.text.noun_chunks:
				if story.ends.main_object.main in np:
					story.ends.main_object.phrase = np

			if story.ends.main_object.phrase:
				for token in story.ends.main_object.phrase:
					if token.dep_ == 'compound' and token.head == story.ends.main_object.main:
						story.ends.main_object.compound = [token, story.ends.main_object.main]

		ends_subj = story.ends.subject.main

		if str.lower(story.ends.subject.main.text) != '' and str.lower(story.ends.subject.main.text) != 'i':
			for np in story.ends.text.noun_chunks:
				if story.ends.subject.main in np:
					story.ends.subject.phrase = np
		
			if story.ends.subject.phrase:
				for token in story.ends.subject.phrase:
					if token.dep_ == 'compound' and token.head == story.ends.subject.main:
						story.ends.subject.compound = [token, story.ends.subject.main]

		pv = MinerUtility.get_phrasal_verb(story, story.ends.main_verb.main, 'ends.text')
		story.ends.main_verb.phrase = MinerUtility.get_span(story, pv[0], 'ends.text')
		story.ends.main_verb.type = pv[1]

		return story	

	def get_free_form(self, story):
		means_free_form = []

		# Get all parts of the main verb
		main_verb = []
		main_verb.append(story.means.main_verb.main)
		main_verb.extend(story.means.main_verb.phrase)

		# Get all parts of the main object
		main_object = []
		main_object.append(story.means.main_object.main)
		main_object.extend(story.means.main_object.phrase)		

		means_not_ff = main_verb + main_object

		# Exclude these from the free form
		for token in story.means.text:
			if token not in means_not_ff and token.i > 0: 
				means_free_form.append(token)
		
		story.means.free_form = MinerUtility.get_span(story, means_free_form, 'means.text')
		
		if story.has_ends:
			story.ends.free_form = story.ends.text
		
		# Extract useful information from free form
		if story.means.free_form or story.has_ends:
			self.get_ff_subj_dobj(story)
			self.get_ff_verbs(story)
			self.get_ff_nouns(story)
			if story.means.free_form:
				story.means.proper_nouns = MinerUtility.get_proper_nouns(story, story.means.nouns)
				story.means.noun_phrases = MinerUtility.get_noun_phrases(story, story.means.free_form)
				story.means.compounds = MinerUtility.get_compound_nouns(story, story.means.free_form)
			if story.has_ends:
				story.ends.proper_nouns = MinerUtility.get_proper_nouns(story, story.ends.nouns)
				story.ends.noun_phrases = MinerUtility.get_noun_phrases(story, story.ends.free_form)
				story.ends.compounds = MinerUtility.get_compound_nouns(story, story.ends.free_form)

		return story

	def get_ff_subj_dobj(self, story):
		story.means.nouns = MinerUtility.get_subj(story, story.means.free_form)
		story.means.nouns = MinerUtility.get_subj(story, story.ends.free_form)

		story.means.nouns = MinerUtility.get_dobj(story, story.means.free_form)
		story.means.nouns = MinerUtility.get_dobj(story, story.ends.free_form)

		return story

	def get_ff_nouns(self, story):
		story.means.nouns = MinerUtility.get_nouns(story, story.means.free_form)
		story.ends.nouns = MinerUtility.get_nouns(story, story.ends.free_form)	

		return story

	def get_ff_verbs(self, story):
		story.means.verbs = MinerUtility.get_verbs(story, story.means.free_form)
		story.ends.verbs = MinerUtility.get_verbs(story, story.ends.free_form)

		if story.means.verbs:
			story.means.phrasal_verbs = MinerUtility.get_phrasal_verbs(story, story.means.verbs)
		if story.ends.verbs:
			story.ends.phrasal_verbs = MinerUtility.get_phrasal_verbs(story, story.ends.verbs)

		return story


class MinerUtility:
	# Fixes that a real lower string is used, instead of a reference
	def lower(str):
		return str.lower()

	# Fixes that spaCy dependencies are not spans, but temporary objects that get deleted when loaded into memory
	def get_span(story, li, part='data'):
		ret = []
		idxlist = NLPUtility.get_idx(li)
		for i in idxlist:
			ret.append(eval('story.' + str(part))[i])
		return ret

	# Obtain noun phrases (including form 'x of y')
	'''
	def get_noun_phrase(story, pointer):
		phrase = []
		main = []

		for chunk in story.data.noun_chunks:
			if pointer == chunk.root.head:
				phrase = MinerUtility.get_span(story, chunk)

		if phrase:
			main = phrase[-1]
			if phrase[-1].i < story.data[-1].i:
				potential_of = story.data[phrase[-1].i + 1]
				if MinerUtility.lower(potential_of.text) == 'of':
					for chunk in story.data.noun_chunks:
						if chunk.root.head == potential_of:	
							phrase.append(potential_of)	
							phrase.extend(MinerUtility.get_span(story, chunk))
		elif pointer == story.data[pointer.i]:
			main = story.system.main
		else:
			main = story.data[pointer.i + 1]

		return main, phrase
	'''

	# Obtain Type I, II and III phrasal verbs
	def get_phrasal_verb(story, head, part='data'):
		particles = TYPE_II_PARTICLES + TYPE_II_PARTICLES_MARGINAL
		phrasal_verb = head
		phrase = []
		dobj_i = 1000
		vtype = ""

		if part == 'means.text' or part == 'ends.text':
			for token in eval('story.' + str(part)):
				if token.dep_ == 'dobj':
					dobj_i = token.i
					break

		if str.lower(phrasal_verb.right_edge.text) in particles and phrasal_verb.right_edge.i < dobj_i:
			phrasal_verb = phrasal_verb.right_edge
			phrase.append(phrasal_verb)
			vtype = "II"
		else:
			for chunk in eval('story.' + str(part) + '.noun_chunks'):
				for c in phrasal_verb.children:
					if c == chunk.root.head and c.i < dobj_i:
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

	def get_subj(story, span):
		subj = []

		for token in span:
			if token.dep_ == "subj":
				subj.append(token)

		return MinerUtility.get_span(story, subj)

	def get_dobj(story, span):
		dobj = []

		for token in span:
			if token.dep_ == "dobj":
				dobj.append(token)

		return MinerUtility.get_span(story, dobj)

	def get_nouns(story, span):
		nouns = []

		for token in span:
			if token.pos_ == "NOUN":
				nouns.append(token)

		return nouns

	def get_proper_nouns(story, nouns):
		proper = []

		for token in nouns:
			if token.tag_ == "NNP" or token.tag_ == "NNPS":
				proper.append(token)

		return proper

	def get_compound_nouns(story, span):
		compounds = []
		nouns = MinerUtility.get_nouns(story, span)

		for token in nouns:
			for child in token.children:
				if child.dep_ == "compound" and child not in compounds:
					compounds.append([child, token])
		
		for c in compounds:
			c = MinerUtility.get_span(story, c)

		if compounds and type(compounds[0]) is list:
			compounds = compounds[0]

		return compounds

	def get_noun_phrases(story, span, part='data'):
		phrases = []
		
		for chunk in eval('story.' + str(part) + '.noun_chunks'):
			chunk = MinerUtility.get_span(story, chunk)
			if Utility.is_sublist(chunk, span):
				phrases.append(MinerUtility.get_span(story, chunk))

		return phrases

	def get_verbs(story, span):
		verbs = []

		for token in span:
			if token.pos_ == "VERB":
				verbs.append(token)

		return MinerUtility.get_span(story, verbs)

	def get_phrasal_verbs(story, verbs):
		phrasal_verbs = []

		for token in verbs:
			phrasal_verbs.append(MinerUtility.get_phrasal_verb(story, token)) 

		return phrasal_verbs
