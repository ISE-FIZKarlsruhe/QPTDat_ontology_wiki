#!/usr/bin/env python 

import pdb

import os
import argparse
import glob

import pylode
import pywikibot
import lxml
import lxml.html

main_page = """= Quality Assurance and Linking of Research Data in Plasma Technology = 

The necessity and potential of systematic archiving and publication of digital research data is increasingly seen in the scientific landscape. Networking and quality assurance of the research data provided are essential factors for the efficient interdisciplinary re-use of research data and for reducing the inhibition threshold for the secondary use of third-party research data. The implementation of these criteria poses a particular challenge in the field of plasma technology, since a multitude of research methods is used in this interdisciplinary research field for which there are hardly any standards for the collection, documentation and storage of research data. At the same time, plasma technology is represented both in established fields of technology and in new areas of application with great social potential, such as new technologies for energy system transformation and in the fields of medicine and hygiene. Thus, the establishment of processes and standards for quality assurance and re-use of research data is of extraordinary importance here.

The project QPTDat – Quality Assurance and Linking of Research Data in Plasma Technology aims at enabling and permanently supporting data-driven research and knowledge transfer in the field of plasma technology. For this purpose, curation criteria and metadata standards are to be developed in accordance with the FAIR Data Principles. Furthermore, in the sense of an open data science approach, concepts are to be investigated and developed to automate quality checks of data and metadata with the help of blockchain technologies. Blockchain technologies will also be used to publish data, quality criteria and processes transparently. Furthermore, domain specific data and metadata will be linked by means of a plasma technology knowledge graph and embedded in adjacent domains. New concepts and services are to be implemented in the data platform INPTDAT.

The QPTDat project is funded by the Federal Ministry of Education and Research (BMBF) under grant marks 16QK03A. 16QK03B, and 16QK03C.

= Community = 
This Semantic MediaWiki discusses all classes and properties introduced as part of the QPTDat project.

    """



def convert_table(node ) -> str: 
    pass

def convert_elements(root, xpath_exp, ) -> dict:
    elements = dict()
    root_node = root.xpath(xpath_exp)
    for node in root_node:
        if len(node.xpath("h3")) > 0 and len(node.xpath("table")) > 0:
            name = node.xpath("h3/text()")[0].strip()
            text = node.xpath("table")[0].text_content().strip()
            elements[name]=text

    return elements
    


def convert_to_wiki(input_path: str, prefix: str = None) -> dict:
    doc = pylode.OntDoc(ontology=input_path)
    html = doc.make_html()
    root = lxml.html.fromstring(html)
    
    metadata_text = root.xpath("//*[@id=\"metadata\"]")[0].text_content().strip()
    classes = convert_elements(root, "//*[@id=\"classes\"]/div")
    object_properties = convert_elements(root, "//*[@id=\"objectproperties\"]/div")
    datatype_properties = convert_elements(root, "//*[@id=\"datatypeproperties\"]/div")
    annotation_properties = convert_elements(root, "//*[@id=\"annotationproperties\"]")

    wiki_dict = classes | object_properties | datatype_properties | annotation_properties| {"Main_Page":f"{main_page}\n= Metadata =\n{metadata_text}"} 

    return wiki_dict, metadata_text

def import_to_wiki(wikiPages: dict, ) -> None:
    site = pywikibot.Site("en")
    site.login()

    for k,v in wikiPages.items():
        page = pywikibot.Page(site, k)
        page.text = v
        page.save("Import from LodView")


def main() -> None:
    pdb.set_trace()

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern')

    args = parser.parse_args()
    dir_pattern = args.pattern
    metadata_text = ""
    for d in glob.glob(dir_pattern):
        metadata, wiki_dict = convert_to_wiki(d)
        metadata_text = f"{metadata_text}\n{metadata}"
        import_to_wiki(wiki_dict)
   import_to_wiki({"MainPage":f"{main_page}\n{metadata_text}"}) 

if __name__ == "__main__":
    main()

