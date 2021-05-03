import argparse
import os
import sys

from .compiler import Compiler

def base_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def main():
    default_out_fpath = os.path.join(base_path(),"..","out.cjmips")

    parser = argparse.ArgumentParser(description="Compile a CJASM to CJMIPS")
    parser.add_argument(f'inputfile', help="input file", )
    parser.add_argument(f'--outputfile', '-o', help="output binary file", default= default_out_fpath)

    #parser.add_argument("--config", help="Name of config file for fuzzing session default is witcher_config.json",default="witcher_config.json")
    args = parser.parse_args()

    if not args.inputfile or not os.path.exists(args.inputfile):
        raise ValueError("The input cjasm file must exist! ")

    c = Compiler()
    in_fpath = os.path.realpath(args.inputfile)

    c.parse(in_fpath)
    c.compile()
    c.write(args.outputfile)

if __name__ == "__main__":
    main()