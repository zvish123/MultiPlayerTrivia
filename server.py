import socket
from _thread import start_new_thread
import constants
from threading import Lock
from idgenerator import GameIdGenerator
from trivia_questions import TriviaOpenDb, TriviaOpenDbFirebase
from trivialocaldb import TriviaLocalDb
from constants import DELIMITER
from protocol import Protocol
from firefox_db import Database
from player import Player
from datetime import datetime
from logger import Logger


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_id_generator = GameIdGenerator()
        self.log_lock = Lock()
        self.log = Logger("log/server.log")
        self.clean_clients_logs()

        print("Server is ready")
        try:
            self.server_socket.bind((constants.SERVER_IP, constants.PORT))
            # print(f"server start at {self.server_socket.getsockname()}")
            self.log.write(f"server start at {self.server_socket.getsockname()}")
        except socket.error as e:
            print(e)

        self.server_socket.listen(2)
        # print("Waiting for a connection, Server Started")
        self.log.write("Waiting for a connection, Server Started")

        self.mp_games = {}
        self.players = []
        self.lock = Lock()

    def add_player(self, my_player):
        to_add = True
        for item in self.players:
            if my_player == item:
                print("player already exists")
                to_add = False
        if to_add:
            self.players.append(my_player)
            print(f"player {my_player.name} appended to list")
        return to_add

    def clean_clients_logs(self):
        Logger.clean_client_logs("log/")

    def remove_player(self, name):
        for item in self.players:
            if name == item.name:
                self.players.remove(item)
                print(f"player: {name}, removed")

    def send_to(self, conn, cmd, params):
        msg = Protocol.build_message(cmd, params)
        conn.send(msg)
        self.log.write(f"{conn.getsockname()} send to {conn.getpeername()}: {msg.decode()}")

    def receive_from(self, conn):
        data = conn.recv(4096).decode()
        self.log.write(f"{conn.getsockname()} receive from {conn.getpeername()}: {data}")
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
        res = f"{sum_val}/{nq * constants.POINTS_PER_QUESTION}"
        return res

    @staticmethod
    def sort_history_list(history_list):
        temp = []
        for item in history_list:
            temp.append((item.split(constants.LIST_DELIMITER)[0], item))
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
            self.send_to(conn, "signin_response", [str(True), player.id])
            return player
        else:
            print("user or password is incorrect")
            self.send_to(conn, "signin_response", [str(False), str(None)])
            return None

    def login(self, conn, data):
        params = data.split(DELIMITER)
        name = params[1]
        password = params[2]
        key, value = Database.search("users", "name", name)
        found = "not found"
        player = None
        if key is not None and value['password'] == password:
            player = Player(name, password, key)
            if self.add_player(player):
                print(f"{name} logged in")
                found = "found"
            else:
                print(f"{name} already logged in")
                found = "logged in"
        else:
            print("user or password is incorrect")
        self.send_to(conn, "login_response", [str(found), str(key)])
        return player

    def logout(self, conn, data):
        params = data.split(DELIMITER)
        name = params[1]
        self.remove_player(name)
        self.send_to(conn, "logout_response", ["ok"])
        return None

    def start_game(self, conn, data):
        params = data.split(DELIMITER)
        player_name = params[1]
        category = params[2]
        difficulty = params[3]
        number_of_questions = int(params[4])
        game_id = self.game_id_generator.get_next_id()
        try:
            # trivia = TriviaOpenDb(category, difficulty, number_of_questions)
            trivia = TriviaLocalDb(category, difficulty, number_of_questions)
            # self.games[game_id] = {"player": player_name, "questions": trivia.questions}
            Database.insert("games", str(game_id),
                            {"category": category,
                             "difficulty": difficulty,
                             "number_questions": number_of_questions,
                             "questions": trivia.questions})
            print(f"{player_name} start game {game_id}. Category: {category}, difficulty: {difficulty}")
            self.send_to(conn, "start_game_response", [str(game_id)])
            # print("send:", game_id)
            return trivia
        except NameError:
            self.send_to(conn, "start_game_response", [str(-1)])
            print("Fail to get answer from opendb")
            return None

    def next_question(self, conn, trivia):
        question_id, question, answers = trivia.get_next_question()
        self.send_to(conn, "next_question_response", [question_id, question, answers])

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
        self.send_to(conn, "check_answer_response", [str(is_correct), correct_ans_txt])
        # print("send:", f"{is_correct}{DELIMITER}{correct_ans_txt}")

    def game_score(self, conn, data):
        params = data.split(DELIMITER)
        game_id = int(params[1])
        player_name = params[2]
        my_answers = Database.get_by_key("games", f"{game_id}/players/{player_name}")
        self.send_to(conn, "game_score_response", [Server.calc_game_score(game_id, my_answers)])

    def active_games(self, conn, player):
        my_games = Database.get_table_data("games")
        # print(my_games)
        active_games = []
        for key, value in my_games.items():
            try:
                number_of_questions = len(value['players'][player.name].values()) - 1
                actual_questions_asked = int(value['number_questions'])
                if number_of_questions != actual_questions_asked:
                    response = f"{key}{constants.LIST_DELIMITER}{value['category']}{constants.LIST_DELIMITER}" \
                               f"{value['difficulty']}{constants.LIST_DELIMITER}{value['number_questions']}"
                    active_games.append(response)
            except KeyError:
                pass
        print(active_games)
        self.send_to(conn, "active_games_response", [active_games])

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
                        f"{update_date}{constants.LIST_DELIMITER}{key}{constants.LIST_DELIMITER}"
                        f"{games[key]['category']}{constants.LIST_DELIMITER}{games[key]['difficulty']}"
                        f"{constants.LIST_DELIMITER}{games[key]['number_questions']}{constants.LIST_DELIMITER}{score}")
            except KeyError:
                pass
        self.send_to(conn, "games_history_response", [Server.sort_history_list(history_games_list)])

    def open_multi_players_game(self, conn, data):
        params = data.split(DELIMITER)
        player_name = params[1]
        category = params[2]
        difficulty = params[3]
        number_of_questions = int(params[4])
        game_id = self.game_id_generator.get_next_id()
        try:
            trivia = TriviaOpenDb(category, difficulty, number_of_questions)
            self.lock.acquire()
            players_answers = []
            self.mp_games[str(game_id)] = {
                "players": {player_name: {"player_socket": conn, "player_answers": players_answers, "manager": True}},
                "questions": trivia.questions,
                "category": category,
                "difficulty": difficulty,
                "number_questions": number_of_questions,
                "next_question": 1
                }
            self.lock.release()
            # print(self.mp_games)
            print(f"{player_name} open multi player game {game_id}. category: {category}, difficulty: {difficulty}")
            self.send_to(conn, "open_mp_game_response", [str(game_id)])
        except NameError:
            self.send_to(conn, "open_mp_game_response", [str(-1)])
            print("Fail to get answer from opendb")
            # return None

    def handle_multi_players_games(self, conn):
        game_ids = list(self.mp_games.keys())
        games = []
        if len(game_ids) > 0:
            for key, value in self.mp_games.items():
                games.append(f"{key}{constants.LIST_DELIMITER}{value['category']}{constants.LIST_DELIMITER}"
                             f"{value['difficulty']}{constants.LIST_DELIMITER}{value['number_questions']}")
        self.send_to(conn, "mp_games_response", [games])

    def join_mp_game(self, conn, data):
        self.lock.acquire()
        params = data.split(DELIMITER)
        game_id = params[1]
        player_name = params[2]
        self.mp_games[game_id]['players'][player_name] = {"player_socket": conn, "player_answers": [], "manager": False}
        self.lock.release()
        self.send_to(conn, "join_mp_game_response", [game_id])
        print(f"{player_name} joined multi player game {game_id}.")
        # add notification to game manager

    def mp_notify_game_manager(self, conn, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        player_name = params[2]
        print(f"player {player_name} joined game {game_id}")
        self.send_to(conn, "mp_games_notify_game_manager_response", [game_id])

    def next_mp_question(self, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        self.next_mp_question_internal(game_id)

    def next_mp_question_internal(self, game_id):
        next_question_id = int(self.mp_games[game_id]["next_question"])
        # print(next_question_id)
        # print(self.mp_games[game_id]["questions"])
        try:
            next_question = self.mp_games[game_id]["questions"][next_question_id]
            question = next_question['question']
            answers = next_question['answers']
        except KeyError:
            next_question_id = None
            question = None
            answers = None
        for key in list(self.mp_games[game_id]['players'].keys()):
            p_conn = self.mp_games[game_id]['players'][key]["player_socket"]
            self.send_to(p_conn, "next_mp_question_response", [next_question_id, question, answers])
        if next_question_id is not None:
            next_question_id += 1
        self.lock.acquire()
        self.mp_games[game_id]["next_question"] = next_question_id
        self.lock.release()

    def start_mp_game(self, conn, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        can_start_mp_game = len(self.mp_games[game_id]['players']) >= 2
        self.send_to(conn, "start_mp_game_response", [str(can_start_mp_game)])
        if can_start_mp_game:
            self.next_mp_question_internal(game_id)
        print(f"Multi player game {game_id} started")

    def close_mp_game(self, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        players = self.mp_games[game_id]['players']

        for key in list(players.keys()):
            p_conn = players[key]["player_socket"]
            self.send_to(p_conn, "leave_mp_game_response", [game_id])

        self.lock.acquire()
        self.mp_games.pop(game_id)
        self.lock.release()
        print(f"Multi player game {game_id} closed")

    def leave_mp_game(self, conn, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        player_name = params[2]
        try:
            players = self.mp_games[game_id]['players']

            for key in list(players.keys()):
                print(players)
                is_manager = players[key]["manager"]
                if key == player_name and is_manager:
                    for key1 in list(players.keys()):
                        p_conn = players[key1]["player_socket"]
                        self.send_to(p_conn, "leave_mp_game_response", [game_id])
                    self.lock.acquire()
                    self.mp_games.pop(game_id)
                    self.lock.release()
                    print(f"game manger: {key}, left multi player game {game_id}")
                    break
                elif key == player_name:
                    self.send_to(conn, "leave_mp_game_response", [game_id])
                    self.lock.acquire()
                    self.mp_games[game_id]['players'].pop(player_name)
                    self.lock.release()
                    print(f"{key} left multi player game {game_id}")
                    break
        except KeyError:
            pass

    def notify_mp_answer(self, conn, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        player_name = params[2]
        question_id = int(params[3])
        # question = params[4]
        p_answer = int(params[5]) - 1
        print(self.mp_games)
        # print(game_id, type(game_id))
        # print(question_id, type(question_id))

        try:
            self.mp_games[game_id]
        except KeyError:
            self.send_to(conn, "leave_mp_game_response", [game_id])
            return

        try:
            current_question = self.mp_games[game_id]['questions'][question_id]
        except KeyError:
            self.send_to(conn, "notify_mp_answer_response", [str(False)])
            return

        # print(current_question)
        correct_ans = int(current_question['correct_answer']) - 1
        # correct_ans_txt = current_question['answers'][correct_ans]
        print(correct_ans, type(correct_ans))
        print(correct_ans, p_answer)
        is_correct = (correct_ans == p_answer)
        val = 0
        if is_correct:
            val = 5
        self.lock.acquire()
        self.mp_games[game_id]["players"][player_name]["player_answers"].append(val)
        print(self.mp_games[game_id]["players"])
        self.lock.release()
        self.send_to(conn, "notify_mp_answer_response", [str(True)])

    def can_move_to_next_mp_question(self, conn, data):
        print("start can_go_next")
        params = data.split(DELIMITER)
        game_id = params[1]
        players = self.mp_games[game_id]["players"]
        previous_question = int(self.mp_games[game_id]["next_question"]) - 1
        can_move = True
        for key in list(players.keys()):
            if len(players[key]["player_answers"]) != previous_question:
                can_move = False
        self.send_to(conn, "can_go_next_response", [str(can_move)])
        print(f"end can_go_next {can_move}")

    def mp_game_result(self, data):
        params = data.split(DELIMITER)
        game_id = params[1]
        players = self.mp_games[game_id]["players"]
        temp = []
        for key in list(players.keys()):
            score = sum(players[key]["player_answers"])
            max_score = len(players[key]["player_answers"]) * constants.POINTS_PER_QUESTION
            temp.append((key, score, max_score))
        temp = sorted(temp, key=lambda x: x[1], reverse=True)
        header = f"category: {self.mp_games[game_id]['category']} difficulty: {self.mp_games[game_id]['difficulty']} " \
                 f"number of questions: {self.mp_games[game_id]['number_questions']}"
        data_list = []
        for item in temp:
            data_list.append(f'{item[0]}{constants.LIST_DELIMITER}{item[1]}{constants.LIST_DELIMITER}{item[2]}')

        for key in list(players.keys()):
            p_conn = players[key]["player_socket"]
            self.send_to(p_conn, "mp_game_result_response", [header, data_list])
        self.lock.acquire()
        self.mp_games.pop(game_id)
        self.lock.release()

    def threaded_client(self, conn):
        reply = "ok"
        self.send_to(conn, "connect_response", [reply])
        to_continue = True
        trivia = None
        player = None
        while to_continue:
            data = conn.recv(4096).decode()
            if data == "":
                break
            # print("receive:", data)
            self.log.write(f"receive: {data}")
            if "signin" in data:
                player = self.signin(conn, data)
            elif "login" in data:
                player = self.login(conn, data)
            elif "logout" in data:
                self.logout(conn, data)
                player = None
            elif "start_game" in data:
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
                # self.games[game_id] = {"player": player_name, "questions": trivia.questions}
                self.send_to(conn, "continue_game_response", [str(game_id)])
            elif "games_history" in data:
                self.games_history(conn, data)
            elif "open_mp_game" in data:
                self.open_multi_players_game(conn, data)
            elif "mp_games" in data:
                self.handle_multi_players_games(conn)
            elif "join_mp_game" in data:
                self.join_mp_game(conn, data)
            elif "mp_games_notify_game_manager" in data:
                self.mp_notify_game_manager(conn, data)
            elif "start_mp_game" in data:
                self.start_mp_game(conn, data)
            elif "close_mp_game" in data:
                self.close_mp_game(data)
            elif "leave_mp_game" in data:
                self.leave_mp_game(conn, data)
            elif "notify_mp_answer" in data:
                self.notify_mp_answer(conn, data)
            elif "next_mp_question" in data:
                self.next_mp_question(data)
            elif "can_go_next" in data:
                self.can_move_to_next_mp_question(conn, data)
            elif "mp_game_result" in data:
                self.mp_game_result(data)

    def run(self):
        while True:
            conn, addr = self.server_socket.accept()
            # print(f"Client Connected: {addr}")
            self.log.write(f"Client Connected: {addr}")
            start_new_thread(self.threaded_client, (conn,))


if __name__ == '__main__':
    s = Server()
    s.run()
