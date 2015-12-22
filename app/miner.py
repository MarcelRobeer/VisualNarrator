from app.utility import Utility, NLPUtility
from lang.en.indicators import *

class StoryMiner:
	def structure(self, story):
		story = self.get_indicators(story)
		if not story.role.indicator:
			raise ValueError('Could not find a role indicator', 0)
		if not story.means.indicator:
			raise ValueError('Could not find a means indicator', 1)

		story = self.replace_I(story)

	def mine(self, story):
		story = self.get_part_text(story)

		story = self.get_functional_role(story)
		if not story.role.functional_role:
			raise ValueError('Could not find a functional role', 2)

		story = self.get_dobj_and_mv(story)
		if not story.means.direct_object.main:
			raise ValueError('Could not find a direct object', 3)
		if not story.means.main_verb.main:
			raise ValueError('Could not find a main verb', 4)	
		story = self.get_phrases(story)		

		story = self.get_free_form(story)

	def get_indicators(self, story):
		foundlist = []
		potentials = []
		returnlist = []
		indicators = ['Role', 'Means', 'Ends']

		for indicator in indicators:
			found_ind = self.get_one_indicator(story, indicator)	
			foundlist.append(found_ind)

		# Removes a role indicator of it comes after the first means/ends indicator, removes a means indicator if it comes after the first ends indicator
		if foundlist[0] and foundlist[1]:
			means_min = min([int(s) for s in [t[0].i for t in foundlist[1]]])
			for f in foundlist[0]:
				if f.i >= means_min:
					foundlist[0].remove(f)
			if foundlist[2]:
				ends_min = min([int(s) for s in [t[0].i for t in foundlist[2]]])
				for f in foundlist[0]:
					if f.i >= ends_min:
						foundlist[0].remove(f)
				for f in foundlist[1]:
					if f.i >= ends_min:
						foundlist[1].remove(f)

		# If there are multiple indicators left, choose the first one
		for found in foundlist:
			if len(found) > 1:
				min_i = min([int(s) for s in [t[0].i for t in found]])
				for f in found:
					if f[0].i == min_i:
						ind = f
				found = ind
			elif found:
				found = found[0]
			returnlist.append(found)

		story.role.indicator = returnlist[0]
		story.means.indicator = returnlist[1]
		story.ends.indicator = returnlist[2]

		return story

	def get_one_indicator(self, story_data, indicator_type):
		'''Returns all longest indicators for one type (role/means/ends)
		'''
		pattern = [x.split(' ') for x in eval(indicator_type.upper() + '_INDICATORS')]
		present_pattern = []
		found_pattern = []

		# Get a list of all patterns present in the text
		for p in pattern:
			if Utility.is_exact_sublist([MinerUtility.lower(pl) for pl in p], [MinerUtility.lower(sd) for sd in NLPUtility.get_tokens(story_data)]) >= 0:
				present_pattern.append(p)

		# Gets equivalent token objects of the indicator(s) from story data
		for p in present_pattern:
			for s in story_data:
				subl = story_data[s.i:s.i++len(p)]
				if [MinerUtility.lower(pp) for pp in p] == [MinerUtility.lower(sl.text) for sl in subl]:
					found_pattern.append(subl) 

		# Gets the longest form of any present pattern (e.g., if 'As' and 'As a', remove 'As' from the list)
		for pattern in found_pattern:
			for p in found_pattern:
				if pattern[0].i == p[0].i and len(pattern) > len(p):
					found_pattern.remove(p)
					
		if found_pattern:
			return found_pattern

		return []

	def replace_I(self, story):
		for token in story.data:
			if token.text == 'I':
				story.iloc.append(token.i)

		return story

	def get_part_text(self, story):
		ends_b_idx = story.data[-1].i+1
		ends_e_idx = ends_b_idx

		if story.ends.indicator:
			ends_b_idx = story.ends.indicator[-1].i-1
			ends_e_idx = ends_b_idx + len(story.ends.indicator)

		story.role.text = story.data[story.role.indicator[-1].i+1:story.means.indicator[0].i]
		story.means.text = story.data[story.means.indicator[-1].i+1:ends_b_idx]

		if story.ends.indicator:
			story.ends.text = story.data[ends_e_idx:]

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
		
		if len(story.role.text) == 1:
			story.role.functional_role.main = story.role.text[0]
		else:		
			compound = MinerUtility.get_compound_nouns(story, potential_without_with)
			story.role.functional_role.compound = compound

			if story.role.functional_role.compound:
				story.role.functional_role.main = story.role.functional_role.compound[-1]
			else:
				story.role.functional_role.main = story.role.indicator[0].right_edge

		return story

	def get_dobj_and_mv(self, story):
		success = False

		for token in story.means.text:
			if token.dep_ == 'dobj':
				story.means.direct_object.main = token
			else:
				story.means.direct_object.main = story.system.main

		if story.means.direct_object.main != story.system.main: # Apply new method
			if story.means.direct_object.main.head.pos_ == 'VERB':
				story.means.main_verb.main = story.means.direct_object.main.head
				success = True

		if not success: # Fallback: apply old method
			story.means.main_verb.main = story.data[story.means.indicator[-1].i].nbor(1)

		if story.means.main_verb.main.pos_ != 'VERB':
			if story.means.main_verb.main.head.pos_ == 'VERB':
				story.means.main_verb.main = story.means.main_verb.main.head

			story = self.get_phrases(story, False)
	
		if not success: # Do rest of old method
			if not story.means.main_verb.phrase:
				pointer = story.means.main_verb.main
			else:
				pointer = story.means.main_verb.phrase[-1]
			
			if pointer.right_edge != pointer:
				story.means.direct_object.main = pointer.right_edge

		if story.means.main_verb.main.pos_ != 'VERB':
			print(story.number, ":", story.means.main_verb.main, story.means.main_verb.main.pos_, story.means.main_verb.main.head)

		return story

	def get_phrases(self, story, assume=True):
		if assume:
			for np in story.data.noun_chunks:
				if story.means.direct_object.main in np:
					story.means.direct_object.phrase = np

			if story.means.direct_object.phrase:
				compound = MinerUtility.get_compound_nouns(story, story.means.direct_object.phrase)
				story.means.direct_object.compound = compound

		pv = MinerUtility.get_phrasal_verb(story,
 story.means.main_verb.main)
		story.means.main_verb.phrase = MinerUtility.get_span(story, pv[0])
		story.means.main_verb.type = pv[1]

		return story	

	def get_free_form(self, story):
		list = []

		main_verb = []
		main_verb.append(story.means.main_verb.main)
		main_verb.extend(story.means.main_verb.phrase)

		direct_obj = []
		direct_obj.append(story.means.direct_object.main)
		direct_obj.extend(story.means.direct_object.phrase)		

		not_free_form = story.indicators + main_verb + direct_obj

		for token in story.data:
			if token not in not_free_form and token.i not in story.iloc:
				list.append(token)
		
		story.free_form = MinerUtility.get_span(story, list)

		means_free_form = []
		ends_free_form = []
		for token in story.free_form:
			if token in story.means.text:
				means_free_form.append(token)
			elif story.ends.indicator and token in story.ends.text:
				ends_free_form.append(token)
		
		story.means.free_form = MinerUtility.get_span(story, means_free_form)
		story.ends.free_form = MinerUtility.get_span(story, ends_free_form)
		
		if story.means.free_form or story.ends.free_form:
			self.get_ff_verbs(story)
			self.get_ff_nouns(story)
			if story.means.free_form:
				story.means.proper_nouns = MinerUtility.get_proper_nouns(story, story.means.nouns)
				story.means.noun_phrases = MinerUtility.get_noun_phrases(story, story.means.free_form)
				story.means.compounds = MinerUtility.get_compound_nouns(story, story.means.free_form)
			if story.ends.free_form:
				story.ends.proper_nouns = MinerUtility.get_proper_nouns(story, story.ends.nouns)
				story.ends.noun_phrases = MinerUtility.get_noun_phrases(story, story.ends.free_form)
				story.ends.compounds = MinerUtility.get_compound_nouns(story, story.ends.free_form)

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
	def get_span(story, li):
		ret = []
		idxlist = NLPUtility.get_idx(li)
		for i in idxlist:
			ret.append(story.data[i])
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
	def get_phrasal_verb(story, head):
		particles = TYPE_II_PARTICLES + TYPE_II_PARTICLES_MARGINAL
		phrasal_verb = head
		phrase = []
		vtype = ""

		if MinerUtility.lower(phrasal_verb.right_edge.text) in particles:
			phrasal_verb = phrasal_verb.right_edge
			phrase.append(phrasal_verb)
			vtype = "II"
		else:
			for chunk in story.data.noun_chunks:
				for c in phrasal_verb.children:
					if c == chunk.root.head:
						if not c in story.indicators:
							if c.pos_ == 'PART':
								phrase.append(c)
								vtype = "I"
							if c.pos_ == 'ADP':
								phrase.append(c)
								vtype = "III"
		
		if phrase:
			phrase.insert(0, head)

		return phrase, vtype

	def get_nouns(story, span):
		nouns = []

		for token in span:
			if token.pos_ == "NOUN":
				nouns.append(token)

		return MinerUtility.get_span(story, nouns)

	def get_proper_nouns(story, nouns):
		proper = []

		for token in nouns:
			if token.tag_ == "NNP" or token.tag_ == "NNPS":
				proper.append(token)

		return MinerUtility.get_span(story, proper)

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

	def get_noun_phrases(story, span):
		phrases = []
		
		for chunk in story.data.noun_chunks:
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
