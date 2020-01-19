# -*- coding: utf-8 -*-
import json
import re
import config
from SPARQLWrapper import SPARQLWrapper, JSON


class SparqlQuery:
    '''
    Clase "Wrapper" de Sparql para poder realizar consultas a la libreria HDT.
    La idea, es encapsular operaciones de consultas, para poder obtener entidades
    de la base de datos, para posteriormente realizar operaciones como inserciones,
    borrar o añadir arcos, realizar counts, entre otros
    '''

    def __init__(self, debug=False):
        self.url = config.url
        self.prefix = config.prefix
        self.debug = debug

    def setPrefix(self, prefix):
        """
        Fija el Prefijo para poder realizar consultas SPARQL, a través del
        definido por argumentos, o el que esta configurado por defecto en config.py
        """
        self.prefix = prefix

    def isStarQuery(self, query):
        """
        Código para identificar si un BGP es una Star query o no. Esto se hace
        analizando los componentes del BGP, y comprobando si algun sujeto se
        repite más de una vez, lo que implicaria que es Star Query.
        Si todos los sujetos de repiten 1 pura vez, entonces el BGP no es un
        Star Query
        """
        matches = re.findall(r'([A-Za-z0-9\?\:]+\s[A-Za-z0-9\?\:]+\s[A-Za-z0-9\?\:]+)(?=\s\.)', query)
        if matches:
            subjects = {}
            for match in matches:
                bgp = re.compile("\s").split(match)
                if bgp[0] in subjects:
                    subjects[bgp[0]] += 1
                else:
                    subjects[bgp[0]] = 1
            for subject in subjects:
                if subjects[subject] > 1:
                    if self.debug:
                        print("Es una Star Query!")
                    return True
        return False

    def extractBGP(self, query):
        """
        De una query, o un BGP por si solo, reconoce si la linea colocada corresponde a
        un BGP. Retorna las variables o constantes de los triples en forma (s,l,p)
        para su posterior uso en el analisis.

        Si encuentra el BGP con sus componentes, retorna un arreglo con ellos.
        De lo contrario, retorna None
        """
        from_fullquery = re.findall(r'(?<=WHERE\s\{)(.*?)(?=\})', query, re.IGNORECASE)
        if from_fullquery:
            bgp_array = re.findall(r'([^-\s]+\s[^-\s]+\s[^-\s]+)(?=\s\.)', from_fullquery[0])
        elif re.match("(\?\w+|<[A-Za-z0-9\:\.\/\#\~]+>|\w+\:\w+)\s+(\?\w+|<[A-Za-z0-9\:\.\/\#\~]+>|\w+\:\w+)\s+(\?\w+|<[A-Za-z0-9\:\.\/\#\~]+>|\w+\:\w+)", query):
            bgp_array = re.findall(r'([A-Za-z0-9\?\:]+\s[A-Za-z0-9\?\:]+\s[A-Za-z0-9\?\:]+)(?=\s\.)', query)
        else:
            return None
        bgp = []
        for value in bgp_array:
            aux = re.split('\t|\s', value)
            bgp.append(aux)
        if self.debug:
            print('BGP Reconocido!')
        return bgp

    def construct_graph(self, bgp):
        """
        Retorna un subgrafo RDF en formate JSON que se obtiene al realizar una consulta CONSTRUCT
        """
        aux = []
        for pattern in bgp:
            pattern_str = ' '.join(pattern)
            aux.append(pattern_str)
        bgp_string = ' . '.join(aux)
        sparqlwrapper = SPARQLWrapper(self.url)
        print('CONSTRUCT QUERY: ' + 'CONSTRUCT WHERE {' + bgp_string + '}')
        sparqlwrapper.setQuery(self.prefix + ' ' + 'CONSTRUCT WHERE {' + bgp_string + '}')
        sparqlwrapper.setReturnFormat(JSON)
        graph = sparqlwrapper.query().convert()
        results = graph.serialize(format='application/ld+json')
        return json.loads(results)

    def raw(self, query, prefix=None):
        """
        Realiza una consulta normal al servidor SPARQL
        """
        if not prefix:
            query = self.prefix  + ' ' + query

        sparqlwrapper = SPARQLWrapper(self.url)
        sparqlwrapper.setQuery(query)
        sparqlwrapper.setReturnFormat(JSON)
        data = sparqlwrapper.query().convert()
        count = data['results']['bindings'][0]['v0_count']['value'] 
        return count
