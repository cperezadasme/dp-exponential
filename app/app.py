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

restricted_args = {'-r', '-restricted'}
elastic_args = {'-e', '-elastic'}
prefix_args = {'-p', '-prefix'}
mf_args = {'-mf', '-maxfrequencies'}
debug_args = {'-d', '-debug'}
read_folder = {'-rf', '-readfolder'}
iterations_arg = {'-it', '-iterations'}
elastic, restricted, new_prefix, mf, debug = None, None, None, None, False
from_folder = False
max_frecuency = []
path = config.default_path
iterations = 10

for idx, arg in enumerate(sys.argv):
    if arg in restricted_args:
        restricted = True
    elif arg in prefix_args:
        print("Prefix Arg")
        prefix_file = str(sys.argv[idx + 1])
        with open(prefix_file, 'r') as myfile:
            new_prefix = myfile.read().replace('\n', '')
    elif arg in elastic_args:
        elastic = True
    elif arg in restricted_args:
        restricted = True
    elif arg in mf_args:
        mf = True
        max_frecuency = sys.argv[idx + 1].split(',')
    elif arg in read_folder:
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
    elif arg in iterations_arg:
        iterations = int(sys.argv[idx + 1])
    elif arg in debug_args:
        debug = True

if not (elastic and restricted):
    elastic = True  # Analisis por defecto: Elastic Sensitivity

"""
APLICACION
"""

sparql = SparqlQuery(debug=debug)
elasticsens = ElasticSens(new_prefix, debug=debug)

x = 0
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
        x = line
        bgp_array = sparql.extractBGP(x)
        elasticsens.reset_bgpvariablesjoin()
        print("--------------------------------------------\nProcesando linea: " + x + '\n')
        if bgp_array:
            if not mf:
                is_star = sparql.isStarQuery(x)
                if is_star:
                    print("Is Star")
                try:
                    graph = sparql.construct_graph(bgp_array)
                    # import ipdb; ipdb.set_trace()

                    exponential_mechanism = ExponentialMechanism(graph)
                    result = exponential_mechanism.query_with_dp(e=0.1, querynum=10)
                    result = exponential_mechanism.query_with_dp(e=0.5, querynum=10)
                    result = exponential_mechanism.query_with_dp(e=0.8, querynum=10)
                    parameters = elasticsens.get_bgp_parameters(num_bgp)
                    max_freqs = elasticsens.calculate_maxfreq(bgp_array)
                    polinomio = elasticsens.getPolFromBGP(max_freqs)
                    elastic_sens = elasticsens.calcElasticSensitivity(polinomio, parameters)
                    obj = {
                        'query': x,
                        'max_value': elastic_sens[0],
                        'k': elastic_sens[1],
                        'n': num_bgp,
                        'pol': str(polinomio),
                    }
                    if from_folder:
                        obj['filename'] = filename
                    queries.append(obj)
                except Exception as e:
                    print(e)
                    # print("Error en Consulta: Posiblemente este mal realizada, debido a que no tiene un conjunto de datos el BGP")
            else:
                print(elasticsens.calculate_maxfreq(x))
        elif re.match('([0-9]+,)+[0-9]+', x):
            print('Arreglo Reconocido!')
            max_freqs = x.split(',')
            max_freqs = list(map(int, max_freqs))
            polinomio = elasticsens.getPolFromBGP(max_freqs)
            elastic_sens = elasticsens.calcElasticSensitivity(polinomio)
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
        errors.append(abs(true_value - value))
    return np.median(errors)


ofile = open('./results.csv', "w")
writer = csv.writer(ofile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
head = [
    "filename",
    "countQueryResult",
    "countQueryResultPlusNoise",
    "Epsilon",
    "elasticStability",
    "k",
    "queryGraphSize",
    "maxElasticStability",
    "medianError",
    "result1",
    "result2",
    "result3",
    "result4",
    "result5",
    "result6",
    "result7",
    "result8",
    "result9",
    "result10",
]
writer.writerow(head)


for value in queries:
    print(value)
    count = sparql.raw(value['query'])
    count = count[0]['v0_count']['value']
    print("Valor real Count : " + str(count))
    resultados_privdiff = []
    laplace_scale = (2 * value['max_value']) / 0.1
    print('laplace_scale vale: ')
    print(laplace_scale)
    laplace_array = np.random.laplace(scale=laplace_scale, size=iterations)
    print('laplace_array vale :')
    print(laplace_array)
    for i in range(0, iterations):
        laplace = laplace_array[i]
        resultado = float(count) + laplace
        resultados_privdiff.append(resultado)
        print("Resultado " + str(i) + " :" + str(resultado))
    print("Median Error : " + str(median_error(int(count), resultados_privdiff)))
    final_result = float(np.median(resultados_privdiff))
    if from_folder:
        query_input = value['filename']
    else:
        query_input = value['query']
    row = [
        query_input,
        count,
        final_result,
        0.1,
        value['pol'],
        value['k'],
        value['n'],
        value['max_value'],
        median_error(int(count), resultados_privdiff),
        resultados_privdiff[0],
        resultados_privdiff[1],
        resultados_privdiff[2],
        resultados_privdiff[3],
        resultados_privdiff[4],
        resultados_privdiff[5],
        resultados_privdiff[6],
        resultados_privdiff[7],
        resultados_privdiff[8],
        resultados_privdiff[9],
    ]
    writer.writerow(row)

ofile.close()
