import argparse
import sys
import random
import re

import pronouncing


from poem_generator import PoemGenerator

parser = argparse.ArgumentParser(prog="poetry_generator")
parser.add_argument("-f", "--file")
parser.add_argument("-p", "--poem_len", default=2, type=int)
parser.add_argument("-w", "--word_len", default=3, type=int)


pg = PoemGenerator([])

if __name__ == "__main__":
    args = parser.parse_args()
    if not args.file:
        if len(sys.argv) == 1:
            print("No input for generating poem from.")
            sys.exit(-1)
        else:
            input_lines = sys.argv[1:]
    else:
        with open(args.file) as fp:
            input_lines = [l.strip() for l in fp.readlines()]
    print("\n".join(pg.get_poem()))
