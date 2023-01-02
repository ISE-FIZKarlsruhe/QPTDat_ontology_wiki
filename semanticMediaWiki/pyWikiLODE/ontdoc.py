
from collections import defaultdict
from typing import Dict
import shutil
from itertools import chain
from pathlib import Path
from typing import Union
from rdflib import Literal, Graph
from rdflib.namespace import (
    DC,
    DCTERMS,
    FOAF,
    ORG,
    OWL,
    PROF,
    PROV,
    RDF,
    RDFS,
    SDO,
    SKOS,
)

from .utils import (
    load_ontology,
    load_background_onts,
    load_background_onts_titles,
    back_onts_label_props,
    get_ns,
)

from rdf_elements import ONTDOC, AGENT_PROPS, ONT_PROPS, CLASS_PROPS, PROP_PROPS

#RDF_FOLDER = Path(__file__).parent / "rdf"


class PylodeError(Exception):
    pass


class OntDoc:
    """Ontology Document class used to create HTML documentation
    from OWL Ontologies.

    Use:
        # initialise
        od = OntDoc(ontology="some-ontology-file.ttl")
    """

    def __init__(self, ontology: Union[Graph, Path, str]):
        self.ont = load_ontology(ontology)
        self._ontdoc_inference(self.ont)
        self.back_onts = load_background_onts()
        self.back_onts_titles = load_background_onts_titles(self.back_onts)
        self.props_labeled = back_onts_label_props(self.back_onts)

        self.toc: Dict[str, str] = {}
        self.fids: Dict[str, str] = {}
        self.ns = get_ns(self.ont)

        # search ontology title
        t = None
        for s in chain(
            self.ont.subjects(RDF.type, OWL.Ontology),
            self.ont.subjects(RDF.type, PROF.Profile),
            self.ont.subjects(RDF.type, SKOS.ConceptScheme),
        ):
            for o2 in self.ont.objects(s, DCTERMS.title):
                t = str(o2)

        if t is None:
            raise PylodeError(
                "You MUST supply a title property "
                "(dcterms:title, rdf:label or sdo:name) for your ontology"
            )
        self.title = t 
        self.content = []
    
    def _ontdoc_inference(self, g):
        """Expands the ontology's graph to make OntDoc querying easier.

        Uses axioms made up for OntDoc, but they are simple and obvious
        and don't collide with well-known ontologies"""
        # class types
        for s_ in g.subjects(RDF.type, OWL.Class):
            g.add((s_, RDF.type, RDFS.Class))

        # name
        for s_, o in chain(
            g.subject_objects(DC.title),
            g.subject_objects(RDFS.label),
            g.subject_objects(SKOS.prefLabel),
            g.subject_objects(SDO.name),
        ):
            g.add((s_, DCTERMS.title, o))

        # description
        for s_, o in chain(
            g.subject_objects(DC.description),
            g.subject_objects(RDFS.comment),
            g.subject_objects(SKOS.definition),
            g.subject_objects(SDO.description),
        ):
            g.add((s_, DCTERMS.description, o))

        # source
        for s_, o in g.subject_objects(DC.source):
            g.add((s_, DCTERMS.source, o))

        #
        #   Blank Node Types
        #
        for s_ in g.subjects(OWL.onProperty, None):
            g.add((s_, RDF.type, OWL.Restriction))

        for s_ in chain(
            g.subjects(OWL.unionOf, None), g.subjects(OWL.intersectionOf, None)
        ):
            g.add((s_, RDF.type, OWL.Class))

        # we do these next few so we only need to loop through
        # Class & Property properties once: single subject
        for s_, o in g.subject_objects(RDFS.subClassOf):
            g.add((o, ONTDOC.superClassOf, s_))

        for s_, o in g.subject_objects(RDFS.subPropertyOf):
            g.add((o, ONTDOC.superPropertyOf, s_))

        for s_, o in g.subject_objects(RDFS.domain):
            g.add((o, ONTDOC.inDomainOf, s_))

        for s_, o in g.subject_objects(SDO.domainIncludes):
            g.add((o, ONTDOC.inDomainIncludesOf, s_))

        for s_, o in g.subject_objects(RDFS.range):
            g.add((o, ONTDOC.inRangeOf, s_))

        for s_, o in g.subject_objects(SDO.rangeIncludes):
            g.add((o, ONTDOC.inRangeIncludesOf, s_))

        for s_, o in g.subject_objects(RDF.type):
            g.add((o, ONTDOC.hasMember, s_))

        #
        #   Agents
        #
        # creator
        for s_, o in chain(
            g.subject_objects(DC.creator),
            g.subject_objects(SDO.creator),
            g.subject_objects(SDO.author),
        ):
            g.remove((s_, DC.creator, o))
            g.remove((s_, SDO.creator, o))
            g.remove((s_, SDO.author, o))
            g.add((s_, DCTERMS.creator, o))

        # contributor
        for s_, o in chain(
            g.subject_objects(DC.contributor),
            g.subject_objects(SDO.contributor),
        ):
            g.remove((s_, DC.contributor, o))
            g.remove((s_, SDO.contributor, o))
            g.add((s_, DCTERMS.contributor, o))

        # publisher
        for s_, o in chain(
            g.subject_objects(DC.publisher), g.subject_objects(SDO.publisher)
        ):
            g.remove((s_, DC.publisher, o))
            g.remove((s_, SDO.publisher, o))
            g.add((s_, DCTERMS.publisher, o))

        # indicate Agent instances from properties
        for o in chain(
            g.objects(None, DCTERMS.publisher),
            g.objects(None, DCTERMS.creator),
            g.objects(None, DCTERMS.contributor),
        ):
            g.add((o, RDF.type, PROV.Agent))

        # Agent annotations
        for s_, o in g.subject_objects(FOAF.name
            g.add((s_, SDO.name, o))

        for s_, o in g.subject_objects(FOAF.mbox):
            g.add((s_, SDO.email, o))

        for s_, o in g.subject_objects(ORG.memberOf):
            g.add((s_, SDO.affiliation, o))



    def make_wiki(self, destination: Path = None):

        """Makes the complete OntDoc Wiki document."""
        
        # create schema.org graph TODO add to SMW
        #_ = self._make_schema_org()

        self._make_metadata()
        self._make_main_sections()
        self._make_namespaces()

    def _make_metadata(self):
        # get all ONT_PROPS props and their (multiple) values
        this_onts_props = defaultdict(list)
        for s_ in chain(
            self.ont.subjects(predicate=RDF.type, object=OWL.Ontology),
            self.ont.subjects(predicate=RDF.type, object=SKOS.ConceptScheme),
            self.ont.subjects(predicate=RDF.type, object=PROF.Profile),
        ):
            iri = s_
            for p_, o in self.ont.predicate_objects(s_):
                if p_ in ONT_PROPS:
                    this_onts_props[p_].append(o)

        wikiDict["title"] = this_onts_props[DCTERMS.title]
        wikiDict["iri"] = str(iri)
        for in ONT_PROPS:
            if 
                wikiDict[]

# TODO make new overview page based on ONT_PROPS
        # create title 
        this_onts_props[DCTERMS.title]
        #Metadata
        #IRI
        str(iri)

        # print all available ONT_PROPS (iterating over it )
        # using
        # prop_obj_pair_html( self.ont, self.back_onts, self.ns, "dl", prop, self.props_labeled[prop]["title"], self.props_labeled[prop]["description"], self.props_labeled[prop]["ont_title"], self.fids, this_onts_props[prop], )


    def _make_schema_org(self):
        sdo = Graph()
        for ont_iri in chain(
            self.ont.subjects(predicate=RDF.type, object=OWL.Ontology),
            self.ont.subjects(predicate=RDF.type, object=SKOS.ConceptScheme),
            self.ont.subjects(predicate=RDF.type, object=PROF.Profile),
        ):
            sdo.add((ont_iri, RDF.type, SDO.DefinedTermSet))
            for p_, o in self.ont.predicate_objects(ont_iri):
                if p_ == DCTERMS.title:
                    sdo.add((ont_iri, SDO.name, o))
                elif p_ == DCTERMS.description:
                    sdo.add((ont_iri, SDO.description, o))
                elif p_ == DCTERMS.publisher:
                    sdo.add((ont_iri, SDO.publisher, o))
                    if not isinstance(o, Literal):
                        for p2, o2 in self.ont.predicate_objects(o):
                            if p2 in AGENT_PROPS:
                                sdo.add((o, p2, o2))
                elif p_ == DCTERMS.creator:
                    sdo.add((ont_iri, SDO.creator, o))
                    if not isinstance(o, Literal):
                        for p2, o2 in self.ont.predicate_objects(o):
                            if p2 in AGENT_PROPS:
                                sdo.add((o, p2, o2))
                elif p_ == DCTERMS.contributor:
                    sdo.add((ont_iri, SDO.contributor, o))
                    if not isinstance(o, Literal):
                        for p2, o2 in self.ont.predicate_objects(o):
                            if p2 in AGENT_PROPS:
                                sdo.add((o, p2, o2))
                elif p_ == DCTERMS.created:
                    sdo.add((ont_iri, SDO.dateCreated, o))
                elif p_ == DCTERMS.modified:
                    sdo.add((ont_iri, SDO.dateModified, o))
                elif p_ == DCTERMS.issued:
                    sdo.add((ont_iri, SDO.dateIssued, o))
                elif p_ == DCTERMS.license:
                    sdo.add((ont_iri, SDO.license, o))
                elif p_ == DCTERMS.rights:
                    sdo.add((ont_iri, SDO.copyrightNotice, o))

        return sdo

    def _make_main_sections(self):
        with self.content:
            if (None, RDF.type, OWL.Class) in self.ont:
                d = section_html(
                    "Classes",
                    self.ont,
                    self.back_onts,
                    self.ns,
                    OWL.Class,
                    CLASS_PROPS,
                    self.toc,
                    "classes",
                    self.fids,
                    self.props_labeled,
                )
                d.render()

            if (None, RDF.type, RDF.Property) in self.ont:
                d = section_html(
                    "Properties",
                    self.ont,
                    self.back_onts,
                    self.ns,
                    RDF.Property,
                    PROP_PROPS,
                    self.toc,
                    "properties",
                    self.fids,
                    self.props_labeled,
                )
                d.render()

            if (None, RDF.type, OWL.ObjectProperty) in self.ont:
                d = section_html(
                    "Object Properties",
                    self.ont,
                    self.back_onts,
                    self.ns,
                    OWL.ObjectProperty,
                    PROP_PROPS,
                    self.toc,
                    "objectproperties",
                    self.fids,
                    self.props_labeled,
                )
                d.render()

            if (None, RDF.type, OWL.DatatypeProperty) in self.ont:
                d = section_html(
                    "Datatype Properties",
                    self.ont,
                    self.back_onts,
                    self.ns,
                    OWL.DatatypeProperty,
                    PROP_PROPS,
                    self.toc,
                    "datatypeproperties",
                    self.fids,
                    self.props_labeled,
                )
                d.render()

            if (None, RDF.type, OWL.AnnotationProperty) in self.ont:
                d = section_html(
                    "Annotation Properties",
                    self.ont,
                    self.back_onts,
                    self.ns,
                    OWL.AnnotationProperty,
                    PROP_PROPS,
                    self.toc,
                    "annotationproperties",
                    self.fids,
                    self.props_labeled,
                )
                d.render()

            if (None, RDF.type, OWL.FunctionalProperty) in self.ont:
                d = section_html(
                    "Functional Properties",
                    self.ont,
                    self.back_onts,
                    self.ns,
                    OWL.FunctionalProperty,
                    PROP_PROPS,
                    self.toc,
                    "functionalproperties",
                    self.fids,
                    self.props_labeled,
                )
                d.render()

    def _make_namespaces(self):
        # get only namespaces used in ont
        nses = {}
        for n in chain(
                self.ont.subjects(),
                self.ont.predicates(),
                self.ont.objects()
        ):
            for prefix, ns in self.ont.namespaces():
                if str(n).startswith(ns):
                    nses[prefix] = ns

        with self.content:
            with div(id="namespaces"):
                h2("Namespaces")
                with dl():
                    if self.toc.get("namespaces") is None:
                        self.toc["namespaces"] = []
                    for prefix, ns in sorted(nses.items()):
                        p_ = prefix if prefix != "" else ":"
                        dt(p_, id=p_)
                        dd(code(ns))
