import streamlit as st #Importiert für streamlit applikation
from geopy.geocoders import Nominatim #importiert um Koordinaten des jeweiligen Standorts zu erhalten
import osmnx as ox #wird verwendet um die Strecken zu analysieren, resp. um eine Strecke mit gewünschter Distanz zu erstellen
import requests 
import folium 
from streamlit_folium import folium_static #Stellt die Karte in Streamlit dar
import networkx as nx 
import random
import gpxpy
import gpxpy.gpx
import io

geolocator = Nominatim(user_agent="strideUp")
#Damit werden die Koordinaten und die Adresse innerhalb einer gesamten Ausführung gespeichert
lat= None
lon= None
distance= None
city= ''
country=''
distancem= None
fullroute=[]
routenkoordinaten= []

col1,col2= st.columns ([4,3]) #damit wird das Format der beiden Kolonnen mit dem Eingabefeld und der Map bestummen.

with col2:
    #Mithilfe des anschliessenden Codes kann der Startpunkt der Strecke eingegeben werden
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
    
    st.header ('Ihre Distanz') #Titel für die eingegebenen Präferenzen
    
#Eingabefeld für Distanz:
    distancekm= st.slider ('Gewünschte Distanz:',0,42, format= "%d km")
    distancem= distancekm*1000 #Damit wird die eingegbene Distanz in Kilometer in Meter umgerechnet. Ist notwendig, um anhand der nodes (Knoten) dann eine Strecke in der gewünschten Distanz ausgegeben wird.
    if distancekm==0: 
        st.error('Wählen Sie Ihre gewünschte Distanz')

#Der folgende Code ruft basierend auf dem eingegebene Standort die im API gespeicherten Wetterinformationen ab.
#Wetter Informationen: gebaut mit: https://www.youtube.com/watch?v=X1Y3HQy5Xfo&t=1113s und https://www.youtube.com/watch?v=vXpKTGCk5h
def wetter_abfrage ():
    if lat is not None and lon is not None:
        apikeyweather= '04471e45c09580cdd116430309ef988b'
        weatherapi= (f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikeyweather}&units=metric")
        response= requests.get(weatherapi)
        weatherdata= response.json()
        weather= (f"Wetter:  \n {weatherdata ['weather'][0]['main']}")
        temperature= (f"Temperatur:  \n {weatherdata ['main']['temp']}°C")
        wind= (f"Windstärke:  \n {weatherdata ['wind']['speed']}m/s")
        st.header ('Wetter')
        col3,col4,col5 = st.columns (3)
        col3.markdown (weather)
        col4.markdown (temperature)
        col5.markdown (wind)
    else: 
        st.error ('Keine Wetterdaten zu diesem Standort gefunden')

#Der folgende Code erstellt einen Rundkurs
#erstellt mithilfe von ChatGPT und 
def route_erstellen():
    if lat is not None and lon is not None:
        apikeymap= '5b3ce3597851110001cf6248ffaa351596d6465b8bd5784c578dcaa6'
        mapapi= 'https://api.openrouteservice.org/optimization'
        response= requests.get(mapapi)
        print (response.json())
        m= folium.Map(location=(float(lat), float(lon)), width=400, height=400) #https://python-visualization.github.io/folium/latest/getting_started.html
        folium.Marker (location=[float(lat), float(lon)], icon=folium.Icon(color='red')).add_to(m) #Damit wird am eingegebenen Ort ein Marker gesetzt für bessere Sichtbarkeit des Standortes, erstellt mithilfe von: #https://python-visualization.github.io/folium/latest/getting_started.html
        
        #Durch diesen Befehl wird die Map in Streamlit sichtbar

        #mit den anschliessenden Befehlen wird das Strassennetzwerk des jeweilig eingegeben Orts heruntergeladen
        b= ox.graph_from_point ((lat, lon), dist= distancem*0.5, network_type='walk') #dadurch wird sichergestellt, dass nur Wege, welche für Fussgänger resp. in unserem Fall Jogger vorgeschlagen resp. verwendet werden. Quelle von Codezeile: https://geoffboeing.com/2016/11/osmnx-python-street-networks/
        ox.plot_graph(b) #https://geoffboeing.com/2016/11/osmnx-python-street-networks/
        startpunkt= ox.distance.nearest_nodes(b, lon, lat)#Damit wird der vom eingegebenen Startpunkt nächst entfernteste Knoten gesucht https://www.geeksforgeeks.org/find-the-nearest-node-to-a-point-using-osmnx-distance-module/
        d=nx.single_source_dijkstra_path_length(b,startpunkt,cutoff=distancem*0.5, weight= 'length') #Diese Codezeile sammelt alle vorhandenen Knotenpunkte, inerhalb der zulässigen Distanz, erstellt mithilfe von: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.single_source_dijkstra_path_length.html
        
        valid_nodes = list(d.keys()) #Erstellt aus den zuvor geladenen Knotenpunkten eine Liste, durch welche anschliessend durchiteriert werden kann. 
        anzahl_versuche=0
        max_versuche= 100 #Eingabe einer Anzahl an maximalen Versuchen, um zu verhindern, dass die anschliessende while-Schleife, sofern keine Route gefunden werden würde, unendlich durchlaufen würde.
        route_ok=False 
        while anzahl_versuche < max_versuche and not route_ok:
            midpoint1 = random.choice(valid_nodes)#Damit wird ein zufälliger Mittelpunkt gewählt
            midpoint2= random.choice(valid_nodes)#Damit wird ein zweiter zufälliger Mittelpunkt gewählt (relevant um einen Rundkurs zu erhalten)
            #midpoint3= random.choice(valid_nodes)#Damit wird ein zufälliger Mittelpunkt gewählt
            anzahl_versuche+=1
            Gesamtstrecke=[]
            #Die anschliessenden Zeilen erstellen einen Rundkurs. Deshalb unterteilt in hinweg Zwischenweg und Rückweg, um zu vermeiden, dass Hinweg und Rückweg gleich sind.
            if nx.has_path(b,startpunkt, midpoint1) and nx.has_path(b,midpoint1, midpoint2) and nx.has_path(b,midpoint2, startpunkt):
                hinweg = nx.shortest_path(b, startpunkt, midpoint1, weight='length') #erstellt eine Liste, der Nodes welche für den Hinweg genutzt werden
                
                zwischenweg= nx.shortest_path(b,midpoint1,midpoint2, weight='length')
                
                #zwischenweg2= nx.shortest_path(b,midpoint2,midpoint3,weight='length')

                rückweg = nx.shortest_path(b, midpoint2, startpunkt, weight='length')

                Gesamtstrecke= hinweg + zwischenweg + rückweg #Damit werden alle Knoten aneinandergehöngt uns es wird sichergestellt, dass der Endpunkt von hinweg und der Startpunkt von Zwischenweg nicht beide aufgelistet werden. 
                Gesamtstrecke = [node for i, node in enumerate(Gesamtstrecke) if i == 0 or node != Gesamtstrecke[i - 1]]
                routenlänge=0

                #In den anschliessenden Code-Zeilen wird die Länge der gesamtstrecke überberprüft.
                for f in range(len(Gesamtstrecke)-1):
                    distance= nx.shortest_path_length(b, Gesamtstrecke[f],Gesamtstrecke[f+1], weight='length')
                    routenlänge+=distance
                if distancem-500 < routenlänge < distancem + 500: #Toleranz eingebaut um mit einer höherer Wahrscheinlichkeit eine passende Strecke zu finden. 
                    route_ok=True

        #Extrahiere die Koordinaten für die Route 
        #Quelle: ChatGPT
        routenkoordinaten = [(b.nodes[node]['y'], b.nodes[node]['x']) for node in Gesamtstrecke if node in b.nodes]
        if routenkoordinaten:
            avg_lat = sum(coord[0] for coord in routenkoordinaten) / len(routenkoordinaten)
            avg_lon = sum(coord[1] for coord in routenkoordinaten) / len(routenkoordinaten)
            m.location = (avg_lat, avg_lon)
            m.fit_bounds([routenkoordinaten[0], routenkoordinaten[-1]])
            folium.PolyLine(routenkoordinaten, color="blue", weight=5, opacity=0.7).add_to(m) #Zeichnet die Route mit Folium
        else:
            st.error("Es konnte keine passende Route gefunden werden") 
        folium_static(m) #Dadurch wird die zuvor erstellte Route in Stramlit dargestellt
        return routenkoordinaten
    else: #Der anschliessende Code stellt, die Karte von St. Gallen dar, sofern nichts anderes eingeben wurde
        apikeymap= '5b3ce3597851110001cf6248ffaa351596d6465b8bd5784c578dcaa6'
        mapapi= 'https://api.openrouteservice.org/optimization'
        response= requests.get(mapapi)
        print (response.json())
        a= folium.Map(location=[47.42391 , 9.37477], width=400, height=400) #eingegebene Längen und Breitengrade sind jene von St. Gallen
        folium_static(a)

def gpx_erstellen (routenkoordinaten):
    gpx = gpxpy.gpx.GPX()
    gpx.name = 'Ihre Route'
    

    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)    
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)
    for lat, lon in routenkoordinaten:
        if not (45.8 <= lat <= 47.8) or not (5.9 <= lon <= 10.5): 
            st.error ('Keine gültigen Koordinantenpunkte')
            return None
        else: 
            point = gpxpy.gpx.GPXTrackPoint(lat, lon)  # Erstelle einen Punkt
            segment.points.append(point)
    return gpx.to_xml()

with col1: 
    st.header('Erstellen Sie Ihre heutige Jogging-Route')
    if st.button('Route erstellen'):
        routenkoordinaten = route_erstellen()
        wetter_abfrage()
        if routenkoordinaten:
            gpxroute = gpx_erstellen(routenkoordinaten)
            gpxroute_bytes = io.BytesIO(gpxroute.encode('utf-8'))
            st.success("Ihre Route wurde erfolgreich erstellt!")
            st.download_button('Ihre Route als GPX herunterladen', gpxroute_bytes, 'route.gpx', 'application/gpx+xml')
            avg_lat = sum(coord[0] for coord in routenkoordinaten) / len(routenkoordinaten)
            avg_lon = sum(coord[1] for coord in routenkoordinaten) / len(routenkoordinaten)

    # Erstelle die Karte mit dem Mittelpunkt
            m = folium.Map(location=(avg_lat, avg_lon), zoom_start=14)
            folium.PolyLine(routenkoordinaten, color="blue", weight=5, opacity=0.7).add_to(m)

    # Zeige die Karte in Streamlit an
            folium_static(m)
        else:
            st.error("Fehler: Konnte keine gültige Route erstellen.")