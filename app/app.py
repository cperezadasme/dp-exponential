#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
from functions import ElasticSens, SparqlQuery
from functions.exponential import ExponentialMechanism
import numpy as np
import csv
import os
import glob
import config

"""
ARGUMENTOS DE APP.PY
"""

prefix_args = {'-p', '-prefix'}
debug_args = {'-d', '-debug'}
read_folder = {'-rf', '-readfolder'}
iterations_arg = {'-it', '-iterations'}
epsilon_arg = {'-e', '-epsilon'}
from_folder = False
path = config.default_path

debug=False
iterations = 10
epsilon = 1

# Leer argumentos
for idx, arg in enumerate(sys.argv):
    if arg in prefix_args:
        print("Prefix Arg")
        prefix_file = str(sys.argv[idx + 1])
        with open(prefix_file, 'r') as myfile:
            new_prefix = myfile.read().replace('\n', '')
    if arg in read_folder:
        from_folder = True
        input_lines = []
        try:
            path = str(sys.argv[idx + 1])
        except:
            pass
        for filename in glob.glob(os.path.join(path, '*.rq')):
            infile = open(filename, "r")
            lines = infile.read().strip().split("\n")
            for line in lines:
                input_lines.append({'filename': filename, 'query': line})
        infile.close()
    if arg in iterations_arg:
        iterations = int(sys.argv[idx + 1])
    if arg in debug_args:
        debug = True
    if arg in epsilon_arg:
        epsilon = float(sys.argv[idx + 1])


"""
APLICACION
"""
sparql = SparqlQuery(debug=debug)
queries = []
if not from_folder:
    infile = open("./input-2.txt", "r")
    lines = infile.read().strip().split("\n")
else:
    lines = input_lines

for line in lines:
    if from_folder:
        filename = line['filename']
        line = line['query']
    # COMPROBAR SI LINEA ES UN COMENTARIO O UN ESPACIO
    if (re.match('^\s*$', line)) or (re.match(r'^\#(.+)', line)):
        pass
    else:
        query = line
        bgp_array = sparql.extractBGP(query)
        print("--------------------------------------------\nProcesando linea: " + query + '\n')
        if bgp_array:
            is_star = sparql.isStarQuery(query)
            if is_star:
                print("Is Star")
            try:
                graph = sparql.construct_graph(bgp_array)
                exponential_mechanism = ExponentialMechanism(graph)
                result = exponential_mechanism.query_with_dp(e=epsilon, querynum=iterations)
                obj = {
                    'query': query,
                    'deltas': result,
                    'size': sparql.size,
                }
 
                if from_folder:
                    obj['filename'] = filename
 
                queries.append(obj)
            except Exception as e:
                print(e)
        else:
            print('Input no reconocido')
infile.close()
print("--------------------------------------------")


"""
EVALUACION QUERIES - LAPLACE
"""
def median_error(true_value, results):
    errors = []
    for value in results:
        errors.append(abs(true_value - value)/true_value)
    return np.median(errors)


## Escribir archivo con respuesta
result_file = open(f'./results_{str(epsilon)}.csv', "w")
writer = csv.writer(result_file, delimiter=',', quoting=csv.QUOTE_ALL)
head = [
    "Consulta",
    "Resultado real",
    "Epsilon",
    'Tamaño subggrafo',
    'Mediana resultado',
    'Mediana error',
]

writer.writerow(head)

for value in queries:
    print(value)
    count = sparql.raw(value['query'])
    result_privdiff = []
 
    for delta in value['deltas']:
        count = int(count)
        result_privdiff.append(count + delta)

    error = float(median_error(int(count), result_privdiff) * 100)
    final_result = float(np.median(result_privdiff))

    if from_folder:
        query_input = value['filename']
    else:
        query_input = value['query']

    row = [
        query_input,
        count,
        epsilon,
        value['size'],
        final_result,
        error,
    ]

    if iterations == 10:
        for result in result_privdiff:
            row.append(result)
    writer.writerow(row)

result_file.close()
