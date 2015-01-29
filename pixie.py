#!/usr/bin/python
#
# Pixie: the python css pre-processor
#
# define your CSS values with the power of Python.
# Usage:
# Make a file called your_css_file_name.pixie. This will be used
# as the raw file, with $variables in the CSS code.  It will output a
# your_css_file_name.css file.
#
# At the top of your pixie file, wrap your code in a <pixie></pixie> tag.
# The last value of all the variables will be the value in the CSS part
# that gets replaced.
#
# To signify a value in the CSS to replace, preface the value with a '$'.
# Pixie will look find the Python variable that matches the name and replace
# it with that value.

import argparse
import re
import sys

SIGIL_CHAR = '$'
PIXIE_TAG = '<pixie>'
CLOSE_TAG = '</pixie>'

def replace_sigils(line, sigils):
    """ Replaces all sigils in line with the values
    from sigils.

    line := a string
    sigils := a dict """
    for var in sigils:
        if var + "[" in line:   # List or dict

            var_search = "(?<=\\" + var + "\[)(\w)*" # Find index into the variable
            index = re.search(var_search, line).group(0)
            var_name = var + "[" + index + "]"

            try:
                index = int(index)
            except ValueError:
                pass # Index is a dict key. It's fine the way it is

            line = line.replace(var_name, str(sigils[var][index]))
        elif var in line:
            line = line.replace(var, str(sigils[var]))

    return line


def main(pixie_file, verbose=False):
    css_data = []
    python_data = []
    out_file = pixie_file[0:pixie_file.rfind('.')] + '.css' # Make outfile name
    sigils = {}

    with open(pixie_file, 'r') as raw:
        line = raw.readline()

        while line != '' and PIXIE_TAG not in line.lower(): # Read until <pixie>
            css_data.append(line)
            line = raw.readline()

        if PIXIE_TAG in line:     # Start gathering python data
            if verbose:
                if '/*' not in line:
                    line = '/*\n' + line
                css_data.append( line)
            line = raw.readline()   # Skip over <pixie> tag

            while line != '' and CLOSE_TAG not in line.lower(): # Collect Python data
                python_data.append(line)
                #TODO put flag in here to keep the pixie data in the final css file
                if verbose:
                    css_data.append(line)
                line = raw.readline()

            if line == '': # Error state. no closing tah
                print("[ERROR] no closing </pixie> tag found")
                return

            py_string = '\n'.join(python_data) # Make python script
            variables = {}
            exec(py_string, variables) # Execute the python code

            for var in variables: # Make sigils out of python variables
                sigils[SIGIL_CHAR + var] = variables[var]

            if verbose:
                if '*/' not in line:
                    line = line + '*/'
                css_data.append(line)
            line = raw.readline() # Jump over closing tag

            while line != '':   # Replace and variables in the CSS with the sigils
                css_data.append(replace_sigils(line, sigils))
                line = raw.readline()

    with open(out_file, 'w') as output: # Write the CSS file
        for line in css_data:
            output.write(line)

    print("[SUCCESS] " + out_file + " created!")

class ArgHolder(object):
    """ Empty class to hold argument values """
    pass

if __name__ == '__main__':

    args = ArgHolder()
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', help='Keeps the Pixie data in the output CSS file')
    parser.add_argument('filename', help='The file to parse')
    parser.parse_args(sys.argv[1:], namespace=args)

    main(args.filename, args.v)
