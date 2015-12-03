import numpy as np
import pandas as pd
from spacy import attrs
from app.helper import Helper


class Matrix:
	def __init__(self, threshold, base, weight):
		self.threshold = threshold
		self.VAL_FUNC_ROLE = base * weight[0]
		self.VAL_DIRECT_OBJ = base * weight[1]
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

		empty_columns = np.zeros((doc_array.shape[0], len(stories)))

		w_us = pd.DataFrame(empty_columns, index=words, columns=ids)
		idx = np.unique(w_us.index, return_index=True)[1]
		w_us = w_us.iloc[idx]
		w_us = self.get_factor(w_us, stories)
		w_us['sum'] = w_us.sum(axis=1)
		w_us = self.remove_stop_words(w_us, doc_array)
		w_us = self.remove_indicators(w_us, stories)

		return w_us
		
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
			namedict[token.lemma] = Helper.case(token)

		return namedict

	def replace_ids(self, arr, words):
		new_arr = []
		[new_arr.append([row[1]]) for row in arr]
		return pd.DataFrame(new_arr, index=words, columns=['IS_STOP'])

	def is_synonym(self, token1, token2):
		if token1.lemma == token2.lemma:
			return True
		return False

	def get_factor(self, matrix, stories):
		for story in stories:
			for token in story.data:
				if Helper.case(token) in matrix.index.values:
					matrix.set_value(Helper.case(token), story.txtnr(), self.score(token, story))
		return matrix

	def score(self, token, story):
		weight = 0

		if token == story.role.functional_role.main:
			weight += self.VAL_FUNC_ROLE
		elif token in story.role.functional_role.compound:
			weight += self.VAL_FUNC_ROLE * self.VAL_COMPOUND
		
		if token == story.means.direct_object.main:
			weight += self.VAL_DIRECT_OBJ
		elif token in story.means.direct_object.compound:
			weight += self.VAL_DIRECT_OBJ * self.VAL_COMPOUND

		if story.means.free_form:									
			if story.means.nouns:
				if token in story.means.nouns:
					weight += self.VAL_MEANS_NOUN
		if story.ends.free_form:
			if story.ends.nouns:
				if token in story.ends.nouns:
					weight += self.VAL_ENDS_NOUN

		return weight

	def remove_indicators(self, matrix, stories):
		indicators = []
		for story in stories:
			for i in story.indicators:
				if Helper.case(i) not in indicators:
					indicators.append(Helper.case(i))

		# Something is off here...
		# Remove if it is in the list of indicators AND its sum is 0...		
		# matrix[(-matrix.index.isin(indicators)) & (matrix['sum'] != 0)]
		return matrix[(-matrix.index.isin(indicators))]

	def remove_stop_words(self, matrix, stopwords):
		result = pd.merge(matrix, stopwords, left_index=True, right_index=True, how='inner')
		result = result[(result['IS_STOP'] == 0)]
		return result.drop('IS_STOP', axis=1)
