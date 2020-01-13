# url: Endpoint para realizar queries de Sparql en un servidor Apache Jena
# Formato : 'http://localhost:3030/<nombre dataset>/query'
url = 'http://localhost:3030/dataset/query'

# Prefix para WatDiv
prefix = '''
PREFIX wsdbm: <http://db.uwaterloo.ca/~galuc/wsdbm/>
PREFIX sorg: <http://schema.org/>
PREFIX gn: <http://www.geonames.org/ontology#>
PREFIX gr: <http://purl.org/goodrelations/>
PREFIX mo: <http://purl.org/ontology/mo/>
PREFIX og: <http://ogp.me/ns#>
PREFIX rev: <http://purl.org/stuff/rev#>
PREFIX foaf: <http://xmlns.com/foaf/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dc: <http://purl.org/dc/terms/>
'''

default_path = '/home/aczombie/memoria_herramientas/TestsProfe/PrivacyEvaluation/queries/selected'
