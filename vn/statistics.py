"""Calculate statistics for `vn.userstory.UserStory` objects"""

class Statistics:
    @staticmethod
    def to_stats_array(stories):
        stats = []
        sent_stats = []

        if stories:
            header = ['US_ID', 'User_Story', 'Words', 'Verbs', 'Nouns', 'NPs',
                      'Ind_R', 'Ind_M', 'Ind_E', 'MV_Type']
            stats.append(header)
            sent_header = ['US_ID',
                           'Role_NP', 'Role_Struct', 'Role_Struct_Detail',
                           'Means_NP', 'Means_Struct', 'Means_Struct_Detail',
                           'Ends_NP', 'Ends_Struct', 'Ends_Struct_Detail']
            sent_stats.append(sent_header)

        for us in stories:
            stats.append([us.number, 
                          us.text, 
                          us.stats.words, 
                          us.stats.verbs, 
                          us.stats.nouns,
                          us.stats.noun_phrases, 
                          us.stats.indicators.role, 
                          us.stats.indicators.means, 
                          us.stats.indicators.ends,
                          us.stats.mv_type])
            sent_stats.append([us.number, 
                               us.stats.role.nps, 
                               us.stats.role.general, 
                               us.stats.role.detail, 
                               us.stats.means.nps, 
                               us.stats.means.general, 
                               us.stats.means.detail, 
                               us.stats.means.nps, 
                               us.stats.means.general, 
                               us.stats.means.detail])

        return stats, sent_stats

class Counter:
    @staticmethod
    def count(story):
        story = Counter.count_basic(story)
        story = Counter.count_nps(story)
        story = Counter.count_indicators(story)
        story = Counter.get_types(story)
        #story = Counter.get_structure(story)
        return story

    @staticmethod
    def count_basic(story):
        for token in story.data:
            story.stats.words += 1
            if token.pos_ == "NOUN":
                story.stats.nouns += 1
            if token.pos_ == "VERB":
                story.stats.verbs += 1

        return story

    @staticmethod
    def count_nps(story):
        story.stats.noun_phrases += len(list(story.data.noun_chunks))        
        return story

    @staticmethod
    def count_indicators(story):
        if story.role.indicator:
            story.stats.indicators.role = str.lower(story.role.indicator)
        if story.means.indicator:
            story.stats.indicators.means = str.lower(story.means.indicator)
        if story.ends.indicator:
            story.stats.indicators.ends = str.lower(story.ends.indicator)

        return story

    @staticmethod
    def get_types(story):
        if not story.means.main_verb.type == "":
            story.stats.mv_type = story.means.main_verb.type
        return story


class UserStoryStatistics:
    def __init__(self):
        self.words = 0
        self.verbs = 0
        self.nouns = 0
        self.noun_phrases = 0
        self.mv_type = "-"
        self.role = Structure()
        self.means = Structure()
        self.ends = Structure()
        self.indicators = IndicatorStats()


class IndicatorStats:
    def __init__(self):
        self.role = "-"
        self.means = "-"
        self.ends = "-"

class Structure:
    def __init__(self):
        self.nps = []
        self.general = []
        self.detail = []
