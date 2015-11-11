from app.helper import Helper

class Counter:
	def count(self, story):
		story = self.count_basic(story)
		story = self.count_nps(story)
		story = self.count_indicators(story)
		story = self.get_mvtype(story)
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

	def get_mvtype(self, story):
		story.stats.mv_type = story.means.main_verb.type
		return story


class UserStoryStatistics:
	def __init__(self):
		self.words = 0
		self.verbs = 0
		self.nouns = 0
		self.noun_phrases = 0
		self.mv_type = ""
		self.indicators = IndicatorStats()


class IndicatorStats:
	def __init__(self):
		self.role = "-"
		self.means = "-"
		self.ends = "-"
