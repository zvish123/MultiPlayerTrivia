from firefox_db import Database
from idgenerator import PlayerIdGenerator


class Player:
    def __init__(self, name, password="123", idn=None):
        if idn is None:
            gen = PlayerIdGenerator()
            self.id = gen.get_next_id()
        else:
            self.id = idn
        self.name = name
        self.password = password

    def __eq__(self, other):
        return self.name == other.name and self.password == other.password and self.id == other.id
    @staticmethod
    def retreive_player(name):
        db = Database()
        db_data = db.get_table_data("users")
        for key, value in db_data.items():
            try:
                if value['name'] == name:
                    return key, value['name'], value['password']
            except TypeError:
                pass
        return None

    def save_player(self):
        db = Database()
        db.insert("users", str(self.id), {"name": self.name, "password": self.password})
        print("New player in users table")

    def __str__(self):
        s = f"id: {self.id}, name: {self.name}, password: {self.password}"
        return s


if __name__ == "__main__":
    a = Player("zvi", "123")
    print(a)
    b = Player.retreive_player("gal")
    print(b)
    b = Player.retreive_player("zvika")
    print(b)
    c = Player("ben", "101", 30)
    c.save_player()
