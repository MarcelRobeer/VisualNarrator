"""General Visual Narrator Module"""

import string
import os.path
import spacy
import sys
import pkg_resources
import json

from jinja2 import FileSystemLoader, Environment, PackageLoader

from vn.config import DEFAULT_THRESHOLD, DEFAULT_BASE, DEFAULT_WEIGHTS
from vn.io import Reader, Writer, Printer
from vn.miner import StoryMiner
from vn.matrix import Matrix
from vn.userstory import UserStory
from vn.pattern import Constructor
from vn.statistics import Statistics, Counter
from vn.utils.utility import multiline, remove_punct, tab, is_comment, occurence_list, timeit
from vn.utils.nlputility import t, is_i, is_us

# Check Python version
if sys.version_info[0] < 3:
    raise Exception("Visual Narrator requires Python 3")


class VisualNarrator:
	"""General class to run Visual Narrator"""

	def __init__(self,
	             threshold = DEFAULT_THRESHOLD, base = DEFAULT_BASE, weights = DEFAULT_WEIGHTS,
				 link = False, per_role = False,
				 stats = False, prolog = False, json = False,
				 spacy_nlp = None):
		"""Initialize across runs

		Args:
			threshold (float): threshold for which classes to select
			base (int): base weight (multiplier for all weights)
			weights (dict): weights for type of objects

			link (bool): link ontology classes to user story they originate from
			per_role (bool): create an additional conceptual model per role

			stats (bool): show user story set statistics and output these to a .csv file
			prolog (bool): generate Prolog output (.pl)
			json (bool): export user stories as JSON (.json)

			spacy_nlp (spacy.load object): spacy NLP using spacy.load('en_core_web_md')
		"""
		self.time = {}

		self.threshold = threshold
		self.base = base
		self.weights = weights
		self.link = link
		self.per_role = per_role
		self.stats = stats
		self.prolog = prolog
		self.json = json
		self.nlp = spacy_nlp if spacy_nlp is not None else self.initialize_nlp(log_time=self.time)

		self.matrix = Matrix(self.base, self.weights)

	def run(self,
	        filename,
			systemname,
			print_us = False,
			print_ont = False,
			stories = None):
		"""Single run of Visual Narrator

		Args:
			filename (str): File name to read
			systemname (str): Name of System (for output and in model)

			print_us (bool): print data per user story in the console
			print_ont (bool): print ontology in the console

			stories (list): preprocessed stories (from filename)
		Returns:
			dict: dictionary with US objects, Ontology + Prolog + JSON objects, matrix
		"""
		if stories is None:
			stories = Reader.parse(filename)

		# Mine stories
		us_instances, failed_stories  = self._mine_stories(stories, systemname, log_time=self.time)

		# Generate the term-by-user story matrix (m), and additional data in two other matrices
		m, count_matrix = self._get_matrix(us_instances, log_time=self.time)

		# Print details per user story, if argument '-u'/'--print_us' is chosen
		if print_us:
			print("Details:\n")
			for us in us_instances:
				Printer.print_us_data(us)

		# Generate the outputs
		output_ontology, output_prolog, onto_per_role = \
			self._get_gen(us_instances, m, systemname, print_ont, log_time=self.time)

		# Gather statistics and print the results
		statsarr = self._get_stats(us_instances, m, log_time=self.time)

		# Write output files
		w = Writer
		output_json = json.dumps([us.toJSON() for us in us_instances], indent=4)
		files, reports_folder = self.write_files(w, systemname, str(output_ontology), str(output_prolog), output_json,
	                                             statsarr, m, onto_per_role)

		# Print the used ontology generation settings
		Printer.print_gen_settings(self.matrix, self.base, self.threshold)

		# Print details of the generation
		fail       = len(failed_stories)
		success    = len(us_instances)
		time_nlp   = self.time['INITIALIZE_NLP']
		time_mine  = self.time['_MINE_STORIES']
		time_matr  = self.time['_GET_MATRIX']
		time_gen   = self.time['_GET_GEN']
		time_stats = self.time['_GET_STATS']

		Printer.print_details(fail, success, time_nlp, time_mine, time_matr, time_gen, time_stats)
		self.time['INITIALIZE_NLP'] = 0

		report_dict = {
			"stories": us_instances,
			"failed_stories": failed_stories,
			"systemname": systemname,
			"us_success": success,
			"us_fail": fail,
			"times": [["Initializing Natural Language Processor (<em>spaCy</em> v" + pkg_resources.get_distribution("spacy").version + ")" , time_nlp],
			          ["Mining User Stories", time_mine],
					  ["Creating Factor Matrix", time_matr],
					  ["Generating Manchester Ontology / Prolog", time_gen],
					  ["Gathering statistics", time_stats]],
			"dir": sys.path[0],
			"inputfile": filename,
			"inputfile_lines": len(stories),
			"outputfiles": files,
			"threshold": self.threshold,
			"base": self.base,
			"matrix": self.matrix,
			"weights": m['sum'].copy().reset_index().sort_values(['sum'], ascending=False).values.tolist(),
			"counts": count_matrix.reset_index().values.tolist(),
			"classes": output_ontology.classes,
			"relationships": output_ontology.relationships,
			"types": list(count_matrix.columns.values),
			"ontology": multiline(str(output_ontology)),
			"print_prolog": self.prolog,
			"prolog": multiline(str(output_prolog))
		}

		# Finally, generate a report
		report = w.make_file(reports_folder, str(systemname) + "_REPORT", "html", self.generate_report(report_dict))
		files.append(["Report", report])

		# Print the location and name of all output files
		for file in files:
			if str(file[1]) != "":
				print(f"{file[0]} file succesfully created at: \"{file[1]}\"")
		
		# Return objects so that they can be used as input for other tools
		return {'us_instances': us_instances,
				'output_ontobj': str(output_ontology),
				'output_prologobj': str(output_prolog),
				'output_json': output_json,
				'matrix': m}

	@timeit
	def initialize_nlp(self, **kw):
		"""Initialize spaCy just once (this takes most of the time...)"""
		print("Initializing Natural Language Processor. . .")
		import spacy
		return spacy.load('en_core_web_md')

	def parse(self, text, id, systemname, miner):
		"""Create a new user story object and mines it to map all data in the user story text to a predefined model
		
		Args:
			text: The user story text
			id: The user story ID, which can later be used to identify the user story
			systemname: Name of the system this user story belongs to
			miner: instance of class Miner

		Returns:
			`vn.userstory.UserStory`: A new user story object
		"""
		no_punct = remove_punct(text)
		no_double_space = ' '.join(no_punct.split())
		doc = self.nlp(no_double_space)
		user_story = UserStory(id, text, no_double_space)
		user_story.system.main = self.nlp(systemname)[0]
		user_story.data = doc
		#Printer.print_dependencies(user_story)
		#Printer.print_noun_phrases(user_story)
		miner.structure(user_story)
		user_story.old_data = user_story.data
		user_story.data = self.nlp(user_story.sentence)
		miner.mine(user_story, self.nlp)
		return user_story
	
	@timeit
	def _mine_stories(self, stories, systemname, **kw):
		# Keep track of all errors	
		errors = ""

		# Keeps track of all succesfully created User Stories objects
		us_instances = []  
		failed_stories = []

		# Parse every user story (remove punctuation and mine)
		for us_id, s in enumerate(stories, start=1):
			try:
				user_story = self.parse(s, us_id, systemname, StoryMiner())
				user_story = Counter.count(user_story)
				us_instances.append(user_story)
			except ValueError as err:
				failed_stories.append([us_id, s, err.args])
				errors += "\n[User Story {} ERROR] {}! (\"{}\")".format(us_id, err.args[0], " ".join(str.split(s)))

		# Print errors (if found)
		if errors:
			Printer._print_head("PARSING ERRORS")
			print(errors)

		return us_instances, failed_stories
	
	@timeit
	def _get_matrix(self, us_instances, **kw):
		matrices = self.matrix.generate(us_instances, ' '.join([u.sentence for u in us_instances]), self.nlp)
		m, count_matrix, _, _ = matrices
		return m, count_matrix
	
	@timeit
	def _get_gen(self, us_instances, m, systemname, print_ont, **kw):
		patterns = Constructor(self.nlp, us_instances, m)
		out = patterns.make(systemname, self.threshold, self.link)

		# Print out the ontology in the terminal, if argument '-o'/'--print_ont' is chosen
		if print_ont:
			Printer._print_head("MANCHESTER OWL")
			print(out[0])
		
		return out

	@timeit
	def _get_stats(self, us_instances, m, **kw):
		statsarr = None
		if self.stats:
			statsarr = Statistics.to_stats_array(us_instances)

			Printer._print_head("USER STORY STATISTICS")
			Printer.print_stats(statsarr[0], True)
			#Printer.print_stats(statsarr[1], True)
			Printer._print_subhead("Term - by - User Story Matrix ( Terms w/ total weight 0 hidden )")
			hide_zero = m[(m['sum'] > 0)]
			print(hide_zero)

		return statsarr
	
	def write_files(self, w, systemname, output_ontology, output_prolog, output_json,
	                statsarr, m, onto_per_role):
		"""Writes Ontology / Prolog / JSON to files
		
		Args:
			w (`vn.io.Writer`): Writer object for I/O
			systemname (str): System name
			output_ontology (str): Manchester Ontology text
			output_prolog (str): Prolog text
			output_json (str): JSON text
			statsarr (list): User story statistics
			m (DataFrame): Term-by-UserStory matrix 
			onto_per_role (list): List of ontologies, one per functional role
		
		Returns:
			list: Files created
			str: Folder the reports were created in
		"""
		s = str(systemname)

		folder = "output/" + s
		reports_folder = folder + "/reports"
		stats_folder = reports_folder + "/stats"
		ontology_folder = folder + "/ontology"

		outputfile = w.make_file(ontology_folder, s, "omn", output_ontology)
		files = [["Manchester Ontology", outputfile]]

		if self.stats:
			files.append(["General statistics", w.make_file(stats_folder, s, "csv", statsarr[0])])
			files.append(["Term-by-User Story matrix", w.make_file(stats_folder, f"{s}-term_by_US_matrix", "csv", m)])
			files.append(["Sentence statistics", w.make_file(stats_folder,  f"{s}-sentences", "csv", statsarr[1])])
		if self.prolog:
			files.append(["Prolog", w.make_file(folder + "/prolog", s, "pl", output_prolog)])
		if self.json:
			files.append(["JSON", w.make_file(folder + "/json", f"{s}-user_stories", "json", output_json)])
		if self.per_role:
			for c, o in onto_per_role:
				files.append([f"Individual Ontology for '{c}'", w.make_file(folder + "/ontology", f"{s}-{c}", "omn", o)])
		
		return files, reports_folder

	def generate_report(self, report_dict):
		"""Generates a report using Jinja2
		
		Args:
			report_dict: Dictionary containing all variables used in the report
		
		Returns:
			str: HTML page
		"""
		CURR_DIR = os.path.dirname(os.path.abspath(__file__))

		loader = FileSystemLoader( searchpath=str(CURR_DIR) + "/templates/" )
		env = Environment( loader=loader, trim_blocks=True, lstrip_blocks=True )
		env.globals['text'] = t
		env.globals['is_i'] = is_i
		env.globals['apply_tab'] = tab
		env.globals['is_comment'] = is_comment
		env.globals['occurence_list'] = occurence_list
		env.tests['is_us'] = is_us
		template = env.get_template("report.html")

		return template.render(report_dict)
