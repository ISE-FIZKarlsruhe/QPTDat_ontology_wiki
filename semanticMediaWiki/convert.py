#!/usr/bin/env python3

import argparse
import sys
import rdflib


def convert(infile, outfile):
    graph = rdflib.Graph()
    graph.parse(infile.name, format="turtle")# TODO check why file handle fails
    graph.serialize(outfile.name, format="nt") # TODO check why file handle fails

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin, help="")
    parser.add_argument("outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout, help="")
    args = parser.parse_args()  
    infile = args.infile
    outfile = args.outfile
    
    convert(infile, outfile)

if __name__ == "__main__":
    main()
