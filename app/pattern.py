import string
import numpy as np
import pandas
from enum import Enum

from app.ontologygenerator import Generator, Ontology
from app.utility import NLPUtility

class Constructor:
	def __init__(self, nlp, user_stories, matrix):
		self.nlp = nlp
		self.user_stories = user_stories
		self.weights = matrix['sum'].reset_index().values.tolist()

	def make(self, ontname, threshold, link):
		pf = PatternFactory(self)
		weight_objects = WeightMaker.make(self.user_stories, self.weights)

		self.onto = Ontology(ontname)

		for us in self.user_stories:
			pf.make_patterns(us, link)

		g = Generator(self.onto.classes, self.onto.relationships)

		for wo in weight_objects:
			print(wo.case, wo.weight, "\t\t", wo.token.i)
		print(np.zeros(10, dtype=[('pre', object),('rel', object),('post', object)]))
		
		return g.prt(self.onto)
			
	def get_main_verb(self, us):
		if not us.means.main_verb.phrase:
			av = NLPUtility.case(us.means.main_verb.main)
		else:
			av = self.make_multiword_string(us.means.main_verb.phrase)	

		return av

	def get_direct_object(self, us):
		if not us.means.direct_object.compound:
			do = NLPUtility.case(us.means.direct_object.main)
		else:
			do = self.make_multiword_string(us.means.direct_object.compound)

		return do

	def make_multiword_string(self, span):
		ret = ""
		
		for token in span:
			ret += NLPUtility.case(token)

		return ret
	
	def t(self, token):
		return token.main.text

class WeightedToken(object):
	def __init__(self, token, weight):
		self.token = token
		self.case = NLPUtility.case(token)
		self.weight = weight

class WeightMaker:
	def make(stories, weights):
		weighted_tokens = []
		indices = [weight[0] for weight in weights]
		w = 0.0
		c = ""

		for story in stories:
			for token in story.data:
				c = NLPUtility.case(token)
				if c in indices:
					for weight in weights:
						if weight[0] == c:
							w = weight[1]
							break
				else:
					w = 0.0
			weighted_tokens.append(WeightedToken(token, w))

		return weighted_tokens


class PatternFactory:
	def __init__(self, constructor):
		self.constructor = constructor

	def make_patterns(self, us, link):
		pi = PatternIdentifier()
		pi.identify_patterns(us, link)

		# WIP Prints all patterns that are found
		#print("US", us.number, ">", pi.found_patterns)

		self.constructor.onto.get_class_by_name('Person')
		self.constructor.onto.get_class_by_name('FunctionalRole', 'Person')

		if link:
			self.constructor.onto.get_class_by_name('UserStory')

		for fp in pi.found_patterns:
			self.construct_pattern(us, fp)

		return self

	def construct_pattern(self, us, pattern):
		action_v = self.constructor.get_main_verb(us)		
		direct_obj = self.make_direct_object(us)

		if pattern == Pattern.desc_func_adj:
			func_role = self.make_subtype_functional_role(us)
		elif pattern == Pattern.basic:
			func_role = self.make_functional_role(us)

		if pattern == Pattern.parent:
			self.make_parent(us)

		if pattern == Pattern.link_to_US:
			self.link(us)

	def link(self, us):
		nr = us.txtnr()
		self.constructor.onto.get_class_by_name(nr, 'UserStory')
		
		for cl in self.constructor.onto.classes:
			self.make_relationship(cl.name, nr, nr, 'partOf')			

	def make_subtype_functional_role(self, us):
		func_role = string.capwords(us.role.functional_role.main.lemma_)
		subtype = ""		
		compound_noun = []

		for token in us.role.functional_role.compound:
			compound_noun.append(token)

		subtype = self.constructor.make_multiword_string(compound_noun)

		self.constructor.onto.get_class_by_name(func_role, 'FunctionalRole')
		self.constructor.onto.get_class_by_name(subtype + func_role, func_role)
		self.constructor.onto.get_class_by_name(subtype)
		self.make_has_relationship(subtype, func_role, subtype + func_role)
		self.make_can_relationship(subtype + func_role, self.constructor.get_main_verb(us), self.constructor.get_direct_object(us))

		return func_role

	def make_parent(self, us):
		head = ""
		compound_noun = []

		for token in us.means.direct_object.compound:
			compound_noun.append(token)
			if token.head not in us.means.direct_object.compound:
				head = string.capwords(token.lemma_)

		cn = self.constructor.make_multiword_string(compound_noun)	
		self.constructor.onto.get_class_by_name(cn, head)

	def make_functional_role(self, us):
		func_role = NLPUtility.case(us.role.functional_role.main)
		self.constructor.onto.get_class_by_name(func_role, 'FunctionalRole')
		self.make_can_relationship(func_role, self.constructor.get_main_verb(us), self.constructor.get_direct_object(us))
		return func_role

	def make_direct_object(self, us):
		direct_obj = self.constructor.get_direct_object(us)
		self.constructor.onto.get_class_by_name(direct_obj)
		return direct_obj

	def make_can_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'can')

	def make_has_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'has')

	def make_relationship(self, pre, rel, post, connector):
		self.constructor.onto.new_relationship(pre, connector + rel, post)	


class PatternIdentifier:
	def __init__(self):
		self.found_patterns = []

	def identify_patterns(self, story, link_to_us):
		if link_to_us:
			self.found_patterns.append(Pattern.link_to_US)
		if self.identify_desc_func_adj(story):
			self.found_patterns.append(Pattern.desc_func_adj)
		else:
			self.found_patterns.append(Pattern.basic)

		if self.identify_parent(story):
			self.found_patterns.append(Pattern.parent)		

	def identify_desc_func_adj(self, story):
		if story.role.functional_role.compound:
			for token in story.role.functional_role.compound:
				if token.dep_ == 'compound':
					return True
		return False

	def identify_parent(self, story):
		if story.means.direct_object.compound:
			return True
		return False
		

class Pattern(Enum):
	link_to_US = 0
	basic = 1
	parent = 2
	desc_func_adj = 3
