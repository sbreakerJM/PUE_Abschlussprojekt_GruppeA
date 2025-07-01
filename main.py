import streamlit as st
import json
import os
from PIL import Image
import pandas as pd

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
st.title("📊 EKG-Analyseplattform")

user = st.session_state["user"]
person = user["person"]

tabs = st.tabs([
    "👤 Benutzerdaten ansehen",
    "✏️ Benutzerdaten bearbeiten",
    "📈 Herzrate über Zeit",
    "🫀 EKG & HF-Verlauf"
])

with tabs[0]:
    st.subheader("👤 Persönliche Daten")
    st.image(Image.open(person["picture_path"]), width=200)
    st.write("🆔 ID:", person["id"])
    st.write("📅 Alter:", 2025 - person["date_of_birth"], "Jahre")
    st.write("❤️ Max. Herzfrequenz:", round(220 - (2025 - person["date_of_birth"])), "bpm")

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
    ekg_tests = person.get("ekg_tests", [])
    if ekg_tests:
        ekg_info = ekg_tests[0]
        ekg = Ekg_tests(id=person["id"], date=ekg_info["date"], result_link=ekg_info["result_link"])
        ekg.find_peaks()
        ekg.estimate_hr()
        fig1 = ekg.plot_time_series()
        st.plotly_chart(fig1)

        hr_df = pd.DataFrame({
            "Peak-Nr": list(range(1, len(ekg.hr) + 1)),
            "Herzfrequenz (bpm)": ekg.hr
        })
        avg_hr = sum(ekg.hr) / len(ekg.hr)
        st.write(f"Durchschnittliche Herzfrequenz: **{round(avg_hr, 2)} bpm**")
        st.dataframe(hr_df)
    else:
        st.warning("⚠️ Keine EKG-Daten vorhanden.")
