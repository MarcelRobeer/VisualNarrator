from vn.utils.minerutility import MinerUtility as mu
from vn.utils.utility import is_compound, is_dobj, is_verb, is_subject
from lang.en.indicators import ROLE_INDICATORS, MEANS_INDICATORS, ENDS_INDICATORS

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

		story = self.get_mobj_and_mv(story)
		if not story.means.main_object.main:
			raise ValueError('Could not find a main object', 3)
		if not story.means.main_verb.main:
			raise ValueError('Could not find a main verb', 4)	
		
		if story.has_ends:
			story = self.get_mobj_and_mv(story, 'ends')

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
			p_min = min(places) if places else -1

			for i in found_ind:
				if i[0] > p_min:
					found_ind.remove(i)
			for i in found_ind:
				found_i.append(i[1])

			# If multiple remain, get the longest match
			i_max = max(found_i, key=len) if found_i else ''
			returnlist.append([i_max, p_min])
			
		story.role.indicator, story.role.indicator_i = returnlist[0]
		story.means.indicator, story.means.indicator_i = returnlist[1]
		story.ends.indicator, story.ends.indicator_i = returnlist[2]

		if story.ends.indicator_i > -1 and story.ends.indicator != '':
			story.has_ends = True

		if story.means.indicator_i > story.ends.indicator_i and story.ends.indicator_i > -1:
			story.means.indicator_i, story.ends.indicator_i = (-1, -1)
			story.means.indicator, story.ends.indicator = ('', '')
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

		story.means.simplified = 'I can' + story.means.t

		if story.has_ends and story.ends.indicator_i > story.means.indicator_i:
			if str.lower(story.ends.t[:1]) == 'i':
				if str.lower(story.ends.t[:12]) == 'i am able to':
					story.ends.simplified = 'I can' + story.ends.t[13:]
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
			if mu.lower(token.text) == 'with' or mu.lower(token.text) == 'w/':
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
				if is_compound(token):
					compound.append([token, token.head])

			if len(compound) == 1 and type(compound[0]) is list:
				compound = compound[0]
			# pick rightmost
			elif len(compound) > 1 and type(compound[-1]) is list:
				compound = compound[-1]

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

	def get_mobj_and_mv(self, story, part='means'):
		simple = False
		subject = None
		main_verb = None
		main_object = None
		mv_phrase = None

		# Simple case if the subj and dobj are linked by a verb
		for token in eval('story.' + str(part) + '.text'):
			if is_subject(token):
				subject = token
				if is_verb(token.head) and str.lower(token.head.text) != 'can':
					main_verb = token.head
					break

		if subject is None:
			subject = eval('story.' + str(part) + '.text')[0]

		for token in eval('story.' + str(part) + '.text'):
			if is_dobj(token):
				if token.pos_ == "PRON": # If it is a pronoun, look for a preposition with a pobj
					f = False
					for child in token.head.children:
						if child.dep_ == "prep" and child.right_edge.dep_ == "pobj" and not f:
							token = child.right_edge
							mv_phrase = [main_verb, child]
							f = True
				elif token.pos_ == "ADJ" or token.pos_ == "ADV": # Set to right edge if there is an adj/adv as dobj, and possibly make a verb phrase
					f = False
					for child in token.children:
						if child.dep_ == "prep" and not f:
							for grandchild in child.children:
								if grandchild.dep_ == "pobj":
									mv_phrase = [main_verb, token, child]
									token = grandchild
									f = True
				if token.head == main_verb:
					simple = True

				main_object = token

				break
	
		# If the root of the sentence is a verb
		if not simple:
			for token in eval('story.' + str(part) + '.text'):
				if token.dep_ == 'ROOT' and is_verb(token):
					main_verb = token
					break
		
		# If no main verb could be found it is the second word (directly after 'I')
		# Possibly a NLP error...
		if main_verb is None:
			if str(part) == 'means' or str.lower(eval('story.' + str(part) + '.text')[1].text) == 'can':
				main_verb = eval('story.' + str(part) + '.text')[2]
			else:
				main_verb = eval('story.' + str(part) + '.text')[1]

		# If the sentence contains no dobj it must be another obj
		if main_object is None:
			for token in eval('story.' + str(part) + '.text'):
				if token.dep_[1:] == 'obj':
					main_object = token
					break

		# If none is found it points to the unknown 'system part'
		# + get phrases for main_object and main_verb
		if main_object is None and part == 'means':
			main_object = story.system.main

		s = story.means if part == 'means' else story.ends	
		s.main_verb.main = main_verb
		s.main_object.main = main_object
		if mv_phrase is not None:
			s.phrase = mu.get_span(story, mv_phrase, 'means.text')
			s.main_verb.type = "II"
		if part == 'ends':
			s.subject.main = subject		


		if type(main_object) is list or main_object == story.system.main:
			story = eval('self.get_' + str(part) + '_phrases(story, ' + str(mv_phrase is not None) + ', False)')
		else:
			story = eval('self.get_' + str(part) + '_phrases(story, ' + str(mv_phrase is not None) + ')')

		return story

	def get_means_phrases(self, story, found_mv_phrase, assume=True):
		sm = story.means
		smo = sm.main_object

		if assume:
			for np in sm.text.noun_chunks:
				if smo.main in np:
					smo.phrase = np
			if smo.phrase:
				m = smo.main
				if m.i > 0 and is_compound(m.nbor(-1)) and m.nbor(-1).head == m:
					smo.compound = [m.nbor(-1), m]
				else:
					for token in smo.phrase:
						if is_compound(token) and token.head == smo.main:
							smo.compound = [token, smo.main]

		if not found_mv_phrase:
			pv = mu.get_phrasal_verb(story, sm.main_verb.main, 'means.text')
			sm.main_verb.phrase = mu.get_span(story, pv[0], 'means.text')
			sm.main_verb.type = pv[1]

		return story	

	def get_ends_phrases(self, story, found_mv_phrase, assume=True):
		se = story.ends
		seo = se.main_object
		if assume:
			for np in se.text.noun_chunks:
				if seo.main in np:
					seo.phrase = np
			if seo.phrase:
				m = seo.main
				if m.i > 0 and is_compound(m.nbor(-1)) and m.nbor(-1).head == m:
					seo.compound = [m.nbor(-1), m]
				else:
					for token in seo.phrase:
						if is_compound(token) and token.head == seo.main:
							seo.compound = [token, seo.main]

		if str.lower(se.subject.main.text) != '' and str.lower(se.subject.main.text) != 'i':
			for np in se.text.noun_chunks:
				if se.subject.main in np:
					se.subject.phrase = np
		
			if se.subject.phrase:
				for token in se.subject.phrase:
					if is_compound(token) and token.head == se.subject.main:
						se.subject.compound = [token, se.subject.main]

		if not found_mv_phrase:
			pv = mu.get_phrasal_verb(story, se.main_verb.main, 'ends.text')
			se.main_verb.phrase = mu.get_span(story, pv[0], 'ends.text')
			se.main_verb.type = pv[1]

		return story	

	def get_free_form(self, story):
		means_free_form = []

		# Get all parts of the main verb
		main_verb = list([story.means.main_verb.main])
		main_verb += story.means.main_verb.phrase

		# Get all parts of the main object
		main_obj = list([story.means.main_object.main])
		main_obj += story.means.main_object.phrase

		# Exclude these from the free form
		for token in story.means.text:
			if token not in (main_verb + main_obj) and token.i > 1: 
				means_free_form.append(token)
		
		story.means.free_form = mu.get_span(story, means_free_form, 'means.text')		
	
		if story.has_ends:
			story.ends.free_form = story.ends.text
		
		# Extract useful information from free form
		if story.means.free_form or story.has_ends:
			self.get_ff(story, story.means)
			self.get_ff(story, story.ends)

			if story.means.free_form:
				self.second_phase(story, story.means)
			if story.has_ends:
				self.second_phase(story, story.ends)
		
		return story

	def get_ff(self, story, s):
		s.nouns = mu.get_subj(story, s.free_form)
		s.nouns = mu.get_dobj(story, s.free_form)
		s.nouns = mu.get_nouns(story, s.free_form)
		s.verbs = mu.get_verbs(story, s.free_form)
		if s.verbs:
			s.phrasal_verbs = mu.get_phrasal_verbs(story, s.verbs)
		return story
	
	def second_phase(self, story, s):
		s.proper_nouns = mu.get_proper_nouns(story, s.nouns)
		s.noun_phrases = mu.get_noun_phrases(story, s.free_form)
		s.compounds    = mu.get_compound_nouns(story, s.free_form)
		return story
