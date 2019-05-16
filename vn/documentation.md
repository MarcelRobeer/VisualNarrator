## Arguments
The most important arguments is `INPUT FILE` to specify the location of the text input file. The table below provides an overview of the currently implemented arguments.

### Positional arguments
Argument | Required? | Description
--------|-----------|------------
`INPUT FILE` | __Yes__ | Specify the file name of the User Story input file


### _Optional_ arguments

##### General

Argument | Parameter | Description
--------|--| ------------
`-h`, `--help` | | Show a help message and exit
`-n SYSTEM_NAME`, `--name SYSTEM_NAME` | `systemname` | Specify a name for your system
`-u`, `--print_us` | `print_us` | Print additional information per User Story
`-o`, `--print_ont` | `print_ont` | Print the output ontology in the terminal
`--prolog` | `prolog` | Output prolog arguments to a _.pl_ file. Combine with `--link` to reason about user stories
`--json` | `json` | Output mined user stories to a _.json_ file.
`--version` | | Display the program's version number and exit

##### Statistics
Argument | Description
--------|------------
`-s`, `--statistics` | Show statistics for the User Story set and output these in .csv files

##### Ontology generation tuning
Argument | Parameter | Description | Type | Default
--------|--|-----------|------------|--------
`-p`, `--per_role` | `per_role` | Create an additional conceptual model per role | _N/A_
`-l`, `--link` |  |  Link all ontology classes to their respective User Story for usage in the set analysis | _N/A_
`-t THRESHOLD` | `threshold` | Set the threshold for the selected classes | _FLOAT_ | 1.0
`-b BASE_WEIGHT` | `base_weight` | Set the base weight | _INT_ | 1
`-wfr WEIGHT_FUNC_ROLE` | `weight` (`weight['func_role']`) |  Weight of functional role | _FLOAT_ | 1.0
`-wmo WEIGHT_MAIN_OBJ` |  `weight` (`weight['main_obj']`) |  Weight of main object | _FLOAT_ | 1.0
`-wffm WEIGHT_FF_MEANS` |  `weight` (`weight['ff_means']`) |  Weight of noun in free form means | _FLOAT_ | 0.7
`-wffe WEIGHT_FF_ENDS` |  `weight` (`weight['ff_ends']`)  | Weight of noun in free form ends | _FLOAT_ | 0.5
`-wcompound WEIGHT_COMPOUND` |  `weight` (`weight['compound']`) | Weight of nouns in compound compared to head | _FLOAT_ | 0.66
