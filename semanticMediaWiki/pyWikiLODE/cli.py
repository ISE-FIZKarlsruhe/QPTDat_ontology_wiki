import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent.parent))
from pyWikiLODE import OntDoc, PylodeError

import pdb


#from mwclient import Site
#
#def edit (page: str, content: str, summary: str = "" , append: bool = False, newpageonly: bool):
#    page = site.pages[page]
#    if page.can("edit"):
#        if newpageonly is True and page.exists:
#            return false # TODO throw exception
#        if page.text():
#            if append is True:
#                content +=
#            page.edit()
#        else:
#            page.edit()
#
#def login(host: str, path: str, scheme: str, username: str="", password: str="") -> Site:
#
#    site_ = Site(host=host, path=path, scheme=scheme)
#    if username and password:
#        site_.login(username=username, password=password)
#    global site
#    site = site_
#    return site_
#
#
#class SMWDoc():
#
#    def __init__(self,):
#
#    def create_class(self, dataDict):
#
#    def create_property(self, dataDict):
#
#    def create_objectProperty(self, dataDict):
#
#    def create_datatypeProperty(self, dataDict):
#
#    def create_annotationProperty(self, dataDict):
#
#    def create_functionalProperty(self, dataDict):
#
#    def create_importFile(self, dataDict):
#



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file location or URL",)

    args = parser.parse_args()

    

    pdb.set_trace()
    try:
        od = OntDoc(args.input)
    except PylodeError as e:
        print("ERROR: " + str(e))
        exit()
    of = "test.html"
    od.make_wiki(of)


if __name__ == "__main__":
    main()
