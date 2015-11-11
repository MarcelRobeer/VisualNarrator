class Counter:
	def count(self, story):
		story = self.count_basic(story)
		story = self.count_nps(story)
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


	


class UserStoryStatistics:
	def __init__(self):
		self.words = 0
		self.verbs = 0
		self.nouns = 0
		self.noun_phrases = 0
