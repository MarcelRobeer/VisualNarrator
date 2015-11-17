import string
from enum import Enum

from app.ontologygenerator import Generator, Ontology

class Constructor:
	def __init__(self, nlp, user_stories):
		self.nlp = nlp
		self.user_stories = user_stories

	def make(self, ontname):
		pf = PatternFactory(self)

		self.onto = Ontology(ontname)

		for us in self.user_stories:
			pf.make_patterns(us)

		g = Generator(self.onto.classes, self.onto.relationships)
		
		return g.prt(self.onto)
			
	def get_main_verb(self, us):
		if not us.means.main_verb.phrase:
			av = self.case(us.means.main_verb.main)
		else:
			av = self.make_multiword_string(us.means.main_verb.phrase)	

		return av

	def get_direct_object(self, us):
		if not us.means.direct_object.compound:
			do = self.case(us.means.direct_object.main)
		else:
			print(us.means.direct_object.compound)
			do = self.make_multiword_string(us.means.direct_object.compound)

		return do

	def make_multiword_string(self, span):
		ret = ""
		
		for token in span:
			ret += self.case(token)

		return ret

	def case(self, token):
		if 'd' in token.shape_ or 'x' not in token.shape_:			
			return token.text
		return string.capwords(token.lemma_)
	
	def t(self, token):
		return token.main.text


class PatternFactory:
	def __init__(self, constructor):
		self.constructor = constructor

	def make_patterns(self, us):
		pi = PatternIdentifier()
		pi.identify_patterns(us)

		# WIP Prints all patterns that are found
		#print("US", us.number, ">", pi.found_patterns)

		self.constructor.onto.get_class_by_name('Person')
		self.constructor.onto.get_class_by_name('FunctionalRole', 'Person')

		for fp in pi.found_patterns:
			self.construct_pattern(us, fp)

		return self

	def construct_pattern(self, us, pattern):
		action_v = self.constructor.get_main_verb(us)		
		direct_obj = self.make_direct_object(us)

		if pattern == Pattern.desc_func_adj:
			func_role = self.make_subtype_functional_role(us)
		else:
			func_role = self.make_functional_role(us)


	def make_subtype_functional_role(self, us):
		func_role = string.capwords(us.role.functional_role.main.lemma_)
		subtype = ""		
		compound_noun = []

		for token in us.role.functional_role.compound:
			compound_noun.append(token)

		self.constructor.make_multiword_string(compound_noun)

		self.constructor.onto.get_class_by_name(func_role, 'FunctionalRole')
		self.constructor.onto.get_class_by_name(subtype + func_role, func_role)
		self.constructor.onto.get_class_by_name(subtype)
		self.make_has_relationship(subtype, func_role, subtype + func_role)
		self.make_can_relationship(subtype + func_role, self.constructor.get_main_verb(us), self.constructor.get_direct_object(us))

		return func_role

	def make_functional_role(self, us):
		func_role = self.constructor.case(us.role.functional_role.main)
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

	def identify_patterns(self, story):
		if self.identify_desc_func_adj(story):
			self.found_patterns.append(Pattern.desc_func_adj)
		else:
			self.found_patterns.append(Pattern.basic)		

	def identify_desc_func_adj(self, story):
		if story.role.functional_role.compound:
			for token in story.role.functional_role.compound:
				if token.dep_ == 'compound':
					return True
		return False

class Pattern(Enum):
	basic = 0
	desc_func_adj = 1
