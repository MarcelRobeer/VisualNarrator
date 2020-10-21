# Visual Narrator

> Tells Your User Story Graphically

This program turns user stories into a conceptual model containing entities and relationships.

#### Input
* __Text file__ (.txt, .csv, etc.) containing _one user story per line_

#### Output
* __Report__ of user story parsing, and conceptual model creation
* __Manchester Ontology__ (.omn) describing the conceptual model
* (Optional) __Prolog__ (.pl) arguments
* (Optional) __JSON__ (.json) of the user stories parts' information
* (Optional) __Statistics__ about the user stories
* Returns the mined user stories, ontology, prolog and matrix of weights, which can be used by other tools

## Publications
Two scientific papers were published on Visual Narrator:
* M. Robeer, G. Lucassen, J. M. E. M. van Der Werf, F. Dalpiaz, and S. Brinkkemper (2016). Automated Extraction of Conceptual Models from User Stories via NLP. In _2016 IEEE 24th International Requirements Engineering (_RE_) Conference_ (pp. 196-205). IEEE. \[[pdf](https://www.staff.science.uu.nl/~dalpi001/papers/robe-luca-werf-dalp-brin-16-re.pdf)\]
* G. Lucassen, M. Robeer, F. Dalpiaz, J. M. E. M. van der Werf, and S. Brinkkemper (2017). Extracting conceptual models from user stories with Visual Narrator. _Requirements Engineering_. \[[url](https://link.springer.com/article/10.1007/s00766-017-0270-1)\]

## Dependencies
The main dependency for the program is its Natural Language Processor (NLP) [spaCy](http://spacy.io/). To run the program, you need:

* _Python_ >= 3.6 (under development using 3.7.3)
* _spaCy_ >= 2.1.2 (under development using 2.1.4; language model 'en_core_web_md')
* _NumPy_ >= 1.16.2
* _Pandas_ >= 0.24.2
* _Jinja2_ >= 2.10

## Running the Project
Running the program can be done in three ways: (1) from the command line, (2) using method `VisualNarrator().run()`, (3) serving VisualNarrator as a REST API.

### (1) Command line
With the program main directory as current directory, run the program by executing:

```bash
python run.py <INPUT FILE> [<arguments>]
```

### (2) Method VisualNarrator().run()
First, install as a package `pip install git+https://github.com/MarcelRobeer/VisualNarrator` (or download and run `python setup.py install` in the VisualNarrator folder).

Next, import the `VisualNarrator` class from `vn.vn` and run `VisualNarrator().run()`:

```python
from vn.vn import VisualNarrator

visualnarrator = VisualNarrator(<ARGUMENTS>)
visualnarrator.run(<INPUT FILE>, <SYSTEM_NAME>)
```

Arguments may be supplied to `VisualNarrator(**args)` to re-use and for a single run to `run(*args, **kwargs)`. Execute `help(visualnarrator)` to see all (optional) arguments.

### (3) REST API
Allows a user to POST their user story file to `/mine/` and retrieve a JSON response. It requires three dependencies (`fastapi`, `uvicorn` and `python-multipart`), and can then be run using `uvicorn`. Execute the following in your terminal:
```bash
pip install fastapi uvicorn python-multipart
uvicorn vn.ui.api:vn_app --reload
```
The REST API is then accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) where documentation on the API can be found at [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/).

#### Arguments
For details on arguments, see our [documentation here](vn/documentation.md).

### Example usage

Command line:
```bash
python run.py example_stories.txt -n "TicketSystem" -u --json
```

From method:
```python
from vn.vn import VisualNarrator

visualnarrator = VisualNarrator(json = True)
visualnarrator.run("example_stories.txt", "TicketSystem", print_us = True)
```

## Conceptual Model
The classes in the program are based on the following conceptual model:

![conceptual_model](https://cloud.githubusercontent.com/assets/1345476/12152551/a6b7dca0-b4b5-11e5-8cee-80f463588df2.png)

The `Reader` starts by reading the input file line by line and generates a list of sentences. These sentences are then enriched using Natural Language Processing, adding Part-of-Speech tags, dependencies, named entity recognition, etc. Subsequently, the `StoryMiner` uses these enriched sentences to create _UserStory_ objects. The User Story objects contain all the information that could be mined from the sentence. These are then used to attach weight to each term in the User Story, creating _Term-by-US Matrix_ in the `Matrix` class. The `Constructor` then constructs patterns out of each user story, using the _Term-by-US Matrix_ to attach a weight to each token. The Constructor forms a model for an ontology, which is then used by the `Generator` to generate a Manchester Ontology file (.omn) and optionally a Prolog file (.pl). Finally, these files are printed to an actual file by the `Writer` in the '/ontologies' and '/prolog' folders respectively. Optionally, the _UserStory_ objects can be output to a JSON file so they can be used in other applications.

## Visual Narrator was developed as part of the _Requirements Engineering Lab_ at _Utrecht University_
[https://www.uu.nl/en/research/software-systems/organization-and-information/labs/requirements-engineering](https://www.uu.nl/en/research/software-systems/organization-and-information/labs/requirements-engineering)
