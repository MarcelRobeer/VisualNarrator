# [WIP] User Story to Ontology (Bachelor Thesis)

This program reads a text file (.txt, .csv, etc.) containing User Stories and outputs a Manchester Ontology file. As of yet, each line may only contain a single User Story.

## Dependencies
The main dependency for the program is its Natural Language Processor (NLP) _spaCy_. To run the program, you need:

* Python >= 3.4
* spaCy >= 0.93

## Running the Project
Running the program can only be done from the command line. With the program main directory as current directory, run the program by executing:

```
python run.py <commands>
```

### Commands
The most important command is `-i` (or `--input`) to specify the location of the text input file. The table below provides an overview of the currently implemented commands.

Command | Required? | Description
--------|-----------|------------
`-h`, `--help` | No | Show a help message and exit
`-i FILENAME`, `--input FILENAME` | Yes | Specify the file name of the User Story input file
`-n SYSTEM_NAME`, `--name SYSTEM_NAME` | No | Specify a name for your system
`-s`, `--statistics` | No | Show statistics for the User Story set
`-u`, `--print_us` | No | Print additional information per User Story
`-o`, `--print_ont` | No | Print the output ontology in the terminal
`--version` | No | Display the program's version number and exit

## Conceptual Model
The classes in the program are based on the following conceptual model:

![conceptual_model](https://cloud.githubusercontent.com/assets/1345476/10763997/7517488c-7ccc-11e5-8cbc-abab1bb2028a.png)

The _Reader_ starts by reading the input file line by line and generates a list of sentences. These sentences are then enriched using Natural Language Processing, adding Part-of-Speech tags, dependencies, named entity recognition, etc. Subsequently, the _StoryMiner_ uses this enriched sentences to create User Story objects. The User Story objects contain all the information that could be mined from the sentence. The _Constructor_ then constructs patterns out of each user story, forming a model for an ontology, which is then used by the _Generator_ to generate a Manchester Ontology file (.omn).
