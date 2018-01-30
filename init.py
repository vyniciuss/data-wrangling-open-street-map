import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import json
import os
from pymongo import MongoClient


osm_file = os.path.join("", "boston.osm")

# ================================================== #
#                Regex Expressions                   #
# ================================================== #
# somente contém letras minúsculas e válidas.
lower = re.compile(r'^([a-z]|_)*$')
# para tags válidas com dois pontos no valor.
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
# para tags com caracteres problemáticos.
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# procura por padrões de escrita de endereços no final do texto
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
# para códigos postais válidos
postal_code_re = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$', re.IGNORECASE)
# ================================================== #
#               Load Properties                    #
# ================================================== #
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Highway"]

mapping_street = { "Ave" :  "Avenue",
                    "Ave." : "Avenue",
                    "Ct" :   "Court",
                    "Hwy" :  "Highway",
                    "Park" : "Parkway",
                    "Pkwy" : "Parkway",
                    "Pl" :   "Place",
                    "Rd" :   "Road",
                    "Sq." :  "Square",
                    "St" :   "Street",
                    "st." :  "Street",
                    "ST" :   "Street",
                    "St" :   "Street",
                    "St." :  "Street",
                    "St," :  "Street",
                    "Cambrdige": "Cambridge",
                    "MA":    "Massachusetts"
                  }

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file,  tags=('node', 'way', 'relation', 'tag'), verify_tags = False):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end':
            if verify_tags:
                if elem.tag in tags:
                    yield elem
                    root.clear()
            else:
                yield elem
                root.clear()

                
def print_sorted_dict(dictionary):
    keys = dictionary.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for key in keys:
        value = dictionary[key]
        print("%s: %d" % (key, value))
        
def audit_count_values(dictionary, value, pattern_regex):
    """Pesquisa os padrões de escrita e quantidade de ocorrência dos mesmos.
    
    Preenche o dicionário informado onde a chave será o padrão encontrado 
    e o valor será a soma das ocorrências encontradas.
    
    Args: 
        dictionary: Dicionário com os padrões de escrita.
        value:  Valor que será verificado.
    
    """
    m = pattern_regex.search(value)
    if m:
        value_type = m.group()
        dictionary[value_type] += 1
        
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    return elem.attrib['k'] == "addr:postcode"

def is_valid_tag(elem):
    """Verifica se a tag é válida.
    
    A tag só é válida se possuir os atributos K e V e se não possuir 
    caracteres inválidos no atributo K
    
    """
    value = problemchars.search(elem.get('k'))
    return value == None and 'k' in elem.attrib and 'v' in elem.attrib