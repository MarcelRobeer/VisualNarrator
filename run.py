#!/usr/bin/env python

import sys
import string
import os.path
import timeit
from argparse import ArgumentParser
from spacy.en import English

from app.io import Reader, Writer
from app.miner import StoryMiner
from app.matrix import Matrix
from app.userstory import UserStory
from app.utility import Utility, Printer
from app.pattern import Constructor
from app.statistics import Statistics, Counter


def main(filename, systemname, print_us, print_ont, statistics, link, threshold, base, weights):
	print("Initializing Natural Language Processor . . .")
	start_nlp_time = timeit.default_timer()
	nlp = English()

	nlp_time = timeit.default_timer() - start_nlp_time
	start_parse_time = timeit.default_timer()
	miner = StoryMiner()

	set = Reader.parse(filename)
	us_id = 0
	success = 0
	fail = 0
	list_of_fails = []

	errors = ""
	c = Counter()
	us_instances = []  # Keeps track of all succesfully created User Stories objects
	matrix = Matrix(base, weights)

	for s in set:
		try:
			user_story = parse(s, us_id, systemname, nlp, miner)
			user_story = c.count(user_story)
			success = success + 1
			us_instances.append(user_story)		
		except ValueError as err:
			errors += "\n[User Story " + str(us_id) + " ERROR] " + str(err.args[0]) + "!"
			fail = fail + 1
		us_id = us_id + 1
	if errors:
		Printer.print_head("PARSING ERRORS")
		print(errors)

	parse_time = timeit.default_timer() - start_parse_time

	start_matr_time = timeit.default_timer()
	m = matrix.generate(us_instances, ''.join(set), nlp)
	matr_time = timeit.default_timer() - start_matr_time

	#Printer.print_head(str(success) + " CREATED USER STORY INSTANCES")	
	#print(us_instances)

	if print_us:
		print("Details:\n")
		for us in us_instances:
			Printer.print_us_data(us)

	start_gen_time = timeit.default_timer()
	patterns = Constructor(nlp, us_instances, m)
	ontname = "http://fakesite.org/" + str(systemname).lower() + ".owl#"

	output_ontology = patterns.make(ontname, threshold, link)

	if print_ont:
		Printer.print_head("MANCHESTER OWL")
		print(output_ontology)

	statsarr = Statistics.to_stats_array(us_instances)

	w = Writer()

	outputfile = w.make_file("ontologies", str(systemname), "omn", output_ontology)

	outputcsv = ""
	sent_outputcsv = ""
	matrixcsv = ""

	gen_time = timeit.default_timer() - start_gen_time

	if statistics:
		Printer.print_head("USER STORY STATISTICS")
		Printer.print_stats(statsarr[0], True)
		Printer.print_stats(statsarr[1], True)
		Printer.print_subhead("Term - by - User Story Matrix ( Terms w/ total weight 0 hidden )")
		hide_zero = m[(m['sum'] > 0)]
		print(hide_zero)
		outputcsv = w.make_file("stats", str(systemname), "csv", statsarr[0])
		matrixcsv = w.make_file("stats", str(systemname) + "-term_by_US_matrix", "csv", m)
		sent_outputcsv = w.make_file("stats", str(systemname) + "-sentences", "csv", statsarr[1])

	Printer.print_gen_settings(matrix, base, threshold)

	Printer.print_details(fail, success, nlp_time, parse_time, matr_time, gen_time)
	if outputfile:
		print("Manchester Ontology file succesfully created at: \"" + str(outputfile) + "\"")
	if outputcsv:
		print("General statistics file succesfully created at: \"" + str(outputcsv) + "\"")
		print("Term-by-User Story Matrix succesfully created at: \"" + str(matrixcsv) + "\"")
		print("Sentence structure statistics file succesfully created at: \"" + str(sent_outputcsv) + "\"")
		

def parse(text, id, systemname, nlp, miner):
	no_punct = Utility.remove_punct(text)
	doc = nlp(no_punct)
	user_story = UserStory(id, text)
	user_story.system.main = nlp(systemname)[0]
	output(user_story, doc, miner)
	return user_story

def output(user_story, doc, miner):
	user_story.data = doc
	#Printer.print_dependencies(user_story)
	#Printer.print_noun_phrases(user_story)
	miner.mine(user_story)
	return user_story
	

def program():
	p = ArgumentParser(
		description="{*} A file should be input using the '-i'/'--input' argument.",
		usage='''run.py <INPUT FILE> [<args>]

	This program has multiple functionalities:
		(1) Mine user story information
		(2) Generate an ontology from a user story set
		(3) Get statistics for a user story set''',
		epilog='''{*} Created for a bachelor thesis in Information Science.
			M.J. Robeer, 2015-2016''')

	p.add_argument("filename",
                    help="input file with user stories", metavar="INPUT FILE",
                    type=lambda x: is_valid_file(p, x))
	p.add_argument('--version', action='version', version='Bachelor Thesis v0.7 BETA by M.J. Robeer')

	g_p = p.add_argument_group("general arguments (optional)")
	g_p.add_argument("-n", "--name", dest="system_name", help="your system name", required=False)
	g_p.add_argument("-u", "--print_us", dest="print_us", help="print data per user story", action="store_true", default=False)
	g_p.add_argument("-o", "--print_ont", dest="print_ont", help="print ontology", action="store_true", default=False)
	g_p.add_argument("-l", "--link", dest="link", help="link ontology classes to user story they originate from", action="store_true", default=False)

	s_p = p.add_argument_group("statistics arguments (optional)")
	s_p.add_argument("-s", "--statistics", dest="statistics", help="show user story set statistics and output these to a .csv file", action="store_true", default=False)

	w_p = p.add_argument_group("ontology generation tuning (optional)")
	w_p.add_argument("-t", dest="threshold", help="set threshold for ontology generation (INT, default = 1.0)", type=float, default=1.0)
	w_p.add_argument("-b", dest="base_weight", help="set the base weight (INT, default = 1)", type=int, default=1)	
	w_p.add_argument("-wfr", dest="weight_func_role", help="weight of functional role (FLOAT, default = 1.0)", type=float, default=1)
	w_p.add_argument("-wdo", dest="weight_direct_obj", help="weight of direct object (FLOAT, default = 1.0)", type=float, default=1)
	w_p.add_argument("-wffm", dest="weight_ff_means", help="weight of noun in free form means (FLOAT, default = 0.7)", type=float, default=0.7)
	w_p.add_argument("-wffe", dest="weight_ff_ends", help="weight of noun in free form ends (FLOAT, default = 0.5)", type=float, default=0.5)		
	w_p.add_argument("-wcompound", dest="weight_compound", help="weight of nouns in compound compared to head (FLOAT, default = 0.66)", type=float, default=0.66)		
	
	args = p.parse_args()

	weights = [args.weight_func_role, args.weight_direct_obj, args.weight_ff_means, args.weight_ff_ends, args.weight_compound]

	if not args.system_name or args.system_name == '':
		args.system_name = "System"
	main(args.filename, args.system_name, args.print_us, args.print_ont, args.statistics, args.link, args.base_weight, args.threshold, weights)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle


if __name__ == "__main__":
	program()
