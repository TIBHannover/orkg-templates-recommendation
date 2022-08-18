TEMPLATED_PAPERS = """PREFIX orkgc: <http://orkg.org/orkg/class/>
PREFIX orkgp: <http://orkg.org/orkg/predicate/>
PREFIX orkgr: <http://orkg.org/orkg/resource/>

SELECT DISTINCT ?template ?templateLabel
       ?templateComponentProperty ?templateComponentPropertyLabel
       ?templateOfResearchField ?templateOfResearchFieldLabel

       ?paper ?paper_label
       ?paper_research_field ?paper_research_field_label
       ?doi
WHERE {
    ?template rdf:type orkgc:ContributionTemplate ;
              rdfs:label ?templateLabel ;
              orkgp:TemplateComponent ?templateComponent .

    FILTER (?template != orkgr:R172145)

    ?templateComponent orkgp:TemplateComponentProperty ?templateComponentProperty .
    ?templateComponentProperty  rdfs:label ?templateComponentPropertyLabel .

    ?template orkgp:TemplateOfClass ?templateOfClass .
    ?templateOfClass rdfs:label ?templateOfClassLabel .

    OPTIONAL { ?template orkgp:TemplateOfResearchField ?templateOfResearchField .
            ?templateOfResearchField rdfs:label ?templateOfResearchFieldLabel } .

    ?contribution rdf:type orkgc:Contribution, ?templateOfClass .
    ?paper orkgp:P31 ?contribution ;
           rdfs:label ?paper_label ;
           orkgp:P30 ?paper_research_field .

    ?paper_research_field rdfs:label ?paper_research_field_label .
    OPTIONAL {{ ?paper orkgp:P26 ?doi }} .


}
ORDER BY ?template"""


PAPERS_QUERY = """PREFIX orkgc: <http://orkg.org/orkg/class/>
    PREFIX orkgp: <http://orkg.org/orkg/predicate/>
    
    SELECT ?paper ?paper_title ?doi ?research_field ?research_field_label
        WHERE {
               ?paper rdf:type orkgc:Paper ;
                      rdfs:label ?paper_title ;
                      orkgp:P30 ?research_field .
               ?research_field rdfs:label ?research_field_label .
               OPTIONAL { ?paper orkgp:P26 ?doi } .
        }
"""

TEMPLATES_RESEARCH_FIELDS = """PREFIX orkgc: <http://orkg.org/orkg/class/>
PREFIX orkgp: <http://orkg.org/orkg/predicate/>
PREFIX orkgr: <http://orkg.org/orkg/resource/>

SELECT DISTINCT ?template ?templateLabel
       ?templateOfResearchField ?templateOfResearchFieldLabel
WHERE {
    ?template rdf:type orkgc:ContributionTemplate ;
              rdfs:label ?templateLabel .

    FILTER (?template != orkgr:R172145)

    OPTIONAL { ?template orkgp:TemplateOfResearchField ?templateOfResearchField .
            ?templateOfResearchField rdfs:label ?templateOfResearchFieldLabel } .
}
ORDER BY ?template"""


def PAPERS_BY_RESEARCH_FIELD_QUERY(research_field):
    return """PREFIX orkgc: <http://orkg.org/orkg/class/>
    PREFIX orkgp: <http://orkg.org/orkg/predicate/>
    
    SELECT ?paper ?paper_title ?doi
        WHERE {{
               ?paper rdf:type orkgc:Paper ;
                      rdfs:label ?paper_title ;
                      orkgp:P30 {}
               OPTIONAL {{ ?paper orkgp:P26 ?doi }} .
        }}""".format(research_field)
