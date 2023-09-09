# https://www.freecodecamp.org/news/how-to-get-started-with-firebase-using-python/
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json


class DB:
    def __init__(self, database_url):
        cred = credentials.Certificate("firebase/service_account_key.json")
        defualt_app = firebase_admin.initialize_app(cred, {'databaseURL': database_url})

    def get_class_data(self, class_name):
        ref = db.reference(f"/{class_name}/")
        return ref.get()

    # overwrite all existing data
    def load_and_overwite_to_class(self, json_file_name, class_name):
        ref = db.reference(f"/{class_name}/")
        with open(json_file_name, "r") as f:
            file_contents = json.load(f)
        ref.set(file_contents)

    def add_to_class_from_file(self, json_file_name, class_name):
        ref = db.reference(f"/{class_name}/")
        with open(json_file_name, "r") as f:
            file_contents = json.load(f)
        for key, value in file_contents.items():
            ref.child(key).set(value)

    def insert_to_class(self, class_name, key, value):
        ref = db.reference(f"/{class_name}/")
        ref.child(key).set(value)

    def update_table_field(self, table, cond_field, cond_value, update_field, update_value):
        ref = db.reference(f"/{table}/")
        my_dict = ref.get()
        for key, value in my_dict.items():
            if value[cond_field] == cond_value:
                value[update_field] = update_value
                ref.child(key).update({update_field: update_value})

    def get_table_field_data(self, table, key, value):
        ref = db.reference(f"/{table}/")
        r = ref.order_by_child(key).equal_to(value).get()
        return list(r.keys()), list(r.values())

    def delete_from_table_by_condition(self, table, cond_field, cond_value):
        ref = db.reference(f"/{table}/")
        my_dict = ref.get()
        for key, value in my_dict.items():
            if value[cond_field] == cond_value:
                ref.child(key).set({})


if __name__ == "__main__":
    d = DB("https://trivia-7c566-default-rtdb.firebaseio.com/")
    fn = "players_info.json"
    d.load_and_overwite_to_class(fn, "users")
    data = d.get_class_data("users")
    print(data)
    afn = "add_players.json"
    d.add_to_class_from_file(afn, "users")
    data = d.get_class_data("users")
    print(data)
    d.update_table_field("users", "name", "nir", "password", "724")

    print(d.get_table_field_data("users", "name", "nir"))

    d.delete_from_table_by_condition("users", "name", "nir")

    print(d.get_table_field_data("users", "name", "nir"))

    print(d.get_table_field_data("users", "name", "rrr"))

    d.insert_to_class("users", "2", {'name': 'lea', 'password': '777'})
    print(d.get_table_field_data("users", "name", "lea"))
