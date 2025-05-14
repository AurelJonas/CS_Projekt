import streamlit as st #Importiert für streamlit applikation
from geopy.geocoders import Nominatim #importiert um Koordinaten des jeweiligen Standorts zu erhalten
import osmnx as ox #wird verwendet um die Strecken zu analysieren, resp. um eine Strecke mit gewünschter Distanz zu erstellen
import requests 
import folium 
from streamlit_folium import folium_static #Stellt die Karte in Streamlit dar
import networkx as nx #Importiert um die Route zu erstellen
import random #importiert um zufällige Zahlen ziehen zu können 
import gpxpy #Importieren des Hauptmoduls welches es ermöglicht, zugriff auf den anschliessenden Import zu haben
import gpxpy.gpx #Importiert um eine GPX Datei zu erstellen
import io #Importiert um auf io.BytesIO zuzugreifen und somit das GPX-File Nutzer*innen zum Download zur Verfügung zu stellen.

#geolocater ermöglicht es uns, den von Nutzer*innen eingegebenen Standort in Koordinaten umzuwandeln.
#Der Parameter user_agent ist notwendig, um als Nutzer*in erkannt zu werden
geolocator = Nominatim(user_agent='strideUp') 


#Codezeile 20 bis 23 stellen sicher, dass die eingegebenen Daten während der jeweiligen Sitzung 
#gespeichert und abrufbar werden.
if 'joggingroute' not in st.session_state:
    st.session_state['joggingroute'] = None
if 'wetterinformationen' not in st.session_state:
    st.session_state['wetterinformationen'] = None                 
#Quelle: 
#Gebaut mithilfe von https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state


#Die Funktion zeige_karte stellt, beim Start unserer Web Applikation die 
#Karte von St. Gallen dar. Sobald ein Standort eingegeben wurde, wird der Kartenausschnitt an den 
#eingegebene Standort aktualisiert.
#mit avg_lat und avg_lon werden jeweils die von der erstellen Joggingroute durchschnittlichen 
#Längen- und Breitengrade berechnet. Dies stellt sicher, dass die erstellte Joggingroute jeweils 
#mittig des  Kartenauschnitts dargestellt wird.
def zeige_karte(koordinaten=None):
    if koordinaten:
        avg_lat = sum(coord[0] for coord in koordinaten) / len(koordinaten) #Berechnet die durchschnittlichen Breitengrade der Joggingroute
        avg_lon = sum(coord[1] for coord in koordinaten) / len(koordinaten) #Berechnet die durchschnittlichen Längengrade der Joggingroute
        m = folium.Map(location=(avg_lat, avg_lon), zoom_start=14) #Stellt die Karte in Streamlit dar
        folium.PolyLine(koordinaten, color='blue', weight=5, opacity=0.7).add_to(m) #Dadurch wird die Strecke auf der Karte dargestellt
        folium.Marker(location=koordinaten[0],popup="Startpunkt", icon=folium.Icon(color="red")).add_to(m) #Stellt Marker beim Startpunkt auf der Karte dar
    else:
        m = folium.Map(location=[47.42391, 9.37477], zoom_start=13)
    folium_static(m, width=700, height=500)


#Die Funktion wetter_abfrage ruft über die API von OpenWeather die Wetterinformationen des angegebenen Standorts auf.
#Der Standort wird dabei über die dazugehörigen Parameter lat und lon (Breiten- und Längengrade) abgerufen.
#Verwendet wird die kostenlose API von OpenWeather
#Die Wetterinformationen werden anschliessend im Streamlit-Interface in drei Spalten dargestellt.
def wetter_abfrage (lat,lon):
    if lat is not None and lon is not None:
        apikeyweather= '04471e45c09580cdd116430309ef988b'
        weatherapi= (f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikeyweather}&units=metric') #Erstellt die URL für die HTTP-GET-Anfrage an die OpenWeather-API für den angegebenen Standort 
        response= requests.get(weatherapi) #Sendet die HTTP-Get Anfrage an die OpenWeather API, um die Wetterinformationen des eingegebenen Standorts zu erhalten.
        weatherdata= response.json() #Speichert die erhaltenen Wetterinformationen in einem JSON-Format.
        weather= (f"🌤️:  \n {weatherdata ['weather'][0]['main']}")
        temperature= (f"🌡️:  \n {weatherdata ['main']['temp']}°C")
        wind= (f"💨:  \n {weatherdata ['wind']['speed']}m/s")
        st.header ('Wetter')
        col3,col4,col5 = st.columns (3)
        col3.markdown (weather)  
        col4.markdown (temperature) 
        col5.markdown (wind)
    else:
        st.error ('Keine Wetterdaten zu diesem Standort gefunden')
#Quellen:
#Erstellt auf Grundlage von https://www.youtube.com/watch?v=X1Y3HQy5Xfo&t=1113s und https://www.youtube.com/watch?v=vXpKTGCk5h


#Die Funktion route_erstellen erstellt basierend auf dem eingegebene Standort und der eingegebenen Distanz einen Route. 
#Um die Route zu erstellen, nutzen wir das Strassennetzwerk von osmnx.
#nx.shortest_path sucht sich die kürzeste Strecke zwischen den Start- und Zielpunkt. die dabei verwendeten Knotenpunkte werden anschliessend als Lite gespiechert.
def route_erstellen(lat, lon, distancem):
        #mit den anschliessenden Befehlen wird das Strassennetzwerk des jeweilig eingegeben Orts heruntergeladen
        b= ox.graph_from_point ((lat, lon), dist= distancem*0.5, network_type='walk') #Die Variable b speichert die notwendigen Knotenpunkte. 
                                                                                      #Wir haben uns dabei dafür entschieden, dass wir einerseits nur Fussgängerwege laden, damit sichergestellt wird, dass keine 
                                                                                      #für Fussgänger unzugänglichen routen erstellt werden, wie beispielsweise Routen, die über eine Autobahn führen. 
                                                                                      #Zudem laden wir das Streckennetz nur im Umkreis von der Hälfte der eingegeben Distanz.
        
        startpunkt= ox.distance.nearest_nodes(b, lon, lat) #ox.distance.nearest_nodes sucht den nächst gelgenen Knotenpunkt basierend auf den Koordinaten und speichert diesen unter der Variable startpunkt
        d=nx.single_source_dijkstra_path_length(b,startpunkt,cutoff=distancem*0.5, weight= 'length') #Die Variable d speichert alle Knotenpunkte, welche innerhalb einer gewissen Distanz vom Startpunkt entfernt sind.
        knotenpunkte = list(d.keys()) #Erstellt aus den zuvor geladenen Knotenpunkten eine Liste, durch welche anschliessend durchiteriert werden kann. 
        anzahl_versuche=0
        max_versuche= 500 #Eingabe einer Anzahl an maximalen Versuchen, damit die anschliessende while-Schleife, sofern keine Route gefunden wird, unendlich durchläuft.
        route_ok=False
        while anzahl_versuche < max_versuche and not route_ok:
            zwischenpunkt1 = random.choice(knotenpunkte) #Damit wird ein erster zufälliger Endpunkt gewählt.
            zwischenpunkt2= random.choice(knotenpunkte) #Damit wird ein erster zufälliger Endpunkt gewählt.(relevant um einen Route zu erhalten)
            anzahl_versuche+=1 ##erhöhung der Anzahl Versuche bei jedem Durchlauf der while-Schleife
            Gesamtstrecke=[]

            #Das nachfolgende If-Statement erstellt eine Route, basierend auf dem Startpunkt, den Zwischenpunkten und Endpunkt
            if nx.has_path(b,startpunkt, zwischenpunkt1) and nx.has_path(b,zwischenpunkt1, zwischenpunkt2) and nx.has_path(b,zwischenpunkt2, startpunkt):
                hinweg = nx.shortest_path(b, startpunkt, zwischenpunkt1, weight='length') #erstellt eine Liste, der Nodes welche für den Hinweg genutzt werden               
                zwischenweg= nx.shortest_path(b,zwischenpunkt1,zwischenpunkt2, weight='length')
                rückweg = nx.shortest_path(b, zwischenpunkt2, startpunkt, weight='length')
                Gesamtstrecke= hinweg + zwischenweg + rückweg #Damit werden alle Knoten aneinandergehöngt uns es wird sichergestellt, dass der Endpunkt von hinweg und der Startpunkt von Zwischenweg nicht beide aufgelistet werden. 
                strecke=[]
                #Entfernt aufeinanderfolgende doppelte Knoten aus der Liste Gesamtstrecke
                for i, node in enumerate(Gesamtstrecke): 
                    if i==0 or node !=Gesamtstrecke [i-1]:
                        strecke.append(node)
                Gesamtstrecke = strecke
                routenlänge=0

                #Die nachfolgende for-Schleife überprüft die gesamtlänge der zuvor erstellten Route. Sofern die Route innerhalb der gewünschten Distanz (inklusive der Toleranz) liegt, wird die Route ausgegeben. 
                for f in range(len(Gesamtstrecke)-1): #Die -1 ist am Ende relevant, um zu verhindern, dass bis zum letzten Wert der Liste gerechnet werden kann.
                    distance= nx.shortest_path_length(b, Gesamtstrecke[f],Gesamtstrecke[f+1], weight='length') #Berechnet auf Grundlage der Knotenpunkte die Distanz zwischen zwei Knotenpunkten aus.
                    routenlänge+=distance
                if distancem-500 < routenlänge < distancem + 500: #Toleranz eingebaut um mit höherer Wahrscheinlichkeit eine passende Strecke zu finden.  
                    route_ok=True
        if route_ok:
            return [(b.nodes[node]['y'], b.nodes[node]['x']) for node in Gesamtstrecke if node in b.nodes]  #Erstellt eine Liste mit allen Koordinatenpunkte der zuvor erstellten Strecke, welche auch innerhalb der gewünschten Distanz liegt.
        return None
#Quellen: 
#d=nx.single_source_dijkstra_path_lengtherstellt mithilfe von  https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.single_source_dijkstra_path_length.html
#Laden des benötigten Strassennetzwerks mithilfe von https://geoffboeing.com/2016/11/osmnx-python-street-networks/
#Startpunkt gebaut mithilfe von https://www.geeksforgeeks.org/find-the-nearest-node-to-a-point-using-osmnx-distance-module/



#Durch die Funktion gpx_erstellen wird der unter der Funktion route_erstellen erstellter Route in ein GPX umgewandelt. 
#Dafür verwenden wird die gpxpy Bibliothek.
def gpx_erstellen(routenkoordinaten):
    gpx = gpxpy.gpx.GPX() #Erstellt ein neues GPX-File
    gpx.name = 'Ihre Route'

    track = gpxpy.gpx.GPXTrack() #Erstellt einen neuen Track
    gpx.tracks.append(track) #Dadurch wird der soeben erstellte Track dem GPX-File hinzugefügt

    segment = gpxpy.gpx.GPXTrackSegment() #Erstellt ein neues Track-Segment. das Segment ist dabei eine Sammlung zahlreicher GPS-Daten
    track.segments.append(segment) #Fügt das Segment dem GPX-File hinzu

    #Diese for-Schleife durchläuft die Liste routenkoordinaten, welche alle einzelnen Breiten- und Längengrade 
    #beinhaltet, die bei der Funktion route_erstellen erstellten Strecke. 
    #Durch GPXTrackPoint, wird von jedem Koordinatenpunkt (besteht jeweils aus Längen- und Breitengraden) den dazugehörigen 
    #GPS-Punkt erstellen und diesen dem Segment im GPX-File hinzufügen.
    for lat, lon in routenkoordinaten:
        point = gpxpy.gpx.GPXTrackPoint(lat, lon)
        segment.points.append(point)

    return gpx.to_xml() #Wandelt das GPX-File in die XLM-Darstellung um. Dies ist notwendig, damit das GPX-File beispielsweise 
                        #auf Plattformen wie Strava hochgeladen werden und verarbeitet werden kann.

#Quellen: 
#Erstellt mithilfe von https://pypi.org/project/gpxpy/
#Zeile 139 erstellt mithilfe von ChatGPT


#AB HIER GEHT ES UMS SEITENLAYOUT

col1, col2 = st.columns([1, 2])

# Die beiden Variablen lat und lon werden initialisiert und erhalten erstmal den Wert None
lat = None
lon = None


#In col1 kann der Startpunkt sowie die gewünschte Distanz eingegeben werden
#Die If-Bedingung in Zeile 171 stellt sicher, dass alle Adressfelder korrekt ausgeüllt wurden und erstellt basierend darauf, die
#adresse. Die Adresse ist anschliessend die Grundlage für die Erstellung der Koordinaten des eingegebene Startpunkts.
#Sollte die eingebene Adresse fehlerhaft sein, wird die Fehlermeldung "Bitte geben Sie einge gültige Adresse ein" ausgelöst. 
#Sollte noch gar keine Adresse eingegeben worden sein, wird die Fehlermeldung "Bitte geben Sie Ihren Startpunkt ein"
with col1:
    st.header ('Gewünschter Startpunkt')
    strasse= st.text_input ('Strasse')
    hausnummer= st.text_input ('Hausnummer')
    plz= st.text_input ('Postleitzahl')
    stadt= st.text_input ('Stadt')
    country = st.selectbox ('Land',['Schweiz', 'Deutschland', 'Österreich'])
    if strasse and hausnummer and stadt:
        adresse = f'{strasse}, {hausnummer}, {plz}, {stadt}'
        koordinaten = geolocator.geocode(adresse) #Erstellt die Breiten- und Längengrade für die eingegebene Adresse.
        if koordinaten: 
            lat= koordinaten.latitude #Speichert Breitengrad des eingegebene Startpunkt in Variable lat
            lon= koordinaten.longitude #Speichert Längengrade des eingegebene Startpunk in Variable lon
        else: 
            st.error ('Bitte geben Sie einge gültige Adresse ein')
    else: 
        st.error('Bitte geben Sie Ihren Startpunkt ein')
    
    #Eingabefeld für Distanz:
    st.header ('Ihre Distanz')
    distancekm= st.slider ('Gewünschte Distanz:',0,42, format= "%d km")
    distancem= distancekm*1000 #Umrechnung der Distanz in Meter. Notwendig, da die Abstände zwischen einzelnen Knotenpunkte in Meter angegeben sind.
    if distancekm==0:
        st.error('Wählen Sie Ihre gewünschte Distanz')

    st.header('Route generieren')
    if st.button('Route erstellen'):
        if lat is not None and lon is not None:
            route = route_erstellen(lat, lon, distancem)
            if route:
                st.session_state['joggingroute'] = route #Speichert die in der Funktion route_erstellen erstellte Route in st.session_state['joggingroute']
                st.session_state['wetterinformationen'] = (lat, lon) #Speichert die Koordinaten des eingegebenen Standorts in st.session_state['wetterinformationen']
                st.success('Route erfolgreich erstellt!')
            else:
                st.error('Es konnte keine geeignete Route gefunden werden')
        else:
            st.error('Bitte geben Sie eine gültige Adresse ein')

    # Wetter anzeigen
    if st.session_state['wetterinformationen']:
        wetter_abfrage(*st.session_state['wetterinformationen']) #Die in session_state['wetterinformationen'] gespeicherten Koordinaten, sind als Tuple vorhanden. 
                                                              #Damit die Funktion wetter_abfrage jedoch das Wetter vom eingegebenen Standort findet, 
                                                              #müssen die Längen- und Breitengrade als einzelnes Argument eingegeben werden. Und dies wird durch
                                                              #den * vor st.session_state['wetterinformationen'] sichergestellt.
    # GPX Download
    if st.session_state['joggingroute']:
        gpx_data = gpx_erstellen(st.session_state['joggingroute'])
        if gpx_data:
            gpx_bytes = io.BytesIO(gpx_data.encode('utf-8')) #Durch gpx_data.encode('utf-8') wird der im gpx_data file gespeicherten Textstring in Bytes um. Notwendig um die GPX-Datei herunterladen zu können.
            st.download_button('GPX herunterladen', gpx_bytes, 'route.gpx', 'application/gpx+xml')
#Quellen: 
#Zeile 212 wurde mithilfe von ChatGPT erstellt.

#In col2 wird die KArte dargestellt.
with col2:
    st.header("Deine heutige Joggingroute")
    if st.session_state.['joggingroute']:
        zeige_karte(st.session_state.['joggingroute'])
    else:
        zeige_karte()