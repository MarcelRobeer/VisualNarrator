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

	def get_idx(tree):
		return [t.i for t in tree]


class Printer:
	def print_head(text):
		print("\n\n////////////////////////////////////////////////")
		print("/////", '{:^36}'.format(text) ,"/////")
		print("////////////////////////////////////////////////")

	def print_us_data(story):
		phrasetext = ""
		pnounstext = ""
		if story.means.main_verb.phrase:
			phrasetext = "( w/ Type " + story.means.main_verb.type + " phrase " + str(Helper.get_tokens(story.means.main_verb.phrase)) + " )"

		print("\n\n<---------- BEGIN U S ---------->")
		print("User Story", story.number, ":", story.text)
		print(" >> INDICATORS\n  All:", Helper.get_tokens(story.indicators), "\n  Role:", Helper.get_tokens(story.role.indicator), "\n  Means:", Helper.get_tokens(story.means.indicator), "\n  Ends:", Helper.get_tokens(story.ends.indicator))
		print(" >> ROLE\n  Functional role:", story.role.functional_role.main, "( w/ adjectives", Helper.get_tokens(story.role.functional_role.adjectives), ")")
		print(" >> MEANS\n  Action verb:", story.means.main_verb.main, phrasetext, "\n  Direct object:", story.means.direct_object.main, "( w/ noun phrase", Helper.get_tokens(story.means.direct_object.phrase), ")")
		if story.means.verbs:
			print("    Verbs:", Helper.get_tokens(story.means.verbs))
		if story.means.nouns:
			if story.means.proper_nouns:
				pnounstext = " ( Proper: " + str(Helper.get_tokens(story.means.proper_nouns)) + ")"
			print("    Nouns:", Helper.get_tokens(story.means.nouns), pnounstext)
		print(" >> ENDS")
		if story.ends.free_form:
			print("  Free form:", Helper.get_tokens(story.ends.free_form))
		if story.ends.verbs:
			print("    Verbs:", Helper.get_tokens(story.ends.verbs))
		if story.ends.nouns:
			if story.ends.proper_nouns:
				pnounstext = " ( Proper: " + str(Helper.get_tokens(story.ends.proper_nouns)) + ")"
			print("    Nouns:", Helper.get_tokens(story.ends.nouns), pnounstext)
		print("<----------- END U S ----------->")

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
		print(story.number, "> Noun Phrases * In the form NP <-- HEAD")
		for chunk in story.data.noun_chunks:
			print(chunk.text, " <-- ", chunk.root.head.text)
