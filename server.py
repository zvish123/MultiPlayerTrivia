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

    def add_player(self, player):
        found = False
        for item in self.players:
            if player == item:
                print("player already exists")
                found = True
        if not found:
            self.players.append(player)
            print(f"player {player.name} appended")
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

    def threaded_client(self, conn):
        reply = "ok"
        Server.send_to(conn, "connect_response", [reply])
        # wait for player name
        # cmd, data = Server.receive_from(conn)
        to_continue = True
        trivia = None
        player = None
        while to_continue:
            data = conn.recv(4096).decode()
            if data == "":
                break
            print("receive:", data)
            if "signin" in data:
                # print("start signin")
                params = data.split(DELIMITER)
                name = params[1]
                password = params[2]
                key, value = Database.search("users", "name", name)
                if key is None:
                    player = Player(name, password)
                    Database.insert("users", player.id, {'name': name, 'password': password})
                    print(f"{name} signed in")
                    Server.send_to(conn, "signin_response", [str(True), player.id])
                else:
                    print("user or password is incorrect")
                    Server.send_to(conn, "signin_response", [str(False), str(None)])

            elif "login" in data:
                # print("start login")
                params = data.split(DELIMITER)
                name = params[1]
                password = params[2]
                key, value = Database.search("users", "name", name)
                found = False
                if key is not None and value['password'] == password:
                    player = Player(name, password, key)
                    self.add_player(player)
                    print(f"{name} logged in")
                    found = True
                else:
                    print("user or password is incorrect")
                Server.send_to(conn, "login_response", [str(found), str(key)])

            elif "logout" in data:
                # print("start logout")
                params = data.split(DELIMITER)
                name = params[1]
                self.remove_player(name)
                player = None
                Server.send_to(conn, "logout_response", ["ok"])

            elif "start" in data:
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
                except NameError:
                    Server.send_to(conn, "start_response", [str(-1)])
                    print("Fail to get answer from opendb")

            elif "next_question" in data:
                question_id, question, answers = trivia.get_next_question()
                Server.send_to(conn, "next_question_response", [question_id, question, answers])
            elif "check_answer" in data:
                params = data.split(DELIMITER)
                game_id = int(params[1])
                question_id = params[2]
                question = params[3]
                p_answer = int(params[4])
                correct_ans, correct_ans_txt = trivia.get_correct_answer(question)
                is_correct = (correct_ans == p_answer)
                val = 0
                if is_correct:
                    val = 5
                Database.insert(f"games", f"{game_id}/players/{player.name}/{question_id}", str(val))
                Server.send_to(conn, "check_answer_response", [str(is_correct), correct_ans_txt])
                print("send:", f"{is_correct}{DELIMITER}{correct_ans_txt}")
            elif "game_score" in data:
                my_answers = Database.get_by_key("games", f"{game_id}/players/{player.name}")
                sum_val = 0
                for val in my_answers[1:]:
                    sum_val += int(val)
                nq = Database.get_by_key("games", f"{game_id}/number_questions")
                res = f"{sum_val}/{nq * 5}"
                Server.send_to(conn, "game_score_response", [res])
            elif "active_games" in data:
                my_games = Database.get_table_data("games")
                # print(my_games)
                active_games = []
                for key, value in my_games.items():
                    try:
                        number_of_questions = len(value['players'][player.name]) - 1
                        actual_questions_asked = int(value['number_questions'])
                        if number_of_questions != actual_questions_asked:
                            response = f"{key}*{value['category']}*{value['difficulty']}*{value['number_questions']}"
                            active_games.append(response)
                    except KeyError:
                        # response = f"{key}*{value['category']}*{value['difficulty']}*{value['number_questions']}"
                        # active_games.append(response)
                        pass
                print(active_games)
                Server.send_to(conn, "active_games_response", [active_games])
            elif "continue_game" in data:
                params = data.split(DELIMITER)
                game_id = params[1]
                player_name = params[2]
                trivia = TriviaOpenDbFirebase(game_id, player_name)
                # print("next question", trivia.next_question)
                self.games[game_id] = {"player": player_name, "questions": trivia.questions}
                Server.send_to(conn, "continue_game_response", [str(game_id)])

    def run(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f"Client Connected: {addr}")
            start_new_thread(self.threaded_client, (conn,))


if __name__ == '__main__':
    s = Server()
    s.run()
