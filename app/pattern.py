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
		weighted_tokens = WeightAttacher.make(self.user_stories, self.weights)
		pf = PatternFactory(self, weighted_tokens)

		self.onto = Ontology(ontname)
		pf.make_patterns(self.user_stories, threshold, link)

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
	def __init__(self, constructor, weighted_tokens):
		self.constructor = constructor
		self.weighted_tokens = weighted_tokens
	
	def make_patterns(self, user_stories, threshold, link):
		pi = PatternIdentifier(self.weighted_tokens)
		for us in user_stories:
			pi.identify(us, link)
		
		th_rel = self.apply_threshold(pi.relationships, threshold)
		unique_rel = self.unique_rel(th_rel)		
	
		print("UNIQUE")
		[Printer.print_rel(r) for r in unique_rel]
		print(len(th_rel), len(unique_rel))

		used_in_relationships = []

		for r in unique_rel:
			pre = NLPUtility.get_case(r[1])
			post = NLPUtility.get_case(r[3])
			if r[2] == Pattern.parent:
				self.constructor.onto.get_class_by_name(pre, post)
			used_in_relationships.append(pre)
			used_in_relationships.append(post)

		for wo in self.weighted_tokens:
			if wo.case not in used_in_relationships:
				if wo.weight >= threshold:
					self.constructor.onto.get_class_by_name(wo.case)
				#print(wo.case, wo.weight, "\t\t", wo.token.i)
		print([0, 'subject', 'relationship', 'object'])
		print(['us.number', 'WeightedToken(s)', 'Pattern', 'WeightedToken(s)'])
		###

		return self

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

		lt = wt[0].weight		
		for w in wt:
			if w.weight < lt:
				lt = w.weight

		return lt

	def get_weighted_tokens(self, relationship):
		wt = []

		if type(relationship[1]) is list:
			wt.extend(relationship[1])
		else:
			wt.append(relationship[1])
		if type(relationship[3]) is list:
			wt.extend(relationship[3])
		else:
			wt.append(relationship[3])

		return wt

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
		self.constructor.onto.get_class_by_name(nr, 'UserStory')
		
		for cl in self.constructor.onto.classes:
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
	'''

	def make_can_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'can')

	def make_has_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'has')

	def make_relationship(self, pre, rel, post, connector):
		self.constructor.onto.new_relationship(pre, connector + rel, post)	


class PatternIdentifier:
	def __init__(self, weighted_tokens):
		self.weighted_tokens = weighted_tokens
		self.relationships = []

	def identify(self, us, link_to_us):
		self.identify_compound(us)

		if link_to_us:
			pass

	def identify_compound(self, us):
		compounds = []
		if us.role.functional_role.compound:
			compounds.append(us.role.functional_role.compound[0])
		if us.means.direct_object.compound:
			compounds.append(us.means.direct_object.compound[0])
		if us.means.free_form:
			if type(us.means.compounds) is list:
				compounds.extend(us.means.compounds)
			elif len(us.means.compounds) > 0:
				compounds.append(us.means.compounds)
		if us.ends.free_form:
			if type(us.ends.compounds) is list:
				compounds.extend(us.ends.compounds)
			elif len(us.ends.compounds) > 0:
				compounds.append(us.ends.compounds)

		if compounds:
			for c in compounds:
				self.relationships.append([us.number, [self.getwt(c[0]), self.getwt(c[1])], Pattern.parent, self.getwt(c[1])])

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
