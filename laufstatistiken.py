import streamlit as st
import requests #Damit HTTP-Anfragen gemacht werden können
import pandas as pd #Damit man Daten verarbeiten kann



# Aktivitäten speichern
if 'activities' not in st.session_state and 'access_token' in st.session_state:
    activities_url = "https://www.strava.com/api/v3/athlete/activities" #Endpunkt für die Aktivitäten herausgezogen werden
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    params = {"per_page": 200, "page": 1} #Anzahl Aktivitäten pro Seite

#Damit das Aktivitäten geladen und gespeichert werden falls noch keine Aktivitäten im Session State gespeichert sind 
# & der Benutzer schon einen Acces Token hat

    activities_response = requests.get(activities_url, headers=headers, params=params) #Damit die Aktivitäten aus Strava gezogen werden

    if activities_response.status_code == 200:
        st.session_state['activities'] = activities_response.json() #Damit wenn die Anfrage erfolgreich war diese als JSON im Session State gespeichert werden
    else:
        st.error("Fehler beim Laden der Aktivitäten.")

# Nach Runs filtern & Daten formatieren
if 'activities' in st.session_state:
    runs = [a for a in st.session_state['activities'] if a["type"] == "Run"] #Damit nur Aktivitäten vom Typ run gezogen werden

    if runs: #wenn Läufe vorhanden sind wird ein Dictionary mit leeren Listen als Values geschaffen
        data = {
            "Name": [],
            "Datum": [],
            "Distanz (km)": [],
            "Zeit (Minuten)": [],
            "Pace (min/km)": []
        }

        for run in runs:
            distanz_km = run["distance"] / 1000 #Damit Strecken als Kilometer angezeigt werden
            zeit_min = run["moving_time"] / 60 #Damit Zeit in Minuten angezeigt wird
            pace = zeit_min / distanz_km 
            pace_min = int(pace)
            pace_sec = int((pace - pace_min) * 60)
            pace_str = f"{pace_min}:{pace_sec:02d}"

            data["Name"].append(run["name"]) 
            data["Datum"].append(run["start_date_local"][:10])
            data["Distanz (km)"].append(round(distanz_km, 2))
            data["Zeit (Minuten)"].append(round(zeit_min, 1))
            data["Pace (min/km)"].append(pace_str)

        df = pd.DataFrame(data) #Oben werden die zuvor geschaffenen Listen durch die Werte erweitert und anschliessend als DataFrame dargestellt

        # Statistiken
        total_km = df["Distanz (km)"].sum() #Total geloffene Kilometer aufsummieren
        total_min = df["Zeit (Minuten)"].sum() #Total geloffene Zeit aufsummieren

        # Levelsystem
        def berechne_level(km):
            level = 1
            grenze = 1
            while km >= grenze:
                level += 1
                grenze *= 1.10  # 10% schwerer pro Level
            vorherige_grenze = grenze / 1.10
            fortschritt = (km - vorherige_grenze) / (grenze - vorherige_grenze)
            return level - 1, fortschritt

        level, fortschritt = berechne_level(total_km)

        #Eine Funktion welche das aktuelle Level des Benutzers rechnet. Sie funktioniert regressiv mit einer unteren Grenze von 1 bzw 0.
        #Um ein Level aufzusteigen wird erwartet, dass der Benutzer 10% mehr Leistung erbringt als im vorherigen Level und nimmt die geloffenene Kilometer als 
        #Instrument um die Leistung zu messen

        # Abzeichen
        def get_abzeichen(level):
            if level >= 100:
                return "🏆Champion"
            elif level >= 80:
                return "💎 Diamant"
            elif level >= 60:
                return "🥇 Gold"
            elif level >= 40:
                return "🥈 Silber"
            elif level >= 20:
                return "🥉 Bronze"
            else:
                return "🔰 Anfänger"

        abzeichen = get_abzeichen(level)

        #Damit je nach Level dem Benutzer ein Abzeichen verliehen wird 

        # Layout
        st.header("Deine Laufstatistiken")
        col1, col2, col3 = st.columns(3)

        col1.metric("Gesamtdistanz", f"{total_km:.1f} km")
        col2.metric("Gesamtzeit", f"{total_min:.0f} Minuten")
        col3.metric("Schnellste Pace", df["Pace (min/km)"].min()) #minimale Pace wird genommen

        # Hier werden die oberen 3 Elemente in 3 Kolonnen angezeigt

        st.header("Dein Level")

        col4, col5 = st.columns(2) #zwei gleichbreite Spalten
        col4.metric("Level", f"{level}")
        col5.metric("Abzeichen", abzeichen)

        st.progress(fortschritt) #Damit ein Fortschrittsbalken erscheint

        st.caption(f"Fortschritt zu Level {level+1}: {fortschritt*100:.1f}%") #gibt als grauen Text an wieviel Prozent geleistet wurde bis zum nächsten Level

        # Läufe filtern
        st.header("Filtere deine Läufe")

        min_dist = st.number_input("Minimale Distanz (km)", value=0.0)
        max_dist = st.number_input("Maximale Distanz (km)", value=100.0)
        min_time = st.number_input("Minimale Zeit (Minuten)", value=0.0)
        max_time = st.number_input("Maximale Zeit (Minuten)", value=1000.0)
        pace_filter = st.text_input("Maximale Pace (min/km) (z.B. 6:00)")

        #Hier werden verschiedene Zahleneingabefelder generiert damit der Benutzer die Läufe filtern kann

        if pace_filter:
            try:
                pace_minuten, pace_sekunden = map(int, pace_filter.split(":"))
                pace_filter_min = pace_minuten + (pace_sekunden / 60)
            except:
                st.error("Bitte Pace im Format mm:ss eingeben.") 
                pace_filter_min = None
        else:
            pace_filter_min = None

        #Hier werden Fehler abgefangen, wenn der Benutzer das falsche Fomrat verwendet wird er darauf hingewiesen, wie man es beheben kann


        gefiltert = df[
            (df["Distanz (km)"] >= min_dist) &
            (df["Distanz (km)"] <= max_dist) &
            (df["Zeit (Minuten)"] >= min_time) &
            (df["Zeit (Minuten)"] <= max_time)
        ]

        #Hier werden Läufe im Dataframe gefiltert

        if pace_filter_min is not None:
            def pace_str_to_min(pace_str):
                minuten, sekunden = map(int, pace_str.split(":")) 
                return minuten + sekunden / 60
            
            #pace_str_to_min wandelt den Pace-string in eine Float Zahl um damit man mit dieser Zahl rechnen kann

            gefiltert = gefiltert[
                gefiltert["Pace (min/km)"].apply(pace_str_to_min) <= pace_filter_min #Filtert alle Pace im Dataframe
            ]

        st.dataframe(gefiltert) #erstellt neue gefilterte Dataframe

    else:
        st.warning("Keine Läufe gefunden.") 
