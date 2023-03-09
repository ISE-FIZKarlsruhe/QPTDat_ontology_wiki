#!/usr/bin/env python 

import os
import argparse
import glob

import pylode

def convert_to_HTML(input_path, output_path) -> None:
    doc = pylode.OntDoc(ontology=input_path)
    doc.make_html(destination=output_path)
    
def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern')

    args = parser.parse_args()
    dir_pattern = args.pattern
    
    for d in glob.glob(dir_pattern):
        o = os.path.splitext(d)[0]+ ".html"
        convert_to_HTML(d, o)
    

if __name__ == "__main__":
    main()
