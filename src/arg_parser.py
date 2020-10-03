import os
import sys
from getopt import getopt

def get_arguments():
    cli_args = sys.argv[1:]
    inputs, extra = getopt(cli_args, 'h:i:o:')

    input_folder = None
    for arg in inputs:
        if arg[0] == '-i':
            input_folder = arg[1]
        elif arg[0] == '-h':
            print("python drumroll -i <input folder>")
            sys.exit()

    if(input_folder == None or os.path.exists(input_folder) == False):
        raise Exception("No input input folder supplied")

    return input_folder