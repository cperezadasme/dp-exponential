import numpy as np
import config


class ExponentialMechanism:
    """
    Mecanismo exponencial
    """

    def __init__(self, graph):
        self.is_wikidata = 'wikidata' in config.url
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

        if self.is_wikidata:
            total = 0
            for element in self.graph:
                element_id = element['subject']['value']
                total += 1
                if element_id in self.offers_count.keys():
                    self.offers_count[element_id] += 1
                else:
                    self.offers_count[element_id] = 1

        else:
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
                    if self.is_wikidata:
                        utility = self.offers_count[offer_id]
                    else:
                        utility = self.offers_price[offer_id] * prop
                    weights.append(self._exponential(utility, e))
            else:
                total = len(self.offers_price.keys())
                prop = 1 / total 
                for offer_id, price in self.offers_price.items():
                    weights.append(self._exponential(price * prop, e))
            response.append(int(sum(weights)))

        return response
