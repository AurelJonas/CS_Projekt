import streamlit as st
import requests
import pandas as pd

# Strava-API Konfiguration
client_id = "155219"
client_secret = "f29e1b698742839f29db2a2f2e8d363cda142c1d"
redirect_uri = "http://localhost:8501"

# Titel
st.set_page_config(page_title="Mein Dashboard", layout="wide")
st.title(":runner: Mein Dashboard")

# Anmeldung
auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=activity:read_all"
st.markdown(f"[ Hier klicken um dich mit Strava zu verbinden]({auth_url})")

# Eingabefeld Login
code = st.text_input(" Füge den Code von Strava hier ein:")

# Token speichern
if 'access_token' not in st.session_state:
    if code:
        token_url = "https://www.strava.com/oauth/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=payload)

        if response.status_code == 200:
            st.session_state['access_token'] = response.json()["access_token"]
            st.success("Erfolgreich eingeloggt!")
        else:
            st.error("Fehler beim Einloggen")

# Aktivitäten speichern
if 'activities' not in st.session_state and 'access_token' in st.session_state:
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    params = {"per_page": 200, "page": 1}

    activities_response = requests.get(activities_url, headers=headers, params=params)

    if activities_response.status_code == 200:
        st.session_state['activities'] = activities_response.json()
    else:
        st.error("Fehler beim Laden der Aktivitäten.")

# Nach Runs filtern & Daten formatieren
if 'activities' in st.session_state:
    runs = [a for a in st.session_state['activities'] if a["type"] == "Run"]

    if runs:
        data = {
            "Name": [],
            "Datum": [],
            "Distanz (km)": [],
            "Zeit (Minuten)": [],
            "Pace (min/km)": []
        }

        for run in runs:
            distanz_km = run["distance"] / 1000
            zeit_min = run["moving_time"] / 60
            pace = zeit_min / distanz_km
            pace_min = int(pace)
            pace_sec = int((pace - pace_min) * 60)
            pace_str = f"{pace_min}:{pace_sec:02d}"

            data["Name"].append(run["name"])
            data["Datum"].append(run["start_date_local"][:10])
            data["Distanz (km)"].append(round(distanz_km, 2))
            data["Zeit (Minuten)"].append(round(zeit_min, 1))
            data["Pace (min/km)"].append(pace_str)

        df = pd.DataFrame(data)

        # Statistiken
        total_km = df["Distanz (km)"].sum()
        total_min = df["Zeit (Minuten)"].sum()

        # Levelsystem
        def berechne_level(km):
            level = 1
            grenze = 1
            while km >= grenze:
                level += 1
                grenze *= 1.10  # 20% schwerer pro Level
            vorherige_grenze = grenze / 1.10
            fortschritt = (km - vorherige_grenze) / (grenze - vorherige_grenze)
            return level - 1, fortschritt

        level, fortschritt = berechne_level(total_km)

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

        # Layout
        st.header("Deine Laufstatistiken")
        col1, col2, col3 = st.columns(3)

        col1.metric("Gesamtdistanz", f"{total_km:.1f} km")
        col2.metric("Gesamtzeit", f"{total_min:.0f} Minuten")
        col3.metric("Schnellste Pace", df["Pace (min/km)"].min())

        st.header("Dein Level")

        col4, col5 = st.columns(2)
        col4.metric("Level", f"{level}")
        col5.metric("Abzeichen", abzeichen)

        st.progress(fortschritt)

        st.caption(f"Fortschritt zu Level {level+1}: {fortschritt*100:.1f}%")

        # Läufe filtern
        st.header("Filtere deine Läufe")

        min_dist = st.number_input("Minimale Distanz (km)", value=0.0)
        max_dist = st.number_input("Maximale Distanz (km)", value=100.0)
        min_time = st.number_input("Minimale Zeit (Minuten)", value=0.0)
        max_time = st.number_input("Maximale Zeit (Minuten)", value=1000.0)
        pace_filter = st.text_input("Maximale Pace (min/km) (z.B. 6:00)")

        if pace_filter:
            try:
                pace_minuten, pace_sekunden = map(int, pace_filter.split(":"))
                pace_filter_min = pace_minuten + (pace_sekunden / 60)
            except:
                st.error("Bitte Pace im Format mm:ss eingeben.")
                pace_filter_min = None
        else:
            pace_filter_min = None

        gefiltert = df[
            (df["Distanz (km)"] >= min_dist) &
            (df["Distanz (km)"] <= max_dist) &
            (df["Zeit (Minuten)"] >= min_time) &
            (df["Zeit (Minuten)"] <= max_time)
        ]

        if pace_filter_min is not None:
            def pace_str_to_min(pace_str):
                minuten, sekunden = map(int, pace_str.split(":"))
                return minuten + sekunden / 60

            gefiltert = gefiltert[
                gefiltert["Pace (min/km)"].apply(pace_str_to_min) <= pace_filter_min
            ]

        st.dataframe(gefiltert)

    else:
        st.warning("Keine Läufe gefunden.")
