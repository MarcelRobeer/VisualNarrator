#!/usr/bin/env python

import sys
import string
import os.path
import timeit
import pkg_resources

from argparse import ArgumentParser
from spacy.en import English
from jinja2 import FileSystemLoader, Environment, PackageLoader

from app.io import Reader, Writer
from app.miner import StoryMiner
from app.matrix import Matrix
from app.userstory import UserStory
from app.utility import Utility, Printer
from app.pattern import Constructor
from app.statistics import Statistics, Counter


def main(filename, systemname, print_us, print_ont, statistics, link, prolog, per_role, threshold, base, weights):
	"""General class to run the entire program
	"""

	# Initialize spaCy just once (this takes most of the time...)
	print("Initializing Natural Language Processor . . .")
	start_nlp_time = timeit.default_timer()
	nlp = English()
	nlp_time = timeit.default_timer() - start_nlp_time

	start_parse_time = timeit.default_timer()
	miner = StoryMiner()

	# Read the input file
	set = Reader.parse(filename)
	us_id = 1

	# Keep track of all errors	
	success = 0
	fail = 0
	list_of_fails = []
	errors = ""
	c = Counter()

	# Keeps track of all succesfully created User Stories objects
	us_instances = []  
	failed_stories = []

	# Parse every user story (remove punctuation and mine)
	for s in set:
		try:
			user_story = parse(s, us_id, systemname, nlp, miner)
			user_story = c.count(user_story)
			success = success + 1
			us_instances.append(user_story)	
		except ValueError as err:
			failed_stories.append([us_id, s, err.args])
			errors += "\n[User Story " + str(us_id) + " ERROR] " + str(err.args[0]) + "! (\"" + " ".join(str.split(s)) + "\")"
			fail = fail + 1
		us_id = us_id + 1

	# Print errors (if found)
	if errors:
		Printer.print_head("PARSING ERRORS")
		print(errors)

	parse_time = timeit.default_timer() - start_parse_time

	# Generate the term-by-user story matrix (m), and additional data in two other matrices
	start_matr_time = timeit.default_timer()

	matrix = Matrix(base, weights)
	matrices = matrix.generate(us_instances, ''.join(set), nlp)
	m = matrices[0]
	count_matrix = matrices[1]
	stories_list = matrices[2]
	rme = matrices[3]

	matr_time = timeit.default_timer() - start_matr_time

	# Print details per user story, if argument '-u'/'--print_us' is chosen
	if print_us:
		print("Details:\n")
		for us in us_instances:
			Printer.print_us_data(us)

	# Generate the ontology
	start_gen_time = timeit.default_timer()
	
	patterns = Constructor(nlp, us_instances, m)
	out = patterns.make(systemname, threshold, link)
	output_ontology = out[0]
	output_prolog = out[1]
	output_ontobj = out[2]
	output_prologobj = out[3]
	onto_per_role = out[4]

	# Print out the ontology in the terminal, if argument '-o'/'--print_ont' is chosen
	if print_ont:
		Printer.print_head("MANCHESTER OWL")
		print(output_ontology)

	gen_time = timeit.default_timer() - start_gen_time

	# Gather statistics and print the results
	stats_time = 0
	if statistics:
		start_stats_time = timeit.default_timer()

		statsarr = Statistics.to_stats_array(us_instances)

		Printer.print_head("USER STORY STATISTICS")
		Printer.print_stats(statsarr[0], True)
		Printer.print_stats(statsarr[1], True)
		Printer.print_subhead("Term - by - User Story Matrix ( Terms w/ total weight 0 hidden )")
		hide_zero = m[(m['sum'] > 0)]
		print(hide_zero)

		stats_time = timeit.default_timer() - start_stats_time	

	# Write output files
	w = Writer()

	folder = "output/" + str(systemname)
	reports_folder = folder + "/reports"
	stats_folder = reports_folder + "/stats"

	outputfile = w.make_file(folder + "/ontology", str(systemname), "omn", output_ontology)
	files = [["Manchester Ontology", outputfile]]

	outputcsv = ""
	sent_outputcsv = ""
	matrixcsv = ""

	if statistics:
		outputcsv = w.make_file(stats_folder, str(systemname), "csv", statsarr[0])
		matrixcsv = w.make_file(stats_folder, str(systemname) + "-term_by_US_matrix", "csv", m)
		sent_outputcsv = w.make_file(stats_folder, str(systemname) + "-sentences", "csv", statsarr[1])
		files.append(["General statistics", outputcsv])
		files.append(["Term-by-User Story matrix", matrixcsv])
		files.append(["Sentence statistics", sent_outputcsv])
	if prolog:
		outputpl = w.make_file(folder + "/prolog", str(systemname), "pl", output_prolog)
		files.append(["Prolog", outputpl])
	if per_role:
		for o in onto_per_role:
			name = str(systemname) + "-" + str(o[0])
			pont = w.make_file(folder + "/ontology", name, "omn", o[1])
			files.append(["Individual Ontology for '" + str(o[0]) + "'", pont])

	# Print the used ontology generation settings
	Printer.print_gen_settings(matrix, base, threshold)

	# Print details of the generation
	Printer.print_details(fail, success, nlp_time, parse_time, matr_time, gen_time, stats_time)

	report_dict = {
		"stories": us_instances,
		"failed_stories": failed_stories,
		"systemname": systemname,
		"us_success": success,
		"us_fail": fail,
		"times": [["Initializing Natural Language Processor (<em>spaCy</em> v" + pkg_resources.get_distribution("spacy").version + ")" , nlp_time], ["Mining User Stories", parse_time], ["Creating Factor Matrix", matr_time], ["Generating Manchester Ontology", gen_time], ["Gathering statistics", stats_time]],
		"dir": os.path.dirname(os.path.realpath(__file__)),
		"inputfile": filename,
		"inputfile_lines": len(set),
		"outputfiles": files,
		"threshold": threshold,
		"base": base,
		"matrix": matrix,
		"weights": m['sum'].copy().reset_index().sort_values(['sum'], ascending=False).values.tolist(),
		"counts": count_matrix.reset_index().values.tolist(),
		"classes": output_ontobj.classes,
		"relationships": output_prologobj.relationships,
		"types": list(count_matrix.columns.values),
		"ontology": Utility.multiline(output_ontology)
	}

	# Finally, generate a report
	report = w.make_file(reports_folder, str(systemname) + "_REPORT", "html", generate_report(report_dict))
	files.append(["Report", report])

	# Print the location and name of all output files
	for file in files:
		if str(file[1]) != "":
			print(str(file[0]) + " file succesfully created at: \"" + str(file[1]) + "\"")
		

def parse(text, id, systemname, nlp, miner):
	"""Create a new user story object and mines it to map all data in the user story text to a predefined model
	
	:param text: The user story text
	:param id: The user story ID, which can later be used to identify the user story
	:param systemname: Name of the system this user story belongs to
	:param nlp: Natural Language Processor (spaCy)
	:param miner: instance of class Miner
	:returns: A new user story object
	"""
	no_punct = Utility.remove_punct(text)
	no_double_space = ' '.join(no_punct.split())
	doc = nlp(no_double_space)
	user_story = UserStory(id, text, no_double_space)
	user_story.system.main = nlp(systemname)[0]
	user_story.data = doc
	#Printer.print_dependencies(user_story)
	#Printer.print_noun_phrases(user_story)
	miner.structure(user_story)
	user_story.old_data = user_story.data
	user_story.data = nlp(user_story.sentence)
	miner.mine(user_story, nlp)
	return user_story
	
def generate_report(report_dict):
	"""Generates a report using Jinja2
	
	:param report_dict: Dictionary containing all variables used in the report
	:returns: HTML page
	"""
	CURR_DIR = os.path.dirname(os.path.abspath(__file__))

	loader = FileSystemLoader( searchpath=str(CURR_DIR) + "/templates/" )
	env = Environment( loader=loader, trim_blocks=True, lstrip_blocks=True )
	env.globals['text'] = Utility.t
	env.globals['is_i'] = Utility.is_i
	env.globals['apply_tab'] = Utility.tab
	env.globals['is_comment'] = Utility.is_comment
	env.globals['occurence_list'] = Utility.occurence_list
	env.tests['is_us'] = Utility.is_us
	template = env.get_template("report.html")

	return template.render(report_dict)

def program():
	p = ArgumentParser(
		usage='''run.py <INPUT FILE> [<args>]

///////////////////////////////////////////
//              PROGRAM_NAME             //
///////////////////////////////////////////

This program has multiple functionalities:
    (1) Mine user story information
    (2) Generate an ontology from a user story set
    (3) Generate Prolog from a user story set (including links to 'role', 'means' and 'ends')
    (4) Get statistics for a user story set
''',
		epilog='''{*} Utrecht University.
			M.J. Robeer, 2015-2016''')

	p.add_argument("filename",
                    help="input file with user stories", metavar="INPUT FILE",
                    type=lambda x: is_valid_file(p, x))
	p.add_argument('--version', action='version', version='PROGRAM_NAME v0.9 BETA by M.J. Robeer')

	g_p = p.add_argument_group("general arguments (optional)")
	g_p.add_argument("-n", "--name", dest="system_name", help="your system name, as used in ontology and output file(s) generation", required=False)
	g_p.add_argument("-u", "--print_us", dest="print_us", help="print data per user story in the console", action="store_true", default=False)
	g_p.add_argument("-o", "--print_ont", dest="print_ont", help="print ontology in the console", action="store_true", default=False)
	g_p.add_argument("-l", "--link", dest="link", help="link ontology classes to user story they originate from", action="store_true", default=False)
	g_p.add_argument("--prolog", dest="prolog", help="generate prolog output (.pl)", action="store_true", default=False)

	s_p = p.add_argument_group("statistics arguments (optional)")
	s_p.add_argument("-s", "--statistics", dest="statistics", help="show user story set statistics and output these to a .csv file", action="store_true", default=False)

	w_p = p.add_argument_group("conceptual model generation tuning (optional)")
	w_p.add_argument("-p", "--per_role", dest="per_role", help="create an additional conceptual model per role", action="store_true", default=False)
	w_p.add_argument("-t", dest="threshold", help="set threshold for conceptual model generation (INT, default = 1.0)", type=float, default=1.0)
	w_p.add_argument("-b", dest="base_weight", help="set the base weight (INT, default = 1)", type=int, default=1)	
	w_p.add_argument("-wfr", dest="weight_func_role", help="weight of functional role (FLOAT, default = 1.0)", type=float, default=1)
	w_p.add_argument("-wmo", dest="weight_main_obj", help="weight of main object (FLOAT, default = 1.0)", type=float, default=1)
	w_p.add_argument("-wffm", dest="weight_ff_means", help="weight of noun in free form means (FLOAT, default = 0.7)", type=float, default=0.7)
	w_p.add_argument("-wffe", dest="weight_ff_ends", help="weight of noun in free form ends (FLOAT, default = 0.5)", type=float, default=0.5)		
	w_p.add_argument("-wcompound", dest="weight_compound", help="weight of nouns in compound compared to head (FLOAT, default = 0.66)", type=float, default=0.66)		
	
	args = p.parse_args()

	weights = [args.weight_func_role, args.weight_main_obj, args.weight_ff_means, args.weight_ff_ends, args.weight_compound]

	if not args.system_name or args.system_name == '':
		args.system_name = "System"
	main(args.filename, args.system_name, args.print_us, args.print_ont, args.statistics, args.link, args.prolog, args.per_role, args.threshold, args.base_weight, weights)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("Could not find file " + str(arg) + "!")
    else:
        return open(arg, 'r')


if __name__ == "__main__":
	program()
