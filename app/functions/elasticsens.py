# -*- coding: utf-8 -*-
import requests
import json
import re
import numpy as np
from sympy import symbols, simplify
import math
import config


class ElasticSens:
    '''
    Clase que encapsula los metodos necesarios para calculo de sensibilidad,
    entre otros factores para poder aplicar privacidad diferencial a las consultas
    realizadas en Sparql
    '''
    # Formato : 'http://localhost:3030/<nombre dataset>/query'
    epsilon = 0.1  # Epsilon de privacidad Diferencial
    k = symbols('k')  # usar k como simbolo de operaciones matematicas
    bgp_joinvariables = []

    def __init__(self, new_prefix, debug=False):
        self.url = config.url
        self.debug = debug
        if new_prefix:
            self.prefix = new_prefix
        else:
            self.prefix = config.prefix

    def reset_bgpvariablesjoin(self):
        """
        Reinicia el valor del arreglo de las variables utilizadas para realizar Join
        en los BGP
        """
        self.bgp_joinvariables = []
        return

    def get_bgp_parameters(self, num_bgp):
        """
        Realiza el calculo de parametros y valores para realizar operaciones de
        ElasticSensitivity, con respecto al BGP utilizado.
        Esto principalmente, dependiendo del tamaño del grafo generado por el
        BGP como agrumento, y obteniendo el numero de elementos
        """
        log_n_delta = np.log(num_bgp)
        delta = np.float_power(num_bgp, -(self.epsilon * log_n_delta))
        beta = self.epsilon / (2 * np.log(2 / delta))

        # self.beta = 0.000235
        if self.debug:
            print('num_bgp : ' + num_bgp)
            print('valores parametros:')
            # print('n :'+str(n))
            print('exponente : ' + str(-(self.epsilon * log_n_delta)))
            print('log_n_delta: ' + str(log_n_delta))
            print('delta: ' + str(delta))
            print('beta: ' + str(beta))
        return {'delta': delta, 'beta': beta, 'n': num_bgp}

    def calculate_maxfreq(self, bgp_array):
        """
        Retorna un arreglo de las frecuencias máximas de los componentes
        de un BGP
        """
        max_frequencies = []
        for bgp in bgp_array:
            max_frequencies.append(float(self.get_maxfreq(bgp)))
        return max_frequencies

    def get_maxfreq(self, bgp):
        """
        Calcula la frecuencia máxima de un elemento de un BGP. Esto, realizando una query
        al servidor Fuseki de COUNT de el BGP, y asi retornando la mayor repetición de un
        item
        """
        a, b, c = bgp[0], bgp[1], bgp[2]
        if len(self.bgp_joinvariables) < 1:
            for variable in bgp:
                if re.match('\?\w+', variable):
                    self.bgp_joinvariables.append(variable)

        for variable in bgp:
            if re.match('\?\w+', variable):
                if variable in self.bgp_joinvariables:
                    mf = ' SELECT ' + variable + '  (count(' + variable + ') as ?count) WHERE { ' + a + ' ' + b + ' ' + c + '} GROUP BY ' + variable + ' ORDER BY DESC(?count) LIMIT 1 '
                    if self.debug:
                        print('variable vale: ' + str(variable))
                        print(mf)
                    try:
                        req = requests.post(self.url, data={'query': self.prefix + mf})
                        if self.debug:
                            print(req.text)
                    except:
                        raise ValueError('Error de conexión!, ¿ha iniciado el servidor de Sparql?')
                else:
                    self.bgp_joinvariables.append(variable)
        data = json.loads(req.text)
        return data['results']['bindings'][0]['count']['value']

    def getPolFromBGP(self, max_freqs):
        """
        Obtiene el polinomio de Elastic Sensitivity para el BGP con el cual se
        opera.

        Nota: En el caso de esta Memoria, no hay interesecciones entre las tablas que
        se unen, por lo que la variable "intersection" siempre de mantendria en False.
        """
        if self.debug:
            print('max_freqs vale: ')
            print(max_freqs)
        aux, max_freq = 0, 0
        k = symbols('k')  # usar k como simbolo de operaciones matematicas
        intersection = False
        for i in range(len(max_freqs)):
            if intersection:
                if i == 0:
                    aux = max_freqs[i] + k + max_freqs[i + 1] + k + 1
                    if max_freqs[i] > max_freqs[i + 1]:
                        max_freq = max_freqs[i]
                    else:
                        max_freq = max_freqs[i + 1]
                else:
                    aux = (max_freq + k) * aux + (max_freqs[i + 1] + k) * 1 + aux * 1
                    if max_freqs[i + 1] > max_freq:
                        max_freq = max_freqs[i + 1]
            else:
                max_freq = max([max_freq, max_freqs[i]])
                aux = max_freq + k
        return aux

    def calcElasticSensitivity(self, pol, parameters):
        """
        Calcula el ElasticSensitivity, basado en las frequencias. Retorna una tupla con el valor
        máximo de la ElasticSensitivity, y el k con el cual este fue encontrado.
        """
        max_e_stability = 0
        if self.debug:
            print('pol vale: ')
            print(type(pol))
            print(simplify(pol))
        arr = []
        x_axis = []

        k_index = 1
        expr = pol.subs(self.k, k_index)  # Sustitucion el polinomio
        e_stability = (math.exp(-1 * k_index * parameters['beta'])) * expr

        for i in range(1, parameters['n']):
            k_index = i
            x_axis.append(i)
            expr = pol.subs(self.k, k_index)  # Sustitucion el polinomio
            e_stability_aux = (math.exp(-1 * k_index * parameters['beta'])) * expr
            # if self.debug:
            # print("e stability aux vale: "+str(e_stability_aux)+"; k vale: "+str(k_index)+"; smoothing:"+str(math.exp(-1*k_index*parameters['beta'])))
            if self.debug:
                arr.append(e_stability_aux)
            if e_stability > e_stability_aux:
                max_e_stability = e_stability
                k_value = k_index - 1
                break
            else:
                e_stability = e_stability_aux

        if self.debug:
            # plt.plot(x_axis, arr)
            # plt.show()
            print('max_value vale: ' + str(max_e_stability))
            print('con k igual a: ' + str(k_value))
        return (max_e_stability, k_value)
