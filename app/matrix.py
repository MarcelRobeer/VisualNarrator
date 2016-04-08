import numpy as np
import pandas as pd
from spacy import attrs
from app.utility import NLPUtility


class Matrix:
	def __init__(self, base, weight):
		self.VAL_FUNC_ROLE = base * weight[0]
		self.VAL_MAIN_OBJ = base * weight[1]
		self.VAL_MEANS_NOUN = base * weight[2]
		self.VAL_ENDS_NOUN = base * weight[3]
		self.VAL_COMPOUND = weight[4]

	def generate(self, stories, set, nlp):
		set = ' '.join(set.split())
		tokens = nlp(set)

		attr_ids = [attrs.LEMMA, attrs.IS_STOP, attrs.IS_PUNCT, attrs.IS_SPACE]
		doc_array = tokens.to_array(attr_ids)

		namedict = self.get_namedict(tokens)
		doc_array = self.unique(doc_array)
		doc_array = self.remove_punct(doc_array)

		words = [namedict[row[0]] for row in doc_array]
		ids = [us.txtnr() for us in stories]

		doc_array = self.replace_ids(doc_array, words)

		w_us = pd.DataFrame(0.0, index=words, columns=ids)
		w_us = w_us.iloc[np.unique(w_us.index, return_index=True)[1]]

		# w_us = self.remove_stop_words(w_us, doc_array)
		w_us = self.remove_indicators(w_us, stories, nlp)
		w_us = self.remove_verbs(w_us, stories)
		w_us = self.get_factor(w_us, stories)

		w_us['sum'] = w_us.sum(axis=1)

		###
		us_ids = []
		rme = []

		for us in stories:
			if us.role.indicator:
				us_ids.append(us.txtnr())
				rme.append('Role') 
			if us.means.indicator:
				us_ids.append(us.txtnr())
				rme.append('Means')
			if us.ends.indicator:
				us_ids.append(us.txtnr())
				rme.append('Ends')

		rme_cols = pd.MultiIndex.from_arrays([us_ids, rme], names=['user_story', 'part'])
		rme_us = pd.DataFrame(0, index=words, columns=rme_cols)
		rme_us = rme_us.iloc[np.unique(rme_us.index, return_index=True)[1]]
		rme_us = self.get_role_means_ends(rme_us, stories)	
		###

		colnames = ['Functional Role', 'Functional Role Compound', 'Man Object', 'Main Object Compound', 'Means Free Form Noun', 'Ends Free Form Noun']
		stories_list = [[l, []] for l in list(w_us.index.values)]
		count_matrix = pd.DataFrame(0, index=w_us.index, columns=colnames)
		co = self.count_occurence(count_matrix, stories_list, stories)
		count_matrix = co[0]
		stories_list = co[1]

		return w_us, count_matrix, stories_list, rme_us
		
	def get_factor(self, matrix, stories):
		for story in stories:
			if story.has_ends:
				parts = ['role', 'means', 'ends']
			else:
				parts = ['role', 'means']

			for part in parts:
				matrix = self.get_factor_part(matrix, story, part)		

		return matrix

	def get_factor_part(self, matrix, story, part):
		for token in eval('story.' + str(part) + '.text'):
			if NLPUtility.case(token) in matrix.index.values:
				matrix = self.add(matrix, NLPUtility.case(token), story.txtnr(), self.score(token, story))

		return matrix

	def score(self, token, story):
		weight = 0

		if self.is_phrasal('role.functional_role', token, story) == 1:
			weight += self.VAL_FUNC_ROLE
		elif self.is_phrasal('role.functional_role', token, story) == 2:
			weight += self.VAL_FUNC_ROLE * self.VAL_COMPOUND

		if self.is_phrasal('means.main_object', token, story) == 1:
			weight += self.VAL_MAIN_OBJ
		elif self.is_phrasal('means.main_object', token, story) == 2:
			weight += self.VAL_MAIN_OBJ * self.VAL_COMPOUND

		if self.is_freeform('means', token, story) == 1:
			weight += self.VAL_MEANS_NOUN

		if self.is_freeform('ends', token, story) == 1:
			weight += self.VAL_ENDS_NOUN	

		return weight

	def count_occurence(self, cm, sl, stories):
		for story in stories:
			for token in story.data:
				c = NLPUtility.case(token)
				if c in cm.index.values:
					for s in sl:
						if s[0] == c:
							s[1].append(story.number)					

					if self.is_phrasal('role.functional_role', token, story) == 1:
						cm = self.add(cm, c, 'Functional Role')
					elif self.is_phrasal('role.functional_role', token, story) == 2:
						cm = self.add(cm, c, 'Functional Role Compound')

					if self.is_phrasal('means.main_object', token, story) == 1:
						cm = self.add(cm, c, 'Main Object')
					elif self.is_phrasal('means.main_object', token, story) == 2:
						cm = self.add(cm, c, 'Main Object Compound')

					if self.is_freeform('means', token, story) == 1:
						cm = self.add(cm, c, 'Means Free Form Noun')

					if self.is_freeform('ends', token, story) == 1:
						cm = self.add(cm, c, 'Ends Free Form Noun')
					
		return cm, sl

	def get_role_means_ends(self, matrix, stories):
		cases = matrix.index.values

		for case in cases:
			for story in stories:
				if story.role.indicator:
					if case in [NLPUtility.case(token) for token in story.role.text]:
						matrix.set_value(case, (story.txtnr(), 'Role'), 1)
				if story.means.indicator:
					if case in [NLPUtility.case(token) for token in story.means.text]:
						matrix.set_value(case, (story.txtnr(), 'Means'), 1)
				if story.ends.indicator:
					if case in [NLPUtility.case(token) for token in story.ends.text]:
						matrix.set_value(case, (story.txtnr(), 'Ends'), 1)
								
		return matrix

	def add(self, matrix, index, column, by=1):
		return matrix.set_value(index, column, matrix.at[index,column]+by)

	def unique(self, arr):
		arr = np.ascontiguousarray(arr)
		unique_arr = np.unique(arr.view([('', arr.dtype)] * arr.shape[1]))
		return unique_arr.view(arr.dtype).reshape((unique_arr.shape[0], arr.shape[1]))

	def remove_punct(self, doc_array):
		doc_array = doc_array[ np.logical_not( np.logical_or( doc_array[:,2] == 1, doc_array[:,3] == 1 )) ]
		return np.delete(doc_array, np.s_[2:4], 1)

	def get_namedict(self, tokens):
		namedict = {}

		for token in tokens:
			namedict[token.lemma] = NLPUtility.case(token)

		return namedict

	def replace_ids(self, arr, words):
		new_arr = []
		[new_arr.append([row[1]]) for row in arr]
		return pd.DataFrame(new_arr, index=words, columns=['IS_STOP'])

	def is_synonym(self, token1, token2):
		if token1.lemma == token2.lemma:
			return True
		return False

	def is_phrasal(self, part, token, story):
		spart = 'story.' + part
		if token == eval(spart + '.main'):
			return 1
		elif token in eval(spart + '.compound'):
			return 2
		elif token in eval(spart + '.phrase'):
			return 3
		return -1

	def is_freeform(self, part, token, story):
		spart = 'story.' + part
		if eval(spart + '.free_form'):
			if eval(spart + '.nouns'):
				if token in eval(spart + '.nouns'):
					return 1
		return -1

	def remove_indicators(self, matrix, stories, nlp):
		indicators = []

		for story in stories:
			ind = story.role.indicator + " " + story.means.indicator
			if story.has_ends:
				ind += " " + story.ends.indicator

			[indicators.append(NLPUtility.case(t)) for t in nlp(ind)]

			[indicators.append(i) for i in story.indicators]

		# Something is off here...
		# Remove if it is in the list of indicators AND its sum is 0...		
		# matrix[(-matrix.index.isin(indicators)) & (matrix['sum'] != 0)]
		return matrix[(-matrix.index.isin(indicators))]

	def remove_verbs(self, matrix, stories):
		verbs = []
		cases = matrix.index.values.tolist()		

		for case in cases:
			pos = []

			for story in stories:
				for token in story.data:
					if NLPUtility.case(token) == case:
						pos.append(token.pos_)

			if len(set(pos)) == 1 and pos[0] == 'VERB':
				verbs.append(case)

		return matrix[(-matrix.index.isin(verbs))]

	def remove_stop_words(self, matrix, stopwords):
		result = pd.merge(matrix, stopwords, left_index=True, right_index=True, how='inner')
		result = result[(result['IS_STOP'] == 0)]

		# Special case: 'I' -> replace by functional role?
		# Should not remove stop words with a high weight
		return result.drop('IS_STOP', axis=1)
