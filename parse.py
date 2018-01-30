CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
ADDRESS = [ "housenumber", "postcode", "street"]

def shape_element(element):
    """Modela um elemento dentro do dicionário.
    
    Converte um elemento xml em um dicionário. 
    
    Returns: 
            Um dicionário com as informações estruturadas
    
    """
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node["type"] = element.tag
        if "lat" in element.attrib and "lon" in element.attrib:
            node["pos"] = [float(element.get('lat')), float(element.get('lon'))]
            
        for attr in element.attrib:
            if attr in ['lat', 'lon']:
                continue
            elif attr in CREATED:
                if "created" not in node:
                    node["created"] = {}
                node["created"][attr] = element.get(attr)
            else:
                node[attr] = element.get(attr)
                
        address_dic = {}
        building_dic = {}
        mapper_second_level_elements(element, node, address_dic, building_dic)
        add_addres(address_dic, node)
        add_building(building_dic, node)
        
        return node
    else:
        return None

def add_addres(address_dic, node):
    """Adiciona dados de endereço no elemento principal.
    
    Caso existam dados de endereço nos elementos de segundo nível,
    estes serão adionados ao elemento principal como um atributo.
    
    Args: 
        address_dic: dicionário com dados de endereço
        node: dicinário que contém as informações do elemento.
    
    """
    if  len(address_dic) > 0:
        node["address"] = {}
        for key in ADDRESS:
            if key in address_dic:
                node["address"][key] = address_dic[key]

def add_building(building_dic, node):
    """Adiciona dados da construção no elemento principal.
    """
    if len(building_dic) > 0:
        node["building"] = building_dic
        
def mapper_second_level_elements(element, node, address_dic, building_dic):
    """Responsável por navegar entre as tags de segundo nível do elemento principal.
    
    Realiza iteração entre os elementos de segundo nível, a fim de estruturar e 
    armazenar suas informações.
    
    Args: 
        element: elemento de nível superior.
        node: dicinário que contém as informações do elemento.
        address_dic: dionário que armazenará os dados de endereço.
        building_dic: dicionário que armazenará os dados da construção.
    
    """
    for elem in element:
        if elem.tag == 'nd':
            mapper_nd(node, elem)
        if elem.tag == 'tag' and is_valid_tag(elem):
            mapper_tag(node, elem, address_dic, building_dic)
                
def mapper_tag(node, elem, address, building):
    """Extrai as informações da tag e separa de acordo com o tipo.
    
    Args: 
        elem: tag que terá seus dados extraídos.
        node: dicinário que contém as informações do elemento.
        address_dic: dionário que armazenará os dados de endereço.
        building_dic: dicionário que armazenará os dados da construção.
    
    """
    if "address" in elem.get('k'):
        return
    elif 'addr:' in elem.get('k'):
        mapper_addr(elem, address)
    elif 'building' in elem.get('k'):
        mapper_building(elem, building)
    else:
        node[elem.get('k')] = elem.get('v')
 

def mapper_building(elem, building):
    """Extrai as informações do elemento do tipo tag e com valor k ="building...
    
    Args: 
        elem: tag que terá seus dados extraídos.
        building_dic: dicionário que armazenará os dados da construção.
    
    """
    k = elem.get('k')
    v = elem.get('v')
    if 'building:' in k:
        k = k.replace('building:', '')
        building[k] = v
    else:
        building[k] = v

def mapper_addr(elem, address):
    """Extrai as informações do elemento do tipo tag e com valor k ="addr...
    
    Args: 
        elem: tag que terá seus dados extraídos.
        address: dicionário que armazenará os dados do endereço.
    
    """
    k = elem.get('k')
    v = elem.get('v')
    k = k.replace('addr:', '')
    if is_postal_code(elem):
        address[k] = update_postal_code(v)
    elif "street" in k:
        k = k.replace('street:', '')
        if k in ADDRESS:
            address[k] = update_name(v, mapping_street)
    else:
        if k in ADDRESS:
            address[k] = v

def mapper_nd(node, elem):
    """Extrai as informações do elemento do tipo nd.
    
    Args: 
        elem: tag que terá seus dados extraídos.
        node: dicionário que armazenará o valor de ref.
    
    """
    if "node_refs" not in node:
        node["node_refs"] = []
    if 'ref' in elem.attrib:
        node["node_refs"].append(elem.get("ref"))

def process_map(file_in, pretty = False):
    """Processa o mapa e converte de XML para JSON.
    
     Args: 
        file_in: mapa que será processado e convertido em JSON.
        pretty: Se True, irá adicionar espaços adionais no arquivo de saída
    
    """
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
