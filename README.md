# Visual Narrator

> Tells Your User Story Graphically

This program reads a text file (.txt, .csv, etc.) containing User Stories and outputs a Manchester Ontology file. As of yet, each line may only contain a single User Story.

Optionally, statistics about the User Story set can be output.

## Dependencies
The main dependency for the program is its Natural Language Processor (NLP) [spaCy](http://spacy.io/). To run the program, you need:

* _Python_ >= 3.4
* _spaCy_ >= 0.93 (currently under development using v0.98)
* _NumPy_ >= 1.10.1
* _Pandas_ >= 0.17.1
* _Jinja2_ >= 2.8

## Running the Project
Running the program can only be done from the command line. With the program main directory as current directory, run the program by executing:

```
python run.py <INPUT FILE> [<arguments>]
```

#### Arguments
The most important arguments is `INPUT FILE` to specify the location of the text input file. The table below provides an overview of the currently implemented arguments.

##### Positional arguments
Argument | Required? | Description
--------|-----------|------------
`INPUT FILE` | __Yes__ | Specify the file name of the User Story input file


##### _Optional_ arguments

###### General

Argument | Description
--------|------------
`-h`, `--help` | Show a help message and exit
`-n SYSTEM_NAME`, `--name SYSTEM_NAME` | Specify a name for your system
`-u`, `--print_us` | Print additional information per User Story
`-o`, `--print_ont` | Print the output ontology in the terminal
`--prolog` | Output prolog arguments to a _.pl_ file. Combine with `--link` to reason about user stories
`--version` | Display the program's version number and exit

###### Statistics
Argument | Description
--------|------------
`-s`, `--statistics` | Show statistics for the User Story set and output these in .csv files

###### Ontology generation tuning
Argument | Description | Type | Default
--------|-----------|------------|--------
`-p`, `--per_role` | Create an additional conceptual model per role | _N/A_
`-l`, `--link` | Link all ontology classes to their respective User Story for usage in the set analysis | _N/A_
`-t THRESHOLD` | Set the threshold for the selected classes | _FLOAT_ | 1.0
`-b BASE_WEIGHT` | Set the base weight | _INT_ | 1
`-wfr WEIGHT_FUNC_ROLE` | Weight of functional role | _FLOAT_ | 1.0
`-wmo WEIGHT_MAIN_OBJ` | Weight of main object | _FLOAT_ | 1.0
`-wffm WEIGHT_FF_MEANS` | Weight of noun in free form means | _FLOAT_ | 0.7
`-wffe WEIGHT_FF_ENDS` | Weight of noun in free form ends | _FLOAT_ | 0.5
`-wcompound WEIGHT_COMPOUND` | Weight of nouns in compound compared to head | _FLOAT_ | 0.66

### Example usage

```
python run.py example_stories.txt -n "TicketSystem" -u
```

## Conceptual Model
The classes in the program are based on the following conceptual model:

![conceptual_model](https://cloud.githubusercontent.com/assets/1345476/12152551/a6b7dca0-b4b5-11e5-8cee-80f463588df2.png)

The `Reader` starts by reading the input file line by line and generates a list of sentences. These sentences are then enriched using Natural Language Processing, adding Part-of-Speech tags, dependencies, named entity recognition, etc. Subsequently, the `StoryMiner` uses these enriched sentences to create _UserStory_ objects. The User Story objects contain all the information that could be mined from the sentence. These are then used to attach weight to each term in the User Story, creating _Term-by-US Matrix_ in the `Matrix` class. The `Constructor` then constructs patterns out of each user story, using the _Term-by-US Matrix_ to attach a weight to each token. The Constructor forms a model for an ontology, which is then used by the `Generator` to generate a Manchester Ontology file (.omn) and optionally a Prolog file (.pl). Finally, these files are printed to an actual file by the `Writer` in the '/ontologies' and '/prolog' folders respectively.
