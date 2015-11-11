from app.helper import Helper

class Statistics:
	def to_stats_array(stories):
		stats = []
		sent_stats = []

		if stories:
			header = ['US_ID', 'User_Story', 'Words', 'Verbs', 'Nouns', 'NPs', 'Ind_R', 'Ind_M', 'Ind_E', 'FR_Type', 'MV_Type', 'DO_Type']
			stats.append(header)
			sent_header = ['US_ID', 'Role_NP', 'Role_Struct', 'Role_Struct_Detail', 'Means_NP', 'Means_Struct', 'Means_Struct_Detail', 'Ends_NP', 'Ends_Struct', 'Ends_Struct_Detail']
			sent_stats.append(sent_header)

		for us in stories:
			stats.append([us.number, us.text, us.stats.words, us.stats.verbs, us.stats.nouns, us.stats.noun_phrases, us.stats.indicators.role, us.stats.indicators.means, us.stats.indicators.ends, us.stats.fr_type, us.stats.mv_type, us.stats.do_type])
			sent_stats.append([us.number, Helper.text(us.stats.role.nps), Helper.text(us.stats.role.general), Helper.text(us.stats.role.detail), Helper.text(us.stats.means.nps), Helper.text(us.stats.means.general), Helper.text(us.stats.means.detail), Helper.text(us.stats.means.nps), Helper.text(us.stats.means.general), Helper.text(us.stats.means.detail)])

		return stats, sent_stats

class Counter:
	def count(self, story):
		story = self.count_basic(story)
		story = self.count_nps(story)
		story = self.count_indicators(story)
		story = self.get_types(story)
		story = self.get_structure(story)
		return story

	def count_basic(self, story):
		for token in story.data:
			story.stats.words += 1
			if token.pos_ == "NOUN":
				story.stats.nouns += 1
			if token.pos_ == "VERB":
				story.stats.verbs += 1

		return story

	def count_nps(self, story):
		for chunk in story.data.noun_chunks:
			story.stats.noun_phrases += 1		

		return story

	def count_indicators(self, story):
		if story.role.indicator:
			story.stats.indicators.role = Helper.text_lower_tokens(story.role.indicator)
		if story.means.indicator:
			story.stats.indicators.means = Helper.text_lower_tokens(story.means.indicator)
		if story.ends.indicator:
			story.stats.indicators.ends = Helper.text_lower_tokens(story.ends.indicator)

		return story

	def get_types(self, story):
		if not story.role.functional_role.type == "":
			story.stats.fr_type = story.role.functional_role.type
		if not story.means.main_verb.type == "":
			story.stats.mv_type = story.means.main_verb.type
		if not story.means.direct_object.type == "":
			story.stats.do_type = story.means.direct_object.type
		return story

	def get_structure(self, story):
		role = []
		means = []
		ends = []

		for token in story.data:
			if not token in story.indicators and token.pos_ != 'PUNCT' and token.pos_ != 'SPACE' and token.pos_ != 'X':
				if token.i < story.means.indicator[0].i:
					role.append([token.pos_, token.tag_, token.i])
				elif story.ends.indicator and token.i > story.ends.indicator[-1].i:
					ends.append([token.pos_, token.tag_, token.i])
				else:
					means.append([token.pos_, token.tag_, token.i])

		for t in role:
			story.stats.role.general.append(t[0])
			story.stats.role.detail.append(t[1])
		for t in means:
			story.stats.means.general.append(t[0])
			story.stats.means.detail.append(t[1])
		for t in ends:
			story.stats.ends.general.append(t[0])
			story.stats.ends.detail.append(t[1])

		# TODO: Replace noun phrases with word 'NP'

		return story


class UserStoryStatistics:
	def __init__(self):
		self.words = 0
		self.verbs = 0
		self.nouns = 0
		self.noun_phrases = 0
		self.mv_type = "-"
		self.fr_type = "-"
		self.do_type = "-"
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
