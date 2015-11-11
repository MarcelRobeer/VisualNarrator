import re

class Helper:
	def split_list(a_list, nr):
		return a_list[:nr], a_list[nr:]

	def is_sublist(list_a, list_b):
		if list_a == []: return True
		if list_b == []: return False
		return list_b[:len(list_a)] == list_a or Helper.is_sublist(list_a, list_b[1:])

	def remove_punct(str):
		return re.sub(r"[,!?\.]", '', str).strip()

	def text(a_list):
		return " ".join(str(x) for x in a_list)

	def get_tokens(tree):
		return [t.text for t in tree]

	def get_lower_tokens(tree):
		return [str.lower(t.text) for t in tree]

	def get_idx(tree):
		return [t.i for t in tree]

	def remove_duplicates(self, arr):
		li = list()
		li_add = li.append
		return [ x for x in arr if not (x in li or li_add(x))]

	def text_lower_tokens(a_list):
		return Helper.text(Helper.get_lower_tokens(a_list))


class Printer:
	def print_head(text):
		print("\n\n////////////////////////////////////////////////")
		print("/////", '{:^36}'.format(text) ,"/////")
		print("////////////////////////////////////////////////")

	def print_subhead(text):
		print("<----------", '{:^9}'.format(text) ,"---------->")

	def print_us_data(story):
		phrasetext = ""
		pnounstext = ""
		if story.means.main_verb.phrase:
			phrasetext = "( w/ Type " + story.means.main_verb.type + " phrase " + str(Helper.get_tokens(story.means.main_verb.phrase)) + " )"

		print("\n\n")
		Printer.print_subhead("BEGIN U S")
		print("User Story", story.number, ":", story.text)
		print(" >> INDICATORS\n  All:", Helper.get_tokens(story.indicators), "\n    Role:", Helper.get_tokens(story.role.indicator), "\n    Means:", Helper.get_tokens(story.means.indicator), "\n    Ends:", Helper.get_tokens(story.ends.indicator))
		print(" >> ROLE\n  Functional role:", story.role.functional_role.main, "( w/ compound", Helper.get_tokens(story.role.functional_role.compound), ")")
		print(" >> MEANS\n  Main verb:", story.means.main_verb.main, phrasetext, "\n  Direct object:", story.means.direct_object.main, "( w/ noun phrase", Helper.get_tokens(story.means.direct_object.phrase), "w/ compound", Helper.get_tokens(story.means.direct_object.compound), ")")
		if story.means.free_form:
			print("  Free form:", Helper.get_tokens(story.means.free_form))
			if story.means.verbs:
				print("    Verbs:", Helper.get_tokens(story.means.verbs))
				if story.means.phrasal_verbs:
					print("      Phrasal:", story.means.phrasal_verbs)
			if story.means.noun_phrases:
				print("    Noun phrases:", story.means.noun_phrases)
			if story.means.nouns:
				if story.means.proper_nouns:
					pnounstext = " ( Proper: " + str(Helper.get_tokens(story.means.proper_nouns)) + ")"
				print("    Nouns:", Helper.get_tokens(story.means.nouns), pnounstext)
		print(" >> ENDS")
		if story.ends.free_form:
			print("  Free form:", Helper.get_tokens(story.ends.free_form))
			if story.ends.verbs:
				print("    Verbs:", Helper.get_tokens(story.ends.verbs))
				if story.ends.phrasal_verbs:
					print("      Phrasal:", story.ends.phrasal_verbs)
			if story.ends.noun_phrases:
				print("    Noun phrases:", story.ends.noun_phrases)
			if story.ends.nouns:
				if story.ends.proper_nouns:
					pnounstext = " ( Proper: " + str(Helper.get_tokens(story.ends.proper_nouns)) + ")"
				print("    Nouns:", Helper.get_tokens(story.ends.nouns), pnounstext)
		Printer.print_subhead("END U S")

	def print_details(fail, success, nlp_time, parse_time, gen_time):
		total = success + fail
		if success is not 0:
			frate = fail/success
		else:
			frate = 1
		Printer.print_head("RUN DETAILS")
		print("User Stories:\n  # Total parsed:", total,"\n  # Succesfully parsed:", success, "\n  # Failed at parsing:", fail, "\n  Failure rate:", frate, "(", round(frate * 100, 2), "% )")
		print("Time elapsed:\n  NLP instantiate:", nlp_time, "s\n  Mining User Stories:", parse_time, "s\n  Generating Manchester Ontology:", gen_time, "s\n")

	def print_dependencies(story):
		print("---------- U S", story.number, "----------")
		for token in story.data:
			print(token.i, "-> ", token.text, " [", token.pos_, " (", token.tag_ ,")", "dep:", token.dep_, " at ", token.idx, "]")
			if token.is_stop:
				print("! PART OF STOP LIST")
			print("Left edge: ", token.left_edge)
			print("Right edge: ", token.right_edge)
			print("Children: ", Helper.get_tokens(token.children))
			print("Subtree: ", Helper.get_tokens(token.subtree))
			print("Head: ", token.head)
			if token is not story.data[0]:
				print("Left neighbor: ", token.nbor(-1))
			if token is not story.data[-1]:
				print("Right neighbor: ", token.nbor(1))
			print("Entity type: ", token.ent_type, "\n")

	def print_noun_phrases(story):
		print("NOUN PHRASES > US " + str(story.number) + ": " + str(story.text))
		for chunk in story.data.noun_chunks:
			print(chunk.root.head.text, " <-- ", chunk.text)
		print("")

	def print_stats(stories, detail):
		stats = []

		for us in stories:
			indicators = [us.stats.indicators.role, us.stats.indicators.means, us.stats.indicators.ends]
			stats.append([us.number, us.stats.words, us.stats.verbs, us.stats.nouns, us.stats.noun_phrases, indicators, us.stats.mv_type])

		if detail:
			print("\n")
			Printer.print_subhead("DETAILS")
			print("US#\tWords\tVerbs\tNouns\tNPs\tInd (R,M,E)\tMV_Type")
			for r in stats:
				print(str(r[0]) + "\t" + str(r[1]) + "\t" + str(r[2]) + "\t" + str(r[3]) + "\t" + str(r[4]) + "\t" + str(r[5]) + "\t" + str(r[6]))

		print("\n")		
		Printer.print_subhead("SUMMARY")
