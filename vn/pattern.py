"""Mine patterns in `vn.userstory.UserStory` and construct Ontology / Prolog file"""

import string
import numpy as np
import copy
from enum import Enum

from vn.generator import Ontology, OntologyGenerator, PrologGenerator
from vn.io import Printer
from vn.utils.utility import is_sublist, flatten
from vn.utils.nlputility import WeightedToken, get_case

class Constructor:
    def __init__(self, nlp, user_stories, matrix):
        self.nlp = nlp
        self.user_stories = user_stories
        self.weights = matrix['sum'].reset_index().values.tolist()

    def make(self, ontname, threshold, link):
        weighted_tokens = WeightAttacher.make(self.user_stories, self.weights)
        
        self.onto = Ontology(ontname, self.user_stories)
        self.prolog = Ontology(ontname, self.user_stories)

        pf = PatternFactory(self.onto, self.prolog, weighted_tokens)
        self.onto = pf.make_patterns(self.user_stories, threshold)
        self.prolog = pf.prolog

        if link:
            self.link_to_story(self.onto.classes, self.user_stories)

        per_role_out = []
        per_role_onto = self.get_per_role(self.user_stories, link)

        for p in per_role_onto:
            per_role_out.append([p[0].replace('/','_'), str(p[1])])

        return (OntologyGenerator(self.onto),
                PrologGenerator(self.prolog),
                per_role_out)

    def link_to_story(self, classes, stories):    
        used_stories = []

        for cl in classes:
            for story in cl.stories:
                if story >= 0:
                    s = self.get_story(int(story), stories)
                    parts = self.get_parts(cl.name, s)

                    #for part in part_name:
                    #    n = s.txtnr() + part
                    #    self.onto.get_class_by_name(-1, n, s.txtnr())
                    #    self.onto.new_relationship(-1, cl.name, cl.name + 'OccursIn' + n, n)
                    self.onto.new_relationship(-1, cl.name, cl.name + 'OccursIn' + s.txtnr(), s.txtnr())

                    for part in parts:                    
                        self.prolog.new_relationship(-1, cl.name, part, s.txtnr())

                    used_stories.append(s.txtnr())
        
        for story in used_stories:
            self.onto.get_class_by_name(-1, story, 'UserStory')

    def get_per_role(self, stories, link):    
        roles_link = []
        roles = []
        stories_per_role = []
        per_role_ontos = []

        # Get a list of roles and a list where the stories are linked to their roles
        for story in self.user_stories:
            roles_link.append([story.role.t, story.number])
            if str.lower(story.role.t) not in [str.lower(s) for s in roles]:
                roles.append(story.role.t)

        # Get a list of stories per role and get the generator object for these stories
        for role in roles:
            stories_per_role = []
            for link in roles_link:
                if str.lower(role) == str.lower(link[0]):
                    stories_per_role.append(link[1])

            per_role_ontos.append([role, self.get_generator(role, stories_per_role, link)])

        return per_role_ontos

    def get_generator(self, role, spr, link):        
        role_classes = []
        role_relationships = []
        cl_names = []

        # Get classes
        for cl in self.onto.classes:
            for story in cl.stories:
                if story >= 0 and story in spr and cl.name not in cl_names:
                    role_classes.append(cl)
                    cl_names.append(cl.name)
                    if cl.parent != '':
                        for cp in self.onto.classes:
                            if cp.name == cl.parent:
                                role_classes.append(cp)

            # Get the general classes
            if cl.stories[0] == -1:
                if cl.name == 'FunctionalRole' or cl.name == 'Person':
                    role_classes.append(cl)
        
        story_classes = []

        # Get all relationships belonging to these classes
        for rel in self.onto.relationships:
            for story in rel.stories:
                if rel.domain in cl_names and rel.range in cl_names and story in spr:
                    role_relationships.append(rel)

            # If 'link' add these classes too
            if link:
                for story in spr:
                    if rel.domain in cl_names and rel.range == 'US' + str(story):
                        role_relationships.append(rel)
                        story_classes.append(rel.range)

        # Retrieve all classes for the relationships created in link
        if link:
            for cl in self.onto.classes:
                for c in story_classes:
                    if cl.name == c:
                        role_classes.append(cl)
                if cl.name == 'UserStory':
                    role_classes.append(cl)

        onto = copy.copy(self.onto)
        onto.classes, onto.relationships = role_classes, role_relationships
        return OntologyGenerator(onto)

    def get_story(self, nr, stories):
        for story in stories:
            if nr == story.number:
                return story
        return False

    def get_parts(self, class_name, story):
        case = class_name.split()

        means_compounds = []
        means_compounds.append(story.means.main_object.compound)
        ends_compounds = flatten(story.ends.compounds)

        if story.means.free_form:
            if len(story.means.compounds) > 0:
                means_compounds.extend(flatten(story.means.compounds))

        role = []
        means = []
        ends = []
        rme = []

        for token in story.data:
            if token in story.role.text:
                if len(case) != 1:
                    role.append(get_case(token))
                elif token not in story.role.functional_role.compound:
                    role.append(get_case(token))
            if token in story.means.text:
                if len(case) != 1:
                    means.append(get_case(token))
                elif token not in means_compounds:
                    means.append(get_case(token))
            if story.has_ends:
                if token in story.ends.text:
                    if len(case) != 1:
                        ends.append(get_case(token))
                    elif token not in ends_compounds:
                        ends.append(get_case(token))

        if is_sublist(case, role):
            rme.append('Role')

        if is_sublist(case, means):
            rme.append('Means')

        if is_sublist(case, ends):
            rme.append('Ends')

        return rme
            
                    
class WeightAttacher:
    @staticmethod
    def make(stories, weights):
        weighted_tokens = []
        indices = [weight[0] for weight in weights]
        w = 0.0
        c = ""

        for story in stories:
            if story.has_ends:
                parts = ['role', 'means', 'ends']
            else:
                parts = ['role', 'means']

            for part in parts:
                for token in eval('story.' + str(part) + '.text'):
                    c = get_case(token)
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
    def __init__(self, onto, prolog, weighted_tokens):
        self.onto = onto
        self.prolog = prolog
        self.weighted_tokens = weighted_tokens
        self.sysname = ""

    def make_patterns(self, user_stories, threshold):
        pi = PatternIdentifier(self.weighted_tokens)
        self.sysname = str.lower(get_case(user_stories[0].system.main))
        
        for story in user_stories:
            pi.identify(story)
        
        relationships = self.apply_threshold(pi.relationships, threshold)

        self.create(relationships, user_stories, threshold, pi.roles)

        return self.onto

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
                if str.lower(get_case(w)) != self.sysname and w.weight < lt: # Exclude system name object from filter
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

    def create(self, relationships, stories, threshold, roles):
        used = []

        for r in relationships:
            pre = get_case(r[1])
            post = get_case(r[3])

            if r[2] == Pattern.parent:
                self.onto.get_class_by_name(r[0], pre, post)
                self.prolog.new_relationship(r[0], pre, 'isa', post)

            if r[2] != Pattern.parent:
                rel = get_case(r[4])

            if r[2] == Pattern.subj_dobj or r[2] == Pattern.compound_has:
                self.onto.get_class_by_name(r[0], pre)
                self.onto.get_class_by_name(r[0], post)
                self.prolog.new_relationship(r[0], pre, rel, post)

                if r[2] == Pattern.subj_dobj:
                    self.make_can_relationship(r[0], pre, rel, post)
                else:
                    self.make_has_relationship(r[0], pre, rel, post)

            self.prolog.get_class_by_name(r[0], pre)
            self.prolog.get_class_by_name(r[0], post)

            used.append(pre)
            used.append(post)

        for wo in self.weighted_tokens:
            if wo.weight >= threshold:
                in_stories = self.find_story(wo, stories)
                for in_story in in_stories:
                    self.onto.get_class_by_name(in_story, wo.case)

        for r in roles:
            self.onto.get_class_by_name(r[0], get_case(r[1]), '', True)

    def make_can_relationship(self, story, pre, rel, post):
        self.make_relationship(story, pre, rel, post, 'can')

    def make_has_relationship(self, story, pre, rel, post):
        self.make_relationship(story, pre, rel, post, 'has')

    def make_relationship(self, story, pre, rel, post, connector):
        self.onto.new_relationship(story, pre, connector + rel, post)    

    def find_story(self, w_token, stories):
        nrs = []
        for story in stories:
            if w_token.case in [get_case(t) for t in story.data]:
                nrs.append(story.number)
        return nrs


class PatternIdentifier:
    def __init__(self, weighted_tokens):
        self.weighted_tokens = weighted_tokens
        self.relationships = []
        self.roles = []

    def identify(self, story):
        self.identify_compound(story)
        self.identify_func_role(story)
        self.identify_subj_dobj(story)
        if story.has_ends:
            self.identify_subj_dobj(story, 'ends')
        self.identify_dobj_conj(story)

    def identify_compound(self, story):
        compounds = []

        if story.role.functional_role.compound:
            compounds.append(story.role.functional_role.compound)
        if story.means.main_object.compound:
            compounds.append(story.means.main_object.compound)
        if story.means.free_form:
            if type(story.means.compounds) is list and len(story.means.compounds) > 0 and type(story.means.compounds[0]) is list:
                compounds.extend(story.means.compounds)
            elif len(story.means.compounds) > 0:
                compounds.append(story.means.compounds)
        if story.ends.free_form:
            if type(story.ends.compounds) is list and len(story.ends.compounds) > 0 and type(story.ends.compounds[0]) is list:
                compounds.extend(story.ends.compounds)
            elif len(story.ends.compounds) > 0:
                compounds.append(story.ends.compounds)

        if compounds:
            ## C5
            for c in compounds:
                self.relationships.append([story.number, [self.getwt(c[0]), self.getwt(c[1])], Pattern.parent, self.getwt(c[1])])

                ## R4
                if c[0].head == c[1]:
                    self.relationships.append([story.number, self.getwt(c[0]), Pattern.compound_has, [self.getwt(c[0]), self.getwt(c[1])], self.getwt(c[1])])

    def identify_func_role(self, story):
        role = []
        has_parent = False

        if story.role.functional_role.compound:
            for c in story.role.functional_role.compound:
                role.append(self.getwt(c))
        else:
            role.append(self.getwt(story.role.functional_role.main))

        self.roles.append([story.number, role])

        is_child = self.is_child(role)
        
        # Checks if the functional role already has a parent, and then makes this parent the child for 'FunctionalRole'
        if is_child[0]:
            for i in is_child[1]:
                if i[1] == Pattern.parent:
                    role = i[2]

        # self.relationships.append([story.number, role, Pattern.parent, 'FunctionalRole'])
        self.func_role = True            

    ## C1, C2, C3, R1, R2
    def identify_subj_dobj(self, story, part='means'):
        if part == 'means':
            fr = self.get_func_role(story)
        else:
            fr = self.get_subject(story)

            if type(fr) is list:
                txtfr = fr[0]
            else:
                txtfr = fr
            
            if str.lower(txtfr.text) == 'i':
                fr = self.get_func_role(story)
            
        if eval('story.' + str(part) + '.main_verb.phrase'):
            #and (eval('story.' + str(part) + '.main_verb.type') == 'II' or str.lower(eval('story.' + str(part) + '.main_verb.phrase')[1].text) in ['on', 'in', 'by', 'to']):
            mv = eval('story.' + str(part) + '.main_verb.phrase')
        else:
            mv = [eval('story.' + str(part) + '.main_verb.main')]

        if eval('story.' + str(part) + '.main_object.compound'):
            do = eval('story.' + str(part) + '.main_object.compound')
        else:
            do = [eval('story.' + str(part) + '.main_object.main')]
        
        if do[0] is not None and type(do[0]) is not list:
            w_fr = [self.getwt(x) for x in fr]
            w_mv = [self.getwt(x) for x in mv]
            w_do = [self.getwt(x) for x in do]

            self.relationships.append([story.number, w_fr, Pattern.subj_dobj, w_do, w_mv])

    def identify_dobj_conj(self, story):
        if story.means.free_form:
            for token in story.means.main_object.phrase:
                if token.dep_ == 'conj':
                    print(token.text, token.dep_, token.head, token.head.dep_, story.text)
                
    def get_func_role(self, story):
        if story.role.functional_role.compound:
            fr = story.role.functional_role.compound
        else:
            fr = [story.role.functional_role.main]

        return fr

    def get_subject(self, story):
        #if story.ends.subject.phrase:
        #    subj = story.ends.subject.phrase
        if story.ends.subject.compound:
            subj = story.ends.subject.compound
        else:
            subj = [story.ends.subject.main]

        return subj

    def is_child(self, weighted_tokens):
        is_child = False
        children = []

        for r in self.relationships:
            if type(r[1]) is list and type(weighted_tokens) is list:
                case = ""
                case_w = ""
                for i in r[1]:
                    case += i.case
                for j in weighted_tokens:
                    case_w += j.case
                if i == j:
                    children.append([r[1], r[2], r[3]])
                    is_subj = True                                                        
            if type(r[1]) is str and type(weighted_tokens) is str:
                if r[1] == weighted_tokens:
                    children.append([r[1], r[2], r[3]])
                    is_subj = True                    
            if type(r[1]) is WeightedToken and type(weighted_tokens) is WeightedToken:
                if r[1].case == weighted_tokens.case:
                    children.append([r[1], r[2], r[3]])
                    is_subj = True

        return is_child, children    

    def getwt(self, token):
        for wt in self.weighted_tokens:
            if str.lower(token.text) == str.lower(wt.token.text):
                return wt
        self.weighted_tokens.append(WeightedToken(token, 0.0))
        return self.getwt(token)
        

class Pattern(Enum):
    link_to_story = 0
    parent = 1
    subj_dobj = 2
    freeform_conj = 3
    compound_has = 4
