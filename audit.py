def count_tags(filename):
    """
    Percorre a ávore de elementos em buscas da quantidade de tags 
    que o arquivo possui.
    
    Args: 
        filename: O arquivo que será análisado.
    
    Returns: 
        Um dicionário com o nome da tag como chave e o total
        de registros encontrados.
        
        {'bounds': 1,
         'member': 36052,
         'meta': 1,
         'nd': 421429}
        
    """
    tags = {}
    for element in get_element(osm_file, verify_tags = False):
        if element.tag not in tags.keys():
            tags[element.tag] = 1
        else:
            tags[element.tag] += 1
    return tags
    

def key_type(element, keys):
    """ Conta a quantidade de padrões encontrados em "K".
     
    Para cada valor encontrado em K, soma-se 1 ao seu 
    padrão correspondente.
    
    Args: 
        element: O elemento que será análisado.
        keys: dicionário com os padrões esperados.
    
    Returns: 
        Um dicionário com nome do padrão e o total de ocorrências encontradas.
        
        {'lower': 148488, 'lower_colon': 30911, 'other': 8092, 'problemchars': 0}
        
    """
    if lower.match(element.attrib['k']):
        keys['lower'] += 1
    elif lower_colon.match(element.attrib['k']):
        keys['lower_colon'] += 1
    elif problemchars.search(element.attrib['k']):
        keys['problemchars'] += 1
    else:
        keys['other'] += 1
    return keys



def process_map(filename):
    """ Processa os dados em busca de padrões no valor de "K".
     
    Define um dicionário com os padrões dos dados esperados em "K" 
    e percorre a ávore de elementos em buscas da quantidade de 
    itens que se encaixem nos padrões.
    
    Padrões dos valores esperados em K:
    
        - lower: somente contém letras minúsculas e válidas.
        - lower_colon: para tags válidas com dois pontos no valor.
        - problemchars: para tags com caracteres problemáticos.
        - other: para outras tags que não se enquadrem nas outras três
                 categorias.
    
    Args: 
        filename: O arquivo que será análisado.
    
    Returns: 
        Um dicionário com nome do padrão e o total de ocorrências encontradas.
        
        {'lower': 148488, 'lower_colon': 30911, 'other': 8092, 'problemchars': 0}
        
    """
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for element in get_element(osm_file, tags=('tag'), verify_tags = True):
        keys = key_type(element, keys)

    return keys


def get_user(element):
    """Recupera o usuário que contribuiu com o mapa.
    
    Args: 
        element: O elemento que será análisado.
    
    Returns: 
        O identificador do usuário encontrado
        
    """
    
    if element.get('uid'):
        uid = element.attrib["uid"]
        return uid
    else:
        return None


def process_map_user(filename):
    """ Processa os dados em busca dos usuários que contribuíram com os dados.
     
    Para para cada tag (node, way, relation) encontrada, recupera o usuário e adiona em um set.

    Args: 
        filename: O arquivo que será análisado.
    
    Returns: 
        Um set com os usuários encontrados.
        
        {'100042', '100049', '100054'}
        
    """
    users = set()
    for element in get_element(osm_file, tags=('node', 'way', 'relation'), verify_tags = True):
        if get_user(element):
             users.add(get_user(element))

    return users



street_types = defaultdict(int) 
def audit_street_occurrences(filename, pattern_regex):
    """Realiza auditoria nos padrões dos nomes das ruas cadastrados.
    
    
     Args: 
        filename: O arquivo que será análisado.
        pattern_regex: padrão que será pesquisado.
    """
    for elem in get_element(filename, tags=('tag'), verify_tags = True):
        if is_street_name(elem):
            audit_count_values(street_types, elem.attrib['v'], pattern_regex)    
    print_sorted_dict(street_types)
   


postal_codes_types = {"Válidos": [], "Inválidos" : []}

def audit_postal_code(filename, pattern_regex):
    """Realiza auditoria nos padrões dos códigos postais cadastrados.
        
    Args: 
        filename: O arquivo que será análisado.
        pattern_regex: padrão que será pesquisado.
        
    """
    for elem in get_element(filename, tags=('tag'), verify_tags = True):
        if is_postal_code(elem):
            value = elem.get('v')
            if pattern_regex.match(value):
                postal_codes_types["Válidos"].append(value)
            else:
                postal_codes_types["Inválidos"].append(value)
                
    print('Foram encontrados {} códigos postais válidos'.format(len(postal_codes_types["Válidos"])))
    print('---------------------------------------------------------------------------------------')
    print('|Exemplo de códigos válidos encontrados {} '.format(postal_codes_types["Válidos"][0:5]))
    print('---------------------------------------------------------------------------------------')
    print('Foram encontrados {} códigos postais inválidos.'.format(len(postal_codes_types["Inválidos"])))
    print('---------------------------------------------------------------------------------------')
    print('|Exemplo de códigos inválidos encontrados {} '.format(postal_codes_types["Inválidos"]))
    print('---------------------------------------------------------------------------------------')



