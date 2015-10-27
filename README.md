# Bachelor Thesis

This program reads a text file (.txt, .csv, etc.) containing User Stories and outputs a Manchester Ontology file. As of yet, each line may only contain a single User Story.

## Dependencies
The program is mainly depends on _spaCy. To run the program, you need:

* Python >= 3.4
* spaCy >= 0.93

## Running the Project
Running the program can only be done from the command line.

```
python run.py <commands>
```

### Commands
The most important command is `-i` (or `--input`) to specify the location of the text input file. The table below provides an overview of the currently implemented commands.

Command | Required? | Description
--------|-----------|------------
`-h`, `--help` | No | Show a help message and exit
`-i FILENAME`, `--input FILENAME` | Yes | Specify the file name of the User Story input file
`-s SYSTEM_NAME`, `--system_name SYSTEM_NAME` | No | Specify a name for your system
`-u`, `--print_us` | No | Print additional information per User Story
`-o`, `--print_ont` | No | Print the output ontology in the terminal
`--version` | No | Display the program's version number and exit
