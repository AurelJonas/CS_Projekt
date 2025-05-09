# -*- coding: utf-8 -*-
"""
Created: Mar 2025

@author: mirko
"""

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st
import hashlib
from streamlit_option_menu import option_menu
import random
import smtplib
import time
import pandas as pd
import requests

# Einrichten der Verbindng zur firestore Datenbank


if not firebase_admin._apps:  
    config = {
        "type": "service_account",
        "project_id": "strideup-c82ba",
        "private_key_id": "be68e3a2aa95f1bfa8d2bc6a386af18500bff09a",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDKVNCiWLaQD9Us\nwghTMyd4zcJfXXSielgotikGmP8dx4SBrQU2BMwt7u6quvwK64IL3s6NoYdzkFlO\noPMehpvH3OKu5TWEpiLtb5tXFlMZavDcp/Vf2XlipQgMl7goF/AfkEUBovIwVIt2\nCkW9BWcJKZdOf+uCC4WX1+erP4wu5wO7k40FUZ1WRwwv4uZz/4mQ9DRE+jzZyZS9\n/OsdfOTUNGMhIhnsN72d27MJKzaNwI2PxvOT9Q9NrIjMfWevFRD49xZlEzfRyH4r\ntVx2Szm/h+nLYUOa31VnpnpY0JyAGqKnCUidaI5VAY0eqXxD3UK7SECkh5le2F3v\naoK/ZpDHAgMBAAECggEAXjjsJcZJUkJFREAhr1khlxS+4Tk8wRNXbbIS3eMu3vfU\nYa0owZSvXu6nT3OfPxiYaZ27M+KWmP8OT9sNDNijwAnBuK+94gWaO1cfkIkxbqNK\nAn/m+VlluUXgPzkCRg2Lwa8mK5Jt1YrxnSlAe7uB1Zb8Qs64ZkmmT2V4mduQlSAk\nQxEJ1IDEI9lJHK+AVbMbBgmuGDWQmHmuF3pGgUeNIiwuczRw0x5GWVZmXFO/eBEC\namOoWCuS9c/mKDxy5/WAPvQzRkIVWV7elot9Cx73JHa7akU8miw1/eZiy/xCm/eh\nQUbXUZkmYMoCjdqhJWa+B5zrJm4twa2G7KiCSzvfbQKBgQDzD2ocCQRGxaZ5O64X\ndYod1h9CZhtyLuaFqH64j8z4wO3wWUM2gL3jr9BH7u0xZpDlW7i+EZ8U2ft7mAxn\nF/jGF7TDIezko/al622DMNANFE6GrGGnERVTk7aVh/DXULxdirvX0Ez6+OeX4d5h\nKbtL5dMWGpE3TuWnogweNqDIuwKBgQDVGlHsT5py1PHQG4MKMgMm/yapDfn1RkHN\nPYr/ccZ/2bSFGNmf5THPf5NhDChjlEkwxUCnKSEaXHMNJR6ki2Fs4rTbvavf9N30\nCY5iInTm9dZSH2Q19g9O3gVE6SyEJWntcpCQwHz1DVNgLI6EzeCozPx0jn0+uo0F\nxxjbHmOtZQKBgQDCuV6xByg96qrsBTv731a/gIOalmL2n0xfWBXtlocH4si8/UYz\nrAB1IK0kc+3i3eDHXywqWcOw2NH4ul91WGcdjHBsxAkdQ56eXnZl2/1R/SrMCd5S\nEgWb54MnWLlCRpQh/Ltwsph5mF8x9upJvT0oGP97fd1JChRCsDg1HF7DcQKBgHIY\nyn4czNPowaOr50hBKMDrYban/gnd2QNbjR1hvGbdmDKe8H4Ux8uSQcV3LfTLAzjy\nk8AsXEXx88O4+SQeYEZdR3pTnj+lqmSr7SkLy82RGHQVzKC7osyWQPn5YlVKduGk\nMlTeSsklnlti39epJz0Zq514YQSB+1l5lQxUxAelAoGBAN65Bmmdp0nRvTs/Yl5I\nb1tTeZ2la5aSxgRuny5fPOZQ0Ey2rADXyRItlhXo5wJG0iC8if+FfcYJceP9I/Q1\n2Kr1vrMLcx2jb4axActBRqjRrg6x0KUCmlAaXxUfISZ80dwvhATZa02dxOIpXhgP\nS97qB2dbeySjpDTFo9DodkR0\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-fbsvc@strideup-c82ba.iam.gserviceaccount.com",
        "client_id": "103696280889436896486",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40strideup-c82ba.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }  
    cred = credentials.Certificate(config)
    firebase_admin.initialize_app(cred)
db = firestore.client()



# session.state wird genutz um Werte dauerhaft in variablen zu speichern.
# Diese werden beibehalten auch wenn die Seite durch eine User Eingabe neu geladen wird.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if 'code' not in st.session_state:
    st.session_state.code = ""
if 'access_token' not in st.session_state:
    st.session_state.token = ""

if not st.session_state.logged_in:
    
    # Funktionen
    
    # Funktion zum verschlüsseln des Passwortes
    
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Funktion um die User Daten zu erfassen und in der Datenbank zu speichern
    # Die Funktion übernimmt die vom User eingegebenen Werte wie Username, Passwort, etc. und überprüft, ob der User bereits vorhanden ist.
    # Falls ja, gibt es eine entsprechende Meldung. Ist der Username noch frei, wird der neue User in der Datenbank angelegt.
    
    def user_reg(username,password,name,last_name,e_mail,strava_id):
        reference = db.collection('users').document(username)
        user = reference.get()
        if user.exists:
            return False
        else:
            reference.set({
                'username': username,
                'password': hash_password(password),
                'name': name,
                'last_name': last_name,
                'user_e_mail': user_e_mail,
                'client_id':client_id,
                'client_secret': client_secret
                })
            return True

    # Log In Funktion
    
    def login(username,password):
        reference = db.collection('users').document(username)
        user = reference.get()
        if user.exists:
            user_data = user.to_dict()
            if user_data['password'] == hash_password(password):
                return True
        return False
    
    def request_new_pw(username):
        reference = db.collection('users').document(username)
        user = reference.get()
        if user.exists:
            user_data = user.to_dict()
            user_e_mail = user.get('user_e_mail')
            e_mail = "no.reply.strideUP@gmail.com"
            subject = "Passwort reset strideUP"
            code = random.randint(100000, 999999)
            message = "Untenstehend finden Sie den Code um das Passwort zurueckzusetzen. Bitte geben Sie diesen auf der strideUP Seite ein."
            text = f"Subject: {subject}\n\nGuten Tag {username}\n\n{message}\n\n{code}"
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(e_mail, "xaydcpwqhdrjiyjn")
            server.sendmail(e_mail, user_e_mail, text.encode('utf-8'))
            return code
        else: return False
    
    def reset_pw(username,new_password):
        reference = db.collection('users').document(username)
        user = reference.get()
        if user.exists:
            reference.update({
                'password': hash_password(new_password)
                })
            return True
   
        
    
    
    st.title('Willkommen bei strideUP')
    
    choice = st.selectbox("Option", ["Login","Registrierung","Passwort zurücksetzen"])
        
    if choice == "Registrierung":
        st.subheader("Registrierung")
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type='password')
        name = st.text_input("Name")
        last_name = st.text_input("Nachname")
        user_e_mail = st.text_input("E-Mail")
        client_id = st.text_input("Strava Identifikationsnummer")
        client_secret =st.text_input("Strava Kundenschlüssel")
        if st.button("Registrieren"):
            result = user_reg(username, password, name, last_name, user_e_mail,client_id)
            if result == False:
               st.error('Benutzername existiert bereits')
            elif result == True:
                st.success('Registrierung erfolgreich. Sie können sich nun Einloggen.')
                
                
    
    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type='password')
        if st.button("Login"):
            result = login(username, password)
            if result == False:
                st.error('Benutzername oder Passwort falsch')
            elif result == True:
                st.success('Login erfolgreich')
                st.session_state.logged_in = True
                reference = db.collection('users').document(username)
                user = reference.get()
                user_data = user.to_dict()
                st.session_state.user = user_data['username']
                st.rerun()
    
    elif choice == "Passwort zurücksetzen":
        username = st.text_input("Benutzername")
        code = st.text_input("Bitte Code aus ihrer Mail eingeben.")
        if code != "":
            code = int(code)
        new_password = st.text_input("Neues Passwort", type= 'password')
        col1,col2 = st.columns([1,4])
        if col1.button("Code anfordern"):
            result = request_new_pw(username)
            if result == False:
                st.error("User nicht gefunden. Bitte überprüfen Sie Ihre Eingaben oder kontaktieren Sie unseren Kundendienst.")
            else:
                st.write('Wir haben Ihnen einen Code zum zurücksetzen des Passwortes per Mail geschickt. Bitte geben Sie den Code und Ihr neues Passwort ein und klicken Sie auf zurücksetzen')
                progress_bar = st.progress(0)
                for perc_completed in range(100):
                    time.sleep(0.1)
                    progress_bar.progress(perc_completed+1)  
                st.session_state.code = result
                st.rerun()
        elif col2.button('Code überprüfen und neues Passwort setzen'):
            if code == st.session_state.code:
                result = reset_pw(username, new_password)
                if result == True:
                    st.success("Passwort erfolgreich zurückgesetzt.")
                        
else:
    # Funktionen
    
    
    
 
    
    
    
    
    
    
    selected = option_menu(
        menu_title= None,
        options= ['Home','Routen','Trainings','Log out'],
        icons=['house-fill','map','strava','person-plus-fill','box-arrow-right'],
        default_index=0,
        orientation='horizontal'
        )
    
    if selected == 'Home':
        st.title(f'Willkommen {st.session_state.user}')
        client_id = "158758"
        client_secret = "a945b138001960fa61796b4c4aa8e598321c9583"
        redirect_uri = "http://localhost:8501"
        
        # Anmeldung
        auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=activity:read_all"
        #st.markdown(f"[ Hier klicken um dich mit Strava zu verbinden]({auth_url})")
        if st.markdown(f'<a href="{redirect_uri}" target="_self"> Mit Strava verbinden</a>',unsafe_allow_html=True):
            st.session_state.logged_in = True
            reference = db.collection('users').document(username)
            user = reference.get()
            user_data = user.to_dict()
            st.session_state.user = user_data['username']
            st.rerun()
        
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
        
        
        
        
        
    elif selected == 'Routen':
        st.title('Lass uns eine neue Route planen!')
        
        
        
        
        
        
    elif selected == 'Trainings':
        st.title('Sieh dir deine Statistiken an!')
        
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
        
        
        
        
        
    
          
        
        
    elif selected == 'Log out':
        st.session_state.logged_in = False
        st.rerun()
        