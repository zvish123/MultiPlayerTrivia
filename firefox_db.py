import requests


DATABASE_URL = "https://trivia-7c566-default-rtdb.firebaseio.com/"
AUTH_KEY = "lrQNgF5VTZTiOCgrcSDK0cWwwggyyMzyU3CZWzeP"


class Database:
    @staticmethod
    def insert(table, key_id, json_data):
        data = {key_id: json_data}
        # You must add .json to the end of the URL
        requests.patch(url=DATABASE_URL + table + "/.json", json=data)

    @staticmethod
    def get_by_key(table, key):
        search_key = DATABASE_URL + table + "/" + key + "/.json" + '?auth=' + AUTH_KEY
        request = requests.get(search_key)
        return request.json()

    @staticmethod
    def get_table_data(table):
        search_key = DATABASE_URL + table + "/.json" + '?auth=' + AUTH_KEY
        request = requests.get(search_key)
        return request.json()

    @staticmethod
    def get_all():
        search_key = DATABASE_URL + "/.json" + '?auth=' + AUTH_KEY
        request = requests.get(search_key)
        return request.json()

    @staticmethod
    def search(table, field, value):
        # Initialize a counter
        counter = 0
        # load the json data

        app_list = Database.get_table_data(table)
        # print(app_list)
        # iterate json to find the list of absent applicant
        for key in app_list:
            if app_list[key][field] == value:
                counter += 1
                # print(key)
                return key, app_list[key]

        # Print the message if no applicant is absent
        if counter == 0:
            print(f" {value} not found for field {field}")
            return None, None

    @staticmethod
    def update(table, key_id, json_data):
        Database.insert(table, key_id, json_data)

    @staticmethod
    def delete(table, key_id):
        requests.delete(url=DATABASE_URL + table + "/" + key_id + "/.json")


if __name__ == "__main__":
    # user = {"name": "ram", "password": "999"}
    # db.insert("users", "ram", "999")
    # print(db.get_by_key("users", "ram"))
    # game = {
    #     "10": {
    #       "active": True,
    #       "questions": {
    #         "q1": {
    #           "answers": [
    #             "Table Tennis",
    #             "Badminton",
    #             "Cricket",
    #             "Rugby"
    #           ],
    #           "correct_answer": 2,
    #           "player_answer": -1,
    #           "question": "In what sport is a 'shuttlecock' used?"
    #         },
    #         "q2": {
    #           "answers": [
    #             "Saudi Arabia",
    #             "United States",
    #             "Germany",
    #             "Russia"
    #           ],
    #           "correct_answer": 4,
    #           "player_answer": -1,
    #           "question": "Which country has hosted the 2018 FIFA World Cup?"
    #         }
    #       }
    #     }
    #   }
    # db.insert("games", "ram", game)

    # print(db.get_table_data("games"))
    # print(db.get_all())
    # print(db.search("users", "name", "gal"))
    # print(Database.search("users", "name", "gal"))
    # print(Database.get_by_key("games", "97/questions"))
    # print(Database.get_by_key("games", "97/players"))
    # Database.insert("games", "97/players/gal/2",5 )
    # my_l = Database.get_by_key("games","97/players/gal")
    # sum = 0
    # for val in my_l[1:]:
    #     sum += val
    # nq = Database.get_by_key("games", "97/number_questions")
    # res = f"{sum}/{nq*5}"
    # print(res)

    # my_l = Database.get_table_data("games")
    # print(my_l)
    # for key,value in my_l.items():
    #     # print(value)
    #     try:
    #         nq = len(value['players']['gal'])-1
    #         tgq = int(value['number_questions'])
    #         if nq != tgq:
    #             st = f"{key}|{value['category']}|{value['difficulty']}|{value['number_questions']}"
    #             print(st)
    #     except KeyError:
    #         pass
    #print(Database.get_by_key("games", "97"))
    #Database.insert("users", "40", {"name": "betty", "password": "012"})
    # print(Database.get_by_key("users", "40"))
    print(Database.get_table_data("users"))

    print(Database.search("users", "password", "777"))
    print(Database.get_table_data("games/97"))
