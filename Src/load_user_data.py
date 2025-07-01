#Open JSON File and load data
import json
import os
from PIL import Image
from datetime import datetime

FILE_PATH = "data/person_db.json"
# Definition der Personenklasse

class Person:
    def __init__(self,id : int, date_of_birth : str, firstname: str, lastname : str, picture_path : str, ekg_tests):
        self.id = id
        self.date_of_birth = date_of_birth
        self.firstname = firstname
        self.lastname = lastname
        self.picture_path = picture_path
        self.ekg_tests = ekg_tests

    
    def get_fullname(self):
        return self.lastname +", " + self.firstname
    
    def calc_age(self):
        return datetime.now().year - self.date_of_birth
    
    def calc_max_heart_rate(self):
        age = self.calc_age()
        return 220 - age
    
     

def load_user_objects(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
        person_list = []

    for person_person_dict in data:
        #print(person_person_dict)
        
        current_person = Person(person_person_dict['id'],
                                person_person_dict['date_of_birth'],
                                person_person_dict['firstname'],
                                person_person_dict['lastname'],
                                person_person_dict['picture_path'],
                                person_person_dict['ekg_tests'])
        person_list.append(current_person)    
    return person_list

def get_person_object_from_list_by_name(current_user_name, users):
    """
    Get a Person object from the list by their full name.
    """
    firstname = current_user_name.split(", ")[1]
    lastname = current_user_name.split(", ")[0]

    for person in users:
        if person.firstname == firstname and person.lastname == lastname:
            return person
        else:
            None

if __name__ == "__main__":

    person_list = load_user_objects(FILE_PATH)
    print(person_list)
    print(person_list[0].calc_age())
    print(person_list[0].calc_max_heart_rate())
    print(person_list[1].load_by_id(id))

