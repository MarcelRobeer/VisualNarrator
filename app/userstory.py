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


class UserStoryPart(object):
	def __init__(self):
		self.indicator = []


class FreeFormUSPart(UserStoryPart):
	def __init__(self):
		self.free_form = []
		self.verbs = []
		self.nouns = []
		self.proper_nouns = []

class Role(UserStoryPart):
	def __init__(self):
		self.functional_role = WithCompound()


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


class WithCompound(WithMain):
	def __init__(self):
		self.compound = []


class WithPhrase(WithMain):
	def __init__(self):
		self.phrase = []


class WithType(WithPhrase):
	def __init__(self):
		self.type = ""
