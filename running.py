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
import requests
import pandas as pd
import datetime

# Einrichten der Verbindng zur firestore Datenbank


if not firebase_admin._apps:  
    config = {
        "type": "service_account",
        "project_id": "strideup-c82ba",
        "private_key_id": "fa9f7f78d1eddc506e19623bb2d2560db4784473",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDYquqgxvf+UWYg\nWvkea3tmrkpgv1pj2dHkFvXuP4Ka/WD7XGXhaeuPTP3K86pnn7FZED/3LrXyXADN\n/m+JgzvosVnY6biFUsMQvjg9cSPn9TcMxGHyy8aN2rODDi8q79UXKvAohY/8weBA\ndSQUZCC0XLZskLtVkAwa6PbyfzEMNpuZVAAN9Tr+1PdlGYsa6c317njLE5p7+3h6\nT7GBM2+aFCoZWgnQQnhWy2kLPr+E0fUgGbR7/8WB4Sub2mwvBL4jCN5ty6sWGSwV\ngn/jYu6QjHoH40g5ZrsNAFm5AT9rO1+sO8NYnpF2CV0BOqRHacUDbE2f9dfQqK/L\nA3qY4hBjAgMBAAECggEANlHfYfCQMw/YQUtdgn1i4jLXDdtbf4YYA42oGZONnGri\n2hHnrvQ9rN8aD7w4ICOetFwJFWD+F6VuRDbCYuDmb6erBWFPNAm0QunVsr2/SUOm\nigpgHh1tiZnngHdZZvPa4iSPMjGOEEnQ/YgAxCX4Nw+5Yo2EkeZ7ynFWnCQ8OTmv\neGPrBTWGYAgUendMTMt120evG700pUeOoo10TmlL1ncJCYqeTYCuEmIMrsd+TAWW\nbcJnX7RHCf9Wt3tCHT3kFPoyckOTAAjsaC08cv05rd1rpmN5hfGDQfR6UgZVC1Tf\nfPb9L69lGdsQr/meC10AEet5mPxDdk3zkTqoi2VlRQKBgQDxC/BebBlcoxpIZmjG\nNYM+VzY+piI09gzy/jWZoQEQlrNuvvcfHMzT7ktlU/zRcC38sIa886R8oGumd1nH\nf/mtn0ZaiTDVz69rstbuqFIHoLl/MZkhlY8jV/193rjOnYnMZD7PWA4bh3HJ4Zy1\nha3cqM2qZa0eDPyNssEsc3TNDQKBgQDmG9CY0cDjn61+ibanjljFCPLh+U/XXUc/\nXJydm5HSqk30/DS44ysMTsI7V4bHwG2eH82YZwriUt+bNTCecZOz8YuiEtUp1olX\nqlrpVCf5f/nYifkZ4XCxqke2uT/UyGXBF1phhExsOKUbHqVrPV3m6/rYKfsgWtyh\nXw/1oYVXLwKBgQCT2lXjJP1dhDIP7LkhsxtAtu/v96mNwMrqlaE9DbQAf9+p83rT\nW7AL4uPeUGkH8n5Su9i5t9zSEPhXEGhCZa45oDPgPrx0ucKJFhaeJyLByQVfDoY2\nQm2dKVC0z1OecKVgeLDKL+HfYvIZ+chM06V0bxpQBbPtddvH8rho0pz3VQKBgQDJ\n73Ty93hICbQujNovVvtOBplnd+v6OtCwqSyEH6cr8eqx6La33hvEFEXd3+TW3WcV\nUiGR8jOaBFJZGaeOFGwjiQEZ/V719WDX/xcDFqhyCz4OKp7heHb2Y1HF5/I9YJPz\njPPzCjAq9Nbn4tAWOWdzpHmhQ84vSa2/K/aMf+/NXwKBgC8DbNi/xdWImN+P9b+q\n6veIeNRZCpTKVb8ANYxOR2B6pQVdeGuZ5KZtpWpi39qGTfryjVPp4uGhwMVOnf8I\nQRSNci+JmewxUfy/gxcembpXcaYViWV3p+81BLqjsJCv9Uuojfn3GjDItwvBgB5z\nKY+UFKFvMCAnYR3SoMB/Y0KP\n-----END PRIVATE KEY-----\n",
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
                'strava_id':strava_id
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
        strava_id = st.text_input("Strava Identifikationsnummer")
        if st.button("Registrieren"):
            result = user_reg(username, password, name, last_name, user_e_mail,strava_id)
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
                st.error("User nicht gefunden. Bitte überprüfen Sie Ihre Eingaben oder rufen Sie uns an unter 031 331 88 67")
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
    
    # Funktion zur erstellung eines neuen Teams
    def create_team(teamname,username):
        reference = db.collection('teams').document(teamname)
        team = reference.get()
        if team.exists:
            return False
        else:
            reference.set({
                "teamname": teamname,
                "members": [username]                
                })
            return True
            
    # Funktion um einem bestehenden Team beizutreten
    def join_team(teamname,username):
        reference = db.collection('teams').document(teamname)
        team = reference.get()
        if team.exists:
            members = team.to_dict()['members']
            if username not in members:
                members.append(username)
                reference.update({
                    "members": members
                    })
                return True
            else:
                return False
        else:
            return False
    
 
    selected = option_menu(
        menu_title= None,
        options= ['Home','Routen','Trainings','Teams','Log out'],
        icons=['house-fill','map','strava','person-plus-fill','box-arrow-right'],
        default_index=0,
        orientation='horizontal'
        )
    
    if selected == 'Home':
        st.title(f'Willkommen {st.session_state.user}')
        
        
        
        
        
        
    elif selected == 'Routen':
        st.title('Lass uns eine neue Route planen!')
        
        
        
        
        
        
    elif selected == 'Trainings':
        st.title('Sieh dir deine Statistiken an!')
        
        #Strava API verbinden
        CLIENT_ID = "DEIN_CLIENT_ID"
        CLIENT_SECRET = "DEIN_CLIENT_SECRET"
        REDIRECT_URI = "http://localhost:8501"  
        
        st.set_page_config(page_title="🏃‍♂️ Strava Lauf-Dashboard", layout="wide")
        st.title("🏃‍♂️ Strava Lauf-Dashboard")
        
        #Authentifizierung
        auth_url = (
            f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=activity:read_all"
        )
        
        st.markdown(f"[🔗 Mit Strava verbinden]({auth_url})")
        
        code = st.text_input("🔑 Code hier einfügen (aus URL nach Login)")
        
        if code:
            with st.spinner("Authentifiziere bei Strava..."):
                token_response = requests.post(
                    "https://www.strava.com/oauth/token",
                    data={
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "code": code,
                        "grant_type": "authorization_code",
                    },
                )
                if token_response.status_code == 200:
                    tokens = token_response.json()
                    access_token = tokens["access_token"]
                    st.success("✅ Zugriff erhalten!")
                else:
                    st.error("❌ Authentifizierung fehlgeschlagen")
                    st.stop()
        
            #Daten von Strava importieren
            with st.spinner("Lade Aktivitäten..."):
                headers = {"Authorization": f"Bearer {access_token}"}
                url = "https://www.strava.com/api/v3/athlete/activities"
                params = {"per_page": 100, "page": 1}
                r = requests.get(url, headers=headers, params=params)
                activities = r.json()
        
                if isinstance(activities, dict) and activities.get("message"):
                    st.error("Fehler beim Laden der Aktivitäten.")
                    st.stop()
        
                df = pd.DataFrame(activities)
                df = df[df["type"] == "Run"]
        
                if df.empty:
                    st.warning("Keine Laufaktivitäten gefunden.")
                    st.stop()
        
                #Pace berechnen und formatieren
                df["distance_km"] = df["distance"] / 1000
                df["moving_time_min"] = df["moving_time"] / 60
                df["pace_min_per_km"] = df["moving_time"] / 60 / df["distance_km"]  # Minuten pro km
                df["pace_str"] = df["pace_min_per_km"].apply(
                    lambda x: f"{int(x)}:{int((x - int(x)) * 60):02d} min/km"
                )
                df["date"] = pd.to_datetime(df["start_date_local"]).dt.date
        
                #kumulierte Werte
                total_distance = df["distance_km"].sum()
                total_time_min = df["moving_time_min"].sum()
                best_pace = df["pace_min_per_km"].min()
                best_pace_str = f"{int(best_pace)}:{int((best_pace - int(best_pace)) * 60):02d} min/km"
        
            # Bestzeiten
            st.header("🏅 Lauf-Statistiken")
        
            col1, col2, col3 = st.columns(3)
            col1.metric("📏 Gesamtdistanz", f"{total_distance:.2f} km")
            col2.metric("🕒 Gesamtzeit", f"{total_time_min:.0f} Min")
            col3.metric("⚡ Schnellste Pace", best_pace_str)
        
        
            # Letzte Läufe
            st.header("📋 Letzte Läufe")
        
            st.dataframe(df[["date", "name", "distance_km", "moving_time_min", "pace_str"]].rename(columns={
                "date": "Datum",
                "name": "Titel",
                "distance_km": "Distanz (km)",
                "moving_time_min": "Dauer (min)",
                "pace_str": "Pace",
            }))

    elif selected == 'Dein Rang':
        st.title('Sieh dir deinen Rang an!')
    
    elif selected == 'Teams':
          
        choice_2 = st.selectbox("Option",["Team erstellen","Team beitreten"])
                
        if choice_2 == "Team erstellen":
            username = st.text_input("Benutzername",value = st.session_state.user)
            teamname = st.text_input("Teamname")
            if st.button("Team erstellen"):
                result = create_team(teamname, username)
                if result == False:
                    st.error('Team existiert bereits')
                elif result == True:
                    st.success('Team erstellt')
                        
                    
        elif choice_2 == "Team beitreten":
            username = st.text_input("Benutzername",value = st.session_state.user)
            teamname = st.text_input("Teamname")
            if st.button("Team beitreten"):
                result = join_team(teamname, username)
                if result == False:
                    st.error('Team nicht gefunden oder Sie sind dem Team bereits beigetreten')
                elif result == True:
                    st.success('Team beigetreten')
        
    elif selected == 'Log out':
        st.session_state.logged_in = False
        st.rerun()
        
