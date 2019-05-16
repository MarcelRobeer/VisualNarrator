__version__ = '0.9.2'
author = 'Marcel Robeer'
description = 'Mine user story (US) information and turn it into a conceptual model'

default_threshold = 1.0
default_base = 1
default_weights = {'func_role': 1.0,
                   'main_obj': 1.0,
				   'ff_means': 0.7,
				   'ff_ends': 0.5,
				   'compound': 0.66}