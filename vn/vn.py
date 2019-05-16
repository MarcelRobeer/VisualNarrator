#!/usr/bin/env python3

__version__ = '0.9.2'
author = 'Marcel Robeer'
description = 'Mine user story (US) information and turn it into a conceptual model'

import spacy
import os.path
import sys
from argparse import ArgumentParser
from vn.run_vn import run_vn
from vn.io import Reader

def initialize_nlp():
	# Initialize spaCy just once (this takes most of the time...)
	print("Initializing Natural Language Processor. . .")
	return spacy.load('en_core_web_md')


def call(filename, spacy_nlp):
	args2 = main("--return-args")
	weights = [args2.weight_func_role, args2.weight_main_obj, args2.weight_ff_means, args2.weight_ff_ends,
			   args2.weight_compound]
	filename = open(filename)
	return main(filename, args2.system_name, args2.print_us, args2.print_ont, args2.statistics, args2.link, args2.prolog,
				args2.json, args2.per_role, args2.threshold, args2.base_weight, weights, spacy_nlp)


def main(*args):
	p = ArgumentParser(
			usage=f'''python -m vn.py <INPUT FILE> [<args>]

	///////////////////////////////////////////
	//              Visual Narrator          //
	///////////////////////////////////////////
	{description}

	This program has multiple functionalities:
		(1) Mine user story information
		(2) Generate an ontology from a user story set
		(3) Generate Prolog from a user story set (including links to 'role', 'means' and 'ends')
		(4) Get statistics for a user story set
	''',
			epilog=f'''(*) Utrecht University.
				{author}, 2015-2019''')

	if "--return-args" not in args:
		p.add_argument("filename",
						help="input file with user stories", metavar="INPUT FILE",
						type=lambda x: is_valid_file(p, x))
	p.add_argument('--version', action='version', version=f'%(prog) v{__version__} by {author}')

	g_p = p.add_argument_group("general arguments (optional)")
	g_p.add_argument("-n", "--name", dest="system_name", help="your system name, as used in ontology and output file(s) generation",
					required=False)
	g_p.add_argument("-u", "--print_us", dest="print_us", help="print data per user story in the console",
					action="store_true",default=False)
	g_p.add_argument("-o", "--print_ont", dest="print_ont", help="print ontology in the console",
					action="store_true", default=False)
	g_p.add_argument("-l", "--link", dest="link", help="link ontology classes to user story they originate from",
					action="store_true", default=False)
	g_p.add_argument("--prolog", dest="prolog", help="generate prolog output (.pl)",
					action="store_true", default=False)
	g_p.add_argument("--return-args", dest="return_args", help="return arguments instead of call VN",
					action="store_true", default=False)
	g_p.add_argument("--json", dest="json", help="export user stories as json (.json)",
					action="store_true", default=False)

	s_p = p.add_argument_group("statistics arguments (optional)")
	s_p.add_argument("-s", "--statistics", dest="statistics", help="show user story set statistics and output these to a .csv file",
					action="store_true", default=False)

	w_p = p.add_argument_group("conceptual model generation tuning (optional)")
	w_p.add_argument("-p", "--per_role", dest="per_role", help="create an additional conceptual model per role",
					action="store_true", default=False)
	w_p.add_argument("-t", dest="threshold", help="set threshold for conceptual model generation (INT, default = 1.0)",
					type=float, default=1.0)
	w_p.add_argument("-b", dest="base_weight", help="set the base weight (INT, default = 1)",
					type=int, default=1)	
	w_p.add_argument("-wfr", dest="weight_func_role", help="weight of functional role (FLOAT, default = 1.0)",
					type=float, default=1)
	w_p.add_argument("-wdo", dest="weight_main_obj", help="weight of main object (FLOAT, default = 1.0)",
					type=float, default=1)
	w_p.add_argument("-wffm", dest="weight_ff_means", help="weight of noun in free form means (FLOAT, default = 0.7)",
					type=float, default=0.7)
	w_p.add_argument("-wffe", dest="weight_ff_ends", help="weight of noun in free form ends (FLOAT, default = 0.5)",
					type=float, default=0.5)		
	w_p.add_argument("-wcompound", dest="weight_compound", help="weight of nouns in compound compared to head (FLOAT, default = 0.66)",
					type=float, default=0.66)		
	
	if len(args) < 1:
		args = p.parse_args()
	else:
		args = p.parse_args(args)

	weights = [args.weight_func_role, args.weight_main_obj,
			args.weight_ff_means, args.weight_ff_ends,
			args.weight_compound]

	if not args.system_name or args.system_name == '':
		args.system_name = "System"
	if not args.return_args:
		spacy_nlp = initialize_nlp()
		return run_vn(args.filename, args.system_name, args.print_us, 
					  args.print_ont, args.statistics, args.link, args.prolog,
					  args.json, args.per_role, args.threshold, args.base_weight,
					  weights, spacy_nlp, stories=Reader.parse(args.filename))
	else:
		return args

def is_valid_file(parser, arg):
	if not os.path.exists(arg):
		parser.error(f"Could not find file {arg}!")
	else:
		return arg
