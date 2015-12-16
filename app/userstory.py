from app.statistics import UserStoryStatistics

class UserStory(object):
	def __init__(self, nr, text, no_punct):
		self.number = nr
		self.text = text
		self.sentence = no_punct
		self.iloc = []
		self.role = Role()
		self.means = Means()
		self.ends = Ends()
		self.indicators = []
		self.free_form = []
		self.system = WithMain()
		self.stats = UserStoryStatistics()

	def txtnr(self):
		return "US" + str(self.number)

	def is_func_role(self, token):
		if token.text == "FUNCROLE" and token.i in self.iloc:
			return True
		return False


class UserStoryPart(object):
	def __init__(self):
		self.text = []
		self.indicator = []


class FreeFormUSPart(UserStoryPart):
	def __init__(self):
		self.free_form = []
		self.verbs = []
		self.phrasal_verbs = []
		self.nouns = []
		self.proper_nouns = []
		self.noun_phrases = []
		self.compounds = []

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
