def audit_street_type(street_types, street_name):
    """Identifica os padrões de escrita dos endereços e separa em um dicinário. 
    
    Args: 
        street_types: Dicionário que separará os padrões encontrados.
        street_name: endereço que será categorizado.
        
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def audit_street_standardization(osmfile):
    """Realiza auditoria nos padrões dos nomes das ruas cadastrados.
    
    Args: 
        osmfile: arquivo que será analisado.
        
    Returns: 
        Dicionário onde cada padrão encontrado será uma chave e o valor será um
        set dos endereços enquadrados no padrão.
        
    """
    street_types = defaultdict(set)
    for elem in get_element(osm_file, tags=('tag', 'way'), verify_tags = True):
        if 'k' in elem.attrib and is_street_name(elem):
            audit_street_type(street_types, elem.get('v'))
    
    return street_types


def update_name(name, mapping):
    """Atualiza o endereço com problema pelo valor padronizado.
    
    As abreviações encontradas serão substituídas pelos valores completos.
    
    Args: 
        name: endereço.
        mapping: dicionário com os valores desejados.
        
    Returns: 
        Se o endereço informado tiver uma abreviação, então terá seu valor 
        substituído pelo valor completo.
    
    """
    #remove valor indevido
    name = name.replace("#", "")
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping.keys():
                name = re.sub(street_type_re, mapping[street_type], name)
    return name


def update_postal_code(value):
    """Atualiza o código postal com problema pelo valor padronizado.
    
    Args: 
        value: código postal.
        
    Returns: 
        Se o código postal informado estiver fora do padrão, então será ignorado
        e irá retornar None.
    
    """
    if postal_code_re.match(value):
        return value
    else:
        v = value.split()
        if len(v) > 1:
            return v[1]
        elif 'MA' in v[0]:
            return None
        else:
            return v[0]


def audit_fix_postal_code(filename, pattern_regex):
    elements = []
    for elem in get_element(filename, tags=('tag'), verify_tags = True):
        if is_postal_code(elem):
            elements.append(elem.get('v'))
    return elements

elements = audit_fix_postal_code(osm_file, postal_code_re)
