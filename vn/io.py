"""Read/write module for inputs and outputs (I/O)"""

import os.path
import csv
import pandas
import datetime as d

from vn.utils.nlputility import get_tokens, get_case


class Reader:
    """Reading from files"""

    @staticmethod
    def parse(fname):
        """Parses a previously open file

        Args:
            fname (str): File name
        
        Returns:
            list: non-empty lines
        """
        with open(fname, 'r') as open_file:
            lines = []
            for line in open_file:
                if not line.isspace():
                    lines.append(line.rstrip('\n\r'))
            return lines


class Writer:
    """Writing to files"""

    @staticmethod
    def make_file(dirname, filename, filetype, content):
        """Makes a file and writes to it

        Args:
            dirname (str): Name of the target directory
            filename (str): File name (without extension)
            filetype (str): Type of file
            content (str): Content to write to file
        
        Returns:
            str: Name and location of the file
        """
        if not os.path.exists(dirname):
                os.makedirs(dirname)
    
        outputname = ""
        filetype = "." + str(filetype)
        potential_outp = dirname + "/" + filename

        f_unique = str(d.datetime.now().date()) + "_" + str(d.datetime.now().time()).replace(':', '.')
        outputname = potential_outp + f_unique + filetype


        if filetype == ".csv":            
            Writer.writecsv(outputname, content)
        else:
            Writer.write(outputname, content)            

        return outputname

    @staticmethod
    def write(outputname, text):
        """Writes text to a file

        Args:
            outputname: Name and location of the output file
            text: Text to write to the file
        """
        with open(outputname, 'w') as f:
            f.write(text)
            f.close()

    @staticmethod
    def writecsv(outputname, li):
        """Writes a list/array/Pandas DataFrame to a CSV file

        Args:
            outputname: Name and location of the output file
            li: List/array/DataFrame
        """
        with open(outputname, 'wt') as f:
            if isinstance(li, pandas.core.frame.DataFrame):
                li.to_csv(path_or_buf=f, sep=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            else:
                writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerows(li)


class Printer:
    """Printing to terminal"""

    @staticmethod
    def _print_head(text):
        """Format and print head"""
        print("\n\n////////////////////////////////////////////////")
        print("/////", '{:^36}'.format(text) ,"/////")
        print("////////////////////////////////////////////////")

    @staticmethod
    def _print_subhead(text):
        """Format and print subhead"""
        print("<----------", '{:^9}'.format(text) ,"---------->")

    @staticmethod
    def _print_rel(rel):
        """Print noun phrases to terminal"""
        print(get_case(rel[1]), "--", rel[2], "->", get_case(rel[3]))

    @staticmethod
    def print_us_data(story):
        """Print user story data to terminal"""
        phrasetext = ""
        if story.means.main_verb.phrase:
            phrasetext = "( w/ Type " + story.means.main_verb.type + " phrase " + str(get_tokens(story.means.main_verb.phrase)) + " )"

        print("\n\n")
        Printer._print_subhead("BEGIN U S")
        print("User Story", story.number, ":", story.text)
        print(" >> INDICATORS\n  Role:", story.role.indicator, "\n    Means:", story.means.indicator, "\n    Ends:", story.ends.indicator)
        print(" >> ROLE\n  Functional role:", story.role.functional_role.main, "( w/ compound", get_tokens(story.role.functional_role.compound), ")")
        print(" >> MEANS\n  Main verb:", story.means.main_verb.main, phrasetext, "\n  Main object:", story.means.main_object.main, "( w/ noun phrase", get_tokens(story.means.main_object.phrase), "w/ compound", get_tokens(story.means.main_object.compound), ")")
        Printer._print_free_form(story, "means")
        Printer._print_free_form(story, "ends")

        Printer._print_subhead("END U S")

    @staticmethod
    def _print_free_form(story, part):
        """Print free form user story part to terminal"""
        p = 'story.' + part + '.'
        if eval(p + 'free_form'):
            print("  Free form:", get_tokens(eval(p + 'free_form')))
            if eval(p + 'verbs'):
                print("    Verbs:", get_tokens(eval(p + 'verbs')))
                if eval(p + 'phrasal_verbs'):
                    print("      Phrasal:", eval(p + 'phrasal_verbs'))
            if eval(p + 'noun_phrases'):
                print("    Noun phrases:", eval(p + 'noun_phrases'))
            if eval(p + 'compounds'):
                print("    Compound nouns:", eval(p + 'compounds'))
            if eval(p + 'nouns'):
                pnounstext = ""
                if eval(p + 'proper_nouns'):
                    pnounstext = " ( Proper: " + str(get_tokens(eval(p + 'proper_nouns'))) + ")"
                print("    Nouns:", get_tokens(eval(p + 'nouns')), pnounstext)

    @staticmethod
    def print_details(fail, success, nlp_time, parse_time, matr_time, gen_time, stats_time):
        """Print run details to terminal
        
        Args:
            fail (int): number of failed user stories
            success (int): number of successfully parsed user stories
            nlp_time (seconds): time for NLP to instantiate
            parse_time (seconds): time to mine user stories
            matr_time (seconds): time to create matrix
            gen_time (seconds): time to generate ontology/prolog files
            stats_time (seconds): time to generate statistics
        """
        total = success + fail
        if success is not 0:
            frate = fail/(success + fail)
        else:
            frate = 1

        Printer._print_head("RUN DETAILS")
        print("User Stories:\n  # Total parsed:\t\t", total,"\n    [+] Success:\t\t", success, "\n    [-] Failed:\t\t\t", fail, "\n  Failure rate:\t\t\t", frate, "(", round(frate * 100, 2), "% )")
        print("Time elapsed:")
        print(f"  NLP instantiate:\t\t {nlp_time:.5f}s")
        print(f"  Mining User Stories:\t\t {parse_time:.5f}s")
        print(f"  Creating factor matrix:\t {matr_time:.5f}s")
        print(f"  Generating Ontology / Prolog:\t {gen_time:.5f}s")
        if stats_time > 0.01:
            print(f"  Generating statistics:\t {stats_time:.5f}s")
        print("")

    @staticmethod
    def print_dependencies(story):
        """Print user story dependencies to terminal"""
        print("---------- U S", story.number, "----------")
        for token in story.data:
            print(token.i, "-> ", token.text, " [", token.pos_, " (", token.tag_ ,")", "dep:", token.dep_, " at ", token.idx, "]")
            if token.is_stop:
                print("! PART OF STOP LIST")
            print("Left edge: ", token.left_edge)
            print("Right edge: ", token.right_edge)
            print("Children: ", get_tokens(token.children))
            print("Subtree: ", get_tokens(token.subtree))
            print("Head: ", token.head)
            if token is not story.data[0]:
                print("Left neighbor: ", token.nbor(-1))
            if token is not story.data[-1]:
                print("Right neighbor: ", token.nbor(1))
            print("Entity type: ", token.ent_type, "\n")

    @staticmethod
    def print_noun_phrases(story):
        """Print noun phrases to terminal"""
        print("NOUN PHRASES > US " + str(story.number) + ": " + str(story.text))
        for chunk in story.data.noun_chunks:
            print(chunk.root.head.text, " <-- ", chunk.text)
        print("")

    @staticmethod
    def print_stats(stats, detail):
        """Print user story statistics to terminal"""
        if detail:
            print("\n")
            Printer._print_subhead("DETAILS")
            for r in stats:
                outline = ""
                for s in r:
                    outline += str(s) + "; "
                print(outline)

        print("\n")        
        Printer._print_subhead("SUMMARY")

    @staticmethod
    def print_gen_settings(matrix, base, threshold):
        """Print settings to terminal"""
        Printer._print_head("ONTOLOGY GENERATOR SETTINGS")
        print("Threshold:\t\t\t", threshold)
        print("Absolute Weights ( base =", base, "):")
        print("  Functional role:\t\t", matrix.VAL_FUNC_ROLE)
        print("  Main object:\t\t\t", matrix.VAL_MAIN_OBJ)
        print("  Noun in free form means:\t", matrix.VAL_MEANS_NOUN)
        print("  Noun in free form ends:\t", matrix.VAL_ENDS_NOUN)
        print("Relative Weights:")
        print("  Compound (compared to parent):", matrix.VAL_COMPOUND)
