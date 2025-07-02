import streamlit as st
import os
from PIL import Image
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from Src.user_db import check_login, create_user, get_user, update_person, list_all_users
from Src.analyze_hr_data import analyze_hr_data
from Src.ekg_data import Ekg_tests

DEFAULT_PICTURE_PATH = "data/pictures/none.jpg"

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
    </style>
""", unsafe_allow_html=True)

# Session vorbereiten
for key in ["logged_in", "user", "username"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Sidebar mit Logout
with st.sidebar:
    st.title("Navigation")
    if st.session_state["logged_in"]:
        st.markdown(f"**Sie sind angemeldet als:** `{st.session_state['username']}`")
        if st.button("Logout"):
            for key in ["logged_in", "user", "username"]:
                st.session_state.pop(key, None)
            st.success("Abgemeldet.")
            st.stop()

# Login / Registrierung
if not st.session_state["logged_in"]:
    st.title("Anmeldung & Registrierung")

    login_col, reg_col = st.columns(2)

    with login_col:
        st.subheader("Login")
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            user = check_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.user = user
                st.success("Login erfolgreich.")
                st.stop()
            else:
                st.error("Benutzername oder Passwort falsch. Bitte versuche es erneut. Sollten Sie Ihr Passwort vergessen haben, kontaktieren Sie bitte den Administrator.")

    with reg_col:
        st.subheader("Registrierung")
        new_username = st.text_input("Benutzername", key="reg_username")
        new_password = st.text_input("Passwort", type="password", key="reg_password")
        new_firstname = st.text_input("Vorname", key="reg_firstname")
        new_lastname = st.text_input("Nachname", key="reg_lastname")
        new_birthyear = st.number_input("Geburtsjahr", min_value=1900, max_value=2100, value=2000, key="reg_birthyear")
        uploaded_img = st.file_uploader("Profilbild (optional)", type=["jpg", "jpeg", "png"])

        if st.button("Registrieren"):
            if get_user(new_username):
                st.error("Benutzername existiert bereits.")
                st.stop()

            used_ids = [u["person"]["id"] for u in list_all_users() if "person" in u]
            new_id = max(used_ids + [0]) + 1

            if uploaded_img:
                os.makedirs("data/images", exist_ok=True)
                img_path = f"data/images/user_{new_id}.jpg"
                Image.open(uploaded_img).save(img_path)
            else:
                img_path = DEFAULT_PICTURE_PATH

            new_person = {
                "id": new_id,
                "firstname": new_firstname,
                "lastname": new_lastname,
                "date_of_birth": new_birthyear,
                "picture_path": img_path,
                "ekg_tests": []
            }

            create_user(new_username, new_password, "user", f"{new_lastname}, {new_firstname}", new_person)
            st.success("Registrierung erfolgreich. Jetzt bitte einloggen.")
            st.stop()

    st.stop()

# App nach Login
st.title("EKG Analyse App")

user = st.session_state["user"]
person = user["person"]

tabs = st.tabs([
    "Dein Profil",
    "Profil bearbeiten",
    "HF-Zonen",
    "EKG & Herzfrequenz",
    "EKG-Datei hochladen"
])

# Tab 1: Profil
with tabs[0]:
    st.header(f"Willkommen, {person['firstname']} {person['lastname']}")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(person["picture_path"], width=200)
    with col2:
        st.write(f"**Du hast folgende ID:** {person['id']}")
        st.write(f"**Dein Alter:** {2025 - person['date_of_birth']} Jahre")
        st.write(f"**Geschätzte maximale Herzfrequenz:** {round(220 - (2025 - person['date_of_birth']))} bpm")

# Tab 2: Bearbeiten
with tabs[1]:
    st.subheader("Benutzerdaten bearbeiten")

    st.text_input("ID (nicht änderbar)", value=str(person["id"]), disabled=True)
    new_firstname = st.text_input("Vorname", value=person["firstname"], key="edit_firstname")
    new_lastname = st.text_input("Nachname", value=person["lastname"], key="edit_lastname")
    new_birthyear = st.number_input("Geburtsjahr", min_value=1900, max_value=2100, value=person["date_of_birth"], step=1, key="edit_birth")

    # Aktuelles Bild anzeigen mit Fehlerbehandlung
    st.markdown("Aktuelles Profilbild:")
    try:
        st.image(Image.open(person["picture_path"]), width=150)
    except Exception as e:
        st.warning("Profilbild konnte nicht geladen werden.")

    # Neues Bild hochladen (optional)
    st.markdown("Optional: Neues Profilbild hochladen")
    new_uploaded_img = st.file_uploader("Neues Bild auswählen", type=["jpg", "jpeg", "png"], key="edit_upload")

    new_picture = person["picture_path"]  # Standard: bisheriges Bild beibehalten

    if new_uploaded_img:
        os.makedirs("data/images", exist_ok=True)
        new_img_path = f"data/images/user_{person['id']}.jpg"
        Image.open(new_uploaded_img).save(new_img_path)
        new_picture = new_img_path

    if st.button("Änderungen speichern"):
        updated_person = {
            "id": person["id"],
            "firstname": new_firstname,
            "lastname": new_lastname,
            "date_of_birth": new_birthyear,
            "picture_path": new_picture,
            "ekg_tests": person.get("ekg_tests", [])
        }

        update_person(st.session_state["username"], updated_person)
        st.success("Änderungen gespeichert. Bitte die Seite neu laden.")
        st.stop()

# Tab 3: HF-Zonen
with tabs[2]:
    st.header("Analyse deiner Herzfrequenz-Zonen")
    max_hr = st.number_input("Maximale Herzfrequenz (bpm)", min_value=40, max_value=240, value=200)
    fig, data = analyze_hr_data(max_hr)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(data, use_container_width=True)

# Tab 4: EKG + HF Verlauf
with tabs[3]:
    st.header("EKG Signal & Herzfrequenz Verlauf")

    sampling_rate = st.number_input("Samplingrate (Hz)", min_value=50, max_value=2000, value=500, step=10)
    threshold = st.slider("Schwellenwert zur Peak-Erkennung", 100, 1000, 360, step=10)

    ekg_tests = person.get("ekg_tests", [])
    if not ekg_tests:
        st.warning("Keine EKG-Daten verfügbar.")
        st.stop()

    # Testauswahl
    label = [f"{i+1}. {t['date']}" for i, t in enumerate(ekg_tests)]
    selected_test = ekg_tests[st.selectbox("EKG-Test auswählen", range(len(ekg_tests)), format_func=lambda i: label[i])]

    ekg = Ekg_tests(
        id=selected_test["id"],
        date=selected_test["date"],
        result_link=selected_test["result_link"],
        sampling_rate=sampling_rate
    )
    ekg.find_peaks(threshold=threshold)
    ekg.estimate_hr()

    signal = ekg.signal
    if not signal or len(signal) < 2:
        st.warning("Ungültiges Signal.")
        st.stop()

    duration = len(signal) / sampling_rate
    st.caption(f"Gesamtdauer: {round(duration/60, 2)} Minuten")

    max_view = st.number_input("Sichtbarer Zeitraum (s)", 1.0, duration, 10.0)
    start, end = st.slider("Bereich wählen", 0.0, round(duration - max_view, 2),
                           (0.0, min(max_view, duration)), step=0.1)
    start_idx, end_idx = int(start * sampling_rate), int(end * sampling_rate)
    visible_signal = signal[start_idx:end_idx]

    # Plot
    x_vals = [i / sampling_rate for i in range(start_idx, end_idx)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=visible_signal, mode="lines", name="EKG"))

    if ekg.peaks:
        peak_times = [i / sampling_rate for i in ekg.peaks if start_idx <= i < end_idx]
        peak_vals = [signal[i] for i in ekg.peaks if start_idx <= i < end_idx]
        fig.add_trace(go.Scatter(x=peak_times, y=peak_vals, mode="markers", marker=dict(color="red", size=6), name="Peaks"))

    fig.update_layout(title="EKG mit Peaks", xaxis_title="Zeit (s)", yaxis_title="Amplitude (mV)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Herzfrequenz
    if ekg.hr:
        df_hr = pd.DataFrame({"Peak-Nr": range(1, len(ekg.hr)+1), "Herzfrequenz (bpm)": ekg.hr})
        st.write(f"Durchschnittliche HF: **{round(np.mean(ekg.hr), 2)} bpm**")

        # Gleitender Durchschnitt
        window = st.slider("Fenstergröße für geglättete HF", 1, 30, 5)
        smoothed = np.convolve(ekg.hr, np.ones(window)/window, mode="valid")
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(y=smoothed, mode="lines+markers", name="Geglättete HF"))
        fig_hr.update_layout(title="Gleitender Durchschnitt (HF)", xaxis_title="Intervall der R-Spitzen", yaxis_title="HF (bpm)", height=400)
        st.plotly_chart(fig_hr, use_container_width=True)
    
    
    st.subheader("Anomalieerkennung (anpassbar)")

    tachy_threshold = st.number_input("Grenzwert Tachykardie (bpm)", min_value=60, max_value=200, value=100)
    brady_threshold = st.number_input("Grenzwert Bradykardie (bpm)", min_value=20, max_value=100, value=60)

    anomalies = ekg.detect_anomalies(tachykard_limit=tachy_threshold, bradykard_limit=brady_threshold)

    if anomalies:
        st.warning("Anomalien erkannt:")
        df_anomalies = pd.DataFrame([
            {"Index": idx, "HF (bpm)": hr if hr else "-", "Typ": typ}
            for idx, hr, typ in anomalies
        ])
        st.dataframe(df_anomalies, use_container_width=True)
    else:
        st.success("Keine Anomalien gefunden.")

# Tab 5: EKG-Datei hochladen
with tabs[4]:
    st.subheader("EKG-Datei hochladen")

    # Sicherstellen, dass ekg_tests existiert
    if "ekg_tests" not in person or not isinstance(person["ekg_tests"], list):
        person["ekg_tests"] = []

    # Eingabe für Datum
    ekg_date = st.date_input("Datum des EKG-Tests")

    # Datei hochladen (nur TXT erlaubt)
    uploaded_file = st.file_uploader("EKG-Datei im .txt-Format hochladen", type=["txt"])

    if uploaded_file and ekg_date:
        # Neuen Dateinamen und Pfad generieren
        new_ekg_id = len(person["ekg_tests"]) + 1
        os.makedirs("data/ekg_data", exist_ok=True)
        save_path = f"data/ekg_data/user{person['id']}_ekg{new_ekg_id}.txt"

        # Datei speichern
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

        # EKG-Eintrag erzeugen
        new_ekg_entry = {
            "id": new_ekg_id,
            "date": ekg_date.strftime("%Y-%m-%d"),
            "result_link": save_path
        }

        # Hinzufügen zu ekg_tests
        person["ekg_tests"].append(new_ekg_entry)

        # Datenbank aktualisieren
        update_person(st.session_state["username"], person)

        st.success("EKG-Datei erfolgreich hochgeladen und gespeichert.")
    elif uploaded_file and not ekg_date:
        st.warning("Bitte ein Datum angeben.")

