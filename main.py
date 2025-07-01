import streamlit as st
import json
import os
from PIL import Image
import pandas as pd
import numpy as np

from Src.user_db import check_login, create_user, get_user, update_person
from Src.analyze_hr_data import analyze_hr_data
from Src.ekg_data import Ekg_tests

DEFAULT_PICTURE_PATH = "data/pictures/none.jpg"

# === Session vorbereiten ===
for key in ["logged_in", "user", "username"]:
    if key not in st.session_state:
        st.session_state[key] = None

# === Sidebar mit Logout ===
with st.sidebar:
    if st.session_state["logged_in"]:
        st.markdown(f"👤 Angemeldet als: **{st.session_state['username']}**")
        if st.button("🚪 Logout"):
            for key in ["logged_in", "user", "username"]:
                st.session_state.pop(key, None)
            st.success("Abgemeldet.")
            st.stop()

# === Login / Registrierung ===
if not st.session_state["logged_in"]:
    st.title("🔐 Anmeldung")

    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Login"):
        user = check_login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.user = user
            st.success("Login erfolgreich.")
            st.stop()
        else:
            st.error("❌ Benutzername oder Passwort falsch.")

    # === Registrierung ===
    st.markdown("---")
    st.subheader("🆕 Neuer Nutzer? Registrieren:")

    new_username = st.text_input("Neuer Benutzername", key="reg_username")
    new_password = st.text_input("Passwort", type="password", key="reg_password")
    new_firstname = st.text_input("Vorname", key="reg_firstname")
    new_lastname = st.text_input("Nachname", key="reg_lastname")
    new_birthyear = st.number_input("Geburtsjahr", min_value=1900, max_value=2100, value=2000, key="reg_birthyear")
    uploaded_img = st.file_uploader("Profilbild (optional)", type=["jpg", "jpeg", "png"])

    if st.button("Registrieren"):
        if get_user(new_username):
            st.error("❌ Benutzername ist bereits vergeben.")
            st.stop()

        # neue ID ermitteln
        from Src.user_db import list_all_users
        all_users = list_all_users()
        used_ids = [u["person"]["id"] for u in all_users if "person" in u]
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

        fullname = f"{new_lastname}, {new_firstname}"
        create_user(new_username, new_password, "user", fullname, new_person)

        st.success("✅ Registrierung erfolgreich. Jetzt bitte einloggen.")
        st.stop()

    st.stop()

# === App nach Login ===
st.title("EKG-Analyse")

user = st.session_state["user"]
person = user["person"]

tabs = st.tabs([
    "Deine Nutzerdaten",
    "Nutzerdaten bearbeiten",
    "Herzrate über Zeit",
    "EKG & HF-Verlauf"
])

with tabs[0]:
    st.subheader("Willkommen, " + person["firstname"] + "! ")
    st.image(Image.open(person["picture_path"]), width=200)
    st.write("**Name:**", f"{person['lastname']}, {person['firstname']}")
    st.write("Deine ID:", person["id"])
    st.write("Dein Alter:", 2025 - person["date_of_birth"], "Jahre")
    st.write("Schätzung deiner maximalen Herzfrequenz:", round(220 - (2025 - person["date_of_birth"])), "bpm")

with tabs[1]:
    st.subheader("✏️ Benutzerdaten bearbeiten")

    st.text_input("ID (nicht änderbar)", value=str(person["id"]), disabled=True)
    new_firstname = st.text_input("Vorname", value=person["firstname"], key="edit_firstname")
    new_lastname = st.text_input("Nachname", value=person["lastname"], key="edit_lastname")
    new_birthyear = st.number_input("Geburtsjahr", min_value=1900, max_value=2100, value=person["date_of_birth"], step=1, key="edit_birth")
    new_picture = st.text_input("Bildpfad", value=person["picture_path"], key="edit_picture")

    if st.button("💾 Änderungen speichern"):
        updated_person = {
            "id": person["id"],
            "firstname": new_firstname,
            "lastname": new_lastname,
            "date_of_birth": new_birthyear,
            "picture_path": new_picture,
            "ekg_tests": person.get("ekg_tests", [])
        }

        update_person(st.session_state["username"], updated_person)
        st.success("✅ Änderungen gespeichert. Seite neu laden, um Änderungen zu sehen.")
        st.stop()

with tabs[2]:
    st.subheader("📈 Herzfrequenz-Zonenanalyse")
    max_hr = st.number_input("Maximale Herzfrequenz (bpm)", min_value=40, max_value=240, value=200, key="hr_input")
    fig, data = analyze_hr_data(max_hr)
    st.plotly_chart(fig)
    st.table(data)

with tabs[3]:
    st.subheader("🫀 EKG & Herzfrequenzverlauf")

    # Samplingrate-Eingabe
    sampling_rate = st.number_input("Samplingrate (Hz)", min_value=50, max_value=2000, value=500, step=10)

    # Threshold für Peak-Erkennung
    threshold = st.slider("Peak-Schwellenwert (Amplitude)", min_value=100, max_value=1000, value=360, step=10)

    ekg_tests = person.get("ekg_tests", [])
    if not ekg_tests:
        st.warning("⚠️ Keine EKG-Daten vorhanden.")
        st.stop()

    # EKG-Test auswählen
    test_labels = [f"{i+1}. {test['date']}" for i, test in enumerate(ekg_tests)]
    selected_index = st.selectbox(
        "Wähle einen EKG-Test",
        options=list(range(len(ekg_tests))),
        format_func=lambda i: test_labels[i]
    )
    selected_test = ekg_tests[selected_index]

    # EKG laden
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
        st.warning("⚠️ Das EKG-Signal ist leer oder zu kurz.")
        st.stop()

    duration_sec = len(signal) / sampling_rate
    st.caption(f"📏 Gesamtdauer des EKG-Signals: {round(duration_sec/60, 2)} Minuten")

    # Bereichssteuerung
    custom_range = st.number_input(
        "🕒 Maximale Anzeigedauer (Sekunden)",
        min_value=1.0,
        max_value=duration_sec,
        value=min(10.0, duration_sec),
        step=1.0
    )
    start_sec, end_sec = st.slider(
        "Zeitraum im Signal wählen",
        min_value=0.0,
        max_value=round(duration_sec - custom_range, 2),
        value=(0.0, round(min(custom_range, duration_sec), 2)),
        step=0.1
    )

    start_idx = int(start_sec * sampling_rate)
    end_idx = int(end_sec * sampling_rate)
    visible_signal = signal[start_idx:end_idx]

    # Plot erstellen
    import plotly.graph_objects as go
    fig = go.Figure()

    x_vals = [i / sampling_rate for i in range(start_idx, end_idx)]
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=visible_signal,
        mode="lines",
        name="EKG"
    ))

    if ekg.peaks:
        peak_times = [i / sampling_rate for i in ekg.peaks if start_idx <= i < end_idx]
        peak_values = [signal[i] for i in ekg.peaks if start_idx <= i < end_idx]
        fig.add_trace(go.Scatter(
            x=peak_times,
            y=peak_values,
            mode="markers",
            marker=dict(color="red", size=6),
            name="Peaks"
        ))

    fig.update_layout(
        title="EKG-Zeitreihe mit Peaks",
        xaxis_title="Zeit (s)",
        yaxis_title="Amplitude (mV)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # HF-Werte als Tabelle
    if ekg.hr:
        df_hr = pd.DataFrame({
            "Peak-Nr": list(range(1, len(ekg.hr)+1)),
            "Herzfrequenz (bpm)": ekg.hr
        })
        avg = round(sum(ekg.hr)/len(ekg.hr), 2)
        st.write(f"📊 Durchschnittliche HF: **{avg} bpm**")
        st.dataframe(df_hr, use_container_width=True)


    # Gleitender Durchschnitt (Fenstergröße 5)
    window_size = st.slider("Fenstergröße für Gleitenden Durchschnitt", min_value=1, max_value=30, value=5, step=1)

    if ekg.hr:
        hr_array = np.array(ekg.hr)
        smoothed_hr = np.convolve(hr_array, np.ones(window_size)/window_size, mode='valid')

        fig_avg = go.Figure()
        fig_avg.add_trace(go.Scatter(
            y=smoothed_hr,
            mode="lines+markers",
            name="Geglättete HF"
        ))
        fig_avg.update_layout(
            title="Geglättete Herzfrequenz über RR-Intervalle",
            xaxis_title="RR-Intervall",
            yaxis_title="Herzfrequenz (bpm)",
            height=400
        )
        st.plotly_chart(fig_avg, use_container_width=True)





