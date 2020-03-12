import sys, re
from functions import SparqlQuery
from tabulate import tabulate
from SPARQLWrapper import SPARQLWrapper2

prefix_args = {'-p', '-prefix'}
debug_args = {'-d', '-debug'}
new_prefix, debug = None, False

for idx, arg in enumerate(sys.argv):
    if arg in prefix_args:
        prefix_file = str(sys.argv[idx+1])
        with open(prefix_file, 'r') as myfile:
            new_prefix = myfile.read().replace('\n', '')
            sparql.setPrefix(new_prefix)
    elif arg in debug_args:
        debug = True

sparql = SparqlQuery(debug=debug)
x = 0
infile = open("./query.txt", "r")
sparqlwrapper = SPARQLWrapper2(sparql.url)
lines = infile.read().strip().split("\n")
for query in lines:
    if re.match('^\s*$',query) or (re.match(r'^\#(.+)',query)):
        pass
    elif re.match('(CONSTRUCT)', query):
        print("CONSTRUCT QUERY!")
        sparqlwrapper.setQuery(sparql.prefix+' '+query)
        graph = sparqlwrapper.query().convert().contexts()
        for element in graph:
            print("CANTIDAD DE ELEMENTOS DEL BGP")
            print(len(element))
    else:
        sparql.isStarQuery(query)
        print("--------------------------------------------\nProcesando consulta: "+query+'\n')
        sparqlwrapper.setQuery(sparql.prefix+' '+query)
        data = []
        for result in sparqlwrapper.query().bindings:
            aux = []
            for index, x in enumerate(result, start=0):
                aux.append(str(result[x].value)+'; type:'+str(result[x].type))
            data.append(aux)
        print(tabulate(data, headers=sparqlwrapper.query().head['vars'], tablefmt='orgtbl'))
        print("--------------------------------------------")

infile.close()
