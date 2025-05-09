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

#mit st.session_state wird sichergestellt, dass die Daten sozusagen zwischengespeichert werden, und nicht nach jeder neuen Eingabe komplett gestartet wird.
if 'routenkoordinaten' not in st.session_state:
    st.session_state.routenkoordinaten = None
if 'wetterposition' not in st.session_state:
    st.session_state.wetterposition = None

#die im Anschluss definierte Funktion zeige_karte stellt, beim Start unsere Web Applikation die 
#Karte von St. Gallen dar.
#Input= 
#Output= 
def zeige_karte(koordinaten=None):
    if koordinaten:
        avg_lat = sum(coord[0] for coord in koordinaten) / len(koordinaten)
        avg_lon = sum(coord[1] for coord in koordinaten) / len(koordinaten)
        m = folium.Map(location=(avg_lat, avg_lon), zoom_start=14)
        folium.PolyLine(koordinaten, color="blue", weight=5, opacity=0.7).add_to(m)
    else:
        m = folium.Map(location=[47.42391, 9.37477], zoom_start=13)
    folium_static(m, width=700, height=500)

#Der folgende Code ruft basierend auf dem eingegebene Standort die im API gespeicherten Wetterinformationen ab.
#Die Funktion wetter_abfrage ertellt auf Grundlage des eingegebenen Standortes die Wetterinformationen aus.
#Wir haben uns dabei für die API von Openweather entschieden. 
#Input= 
#Output= 
def wetter_abfrage (lat,lon):
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
#Quelle von wetter_abfrage: Gebaut mithilfe von https://www.youtube.com/watch?v=X1Y3HQy5Xfo&t=1113s und https://www.youtube.com/watch?v=vXpKTGCk5h



#Die Funktion route_erstellen erstellt basierend auf dem eingegebene Standort und der eingegebenen Distanz einen Rundkurs. 
#Um die Route zu erstellen, nutzen wir das Strassennetzwerk von osmnx.

#Input= 
#Output= 
#
#erstellt mithilfe von ChatGPT 
def route_erstellen(lat, lon, distancem):
        #mit den anschliessenden Befehlen wird das Strassennetzwerk des jeweilig eingegeben Orts heruntergeladen
        b= ox.graph_from_point ((lat, lon), dist= distancem*0.5, network_type='walk') #Die Variable b speichert die notwendigen Knotenpunkte. 
        #Wir haben uns dabei dafür entschieden, dass wir einerseits nur Fussgängerwege laden, damit sichergestellt wird, dass keine 
        #für Fussgänger unzugänglichen routen erstellt werden, wie beispielsweise Routen, die über eine Autobahn führen. 
        #Zudem laden wir das Streckennetz nur im Umkreis von der Hälfte der eingegeben Distanz.
        
        
        startpunkt= ox.distance.nearest_nodes(b, lon, lat) #Damit wird der vom eingegebenen Startpunkt nächst entfernteste Knoten gesucht
        d=nx.single_source_dijkstra_path_length(b,startpunkt,cutoff=distancem*0.5, weight= 'length') #Diese Codezeile sammelt alle vorhandenen Knotenpunkte, inerhalb der zulässigen Distanz, erstellt mithilfe von: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.single_source_dijkstra_path_length.html
        valid_nodes = list(d.keys()) #Erstellt aus den zuvor geladenen Knotenpunkten eine Liste, durch welche anschliessend durchiteriert werden kann. 
        anzahl_versuche=0
        max_versuche= 500 #Eingabe einer Anzahl an maximalen Versuchen, um zu verhindern, dass die anschliessende while-Schleife, sofern keine Route gefunden werden würde, unendlich durchlaufen würde.
        route_ok=False
        while anzahl_versuche < max_versuche and not route_ok: #Dieser While-Loop wählt zunächst zufälli
            zwischenpunkt1 = random.choice(valid_nodes) #Damit wird ein zufälliger Mittelpunkt gewählt
            zwischenpunkt2= random.choice(valid_nodes)#Damit wird ein zweiter zufälliger Mittelpunkt gewählt (relevant um einen Rundkurs zu erhalten)
            #midpoint3= random.choice(valid_nodes)#Damit wird ein zufälliger Mittelpunkt gewählt
            anzahl_versuche+=1
            Gesamtstrecke=[]
            #Die anschliessenden Zeilen erstellen einen Rundkurs. Deshalb unterteilt in hinweg Zwischenweg und Rückweg, um zu vermeiden, dass Hinweg und Rückweg gleich sind.
            if nx.has_path(b,startpunkt, zwischenpunkt1) and nx.has_path(b,zwischenpunkt1, zwischenpunkt2) and nx.has_path(b,zwischenpunkt2, startpunkt):
                hinweg = nx.shortest_path(b, startpunkt, zwischenpunkt1, weight='length') #erstellt eine Liste, der Nodes welche für den Hinweg genutzt werden               
                zwischenweg= nx.shortest_path(b,zwischenpunkt1,zwischenpunkt2, weight='length')
                rückweg = nx.shortest_path(b, zwischenpunkt2, startpunkt, weight='length')
                Gesamtstrecke= hinweg + zwischenweg + rückweg #Damit werden alle Knoten aneinandergehöngt uns es wird sichergestellt, dass der Endpunkt von hinweg und der Startpunkt von Zwischenweg nicht beide aufgelistet werden. 
                Gesamtstrecke = [node for i, node in enumerate(Gesamtstrecke) if i == 0 or node != Gesamtstrecke[i - 1]]
                routenlänge=0

                #In den anschliessenden Code-Zeilen wird die Länge der gesamtstrecke überberprüft.
                for f in range(len(Gesamtstrecke)-1):
                    distance= nx.shortest_path_length(b, Gesamtstrecke[f],Gesamtstrecke[f+1], weight='length')
                    routenlänge+=distance
                if distancem-500 < routenlänge < distancem + 500: #Toleranz eingebaut um mit einer höherer Wahrscheinlichkeit eine passende Strecke zu finden. 
                    route_ok=True


        if route_ok:
            return [(b.nodes[node]['y'], b.nodes[node]['x']) for node in Gesamtstrecke if node in b.nodes]
        return None
#Quellen: 
#Laden des benötigten Strassennetzwerks mithilfe von https://geoffboeing.com/2016/11/osmnx-python-street-networks/
#Startpunkt gebaut mithilfe von https://www.geeksforgeeks.org/find-the-nearest-node-to-a-point-using-osmnx-distance-module/
#

#Durch die Funktion gpx_erstellen wird der unter der Funktion route_erstellen erstellter Rundkurs in ein GPX umgewandelt
#Input:
#Output: 
def gpx_erstellen(routenkoordinaten):
    gpx = gpxpy.gpx.GPX()
    gpx.name = 'Ihre Route'

    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)

    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    for lat, lon in routenkoordinaten:
        point = gpxpy.gpx.GPXTrackPoint(lat, lon)
        segment.points.append(point)

    return gpx.to_xml()



#Anschliessend folgt das Seitenlayout
st.set_page_config(page_title="StrideUp", layout="wide") #https://blog.streamlit.io/designing-streamlit-apps-for-the-user-part-ii/
adresseingabe, kartendarstellung = st.columns([1, 2])

#Mithilfe des anschliessenden Codes kann der Startpunkt der Strecke eingegeben werden
with adresseingabe:
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
    
    #Eingabefeld für Distanz:
    st.subheader ('Ihre Distanz')
    distancekm= st.slider ('Gewünschte Distanz:',0,42, format= "%d km")
    distancem= distancekm*1000 #Umrechnung der Distanz in Meter, da die Abstände zwischen den einzelnen Knotenpunkte in Meter angegeben sind.
    if distancekm==0:
        st.error('Wählen Sie Ihre gewünschte Distanz')

    st.subheader("Route generieren")
    if st.button("Route erstellen"):
        if lat and lon:
            route = route_erstellen(lat, lon, distancem)
            if route:
                st.session_state.routenkoordinaten = route
                st.session_state.wetterposition = (lat, lon)
                st.success("Route erfolgreich erstellt!")
            else:
                st.error("Es konnte keine geeignete Route gefunden werden.")
        else:
            st.error("Bitte gib eine gültige Adresse ein.")

    # Wetter anzeigen
    if st.session_state.wetterposition:
        wetter_abfrage(*st.session_state.wetterposition)

    # GPX Download
    if st.session_state.routenkoordinaten:
        gpx_data = gpx_erstellen(st.session_state.routenkoordinaten)
        if gpx_data:
            gpx_bytes = io.BytesIO(gpx_data.encode("utf-8"))
            st.download_button("GPX herunterladen", gpx_bytes, "route.gpx", "application/gpx+xml")
#Quellen: 
#Zeile 186 wurde mithilfe von ChatGPT erstellt

#Rechte Spalte: Karte
with kartendarstellung:
    st.subheader("Deine heutige Joggingroute")
    zeige_karte(st.session_state.routenkoordinaten)