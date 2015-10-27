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
		if story.means.main_verb.phrase:
			phrasetext = "( w/ Type " + story.means.main_verb.type + " phrase " + str(Helper.get_tokens(story.means.main_verb.phrase)) + " )"

		print("\n\n<---------- BEGIN U S ---------->")
		print("User Story", story.number, ":", story.text)
		print(" >> INDICATORS\n  All:", Helper.get_tokens(story.indicators), "\n  Role:", Helper.get_tokens(story.role.indicator), "\n  Means:", Helper.get_tokens(story.means.indicator), "\n  Ends:", Helper.get_tokens(story.ends.indicator))
		print(" >> ROLE\n  Functional role:", story.role.functional_role.main, "( w/ adjectives", Helper.get_tokens(story.role.functional_role.adjectives), ")")
		print(" >> MEANS\n  Action verb:", story.means.main_verb.main, phrasetext, "\n  Direct object:", story.means.direct_object.main, "( w/ noun phrase", Helper.get_tokens(story.means.direct_object.phrase), ")")
		print(" >> ENDS")
		print(" >> FREE FORM\n", Helper.get_tokens(story.free_form))
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
