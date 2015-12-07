import string
import numpy as np
import pandas
from enum import Enum

from app.ontologygenerator import Generator, Ontology
from app.utility import NLPUtility, Printer

class Constructor:
	def __init__(self, nlp, user_stories, matrix):
		self.nlp = nlp
		self.user_stories = user_stories
		self.weights = matrix['sum'].reset_index().values.tolist()

	def make(self, ontname, threshold, link):
		weighted_tokens = WeightAttacher.make(self.user_stories, 
self.weights)

		self.onto = Ontology(ontname)
		pf = PatternFactory(self.onto, weighted_tokens)
		self.onto = pf.make_patterns(self.user_stories, threshold, link)
		
		#for c in self.onto.classes:		
		#	print("\"" + c.name + "\"", "\"" + c.parent + "\"")

		g = Generator(self.onto.classes, self.onto.relationships)
		
		return g.prt(self.onto)
		
	'''	
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
	'''

class WeightedToken(object):
	def __init__(self, token, weight):
		self.token = token
		self.case = NLPUtility.case(token)
		self.weight = weight


class WeightAttacher:
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
	def __init__(self, onto, weighted_tokens):
		self.onto = onto
		self.weighted_tokens = weighted_tokens

	def make_patterns(self, user_stories, threshold, link):
		pi = PatternIdentifier(self.weighted_tokens)

		for us in user_stories:
			pi.identify(us, link)
		
		th_rel = self.apply_threshold(pi.relationships, threshold)
		unique_rel = self.unique_rel(th_rel)		

		self.create_spare_classes(unique_rel, threshold)

		return self.onto

	def unique_rel(self, relationships):
		rel = []
		wt_pairs = []
		new_pairs = []
		s = ""
		o = ""

		for r in relationships:
			s = NLPUtility.get_case(r[1])
			o = NLPUtility.get_case(r[3])
			wt_pairs.append([s, r[2].name, o, r])
	
		for r in wt_pairs:
			if [r[0], r[1], r[2]] not in new_pairs:
				new_pairs.append([r[0], r[1], r[2]])
				rel.append(r[3])

		return rel

	def apply_threshold(self, relationships, threshold):
		rel = []

		for r in relationships:
			if self.get_lowest_threshold(r) >= threshold:
				rel.append(r)
		
		return rel

	def get_lowest_threshold(self, relationship):
		wt = self.get_weighted_tokens(relationship)
		lt = 1000.0

		if wt:		
			lt = wt[0].weight
			for w in wt:
				if w.weight < lt:
					lt = w.weight

		return lt

	def get_weighted_tokens(self, relationship):
		wt = []

		if type(relationship[1]) is list:
			wt.extend(relationship[1])
		elif type(relationship[1]) is WeightedToken:
			wt.append(relationship[1])
		if type(relationship[3]) is list:
			wt.extend(relationship[3])
		elif type(relationship[3]) is WeightedToken:
			wt.append(relationship[3])

		return wt

	def create_spare_classes(self, relationships, threshold):
		used = []

		for r in relationships:
			pre = NLPUtility.get_case(r[1])
			post = NLPUtility.get_case(r[3])
			if r[2] == Pattern.parent:
				self.onto.get_class_by_name(pre, post)
			used.append(pre)
			used.append(post)

		for wo in self.weighted_tokens:
			if wo.case not in used:
				if wo.weight >= threshold:
					self.onto.get_class_by_name(wo.case)

	'''
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
	'''

	def link(self, us):
		nr = us.txtnr()
		self.onto.get_class_by_name(nr, 'UserStory')
		
		for cl in self.onto.classes:
			self.make_relationship(cl.name, nr, nr, 'partOf')			

	'''
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
	'''

	def make_can_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'can')

	def make_has_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'has')

	def make_relationship(self, pre, rel, post, connector):
		self.onto.new_relationship(pre, connector + rel, post)	


class PatternIdentifier:
	def __init__(self, weighted_tokens):
		self.weighted_tokens = weighted_tokens
		self.relationships = []
		self.func_role = False

	def identify(self, us, link_to_us):
		self.identify_compound(us)
		self.identify_func_role(us)

		if link_to_us:
			pass

		if self.func_role:
			self.relationships.append([-1, 'FunctionalRole', Pattern.parent, 'Person'])

	def identify_compound(self, us):
		compounds = []
		if us.role.functional_role.compound:
			compounds.append(us.role.functional_role.compound)
		if us.means.direct_object.compound:
			compounds.append(us.means.direct_object.compound)
		if us.means.free_form:
			if type(us.means.compounds) is list and len(us.means.compounds) > 0 and type(us.means.compounds[0]) is list:
				compounds.extend(us.means.compounds)
			elif len(us.means.compounds) > 0:
				compounds.append(us.means.compounds)
		if us.ends.free_form:
			if type(us.ends.compounds) is list and len(us.ends.compounds) > 0 and type(us.ends.compounds[0]) is list:
				compounds.extend(us.ends.compounds)
			elif len(us.ends.compounds) > 0:
				compounds.append(us.ends.compounds)

		if compounds:
			for c in compounds:
				self.relationships.append([us.number, [self.getwt(c[0]), self.getwt(c[1])], Pattern.parent, self.getwt(c[1])])

	def identify_func_role(self, us):
		role = []
		has_parent = False

		if us.role.functional_role.compound:
			for c in us.role.functional_role.compound:
				role.append(self.getwt(c))
		else:
			role.append(self.getwt(us.role.functional_role.main))
		
		is_subj = self.is_subject(role)
		
		# Checks if the functional role already has a parent, and then makes this parent the child for 'FunctionalRole'
		if is_subj[0]:
			for i in is_subj[1]:
				if i[1] == Pattern.parent:
					role = i[2]

		self.relationships.append([us.number, role, Pattern.parent, 'FunctionalRole'])
		self.func_role = True			

	def is_subject(self, weighted_tokens):
		is_subj = False
		subjects = []

		for r in self.relationships:
			if type(r[1]) is list and type(weighted_tokens) is list:
				case = ""
				case_w = ""
				for i in r[1]:
					case += i.case
				for j in weighted_tokens:
					case_w += j.case
				if i == j:
					subjects.append([r[1], r[2], r[3]])
					is_subj = True														
			if type(r[1]) is str and type(weighted_tokens) is str:
				if r[1] == weighted_tokens:
					subjects.append([r[1], r[2], r[3]])
					is_subj = True					
			if type(r[1]) is WeightedToken and type(weighted_tokens) is WeightedToken:
				if r[1].case == weighted_tokens.case:
					subjects.append([r[1], r[2], r[3]])
					is_subj = True

		return is_subj, subjects	

	def getwt(self, token):
		for wt in self.weighted_tokens:
			if token == wt.token:
				return wt
		self.weighted_tokens.append(WeightedToken(token, 0.0))
		return self.getwt(token)
		

class Pattern(Enum):
	link_to_US = 0
	basic = 1
	parent = 2
	desc_func_adj = 3
