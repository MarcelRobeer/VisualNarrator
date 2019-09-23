"""Generate Ontology / Prolog from extracted classes and relationships in `vn.pattern`"""

from lang.owlprefix import PREFIX_DICT

class Generator:
    """Generate text conceptual models from a list of classes and a list of relationships (in `Ontology` object)"""
    def __init__(self, onto, is_long=None):
        """
        Args:
            onto (`Ontology`): ontology object
        """
        self.onto = onto
        self.classes = onto.classes
        self.relationships = onto.relationships
        self.long = is_long

    def _make_unique_relationships(self):
        rel_names = set([r.name for r in self.relationships])
        new_rels = []

        for rn in rel_names:
            rels_of_name = []
            pairs = []

            for r in self.relationships:
                if r.name == rn:
                    if [r.domain, r.range] not in pairs:
                        rels_of_name.append(r)
                        pairs.append([r.domain, r.range])

            if len(rels_of_name) > 1:
                for i, ron in enumerate(rels_of_name, start=1):
                    new_relationship = OntProperty(ron.ontobj, "Object", ron.name + str(i), ron.domain, ron.range)
                    new_relationship.stories = ron.stories
                    new_rels.append(new_relationship)
            else:
                for r in self.relationships:
                    if r.name == rn:
                        new_rels.append(r)        

        return new_rels


class OntologyGenerator(Generator):
    """Generate Manchester-style ontology from an `Ontology` object"""
    
    def __str__(self):
        for c in self.classes:
            c.stories.sort()
        
        ontologytext = ''
        ontologytext += self.onto.gen_head(self.onto.get_prefixes()).prt() + "\n"

        if self.relationships:
            ontologytext += self.onto._comment("Relationships")

        unique_rels = self._make_unique_relationships()

        for r in unique_rels:    
            ontologytext += r.prt() + "\n"

        if self.classes:
            ontologytext += self.onto._comment("Classes")

        for c in self.classes:
            ontologytext += c.prt() + "\n"

        return ontologytext


class PrologGenerator(Generator):
    """Generate Prolog from `Ontology` object"""

    def __str__(self):
        prologtext = []
        concept = ""

        for c in self.classes:
            concept = self._get_concept(c.name)
            prologtext.append(concept)
            for s in c.stories:
                if self._get_found(concept, s):
                    prologtext.append(self._get_found(concept, s))

        for r in self.relationships:
            d_concept = self._get_concept(r.domain)
            r_concept = self._get_concept(r.range)
            rel = ""
            linkrel = ['role', 'means', 'ends']
            diffrel = linkrel + ['isa']

            if str.lower(r.name) in diffrel:
                if str.lower(r.name) in linkrel:
                    prologtext.append(f"{str.lower(r.name)}({d_concept},'{r.range}')")                
                else:
                    prologtext.append(f"{str.lower(r.name)}({d_concept},{r_concept})")
            else:
                rel = f"rel({d_concept},'{r.name}',{r_concept})"
                prologtext.append(rel)
                for s in r.stories:
                    if self._get_found(rel, s):
                        prologtext.append(self._get_found(rel, s))

        prologtext = list(set(prologtext))
        prologtext.sort()

        return '.\n'.join(prologtext) + '.'

    def _get_concept(self, text):
        return f"concept('{str(text)}')"

    def _get_found(self, text, story):
        if story >= 0:
            return f"found({text},'US{str(story)}')"
        return False
    

class Ontology:
    """Holds information on the ontology to construct"""

    def __init__(self, sysname, stories, option=None):
        self.sys_name = sysname
        self.ontology = "http://fakesite.org/{}.owl#".format("_".join(str(sysname).lower().split()))
        self.ontology_name = "onto"
        self.option = option
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
        return OntProperty(self, "Object", name, domain, range)

    def get_class_by_name(self, story, name, parent='', is_role=False):        
        if self.is_empty(name):
            return False

        c_stories = []

        if self.classes:
            for c in self.classes:
                if ((str.lower(name) == str.lower(c.name) and (str.lower(parent) == str.lower(c.parent) or (self.is_empty(parent) and self.is_empty(c.parent)))) or 
                        (str.lower(name) == str.lower(c.name) and not self.is_empty(c.parent) and self.is_empty(parent))):
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
    
    def _make_prefix(self, indicator, link):
        return f"Prefix: {indicator}: <{link}>\n" 
    
    def _make_obj(self, name, prefix='', isname=None):
        if not self.option:
            return f"{prefix}:{name}\n"    
        else:
            if prefix is '':
                prefix = self.ontology
            else:
                prefix = PREFIX_DICT[prefix]
            return f"<{prefix}{name}>\n"

    def _make_part(self, left, right):
        return f"\t{left}: {right}"

    def _space(self):
        return ""

    def _comment(self, com):
        return f"# {com}\n"


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
        returnstr += "Class: " + self.ontobj._make_obj(name)
        if self.parent == "Thing" or self.parent == '':
            pass            
        else:
            returnstr += self.ontobj._make_part("SubClassOf", self.ontobj._make_obj(parent, self.prefix))

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
        returnstr += self.type + "Property: " + self.ontobj._make_obj(name)
        returnstr += self.ontobj._make_part("Domain", self.ontobj._make_obj(domain))
        returnstr += self.ontobj._make_part("Range", self.ontobj._make_obj(range))
        return returnstr

class Header:
    def __init__(self, ontology, used_prefixes):
        self.ontobj = ontology
        self.standard_prefixes = ['owl', 'rdf', 'rdfs', 'xsd', 'dc']
        self.used_prefixes = self.standard_prefixes + used_prefixes

    def prt(self):
        returnstr = ""
        returnstr += self.ontobj._comment("Generated with Visual Narrator")
        returnstr += self.ontobj._make_prefix('', self.ontobj.ontology)
        for prefix in self.used_prefixes:
            if prefix is not '':
                link = str(PREFIX_DICT[prefix])
                returnstr += self.ontobj._make_prefix(prefix, link)
        returnstr += self.ontobj._make_prefix(self.ontobj.ontology_name, self.ontobj.ontology)    
        returnstr += "\nOntology: <:>\n\n"
        returnstr += "Annotations:\n\tdc:title \"" + str(self.ontobj.sys_name) + "\",\n\tdc:creator \"Visual Narrator\",\n\trdfs:comment \"Generated with Visual Narrator\"\n\n"
        returnstr += "AnnotationProperty: dc:creator\n\n"
        returnstr += "AnnotationProperty: dc:title\n\n"
        return returnstr
