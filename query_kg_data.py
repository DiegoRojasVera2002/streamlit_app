from neo4j import GraphDatabase
import json
from random import random
import json
from collections import defaultdict

class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None, db=None):
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            # Collect all records at once to avoid ResultConsumedError
            return [record for record in result]

import random

def query_kg(date: str = '13-08-2024'):
    print("fecha a filtrar: ", date)
    query = f"""MATCH (e:News)-[:HAS_THEME]->(t:Theme)
        WHERE e.date = '{date}'
        OPTIONAL MATCH (e)-[:INVOLVES]->(p:Person)
        OPTIONAL MATCH (e)-[:INVOLVES_ORGANIZATION]->(o:Organization)
        OPTIONAL MATCH (e)-[:REPORTED_BY]->(s:Source)
        
        RETURN e.id AS NewsID, 
            e.title AS Title, 
            e.date AS Date, 
            e.tone AS Tone, 
            e.content AS Content, 
            e.first_sourceurl AS SourceURL,
            t.name AS Topic, 
            p.name AS Person, 
            o.name AS Organization, 
            s.name AS Source,
            'HAS_THEME' AS RelacionTopic,
            'INVOLVES' AS RelacionPersona, 
            'INVOLVES_ORGANIZATION' AS RelacionOrganizacion
        LIMIT 500
        """
    conn = Neo4jConnection(uri="neo4j+s://614dfd28.databases.neo4j.io", user="neo4j" , pwd="iSqda4HLJiAZo1TgAyRH0SrvYyj9Nd3olNj6PvZ33sE")
    results = conn.query(query)
    data =[]
    
    for result in results:
       data.append(dict(result))
    # Crear la estructura jerárquica
       

    # Initialize the final structure
    structured_data = {
        "Fecha": date,
        "Noticias": []
    }

    # Process each news entry
    for entry in data:
        noticia = {
            "Noticia": entry['Title'],
            "embedding": entry['Tone'],
            "title": entry['Title'],
            "source": entry['SourceURL'],
            "Relaciones": {
                "Persona": {
                    "Persona": entry['Person'],
                    "RelacionPersona": entry['RelacionPersona']
                },
                "Organizacion": {
                    "Organizacion": entry['Organization'],
                    "RelacionOrganizacion": entry['RelacionOrganizacion']
                },
                "Topico": {
                    "Topic": entry['Topic'],
                    "RelacionTopic": entry['RelacionTopic']
                }
            }
        }
        
        # Append to Noticias list
        structured_data['Noticias'].append(noticia)

    # Output the structured data as JSON
    output_json = json.dumps([structured_data], indent=4)

    print("Este es la data de retorno: ",output_json)

    # Print the JSON output
    data_final= json.loads(output_json)
    return data_final
   

if __name__=="__main__":
    data = query_kg()
    print(data[0]["Fecha"])





