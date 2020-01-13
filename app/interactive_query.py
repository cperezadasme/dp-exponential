import pprint
from tabulate import tabulate
from functions import SparqlQuery
from SPARQLWrapper import SPARQLWrapper, N3, SPARQLWrapper2
"""
Programa interactivo de consultas de Query SPARQL

Se utiliza el plugin de SPARQLWrapper, para poder realizar consultas a Fuseki, y que estas posteriormente sean respondidas
en tablas a través de linea de comandos para su comprensión
"""

sparql = SparqlQuery()
sparqlwrapper = SPARQLWrapper2(sparql.url)

a = input("Enter a query: ")
while a != ("stop"):
    sparqlwrapper.setQuery(sparql.prefix +' '+ a)
    data = []
    #print(dir(sparqlwrapper.query()))
    #print(sparqlwrapper.query().head)
    for result in sparqlwrapper.query().bindings:
        aux = []
        for index, x in enumerate(result, start=0):
            aux.append(str(result[x].value)+'; type:'+str(result[x].type))
        data.append(aux)
    print(tabulate(data, headers=sparqlwrapper.query().head['vars'], tablefmt='orgtbl'))
    a = input("Enter a query: ")
