import numpy as np
import pandas as pd
from vn.utils.utility import flatten
from vn.utils.nlputility import get_case, is_verb


class Matrix:
    """Calculate weights for each term per user story and a matrix of count occurences"""

    def __init__(self, base, weight):
        self.VAL_FUNC_ROLE = base * weight['func_role']
        self.VAL_MAIN_OBJ = base * weight['main_obj']
        self.VAL_MEANS_NOUN = base * weight['ff_means']
        self.VAL_ENDS_NOUN = base * weight['ff_ends']
        self.VAL_COMPOUND = weight['compound']

    def generate(self, stories, all_words, nlp):
        all_words = ' '.join(all_words.split())
        words = [get_case(t) for t in nlp(all_words)]
        ids = [us.txtnr() for us in stories]

        # Add weighted scores to the words in the term-by-US matrix
        w_us = pd.DataFrame(0.0, index=words, columns=ids)
        w_us = w_us.iloc[np.unique(w_us.index, return_index=True)[1]]
        w_us = self.get_factor(w_us, stories)
        w_us['sum'] = w_us.sum(axis=1)

        # w_us = self._remove_stop_words(w_us, doc_array)
        w_us = self._remove_indicators(w_us, stories, nlp)
        w_us = self._remove_verbs(w_us, stories)

        # Link to US part
        us_ids, rme = self._get_rme(stories)

        rme_cols = pd.MultiIndex.from_arrays([us_ids, rme], names=['user_story', 'part'])
        rme_us = pd.DataFrame(0, index=words, columns=rme_cols)
        rme_us = rme_us.iloc[np.unique(rme_us.index, return_index=True)[1]]
        rme_us = self.get_role_means_ends(rme_us, stories)    

        # ...
        colnames = ['Functional Role', 'Functional Role Compound',
                    'Main Object', 'Main Object Compound',
                    'Means Free Form Noun', 'Ends Free Form Noun']
        stories_list = [[l, []] for l in list(w_us.index.values)]
        count_matrix = pd.DataFrame(0, index=w_us.index, columns=colnames)
        count_matrix, stories_list = self.count_occurence(count_matrix, stories_list, stories)

        return w_us, count_matrix, stories_list, rme_us
        
    def get_factor(self, matrix, stories):
        """Get factor score for all stories"""
        for story in stories:
            parts = ['role', 'means', 'ends'] if story.has_ends else ['role', 'means']

            for part in parts:
                matrix = self._get_factor_part(matrix, story, part)        

        return matrix

    def _get_factor_part(self, matrix, story, part):
        for token in eval(f'story.{part}.text'):
            if get_case(token) in matrix.index.values:
                matrix.at[get_case(token), story.txtnr()] += eval(f'self.score_{part}(token, story)')

        return matrix

    def score_role(self, token, story):
        """Add weights to tokens in the user story role"""
        weight = 0

        if self.is_phrasal('role.functional_role', token, story) == 1:
            weight += self.VAL_FUNC_ROLE
        elif self.is_phrasal('role.functional_role', token, story) == 2:
            weight += self.VAL_FUNC_ROLE * self.VAL_COMPOUND

        return weight

    def score_means(self, token, story):
        """Add weights to tokens in the user story means"""
        weight = 0

        if self.is_phrasal('means.main_object', token, story) == 1:
            weight += self.VAL_MAIN_OBJ
        elif self.is_phrasal('means.main_object', token, story) == 2:
            weight += self.VAL_MAIN_OBJ * self.VAL_COMPOUND

        if self.is_freeform('means', token, story) == 1:
            weight += self.VAL_MEANS_NOUN
        
        return weight

    def score_ends(self, token, story):
        """Add weights to tokens in the user story ends"""
        weight = 0
        
        if story.ends.free_form:
            if self.is_phrasal('ends.main_object', token, story) == 1 or self.is_phrasal('ends.main_object', token, story) == 2:
                weight += self.VAL_ENDS_NOUN
            elif self.is_freeform('ends', token, story) == 1:
                weight += self.VAL_ENDS_NOUN
        
        return weight

    def count_occurence(self, cm, sl, stories):
        """Count how often a token (t) occurs in a story (s)"""
        for s in stories:
            for t in s.data:
                c = get_case(t)
                if c in cm.index.values:
                    for word, us in sl:
                        if word == c:
                            us.append(s.number)                    

                    if self.is_phrasal('role.functional_role', t, s) == 1:
                        cm.at[c, 'Functional Role'] += 1
                    elif self.is_phrasal('role.functional_role', t, s) == 2:
                        cm.at[c, 'Functional Role Compound'] += 1

                    if self.is_phrasal('means.main_object', t, s) == 1:
                        cm.at[c, 'Main Object'] += 1
                    elif self.is_phrasal('means.main_object', t, s) == 2:
                        cm.at[c, 'Main Object Compound'] += 1

                    if self.is_freeform('means', t, s) == 1:
                        cm.at[c, 'Means Free Form Noun'] += 1
                    
                    if s.ends.free_form:
                        if self.is_phrasal('ends.main_object', t, s) > 0 or self.is_freeform('ends', t, s) == 1:
                            cm.at[c, 'Ends Free Form Noun'] += 1
                    
        return cm, sl

    def get_role_means_ends(self, matrix, stories):
        """Link cases (c) in matrix to their respective user stories (s)"""
        for c in matrix.index.values:
            for s in stories:
                if s.role.indicator:
                    if c in [get_case(t) for t in s.role.text]:
                        matrix.at[c, (s.txtnr(), 'Role')] = 1
                if s.means.indicator:
                    if c in [get_case(t) for t in s.means.text]:
                        matrix.at[s, (s.txtnr(), 'Means')] = 1
                if s.ends.indicator:
                    if c in [get_case(t) for t in s.ends.text]:
                        matrix.at[c, (s.txtnr(), 'Ends')] = 1

        return matrix

    def is_phrasal(self, part, token, story):
        """Check in which part of a WithPhrase() the token occurs
        
        Returns:
            int: -1 if not phrasal, 1 if in .main, 2 if in .compound, 3 if in .phrase"""
        spart = 'story.' + part
        if type(eval(spart + '.main')) is list:
            return -1
        elif token == eval(spart + '.main'):
            return 1
        elif token in eval(spart + '.compound'):
            return 2
        elif token in eval(spart + '.phrase'):
            return 3
        return -1

    def is_freeform(self, part, token, story):
        """Check whether a token is in the freeform part of a user story
        
        Returns:
            int: 1 if in free form else -1
        """
        spart = 'story.' + part
        if eval(spart + '.free_form'):
            if eval(spart + '.nouns'):
                if token in eval(spart + '.nouns'):
                    return 1
                elif eval(spart + '.compounds') and token in flatten(eval(spart + '.compounds')):
                    return 1
        return -1

    def _remove_from(self, matrix, to_drop):
        for d in to_drop:
            if d in matrix.index.values and matrix.loc[d, 'sum'] > 0:
                to_drop.remove(d)

        return matrix[~matrix.index.isin(to_drop)]

    def _remove_indicators(self, matrix, stories, nlp):
        indicators = []

        for story in stories:
            ind = story.role.indicator + " " + story.means.indicator
            if story.has_ends:
                ind += " " + story.ends.indicator

            [indicators.append(get_case(t)) for t in nlp(ind)]

            [indicators.append(i) for i in story.indicators]

        return self._remove_from(matrix, indicators)

    def _remove_verbs(self, matrix, stories):
        verbs = []
        cases = matrix.index.values.tolist()        

        for case in cases:
            pos = []

            for story in stories:
                for token in story.data:
                    if get_case(token) == case:
                        pos.append(token)

            if len(set(pos)) == 1 and is_verb(pos[0]):
                verbs.append(case)

        return self._remove_from(matrix, verbs)
    
    def _get_rme(self, stories):
        us_ids = []
        rme = []

        for us in stories:
            if us.role.indicator:
                us_ids.append(us.txtnr())
                rme.append('Role') 
            if us.means.indicator:
                us_ids.append(us.txtnr())
                rme.append('Means')
            if us.ends.indicator:
                us_ids.append(us.txtnr())
                rme.append('Ends')
    
        return us_ids, rme

    def _remove_stop_words(self, matrix, stopwords):
        result = pd.merge(matrix, stopwords, left_index=True, right_index=True, how='inner')
        result = result[(result['IS_STOP'] == 0)]

        # Special case: 'I' -> replace by functional role?
        # Should not remove stop words with a high weight
        return result.drop('IS_STOP', axis=1)
