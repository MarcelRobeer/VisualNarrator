"""Configuration file"""

__version__ = '0.9.2'
author = 'Marcel Robeer'
description = 'Mine user story (US) information and turn it into a conceptual model'

DEFAULT_THRESHOLD = 1.0
DEFAULT_BASE      = 1
DEFAULT_WEIGHTS   = {'func_role': 1.0,
                     'main_obj': 1.0,
				     'ff_means': 0.7,
				     'ff_ends': 0.5,
				     'compound': 0.66}
