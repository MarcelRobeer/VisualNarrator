from lang.owlprefix import PREFIX_DICT

class Generator:
	def __init__(self, classes, relationships, is_long=None):
		self.classes = classes
		self.relationships = relationships
		self.long = is_long

	def prt(self, onto): 
		if self.long is None:
			li = self.gen_ontology(onto)
		else:
			li = self.gen_ontology(onto)
		return li	
		
	def gen_ontology(self, onto):
		ontologytext = ''
		rellist = []
		clist = []		
		ontologytext += onto.gen_head(onto.get_prefixes()).prt() + "\n"

		if self.relationships:
			ontologytext += onto.gh.comment("Relationships")

		for r in self.relationships:
			ontologytext += r.prt() + "\n"

		if self.classes:
			ontologytext += onto.gh.comment("Classes")

		for c in self.classes:
			ontologytext += c.prt() + "\n"

		return ontologytext


class GenHelp:
	def __init__(self, ontology, option=None):
		self.ontology = ontology
		self.option = option

	def make_prefix(self, indicator, link):
		return "Prefix: " + indicator + ": <" + link + ">\n" 
	
	def make_obj(self, name, prefix='', isname=None):
		if not self.option:
			return prefix + ":" + name + "\n"	
		else:
			if prefix is '':
				prefix = self.ontology
			else:
				prefix = PREFIX_DICT[prefix]
			return "<" + prefix + name + ">\n"

	def make_part(self, left, right):
		return "\t" + left + ": " + right

	def space(self):
		return ""

	def comment(self, com):
		return "# " + com + "\n"

class Ontology:
	def __init__(self, ontology_name, option=None):
		self.ontology = ontology_name
		self.ontology_name = "onto"
		self.option = option
		self.gh = GenHelp(self.ontology, option)
		self.classes = []
		self.relationships = []

	def gen_head(self, parts):
		return Header(self, parts)

	def get_prefixes(self):
		return [str(c.prefix) for c in self.classes]

	def make_class(self, name, parent="Thing", prefix=''):
		new_class = OntClass(self, name, parent, prefix)
		return new_class
	
	def make_relationship(self, name, domain, range):
		new_property = OntProperty(self, "Object", name, domain, range)
		return new_property
	'''OLD
	def get_class_by_name(self, name, parent='', isp=False):
		appendclass=True

		if name.isspace():
			appendclass=False

		if self.classes:
			for c in self.classes:
				if str.lower(name) == str.lower(c.name) and str.lower(parent) == str.lower(c.parent):
					appendclass=False
					return c
				elif str.lower(name) == str.lower(c.name) and c.parent.isspace() and not parent.isspace() and not isp:
					self.classes.remove(c)

		if parent.isspace():
			parent = ''

		new_class = self.make_class(name, parent)
		if appendclass:
			self.classes.append(new_class)		

		if not isp:
			parent_class = self.get_class_by_name(parent, '', True)
			self.classes.append(parent_class)
	
		return new_class
	'''

	def get_class_by_name(self, name, parent=''):
		if self.is_empty(name):
			return False

		if self.classes:
			for c in self.classes:
				if str.lower(name) == str.lower(c.name) and str.lower(parent) == str.lower(c.parent):
					return c
				elif str.lower(name) == str.lower(c.name) and not self.is_empty(parent):
					self.classes.remove(c)
		
		new_class = self.make_class(name, parent)
		self.classes.append(new_class)

		if not self.is_empty(parent):
			parent_class = self.get_class_by_name(parent, '')
			
		return new_class

	def is_empty(self, word):
		if word.isspace() or word == '':
			return True
		return False

	def new_relationship(self, pre, rel, post):
		if self.relationships:
			for r in self.relationships:
				if r.domain == pre and r.name == rel and r.range == post:
					return r

		new_rel = self.make_relationship(rel, pre, post)
		self.relationships.append(new_rel)
		return new_rel


class OntClass(object):
	def __init__(self, ontology, name, parent, prefix=''):
		self.ontobj = ontology
		self.name = name
		self.parent = parent
		self.prefix = prefix

	def prt(self):
		returnstr = ""
		returnstr += "Class: " + self.ontobj.gh.make_obj(self.name)
		if self.parent == "Thing" or self.parent == '':
			pass			
		else:
			returnstr += self.ontobj.gh.make_part("SubClassOf", self.ontobj.gh.make_obj(self.parent, self.prefix))
		return returnstr

class OntProperty(object):
	def __init__(self, ontology, type, name, domain, range):
		self.ontobj = ontology
		self.type = type
		self.name = name
		self.domain = domain
		self.range = range

	def prt(self):
		returnstr = ""
		returnstr += self.type + "Property: " + self.ontobj.gh.make_obj(self.name)
		returnstr += self.ontobj.gh.make_part("Domain", self.ontobj.gh.make_obj(self.domain))
		returnstr += self.ontobj.gh.make_part("Range", self.ontobj.gh.make_obj(self.range))
		return returnstr

class Header:
	def __init__(self, ontology, used_prefixes):
		self.ontobj = ontology
		self.standard_prefixes = ['owl', 'rdf', 'rdfs', 'xsd']
		self.used_prefixes = self.standard_prefixes + used_prefixes

	def prt(self):
		returnstr = ""
		returnstr += self.ontobj.gh.comment("Generated with PROGRAM_NAME")
		returnstr += self.ontobj.gh.make_prefix('', self.ontobj.ontology)
		for prefix in self.used_prefixes:
			if prefix is not '':
				link = str(PREFIX_DICT[prefix])
				returnstr += self.ontobj.gh.make_prefix(prefix, link)
		returnstr += self.ontobj.gh.make_prefix(self.ontobj.ontology_name, self.ontobj.ontology)	
		if self.ontobj.option is not None:
			returnstr += "\nOntology: <" + self.ontobj.ontology + ">"
		return returnstr	

	
