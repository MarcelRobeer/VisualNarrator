import numpy as np
from spacy import attrs

class Matrix:
	def __init__(self, threshold, base, weight):
		self.matrix = []
		self.threshold = threshold
		self.VAL_FUNC_ROLE = base * weight[0]
		self.VAL_DIRECT_OBJ = base * weight[1]
		self.VAL_MEANS_NOUN = base * weight[2]
		self.VAL_ENDS_NOUN = base * weight[3]
		self.VAL_COMPOUND = weight[4]

	def generate(self, stories, set, nlp):
		set = ' '.join(set.split())
		tokens = nlp(set)

		attr_ids = [attrs.LEMMA, attrs.IS_STOP, attrs.IS_PUNCT, attrs.IS_SPACE, attrs.NULL_ATTR, attrs.NULL_ATTR]
		doc_array = tokens.to_array(attr_ids)

		doc_array = self.remove_stop_punct_space(doc_array)
		doc_array = self.unique(doc_array)
		doc_array = self.get_factor(tokens, doc_array, stories)

		namedict = self.get_namedict(tokens)

		potential_classes = []
		[potential_classes.append([namedict[row[0]], row[1], row[2]]) for row in doc_array]
		potential_classes = sorted(potential_classes, key=lambda cl: cl[1], reverse=True)

		classes = []
		[classes.append(row[0]) for row in potential_classes if row[1] >= self.threshold]

		print("Threshold:\t\t\t", self.threshold)
		print("Functional role weight:\t\t", self.VAL_FUNC_ROLE)
		print("Direct object weight:\t\t", self.VAL_DIRECT_OBJ)
		print("Noun in free form means weight:\t", self.VAL_MEANS_NOUN)
		print("Noun in free form ends weight:\t", self.VAL_ENDS_NOUN)
		print("Compound weight:\t\t", self.VAL_COMPOUND, "\n\n")


		print("Potential classes")
		print(potential_classes)

		print("\nList of classes ( threshold =", self.threshold, ")")
		print(classes)

		
	def unique(self, arr):
		arr = np.ascontiguousarray(arr)
		unique_arr = np.unique(arr.view([('', arr.dtype)] * arr.shape[1]))
		return unique_arr.view(arr.dtype).reshape((unique_arr.shape[0], arr.shape[1]))

	def remove_stop_punct_space(self, doc_array):
		doc_array = doc_array[ np.logical_not( np.logical_or( doc_array[:,1] == 1, doc_array[:,2] == 1, doc_array[:,3] == 1 )) ]
		return np.delete(doc_array, np.s_[1:4], 1)

	def get_namedict(self, tokens):
		namedict = {}

		for token in tokens:
			namedict[token.lemma] = token.lemma_

		return namedict

	def is_synonym(self, token1, token2):
		if token1.lemma == token2.lemma:
			return True
		return False

	def get_factor(self, tokens, doc_array, stories):
		for story in stories:
			for token in story.data:
				for row in doc_array:
					if row[0] == token.lemma:
						row[1] += self.score(token, story)
						row[2] += 1

		return doc_array

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
