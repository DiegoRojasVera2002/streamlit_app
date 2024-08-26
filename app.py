import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json
from collections import defaultdict
import datetime
from query_kg_data import query_kg
import random

# Función para cargar datos desde un archivo JSON


if 'list_topics' not in st.session_state:
    st.session_state['list_topics'] = []
if 'list_news' not in st.session_state:
    st.session_state['list_news'] = query_kg()
if 'date_saved' not in st.session_state:
    st.session_state['date_saved'] = st.session_state['list_news'][0]["Fecha"]

# Function to build nodes and edges based on the hierarchy
def build_graph(data, selected_date, selected_topic):
    nodes = []
    edges = []
    processed_nodes = set()   # Set to track added nodes (to avoid duplicates)
    
    images = {
        "person": "https://cdn-icons-png.flaticon.com/512/6621/6621650.png",
        "organization": "https://cdn-icons-png.flaticon.com/512/7018/7018508.png",
        "new": "https://cdn-icons-png.flaticon.com/512/2964/2964063.png",
    }
    
    for entry in data:
        for noticia in entry['Noticias']:
            topic_relation = noticia['Relaciones']['Topico']
            
            if topic_relation["Topic"] == selected_topic:
                
                # Main topic node
                topic_id = topic_relation["Topic"]
                if topic_id not in processed_nodes:
                    nodes.append(
                        Node(
                            id=topic_id,
                            label=topic_relation["Topic"],
                            color="orange"
                        )
                    )
                    processed_nodes.add(topic_id)
                
                # Associated news node, using source and noticia as unique identifier
                news_id = f"{noticia['Noticia']}_{noticia['source']}"
                if news_id not in processed_nodes:
                    nodes.append(
                        Node(
                            id=news_id,
                            label=noticia['title'],
                            shape="circularImage",
                            image=images["new"]
                        )
                    )
                    processed_nodes.add(news_id)
                
                edges.append(
                    Edge(
                        source=news_id,
                        target=topic_id,
                        label=topic_relation["RelacionTopic"]
                    )
                )

                # Handle multiple persons
                personas = noticia['Relaciones']['Persona']
                if isinstance(personas, list):
                    for persona_relation in personas:
                        persona_id = persona_relation["Persona"]
                        if persona_id not in processed_nodes:
                            nodes.append(
                                Node(
                                    id=persona_id,
                                    label=persona_relation["Persona"],
                                    shape="circularImage",
                                    image=images["person"]
                                )
                            )
                            processed_nodes.add(persona_id)
                        
                        edges.append(
                            Edge(
                                source=persona_id,
                                target=news_id,
                                label=persona_relation["RelacionPersona"]
                            )
                        )
                else:
                    # Single person case
                    persona_id = personas["Persona"]
                    if persona_id not in processed_nodes:
                        nodes.append(
                            Node(
                                id=persona_id,
                                label=personas["Persona"],
                                shape="circularImage",
                                image=images["person"]
                            )
                        )
                        processed_nodes.add(persona_id)
                    
                    edges.append(
                        Edge(
                            source=persona_id,
                            target=news_id,
                            label=personas["RelacionPersona"]
                        )
                    )

                # Handle multiple organizations
                organizaciones = noticia['Relaciones']['Organizacion']
                if isinstance(organizaciones, list):
                    for organizacion_relation in organizaciones:
                        organizacion_id = organizacion_relation["Organizacion"]
                        if organizacion_id not in processed_nodes:
                            nodes.append(
                                Node(
                                    id=organizacion_id,
                                    label=organizacion_relation["Organizacion"],
                                    shape="circularImage",
                                    image=images["organization"]
                                )
                            )
                            processed_nodes.add(organizacion_id)
                        
                        edges.append(
                            Edge(
                                source=organizacion_id,
                                target=news_id,
                                label=organizacion_relation["RelacionOrganizacion"]
                            )
                        )
                else:
                    # Single organization case
                    organizacion_id = organizaciones["Organizacion"]
                    if organizacion_id not in processed_nodes:
                        nodes.append(
                            Node(
                                id=organizacion_id,
                                label=organizaciones["Organizacion"],
                                shape="circularImage",
                                image=images["organization"]
                            )
                        )
                        processed_nodes.add(organizacion_id)
                    
                    edges.append(
                        Edge(
                            source=organizacion_id,
                            target=news_id,
                            label=organizaciones["RelacionOrganizacion"]
                        )
                    )

    return nodes, edges

# Streamlit UI
st.title("Visualización de Noticias por Temas")
# Display the unique topics found

# Construcción del grafo
data = st.session_state['list_news']
topics = set()
for entry in data:
    for noticia in entry['Noticias']:
        topic = noticia['Relaciones']['Topico']['Topic']
        topics.add(topic)

st.session_state['list_topics'] = list(topics)

with st.sidebar:
    
    st.title("Filtros")
    
    # Selección de fecha
    selected_date = st.date_input("Seleccionar Fecha", datetime.date(2024, 8, 13))
    st.write("Fecha seleccionada:", selected_date)
    

    
    st.divider()
    
    # Selección de tema de interés
    options_title = st.selectbox(
        "Seleccionar Tópico de Interés",
        st.session_state['list_topics'],
        key="single_selector"
    )



if selected_date:
    if options_title:
        selected_topic = options_title
        with st.container():
            nodes, edges = build_graph(data, selected_date.strftime("%d-%m-%Y"), selected_topic)
            
            config = Config(
                width=750,
                height=950,
                directed=True,
                physics=True,
                hierarchical=False,
            )
            
            return_value = agraph(nodes=nodes, edges=edges, config=config)
    
    ## solo si cambio de fecha hará el filtro
    print("data sabved: " ,st.session_state['date_saved'])
    
    print("data selected: ",selected_date.strftime("%d-%m-%Y"))

    print(str(st.session_state['date_saved'])!=str(selected_date.strftime("%d-%m-%Y")))

    if str(st.session_state['date_saved'])!=str(selected_date.strftime("%d-%m-%Y")):
        st.session_state['list_news']=query_kg(date=selected_date.strftime("%d-%m-%Y"))
        with st.container():
            nodes, edges = build_graph(query_kg(date=selected_date.strftime("%d-%m-%Y")), selected_date.strftime("%d-%m-%Y"), selected_topic)
            
            config = Config(
                directed=True,
                physics=False,
                hierarchical=True,
            )
            
            return_value = agraph(nodes=nodes, edges=edges, config=config)
        
    else:
        topics = set()
        for entry in data:
            for noticia in entry['Noticias']:
                topic = noticia['Relaciones']['Topico']['Topic']
                topics.add(topic)

        st.session_state['list_topics'] = list(topics)

        

        #topic_list_filter = [topic_mapping.get(t) for t in topics_list if t in topic_mapping]
        #select_keys ={}
    
