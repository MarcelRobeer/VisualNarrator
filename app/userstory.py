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
		self.text = ""
		self.indicator = []


class Role(UserStoryPart):
	def __init__(self):
		self.functional_role = WithAdjectives()


class Means(UserStoryPart):
	def __init__(self):
		self.main_verb = WithPhrase()
		self.direct_object = WithPhrase()
		self.indirect_object = ""
		self.free_form = []


class Ends(UserStoryPart):
	def __init__(self):
		self.free_form = []


class WithMain(object):
	def __init__(self):
		self.main = []


class WithAdjectives(WithMain):
	def __init__(self):
		self.adjectives = []


class WithPhrase(WithMain):
	def __init__(self):
		self.phrase = []


class WithType(WithPhrase):
	def __init__(self):
		self.type = ""
