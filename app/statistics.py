from app.utility import Utility, NLPUtility

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
			sent_stats.append([us.number, Utility.text(us.stats.role.nps), Utility.text(us.stats.role.general), Utility.text(us.stats.role.detail), Utility.text(us.stats.means.nps), Utility.text(us.stats.means.general), Utility.text(us.stats.means.detail), Utility.text(us.stats.means.nps), Utility.text(us.stats.means.general), Utility.text(us.stats.means.detail)])

		return stats, sent_stats

class Counter:
	def count(self, story):
		story = self.count_basic(story)
		story = self.count_nps(story)
		story = self.count_indicators(story)
		story = self.get_types(story)
		#story = self.get_structure(story)
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
			story.stats.indicators.role = str.lower(story.role.indicator)
		if story.means.indicator:
			story.stats.indicators.means = str.lower(story.role.indicator)
		if story.ends.indicator:
			story.stats.indicators.ends = str.lower(story.role.indicator)

		return story

	def get_types(self, story):
		#if not story.role.functional_role.type == "":
		#	story.stats.fr_type = story.role.functional_role.type
		if not story.means.main_verb.type == "":
			story.stats.mv_type = story.means.main_verb.type
		#if not story.means.main_object.type == "":
		#	story.stats.do_type = story.means.main_object.type
		return story

	'''def get_structure(self, story):
		role = story.role.text
		means = story.means.text
		if story.has_ends:
			ends = story.ends.text
		else:
			ends = []

		print(type(role))
		print(type(means))
		print(type(ends))

		return self.replace_nounphrase(story, role, means, ends)

	def replace_nounphrase(self, story, role, means, ends):
		idx = []
		c = 0

		for chunk in story.data.noun_chunks:
			if len(chunk) > 1:
				c += 1
				for token in chunk:
					idx.append([token.i, c])
		
		story = self.fill('role', story, role, idx)
		story = self.fill('means', story, means, idx)
		story = self.fill('ends', story, ends, idx)

		return self.replace(story, idx)

	def fill(self, part, story, list, idx):
		for t in list:
			if t[2] not in [i[0] for i in idx]:
				eval('story.stats.' + part + '.nps.append(t[0])')
			else:
				for i in idx:
					if t[2] == i[0]:
						eval('story.stats.' + part + '.nps.append(i[1])')
			eval('story.stats.' + part + '.general.append(t[0])')
			eval('story.stats.' + part + '.detail.append(t[1])')

		return story

	def replace(self, story, idx):
		cnt = [i[1] for i in idx]
		vals = list(set(cnt))
		
		for v in vals:
			if v in story.stats.role.nps:
				story = self.set_np('role', story, v, cnt)
			elif v in story.stats.means.nps:
				story = self.set_np('means', story, v, cnt)
			elif v in story.stats.ends.nps:
				story = self.set_np('ends', story, v, cnt)

		story.stats.role.nps = [x for x in story.stats.role.nps if not isinstance(x, int)]
		story.stats.means.nps = [x for x in story.stats.means.nps if not isinstance(x, int)]
		story.stats.ends.nps = [x for x in story.stats.ends.nps if not isinstance(x, int)]

		return story

	def set_np(self, part, story, v, cnt):
		index = eval('story.stats.' + part + '.nps').index(v)
		eval('story.stats.' + part + '.nps')[index] = 'NOUNPHRASE(' + str(cnt.count(v)) + ')'
		return story
	'''


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
