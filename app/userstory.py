from app.statistics import UserStoryStatistics

class UserStory(object):
	def __init__(self, nr, text):
		self.number = nr
		self.text = text
		self.role = Role()
		self.means = Means()
		self.ends = Ends()
		self.indicators = []
		self.system = WithMain()
		self.free_form = []
		self.stats = UserStoryStatistics()

	def txtnr(self):
		return "US" + str(self.number)


class UserStoryPart(object):
	def __init__(self):
		self.indicator = []


class FreeFormUSPart(UserStoryPart):
	def __init__(self):
		self.free_form = []
		self.verbs = []
		self.phrasal_verbs = []
		self.nouns = []
		self.proper_nouns = []
		self.noun_phrases = []

class Role(UserStoryPart):
	def __init__(self):
		self.functional_role = WithPhrase()


class Means(FreeFormUSPart):
	def __init__(self):
		self.main_verb = WithPhrase()
		self.direct_object = WithPhrase()
		self.indirect_object = ""


class Ends(FreeFormUSPart):
	pass


class WithMain(object):
	def __init__(self):
		self.main = []

class WithPhrase(WithMain):
	def __init__(self):
		self.phrase = []
		self.compound = []
		self.type = ""
