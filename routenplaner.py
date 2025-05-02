import streamlit as st #Importiert für streamlit applikation
from geopy.geocoders import Nominatim #importiert um Koordinaten des jeweiligen Standorts zu erhalten
import osmnx as ox #wird verwendet um die Strecken zu analysieren, resp. um eine Strecke mit gewünschter Distanz zu erstellen
import requests 
import folium
from streamlit_folium import folium_static #Stellt die Karte in Streamlit dar
import networkx as nx
import random

geolocator = Nominatim(user_agent="strideUp")
#Damit werden die Koordinaten und die Adresse innerhalb einer gesamten Ausführung gespeichert
lat= None
lon= None
distance= None
city= ''
country=''
distancem= None
fullroute=[]

col1,col2= st.columns ([4,3]) #damit wird das Format der beiden Kolonnen mit dem Eingabefeld und der Map bestummen.

with col2:
    #Eingabefeld für aktuelle Location
    st.header ('Ihr Startpunkt')
    street= st.text_input ('Strasse')
    housenmbr= st.text_input ('Hausnummer') 
    plz= st.text_input ('Postleitzahl') 
    city= st.text_input ('Stadt')
    country = st.selectbox ('Land',['Schweiz', 'Deutschland', 'Österreich'])

    if street and housenmbr and city: #damit wird sichergesellt, dass alle Felder ausgefüllt sind
        location = f'{street}, {housenmbr}, {plz}, {city}'
        koordinaten = geolocator.geocode(location) # Dieser erstellt die Koordinaten des eingegebenen Standorts.
        if koordinaten: 
            lat= koordinaten.latitude #Breitengrad
            lon= koordinaten.longitude #Längengrad
        else: 
            st.error ('Standort nicht gefunden') #Wird nur ausgegeben, wenn die Koordinaten nicht korrekt erstellt werden konnten
    
    else: 
        st.error('Bitte füllen Sie alle Felder aus') #stellt sicher, dass alle Felder ausgefüllt werden. Falls dies noch nicht geschehen ist, wird diese Fehlermeldung ausgegeben
    
    st.header ('Laufpräferenzen') #Titel für die eingegebenen Präferenzen
    
#Eingabefeld für Distanz:
    distancekm= st.slider ('Gewünschte Distanz:',0,50, format= "%d km")
    distancem= distancekm*1000 #Damit wird die eingegbene Distanz in Kilometer in Meter umgerechnet. Ist notwendig, um anhand der nodes (Knoten) dann eine Strecke in der gewünschten Distanz ausgegeben wird.
    if distancekm==0: 
        st.error('Wählen Sie Ihre gewünschte Distanz')
#Level (Wenn es darum geht, dass wir es für Stravanutzer auslegen allenfalls auch möglich, Eingabefeld erstellen mit jeweiligen Dauer pro KmH)
    #route_type= st.selectbox ('Welchen Typ von Routen bevorzugen Sie?', ['Steil', 'Flach', 'Keine Angabe'])

#nur falls möglich sprich Map muss diese Unterschiede machen
#Art von Routen
    #underground= st.selectbox ('Welchen Untergrund bevorzugen Sie?', ['Trails','Asphalt', 'Keine Angabe'])

    #Hier muss dann der Befehl ausgeführt werden, der die Strecke erstellt.
    
with col1: 
    st. header ('Ihre Route')
    #Der anschliessende Code erstellt einen Marker an der vom Nutzer eingegebenen Adresse
    if lat is not None and lon is not None: 
            apikeymap= '5b3ce3597851110001cf6248ffaa351596d6465b8bd5784c578dcaa6'
            mapapi= 'https://api.openrouteservice.org/optimization'
            response= requests.get(mapapi)
            print (response.json())
            m= folium.Map(location=(float(lat), float(lon)), width=400, height=400) #https://python-visualization.github.io/folium/latest/getting_started.html
            folium.Marker (location=[float(lat), float(lon)], icon=folium.Icon(color='red')).add_to(m) #Damit wird am eingegebenen Ort ein Marker gesetzt für bessere Sichtbarkeit des Standortes
         #Durch diesen Befehl wird die Map in Streamlit sichtbar

        #mit den anschliessenden Befehlen wird das Strassennetzwerk des jeweilig eingegeben Orts heruntergeladen
            b= ox.graph_from_point ((lat, lon), dist= distancem, network_type='walk') #dadurch wird sichergestellt, dass nur Wege, welche für Fussgänger resp. in unserem Fall Jogger vorgeschlagen resp. verwendet werden. Quelle von Codezeile: https://geoffboeing.com/2016/11/osmnx-python-street-networks/
            ox.plot_graph(b) #https://geoffboeing.com/2016/11/osmnx-python-street-networks/
            startpunkt= ox.distance.nearest_nodes(b, lon, lat)#Damit wird der vom eingegebenen Startpunkt nächst entfernteste Knoten gesucht https://www.geeksforgeeks.org/find-the-nearest-node-to-a-point-using-osmnx-distance-module/
            d=nx.single_source_dijkstra_path_length(b,startpunkt,cutoff=distancem, weight= 'length') #https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.single_source_dijkstra_path_length.html
        
            valid_nodes = list(d.keys()) #erstellet eine Liste mit allen zulässigen nodes. 
            anzahl_versuche=0
            max_versuche= 100
            route_ok=False
            while anzahl_versuche < max_versuche and not route_ok:
                midpoint = random.choice(valid_nodes)#Damit wird ein zufälliger Mittelpunkt gewählt
                zweitermidpoint= random.choice(valid_nodes)#Damit wird ein zweiter zufälliger Mittelpunkt gewählt (relevant um einen Rundkurs zu erhalten)
                anzahl_versuche+=1
                fullroute=[]
            #Die anschliessenden Zeilen erstellen einen Rundkurs. Deshalb unterteilt in hinweg Zwischenweg und Rückweg, um zu vermeiden, dass Hinweg und Rückweg gleich sind.
                if nx.has_path(b,startpunkt, midpoint) and nx.has_path(b,midpoint, zweitermidpoint) and nx.has_path(b,zweitermidpoint, startpunkt):
                    hinweg = nx.shortest_path(b, startpunkt, midpoint, weight='length') #erstellt eine Liste, der Nodes welche für den Hinweg genutzt werden
                
                    zwischenweg= nx.shortest_path(b,midpoint,zweitermidpoint, weight='length')
                
                    rückweg = nx.shortest_path(b, zweitermidpoint, startpunkt, weight='length')

                    fullroute= hinweg + zwischenweg + rückweg #Damit werden alle Knoten aneinandergehöngt uns es wird sichergestellt, dass der Endpunkt von hinweg und der Startpunkt von Zwischenweg nicht beide aufgelistet werden. 
                    fullroute = [node for i, node in enumerate(fullroute) if i == 0 or node != fullroute[i - 1]]
                    routenlänge=0

                    #Damit wird die Gesamtlänge des Rundkurses berechnet.
                    for f in range(len(fullroute)-1):
                        distance= nx.shortest_path_length(b, fullroute[f],fullroute[f+1], weight='length')
                        routenlänge+=distance
                    if distancem-500 < routenlänge < distancem + 500: #einbauen einer Distanz bei der Erstellung der Route.
                        route_ok=True

            #Extrahiere die Koordinaten für die Route 
            #Quelle: ChatGPT 
            route_coords = [(b.nodes[node]['y'], b.nodes[node]['x']) for node in fullroute if node in b.nodes]
            if route_coords:
                avg_lat = sum(coord[0] for coord in route_coords) / len(route_coords)
                avg_lon = sum(coord[1] for coord in route_coords) / len(route_coords)
                m.location = (avg_lat, avg_lon)
                m.fit_bounds([route_coords[0], route_coords[-1]])
                folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(m) #Zeichnet die Route mit Folium
            else:
                st.error("Es konnte keine passende Route gefunden werden") 
            folium_static(m)  #Karte in Streamlit anzeigen lassen
  

    else: #wenn noch kein Ort eingegeben wurde, wird damit die Map von St.Gallen dargestellt
            apikeymap= '5b3ce3597851110001cf6248ffaa351596d6465b8bd5784c578dcaa6'
            mapapi= 'https://api.openrouteservice.org/optimization'
            response= requests.get(mapapi)
            print (response.json())
            a= folium.Map(location=[47.42391 , 9.37477], width=400, height=400) #eingegebene Längen und Breitengrade sind jene von St. Gallen
            folium_static(a)
    
#Abrufen der Wetter API 
#Wetter Informationen: gebaut mit: https://www.youtube.com/watch?v=X1Y3HQy5Xfo&t=1113s und https://www.youtube.com/watch?v=vXpKTGCk5h
    st.header ('Wetter')
    if lat is not None and lon is not None:
            apikeyweather= '04471e45c09580cdd116430309ef988b'
            weatherapi= (f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikeyweather}&units=metric")
            response= requests.get(weatherapi)
            weatherdata= response.json()
            weather= (f"Wetter:  \n {weatherdata ['weather'][0]['main']}")
            temperature= (f"Temperatur:  \n {weatherdata ['main']['temp']}°C")
            wind= (f"Windstärke:  \n {weatherdata ['wind']['speed']}m/s")
            col3,col4,col5 = st.columns (3)
            col3.markdown (weather)
            col4.markdown (temperature)
            col5.markdown (wind)
    else: 
         st.error ('Wählen Sie Ihren Startpunkt')

#if route_type== 'Steil' and underground== 'Waldwege': 
    #
#elif route_type== 'Steil' and underground == 'Asphalt': 
    #
#elif route_type=='Steil' and underground == 'Keine Angaben': 
    #
#elif route_type=='Flach' and underground=='Waldwege':
    #
#elif route_type=='Flach' and underground =='Aspahlt': 
    #
#elif route_type =='Flach' and underground =='Keine Angaben': 
    #
#elif route_type=='Keine Angaben' and underground =='Waldwege': 
    #
#elif route_type=='Keine Angaben' and underground =='Asphalt':
    #
#elif route_type=='Keine Angaben' and underground == 'Keine Angaben':
    #

#Höhenmeter berechnen 

#Berechnung Höhenmeter gesamter Weg 
#allnodes= fullroute
#routenkoordinaten= []
#for node in allnodes:
    #latitude = b.nodes[node]['y']
    #longitude = b.nodes[node]['x']
    #routenkoordinaten.append((latitude, longitude))

#st.write('Höhenmeter')
#Liste mit Koordinaten zu nodes erstellen 
#Abrufen von Höhenmeter der jeweiligen Koordinaten 
#höhenmeterliste=[]
#for latitude, longitude in routenkoordinaten:
    #headers = {
        #'Authorization': '5b3ce3597851110001cf6248ffaa351596d6465b8bd5784c578dcaa6',  # Dein API-Key
       #'Content-Type': 'application/json'
#}

    #body = {
       # "format_in": "geojson",
       # "format_out": "geojson",
        #"geometry": {
         #   "coordinates": [longitude, latitude],
         #   "type": "Point"
    #}
#}

    #response = requests.post(
        #'https://api.openrouteservice.org/elevation/point',
        #headers=headers,
        #json=body
#)
    #try:
       # data = response.json()
        #coords = data.get('geometry', {}).get('coordinates', [])
        #if len(coords) == 3:
           # höhe = coords[2]
           # höhenmeterliste.append(höhe)
       # else:
           # st.warning(f"Keine gültige Höhenantwort für Punkt: {latitude}, {longitude}")
    #except Exception as e:
        #st.warning(f"Fehler beim Abrufen der Höhe für Punkt: {latitude}, {longitude} – {e}")
