from lang.owlprefix import PREFIX_DICT

class Generator:
	def __init__(self, classes, relationships, onto=True, is_long=None):
		self.classes = classes
		self.relationships = relationships
		self.long = is_long
		self.onto = onto

	def prt(self, onto): 
		for c in self.classes:
			c.stories.sort()

		if not self.onto:
			return self.gen_prolog_from_onto()

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

		unique_rels = self.make_unique_relationships()

		for r in unique_rels:	
			ontologytext += r.prt() + "\n"

		if self.classes:
			ontologytext += onto.gh.comment("Classes")

		for c in self.classes:
			ontologytext += c.prt() + "\n"

		return ontologytext

	def make_unique_relationships(self):
		rel_names = set([r.name for r in self.relationships])
		new_rels = []

		for rn in rel_names:
			rels_of_name = []
			pairs = []
			cnt = 1

			for r in self.relationships:
				if r.name == rn:
					if [r.domain, r.range] not in pairs:
						rels_of_name.append(r)
						pairs.append([r.domain, r.range])

			if len(rels_of_name) > 1:
				for ron in rels_of_name:
					new_relationship = OntProperty(ron.ontobj, "Object", ron.name + str(cnt), ron.domain, ron.range)
					new_relationship.stories = ron.stories
					new_rels.append(new_relationship)
					cnt += 1

			else:
				for r in self.relationships:
					if r.name == rn:
						new_rels.append(r)		

		return new_rels

	def gen_prolog_from_onto(self):
		prologtext = []
		concept = ""

		for c in self.classes:
			concept = self.get_concept(c.name)
			prologtext.append(concept)
			for s in c.stories:
				if self.get_found(concept, s):
					prologtext.append(self.get_found(concept, s))

		for r in self.relationships:
			d_concept = self.get_concept(r.domain)
			r_concept = self.get_concept(r.range)
			rel = ""
			linkrel = ['role', 'means', 'ends']
			diffrel = linkrel + ['isa']

			if str.lower(r.name) in diffrel:
				if str.lower(r.name) in linkrel:
					prologtext.append(str.lower(r.name) + "(" + d_concept + ",'" + r.range + "')")				
				else:
					prologtext.append(str.lower(r.name) + "(" + d_concept + "," + r_concept + ")")
			else:
				rel = "rel(" + d_concept + ",'" + r.name + "'," + r_concept + ")"
				prologtext.append(rel)
				for s in r.stories:
					if self.get_found(rel, s):
						prologtext.append(self.get_found(rel, s))

		prologtext.sort()

		return '.\n'.join(prologtext)

	def get_concept(self, text):
		return "concept('" + str(text) + "')"

	def get_found(self, text, story):
		if story >= 0:
			return "found(" + text + ",'US" + str(story) + "')"
		return False


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
	def __init__(self, sysname, stories, option=None):
		self.sys_name = sysname
		self.ontology = "http://fakesite.org/" + "_".join(str(sysname).lower().split()) + ".owl#"
		self.ontology_name = "onto"
		self.option = option
		self.gh = GenHelp(self.ontology, option)
		self.stories = stories
		self.classes = []
		self.relationships = []

	def gen_head(self, parts):
		return Header(self, parts)

	def get_prefixes(self):
		return [str(c.prefix) for c in self.classes]

	def make_class(self, name, parent="Thing", prefix=''):
		return OntClass(self, name, parent, prefix)
	
	def make_relationship(self, name, domain, range):
		new_property = OntProperty(self, "Object", name, domain, range)
		return new_property

	def get_class_by_name(self, story, name, parent='', is_role=False):		
		if self.is_empty(name):
			return False

		c_stories = []

		if self.classes:
			for c in self.classes:
				if str.lower(name) == str.lower(c.name) and (str.lower(parent) == str.lower(c.parent) or (self.is_empty(parent) and self.is_empty(c.parent))):
					if is_role:
						c.is_role = True
					c.stories.append(story)
					return c
				if str.lower(name) == str.lower(c.name) and not self.is_empty(c.parent) and self.is_empty(parent):
					if is_role:
						c.is_role = True
					c.stories.append(story)
					return c
				if str.lower(name) == str.lower(c.name) and not self.is_empty(parent):
					c_stories = c.stories
					self.classes.remove(c)

		new_class = self.make_class(name, parent)
		if is_role:
			new_class.is_role = True
		new_class.stories = c_stories
		new_class.stories.append(story)
		self.classes.append(new_class)

		if not self.is_empty(parent):
			parent_class = self.get_class_by_name(-1, parent, '')
			
		return new_class

	def is_empty(self, word):
		if word.isspace() or word == '':
			return True
		return False

	def new_relationship(self, story, pre, rel, post):
		if self.relationships:
			for r in self.relationships:
				if r.domain == pre and r.name == rel and r.range == post:
					r.stories.append(story)
					return r

		new_rel = self.make_relationship(rel, pre, post)
		new_rel.stories.append(story)
		self.relationships.append(new_rel)
		return new_rel


class OntClass(object):
	def __init__(self, ontology, name, parent, prefix=''):
		self.ontobj = ontology
		self.name = name
		self.parent = parent
		self.prefix = prefix
		self.stories = []
		self.is_role = False

	def prt(self):
		name = ''.join(self.name.split())
		parent = ''.join(self.parent.split())

		returnstr = ""
		returnstr += "Class: " + self.ontobj.gh.make_obj(name)
		if self.parent == "Thing" or self.parent == '':
			pass			
		else:
			returnstr += self.ontobj.gh.make_part("SubClassOf", self.ontobj.gh.make_obj(parent, self.prefix))

		if self.name != name or self.is_role:
			returnstr += "\tAnnotations:"
		if self.name != name:
			returnstr += "\n\t\trdfs:label \"%s\"" % (self.name)
		if self.name != name and self.is_role:
			returnstr += ","
		if self.is_role:
			returnstr += "\n\t\trdfs:comment \"Functional Role\""
		returnstr += "\n"

		return returnstr

	def set_role(self):
		self.is_role = True

class OntProperty(object):
	def __init__(self, ontology, type, name, domain, range):
		self.ontobj = ontology
		self.type = type
		self.name = name
		self.domain = domain
		self.range = range
		self.stories = []

	def prt(self):
		name = ''.join(self.name.split())
		domain = ''.join(self.domain.split())
		range = ''.join(self.range.split())

		returnstr = ""
		returnstr += self.type + "Property: " + self.ontobj.gh.make_obj(name)
		returnstr += self.ontobj.gh.make_part("Domain", self.ontobj.gh.make_obj(domain))
		returnstr += self.ontobj.gh.make_part("Range", self.ontobj.gh.make_obj(range))
		return returnstr

class Header:
	def __init__(self, ontology, used_prefixes):
		self.ontobj = ontology
		self.standard_prefixes = ['owl', 'rdf', 'rdfs', 'xsd', 'dc']
		self.used_prefixes = self.standard_prefixes + used_prefixes

	def prt(self):
		returnstr = ""
		returnstr += self.ontobj.gh.comment("Generated with Visual Narrator")
		returnstr += self.ontobj.gh.make_prefix('', self.ontobj.ontology)
		for prefix in self.used_prefixes:
			if prefix is not '':
				link = str(PREFIX_DICT[prefix])
				returnstr += self.ontobj.gh.make_prefix(prefix, link)
		returnstr += self.ontobj.gh.make_prefix(self.ontobj.ontology_name, self.ontobj.ontology)	
		returnstr += "\nOntology: <:>\n\n"
		returnstr += "Annotations:\n\tdc:title \"" + str(self.ontobj.sys_name) + "\",\n\tdc:creator \"Visual Narrator\",\n\trdfs:comment \"Generated with Visual Narrator\"\n\n"
		returnstr += "AnnotationProperty: dc:creator\n\n"
		returnstr += "AnnotationProperty: dc:title\n\n"
		return returnstr	

	
