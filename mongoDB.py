#abrindo conexão
client = MongoClient("mongodb://localhost:27017")
db = client.project

#Importando dados no MongoDB
data = []    
with open('boston.osm.json') as f:
    
    for line in f:
        data.append(json.loads(line))
        
db.streetmap.insert_many(data)
print( db.streetmap.find_one())

#Número de documentos
print("Existem {} documentos cadastrados".format(db.streetmap.find().count())) 

#Número de nós e caminhos
print("Existem {} nodes cadastrados".format(db.streetmap.find({"type" : "node"}).count()))
print("Existem {} ways cadastrados".format(db.streetmap.find({"type" : "way"}).count())) 

#Número de usuários únicos
print("Existem {} usuários cadastrados".format(len(db.streetmap.distinct("created.user"))))

#Número de dormitórios
print("Existem {} dormitórios cadastrados".format(db.streetmap.find({'building.building': "dormitory"}).count()))

#Número de universidades
print("Existem {} universidades cadastradas".format(db.streetmap.find({'building.building': "university"}).count()))

#Lista dos 10 usuários que mais contribuíram
group = {"$group" : {"_id" : "$created.user", "count": {"$sum": 1}}}
sort  = {"$sort": {"count": -1}}
limit = {"$limit": 10}
pipeline = [group, sort, limit]

lista = db.streetmap.aggregate(pipeline)
pprint.pprint(list(lista))

# Lista das 10 origens que mais contribuíram
group = {"$group" : {"_id" : "$source", "count": {"$sum": 1}}}
sort  = {"$sort": {"count": -1}}
limit = {"$limit": 10}
pipeline = [group, sort, limit]
lista = db.streetmap.aggregate(pipeline)
pprint.pprint(list(lista))

