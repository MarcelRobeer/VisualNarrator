#!/usr/bin/env python3

import difflib
import sys

if len(sys.argv) <= 1 or sys.argv[1] == 'test.py':
    print("Give the .omn file to test as input argument, e.g. 'python test.py output/System/ontology/System1.omn'")
else:
    sysfile = str(sys.argv[1])

    with open('test.omn', 'r') as test:
        with open(sysfile, 'r') as input:
            diff = difflib.unified_diff(
                test.readlines(),
                input.readlines(),
                fromfile='test',
                tofile=sysfile,
            )
            for line in diff:
                sys.stdout.write(line)