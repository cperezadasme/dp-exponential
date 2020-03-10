import numpy as np


class ExponentialMechanism:
    """
    Mecanismo exponencial
    """

    def __init__(self, graph):
        self.graph = graph
        self.sensitivity = self._calculate_sensitivity()
        self._create_freq_dict()

    def _calculate_sensitivity(self):
        """
        Función para calcular sensibilidad
        En este caso es 1, dado que esta dado por presencia o ausencia de una oferta
        """
 
        return 1

    def _create_freq_dict(self):
        """
        Función para crear diccionario de precios, cantidad y probabilidad de una oferta.
        A partir del subgrafo generado por la consulta
        """

        self.offers_count = {}
        self.offers_prop = {}
        self.offers_price = {}

        for element in self.graph:
            element_id = element['@id']

            # Se obtiene los precios de la oferta, esto se utilizará para calcular la utilidad
            if 'Offer' in element_id:
                if element_id not in self.offers_price.keys():
                    price  = element.get('http://purl.org/goodrelations/price', None)
                    if price:
                        value = element['http://purl.org/goodrelations/price'][0]['@value']
                    else:
                        value = 1
                    self.offers_price[element_id] = int(value)

            # Se cuentan las conexiones a una oferta
            if 'Retailer' in element_id:
                for offer in element['http://purl.org/goodrelations/offers']:
                    offer_id = offer['@id']

                    if offer_id not in self.offers_count.keys():
                        self.offers_count[offer_id] = 1
                    else:
                        self.offers_count[offer_id] += 1

        total = sum(self.offers_count.values())

        for offer_id, count in self.offers_count.items():
            self.offers_prop[offer_id] = count / total

    def _exponential(self, u, e):
        """
        Retorna la probabilidad exponencial. A partir de la utilidad, epsilon y sensibilidad
        """

        return np.random.exponential(e * u / (2 * self.sensitivity))

    def query_with_dp(self, e=1, querynum=1000):
        """
        Retorna el ruido total de la consulta, dado que calcula la probabilidad exponencial para cada elemento,
        luego las suma y entrega el resultado agregado.
        
        Responde una lista según la cantidad de veces que se repita la consulta
        """

        response = []

        for _ in range(querynum):
            weights = []
            if self.offers_prop:
                for offer_id, prop in self.offers_prop.items():
                    weights.append(self._exponential(self.offers_price[offer_id] * prop, e))
            else:
                total = len(self.offers_price.keys())
                prop = 1 / total
                for offer_id, price in self.offers_price.items():
                    weights.append(self._exponential(price * prop, e))

            response.append(int(sum(weights)))

        return response

#     def calc_groundtruth(self):
#         """
#         calculate the groundtruth
#         the most frequent education value

#         Returns:  
#             [string] -- [most frequent education value]
#         """

#         eduidx = ATTNAME.index('education')
#         return Counter([record[eduidx] for record in self.records if record[eduidx] != '*']).most_common(1)[0][0]

#     def calc_distortion(self, queryres):
#         """
#         calculate the distortion

#         Arguments:
#             queryres {[list]} -- [query result]

#         Returns:
#             [float] -- [distortion]
#         """

#         return 1 - Counter(queryres)[self.calc_groundtruth()] / len(queryres)


# def prove_indistinguishable(queryres1, queryres2):
#     """
#     proove the indistinguishable for two query results

#     Arguments:
#         queryres1 {[list]} -- [query 1 result]
#         queryres2 {[list]} -- [query 2 result]

#     Returns:
#         [float] -- [probability quotient]
#     """

#     prob1 = Counter(queryres1)
#     for key in prob1:
#         prob1[key] /= len(queryres1)
#     prob2 = Counter(queryres2)
#     for key in prob2:
#         prob2[key] /= len(queryres2)
#     res = 0
#     num = 0
#     for key in prob1:
#         if key not in prob2:
#             print('no query result {} in query 2'.format(key))
#             continue
#         res += prob1[key] / prob2[key]
#         num += 1
#     res1overres2 = res / num
#     res = 0
#     num = 0
#     for key in prob2:
#         if key not in prob1:
#             print('no query result {} in query 1'.format(key))
#             continue
#         res += prob2[key] / prob1[key]
#         num += 1
#     res2overres1 = res / num
#     return res1overres2, res2overres1


# if __name__ == "__main__":
#     records = readdata()
#     ExpMe = ExponentialMechanism(records)
#     res1 = ExpMe.query_with_dp(0.05, 1000)
#     # res2 = ExpMe.query_with_dp(0.05, 1000)
#     v1, v2, v3 = generate_data_for_exponential_mechanism(records)
#     ExpMe2 = ExponentialMechanism(v1)
#     res2 = ExpMe2.query_with_dp(0.05, 1000)
#     # print(res1)
#     print(ExpMe.calc_distortion(res1))
#     print(ExpMe.calc_distortion(ExpMe.query_with_dp(1, 1000)))
#     print(ExpMe.calc_distortion(res2))
#     print(prove_indistinguishable(res1, res2))
#     print(prove_indistinguishable(res2, res1))
#     print(math.exp(0.05))
