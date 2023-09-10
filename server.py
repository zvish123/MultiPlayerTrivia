import socket
from _thread import start_new_thread
import constants
from threading import Lock
from idgenerator import GameIdGenerator
from trivia_questions import TriviaOpenDb, TriviaOpenDbFirebase
from constants import DELIMITER
from protocol import Protocol
from firefox_db import Database
from player import Player
from datetime import datetime


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_id_generator = GameIdGenerator()
        try:
            self.server_socket.bind((constants.SERVER_IP, constants.PORT))
            print(f"server start at {self.server_socket.getsockname()}")
        except socket.error as e:
            print(e)

        self.server_socket.listen(2)
        print("Waiting for a connection, Server Started")

        self.games = {}
        self.players = []
        self.lock = Lock()

    def add_player(self, my_player):
        found = False
        for item in self.players:
            if my_player == item:
                print("player already exists")
                found = True
        if not found:
            self.players.append(my_player)
            print(f"player {my_player.name} appended")
        return True

    def remove_player(self, name):
        for item in self.players:
            if name == item.name:
                self.players.remove(item)
                print(f"player: {name}, removed")

    @staticmethod
    def send_to(conn, cmd, params):
        msg = Protocol.build_message(cmd, params)
        conn.send(msg)
        print(f"{conn.getsockname()} send to {conn.getpeername()}: {msg.decode()}")

    @staticmethod
    def receive_from(conn):
        data = conn.recv(4096).decode()
        print(f"{conn.getsockname()} receive from {conn.getpeername()}: {data}")
        return Protocol.parse_message(data)

    @staticmethod
    def calc_game_score(game_id, my_answers):
        sum_val = 0
        for val in list(my_answers.values()):
            try:
                sum_val += int(val)
            except ValueError:
                pass
        nq = Database.get_by_key("games", f"{game_id}/number_questions")
        res = f"{sum_val}/{nq * 5}"
        return res

    @staticmethod
    def sort_history_list(history_list):
        temp = []
        for item in history_list:
            temp.append((item.split('@')[0], item))
        temp = sorted(temp, key=lambda x: datetime.strptime(x[0], '%d/%m/%Y %H:%M:%S'), reverse=True)
        result = []
        for item in temp:
            result.append(item[1])
        return result

    def signin(self, conn, data):
        params = data.split(DELIMITER)
        name = params[1]
        password = params[2]
        key, value = Database.search("users", "name", name)
        if key is None:
            player = Player(name, password)
            Database.insert("users", player.id, {'name': name, 'password': password})
            print(f"{name} signed in")
            Server.send_to(conn, "signin_response", [str(True), player.id])
            return player
        else:
            print("user or password is incorrect")
            Server.send_to(conn, "signin_response", [str(False), str(None)])
            return None

    def login(self, conn, data):
        params = data.split(DELIMITER)
        name = params[1]
        password = params[2]
        key, value = Database.search("users", "name", name)
        found = False
        player = None
        if key is not None and value['password'] == password:
            player = Player(name, password, key)
            self.add_player(player)
            print(f"{name} logged in")
            found = True
        else:
            print("user or password is incorrect")
        Server.send_to(conn, "login_response", [str(found), str(key)])
        return player

    def logout(self, conn, data):
        params = data.split(DELIMITER)
        name = params[1]
        self.remove_player(name)
        player = None
        Server.send_to(conn, "logout_response", ["ok"])
        return player

    def start_game(self, conn, data):
        params = data.split(DELIMITER)
        player_name = params[1]
        category = params[2]
        difficulty = params[3]
        number_of_questions = int(params[4])
        game_id = self.game_id_generator.get_next_id()
        try:
            trivia = TriviaOpenDb(category, difficulty, number_of_questions)
            self.games[game_id] = {"player": player_name, "questions": trivia.questions}
            Database.insert("games", str(game_id),
                            {"category": category,
                             "difficulty": difficulty,
                             "number_questions": number_of_questions,
                             "questions": trivia.questions})
            # print(trivia.questions)
            Server.send_to(conn, "start_response", [str(game_id)])
            print("send:", game_id)
            return trivia
        except NameError:
            Server.send_to(conn, "start_response", [str(-1)])
            print("Fail to get answer from opendb")
            return None

    def next_question(self, conn, trivia):
        question_id, question, answers = trivia.get_next_question()
        Server.send_to(conn, "next_question_response", [question_id, question, answers])

    def check_answer(self, conn, data, trivia, player):
        params = data.split(DELIMITER)
        game_id = int(params[1])
        question_id = params[2]
        question = params[3]
        p_answer = int(params[4])
        correct_ans, correct_ans_txt, max_number_of_questions = trivia.get_correct_answer(question)
        is_correct = (correct_ans == p_answer)
        val = 0
        if is_correct:
            val = 5
        Database.insert(f"games", f"{game_id}/players/{player.name}/{question_id}", str(val))
        # if question_id == max_number_of_questions:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        Database.insert(f"games", f"{game_id}/players/{player.name}/{'update_date'}", dt_string)
        Server.send_to(conn, "check_answer_response", [str(is_correct), correct_ans_txt])
        print("send:", f"{is_correct}{DELIMITER}{correct_ans_txt}")

    def game_score(self, conn, data):
        params = data.split(DELIMITER)
        game_id = int(params[1])
        player_name = params[2]
        my_answers = Database.get_by_key("games", f"{game_id}/players/{player_name}")
        Server.send_to(conn, "game_score_response", [Server.calc_game_score(game_id, my_answers)])

    def active_games(self, conn, player):
        my_games = Database.get_table_data("games")
        # print(my_games)
        active_games = []
        for key, value in my_games.items():
            try:
                number_of_questions = len(value['players'][player.name].values()) - 1
                actual_questions_asked = int(value['number_questions'])
                if number_of_questions != actual_questions_asked:
                    response = f"{key}*{value['category']}*{value['difficulty']}*{value['number_questions']}"
                    active_games.append(response)
            except KeyError:
                pass
        print(active_games)
        Server.send_to(conn, "active_games_response", [active_games])

    def games_history(self, conn, data):
        params = data.split(DELIMITER)
        player_name = params[1]

        games = Database.get_table_data("games")
        games_ids = list(games.keys())
        history_games_list = []
        for key in games_ids:
            try:
                nq = int(games[key]['number_questions'])
                answers = games[key]['players'][player_name]
                actual = len(answers.values()) - 1
                update_date = games[key]['players'][player_name]['update_date']
                score = Server.calc_game_score(key, answers)
                if nq == actual:
                    history_games_list.append(
                        f"{update_date}@{key}@{games[key]['category']}@{games[key]['difficulty']}@{games[key]['number_questions']}@{score}")
            except KeyError:
                pass
        Server.send_to(conn, "games_history_response", [Server.sort_history_list(history_games_list)])

    def threaded_client(self, conn):
        reply = "ok"
        Server.send_to(conn, "connect_response", [reply])
        to_continue = True
        trivia = None
        player = None
        while to_continue:
            data = conn.recv(4096).decode()
            if data == "":
                break
            print("receive:", data)
            if "signin" in data:
                player = self.signin(conn, data)
            elif "login" in data:
                player = self.login(conn, data)
            elif "logout" in data:
                player = self.logout(conn, data)
            elif "start" in data:
                trivia = self.start_game(conn, data)
            elif "next_question" in data:
                self.next_question(conn, trivia)
            elif "check_answer" in data:
                self.check_answer(conn, data, trivia, player)
            elif "game_score" in data:
                self.game_score(conn, data)
            elif "active_games" in data:
                self.active_games(conn, player)
            elif "continue_game" in data:
                params = data.split(DELIMITER)
                game_id = params[1]
                player_name = params[2]
                trivia = TriviaOpenDbFirebase(game_id, player_name)
                self.games[game_id] = {"player": player_name, "questions": trivia.questions}
                Server.send_to(conn, "continue_game_response", [str(game_id)])
            elif "games_history" in data:
                self.games_history(conn, data)

    def run(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f"Client Connected: {addr}")
            start_new_thread(self.threaded_client, (conn,))


if __name__ == '__main__':
    s = Server()
    s.run()
