#!/usr/bin/env python

import sys
import string
import os.path
import timeit
from argparse import ArgumentParser
from spacy.en import English

from app.input import Reader
from app.miner import StoryMiner
from app.userstory import UserStory
from app.helper import Helper, Printer
from app.pattern import Constructor
from app.statistics import Counter


def main(filename, systemname, print_us, print_ont, statistics):
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
	us_instances = []  # Keeps track of all succesfully created User Stories objects
	for s in set:
		try:
			user_story = parse(s, us_id, systemname, nlp, miner)
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

	#Printer.print_head(str(success) + " CREATED USER STORY INSTANCES")	
	#print(us_instances)

	if print_us:
		print("Details:\n")
		for us in us_instances:
			Printer.print_us_data(us)

	start_gen_time = timeit.default_timer()
	patterns = Constructor(nlp, us_instances)
	ontname = "http://fakesite.org/" + str(systemname).lower() + ".owl#"
	if print_ont:
		Printer.print_head("MANCHESTER OWL")
		print(patterns.make(ontname))
	outputfile = make_file("GenOnt" + str(systemname), patterns.make(ontname))
	gen_time = timeit.default_timer() - start_gen_time

	if statistics:
		Printer.print_head("USER STORY STATISTICS")
		print("To be implemented...")

	Printer.print_details(fail, success, nlp_time, parse_time, gen_time)
	print("File succesfully created at: \"" + str(outputfile) + "\"")	

def parse(text, id, systemname, nlp, miner):
	no_punct = Helper.remove_punct(text)
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

def make_file(filename, text):
	if not os.path.exists("ontologies"):
    		os.makedirs("ontologies")
	
	outputname = "ontologies/" + filename + ".omn"
	f = open(outputname, 'w')
	f.write(text)
	f.close()
	return outputname
	

def program():
	p = ArgumentParser(prog="Obtaining User Story Information", description='Generate Manchester Ontology from User Story set.')
	p.add_argument("-i", "--input", dest="filename", required=True,
                    help="input file with user stories", metavar="FILE",
                    type=lambda x: is_valid_file(p, x))
	p.add_argument("-n", "--name", dest="system_name", help="your system name", required=False)
	p.add_argument("-u", "--print_us", dest="print_us", help="print data per user story", action="store_true", default=False)
	p.add_argument("-o", "--print_ont", dest="print_ont", help="print ontology", action="store_true", default=False)
	p.add_argument("-s", "--statistics", dest="statistics", help="show user story set statistics", action="store_true", default=False)
	p.add_argument('--version', action='version', version='%(prog)s v0.1 by M.J. Robeer')
	args = p.parse_args()
	if not args.system_name or args.system_name == '':
		args.system_name = "System"
	main(args.filename, args.system_name, args.print_us, args.print_ont, args.statistics)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle


if __name__ == "__main__":
	program()
