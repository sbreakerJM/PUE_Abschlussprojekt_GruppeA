import os
import shutil
from tinydb import TinyDB, Query

DB_PATH = "data/users_db.json"
TEMPLATE_PATH = "data/users_db_template.json"

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Falls DB noch nicht existiert Vorlage kopieren (nur für Streamlit Deployment)
    if not os.path.exists(DB_PATH):
        shutil.copyfile(TEMPLATE_PATH, DB_PATH)

    return TinyDB(DB_PATH)



def create_user(username, password, role, fullname, person_dict):
    db = get_db()
    User = Query()

    # Benutzername darf nicht doppelt sein
    if db.contains(User.username == username):
        return False

    # Benutzer einfügen
    db.insert({
        "username": username,
        "password": password,  # ggf. später gehashed
        "role": role,
        "fullname": fullname,
        "person": person_dict
    })
    return True

def get_user(username):
    db = get_db()
    User = Query()
    result = db.get(User.username == username)
    return result

def check_login(username, password):
    user = get_user(username)
    if user and user["password"] == password:
        return user
    return None

def update_user(username, updated_data: dict):
    db = get_db()
    User = Query()
    return db.update(updated_data, User.username == username)

def update_person(username, new_person_data: dict):
    db = get_db()
    User = Query()
    return db.update({"person": new_person_data}, User.username == username)

def delete_user(username):
    db = get_db()
    User = Query()
    return db.remove(User.username == username)

def list_all_users():
    db = get_db()
    return db.all()
