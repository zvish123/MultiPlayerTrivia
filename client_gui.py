import logging

from gui import main_gui
from client_communication import ClientCommunication
from trivia_questions import trivia_difficulty_dict, trivia_categories_dict
from player import Player
import time
from gui.main_gui import *
from functions import *
from cipher import Cipher

menu_options = {
    "Login": "1",
    "Sign in": "2",
    "Start new game": "3",
    "Continue game": "4",
    "Games history": "5",
    "Multi player game options": "6",
    "Logout": "8",
    "Exit": "9"
}

multi_players_options = {
    "Open game": "1",
    "Join game": "2",
    "Start game": "3",
    "Leave game": "4",
    "Exit": "9"
}


class Client:

    def __init__(self):
        self.communication = ClientCommunication()
        self.player = None
        self.mp_game_id = None
        self.log = None
        if constants.DH_ENCRYPT:
            client_ip_port = self.communication.client.getsockname()
            dh, pk = Cipher.get_dh_public_key()
            cmd, params = self.communication.send_response("exchange_key", [client_ip_port, pk])
            self.communication.set_shared_key(Cipher.get_dh_shared_key(dh, eval(params[0])))

    def redraw(self, game, p):
        pass

    def handle_menu(self, title, options):
        if self.player is None:
            print(title)
        else:
            print(f"{title} ({self.player.name})")
        for key, value in options.items():
            print(f"{value}. {key}")

        can_continue = False
        ans = ''
        while not can_continue:
            ans = input("Enter you selection: ")
            if ans in list(options.values()):
                can_continue = True
            else:
                print("illegal menu option")
        return ans

    @staticmethod
    def draw_signin_menu():
        # print("Sign in:")
        user_name = input("Enter user name: ")
        password = input("Enter user password: ")
        return user_name, password

    @staticmethod
    def draw_login_menu():
        user_name = input("Enter user name: ")
        password = input("Enter user password: ")
        return user_name, password

    @staticmethod
    def get_field_value_with_checks(explain_text, list_of_values):
        can_continue = False
        val = ""
        while not can_continue:
            val = input(f"{explain_text}\n{list_of_values}: ")
            if val in list_of_values:
                can_continue = True
            else:
                my_print("illegal value")
        return val

    def get_next_question(self, game_id):
        cmd, params = self.communication.send_response("next_question", [game_id])

        if params[0] == "None":
            question_id = None
        else:
            question_id = params[0]
        question = params[1]
        answers = eval(params[2])
        return question_id, question, answers

    def check_question_answer(self, game_id, question_id, question, p_reply):
        cmd, params = self.communication.send_response("check_answer",
                                                       [game_id, question_id, question, p_reply])
        is_correct = eval(params[0])
        correct_ans_txt = params[1]
        if is_correct:
            my_print("correct")
        else:
            my_print(f"incorrect, correct answer: {correct_ans_txt}")

        return is_correct, correct_ans_txt

    def game_score(self, game_id):
        cmd, params = self.communication.send_response("game_score", [game_id, self.player.name])
        game_score = params[0]
        my_print(f"game score: {game_score}")
        return game_score

    def wait_for_next_mp_question(self):
        leave_game = None
        cmd, params = self.communication.receive()
        # print(cmd, params)
        # add handle leave command
        if cmd == 'leave_mp_game_response':
            return True, None, None
        else:

            if params[0] == "None":
                question_id = None
            else:
                question_id = params[0]
            question = params[1]
            answers = eval(params[2])
            return leave_game, question_id, question, answers

    def handle_next_mp_question(self):
        # is_notified = None
        leave_game = None
        # print("handle_next_mp_question - waiting for question")
        cmd, params = self.communication.receive()
        # print(cmd, params)
        # add handle leave command
        if cmd == 'leave_mp_game_response':
            return None, "", "", []
        else:

            if params[0] == "None":
                question_id = None
            else:
                question_id = params[0]
            question = params[1]
            answers = eval(params[2])
        # print(leave_game, question_id, question, answers)
        return leave_game, question_id, question, answers

    def leave_mp_game(self):
        self.communication.send_response("leave_mp_game", [self.mp_game_id, self.player.name])
        return True

    def notify_mp_answer(self, question_id, question, p_reply):
        cmd, params = self.communication.send_response("notify_mp_answer",
                                                       [self.mp_game_id, self.player.name,
                                                        question_id, question, p_reply])
        is_notified = eval(params[0])
        # print(f"game {self.mp_game_id} notified for question {question_id}")
        return is_notified

    def can_moveto_next_mp_question(self):
        # print("can_moveto_next_mp_question")
        cmd, data = self.communication.send_response("can_go_next", [self.mp_game_id])
        # print("can_moveto_next_mp_question", cmd, data)
        can_cont = eval(data[0])
        # print(can_cont)
        # if can_continue:
        #     self.communication.send("next_mp_question", [self.mp_game_id])
        #     to_start, leave_game = self.handle_next_mp_question()
        return can_cont

    def ask_for_next_mp_question(self):
        self.communication.send("next_mp_question", [self.mp_game_id])

    def login(self, name, password):
        # print("start login")
        if self.player is None:
            # name, password = Client.draw_login_menu()
            cmd, data = self.communication.send_response("login", [name, password])
            if data[0] == "found":
                my_print(f"login successfully")
                self.player = Player(name, password, int(data[1]))
                return 1
            elif data[0] == "not found":
                my_print("incorrect user name or password")
                return -1
            elif data[0] == "logged in":
                my_print("can't login twice")
                return -2
        else:
            my_print("you already logged in")
            return 0

    def logout(self):
        if self.player is not None:
            cmd, data = self.communication.send_response("logout", [self.player.name])
            if data[0] == 'ok':
                my_print("logout successfully")
                self.player = None
        else:
            my_print("you are not logged in")

    def signin(self, name, password):
        if self.player is None:
            # name, password = Client.draw_signin_menu()
            cmd, data = self.communication.send_response("signin", [name, password])
            if eval(data[0]):
                my_print(f"signin successfully")
                return 1
            else:
                my_print("user already exists")
                return -1
        else:
            my_print("you already logged in")
            return 0

    def start_new_game(self, category, difficulty, number_of_questions):
        if self.player is not None:
            # print("Start new Trivia Game")

            cmd, data = self.communication.send_response("start_game",
                                                         [self.player.name, category, difficulty,
                                                          number_of_questions])
            game_id = data[0]
            return game_id

    def continue_game(self):
        if self.player is not None:
            # get my active games and shoe for selection
            cmd, params = self.communication.send_response("active_games", [self.player.name])
            active_games = eval(params[0])
            active_games_list = []
            if len(active_games) > 0:
                # print("Games to continue...")
                # print("Game Id  Category           Difficulty Number of questions")
                for item in active_games:
                    prms = item.split("*")
                    g_id = prms[0]
                    cat = prms[1]
                    diclt = prms[2]
                    noq = prms[3]
                    diff_val = constants.DIFFICULT_DICT[diclt]
                    # print(f"{str(g_id).ljust(9, ' ')}{cat.ljust(19, ' ')}{diff_val.ljust(11, ' ')}{str(noq)}")
                    active_games_list.append(g_id)
                found = False
                selected_game_id = ""
                while not found:
                    selected_game_id = input("Select game id to continue: ")
                    if selected_game_id in active_games_list:
                        found = True
                    else:
                        my_print("illegal game Id")
                my_print(f"Continue Trivia Game {selected_game_id}")
                cmd, data = self.communication.send_response("continue_game",
                                                             [selected_game_id, self.player.name])
                game_id = data[0]
                cmd, params = self.communication.send_response("next_question", [game_id])

                if params[0] == "None":
                    question_id = None
                else:
                    question_id = params[0]
                question = params[1]
                answers = eval(params[2])
                # i = 1
                while question_id is not None:
                    print(f"{question_id}. {question}")
                    j = 1
                    for answer in answers:
                        print(f"   {j}. {answer}")
                        j = j + 1
                    # p_reply = int(input("Enter you answer: "))
                    p_reply = Client.get_field_value_with_checks("Enter you answer: ", ["1", "2", "3", "4"])
                    cmd, params = self.communication.send_response("check_answer",
                                                                   [game_id, question_id, question, p_reply])
                    is_correct = eval(params[0])
                    correct_ans_txt = params[1]
                    if is_correct:
                        print("correct")
                    else:
                        print(f"incorrect, correct answer: {correct_ans_txt}")
                    # i += 1
                    cmd, params = self.communication.send_response("next_question", [game_id])
                    if params[0] == "None":
                        question_id = None
                    else:
                        question_id = params[0]
                    question = params[1]
                    answers = eval(params[2])
                cmd, params = self.communication.send_response("game_score", [game_id, self.player.name])
                game_score = params[0]
                print(f"game score: {game_score}")
                time.sleep(2)
            else:
                print("no games to continue...")
        else:
            print("you need to login before continue game")

    def games_history(self):
        games_history_dict = {}
        if self.player is not None:
            cmd, data = self.communication.send_response("games_history", [self.player.name])
            games_history = eval(data[0])
            if len(games_history) > 0:
                for item in games_history:
                    prms = item.split(constants.LIST_DELIMITER)
                    udate = prms[0]
                    g_id = prms[1]
                    cat = prms[2]
                    diclt = prms[3]
                    noq = prms[4]
                    score = prms[5]
                    diff_val = constants.DIFFICULT_DICT[diclt]
                    games_history_dict[g_id] = [udate, cat, diff_val, noq, score]
            else:
                my_print(f"no history for {self.player.name}")
        else:
            my_print("login to watch games history")
        return games_history_dict

    def get_active_player_games(self):
        cmd, params = self.communication.send_response("active_games", [self.player.name])
        active_games = eval(params[0])
        active_games_dict = {}
        if len(active_games) > 0:
            for item in active_games:
                prms = item.split(constants.LIST_DELIMITER)
                g_id = prms[0]
                cat = prms[1]
                diclt = prms[2]
                noq = prms[3]
                diff_val = constants.DIFFICULT_DICT[diclt]
                # print(f"{str(g_id).ljust(9, ' ')}{cat.ljust(19, ' ')}{diff_val.ljust(11, ' ')}{str(noq)}")
                active_games_dict[g_id] = [cat, diff_val, noq]
        return active_games_dict

    def ask_to_continue_game(self, selected_game_id):
        cmd, data = self.communication.send_response("continue_game",
                                                     [selected_game_id, self.player.name])
        game_id = data[0]
        return game_id

    def open_game(self, category, difficulty, number_of_questions):
        if self.mp_game_id is None:
            cmd, data = self.communication.send_response("open_mp_game",
                                                         [self.player.name, category, difficulty,
                                                          number_of_questions])
            game_id = data[0]
            my_print(f"game_id={game_id} open for multiplayer game")
            self.mp_game_id = game_id
            return game_id
        else:
            my_print("you have already open a multy player game")
            return None

    def get_games_for_join(self):
        mp_games_dict = {}
        if self.mp_game_id is None:
            # print("select Multi players Trivia Game")
            cmd, data = self.communication.send_response("mp_games", [self.player.name])
            mp_games = eval(data[0])
            if len(mp_games) > 0:
                for item in mp_games:
                    prms = item.split(constants.LIST_DELIMITER)
                    g_id = prms[0]
                    cat = prms[1]
                    diclt = prms[2]
                    noq = prms[3]
                    diff_val = constants.DIFFICULT_DICT[diclt]
                    mp_games_dict[g_id] = [cat, diff_val, noq]
        return mp_games_dict

    def join_mp_game(self, selected_game_id):
        cmd, data = self.communication.send_response("join_mp_game", [selected_game_id, self.player.name])
        game_id = data[0]
        self.mp_game_id = game_id
        return game_id

    def handle_multi_player_game_end(self, receive_only=False):
        # print("multi player game finished")
        if receive_only:
            cmd, params = self.communication.receive()
        else:
            cmd, params = self.communication.send_response("mp_game_result", [self.mp_game_id])
        # header = params[0]
        players_list = eval(params[1])
        score = ""
        for p in players_list:
            items = p.split(constants.LIST_DELIMITER)
            my_print(f"{self.player.name} {items[0]}")
            if self.player.name == items[0]:
                score = f"{items[1]}/{items[2]}"
                # print(score)

        # input("press any key to continue...")
        self.mp_game_id = None
        return cmd, score

    def start_mp_game(self):
        to_start = False
        if self.player is not None and self.mp_game_id is not None:
            cmd, data = self.communication.send_response("start_mp_game", [self.mp_game_id])
            to_start = eval(data[0])
        return to_start

    def leave_game(self):
        if self.mp_game_id is not None:
            self.communication.send_response("leave_mp_game", [self.mp_game_id, self.player.name])
            self.mp_game_id = None
        else:
            my_print("you are not in multy player game")

    def get_categories(self):
        return list(trivia_categories_dict.keys())

    def get_difficulties(self):
        # return list(trivia_difficulty_dict.keys())
        return list(trivia_difficulty_dict.values())

    def get_difficulty_key(self, value):
        for key, val in trivia_difficulty_dict.items():
            if val == value:
                return key
        return -1

    def get_number_of_questions(self):
        # print(str(constants.NUMBER_OF_QUESTIONS))
        return str(constants.NUMBER_OF_QUESTIONS)

    def handle_exit(self):
        self.logout()
        if self.communication.shared_key is not None:
            client_ip_port = self.communication.client.getsockname()
            cmd, data = self.communication.send_response("remove_shared_key", [client_ip_port])
            # print(data)
            if data[0] == 'ok':
                my_print("shared key removed")
        self.communication.client.close()

    def run_gui(self):
        try:
            my_app = QApplication(sys.argv)
            my_app.aboutToQuit.connect(self.handle_exit)
            my_win = main_gui.Window(self)
            my_win.show()
            sys.exit(my_app.exec_())
        except KeyboardInterrupt:
            my_print("leave game with Ctrl+C", logging.ERROR)
            self.handle_exit()


if __name__ == "__main__":
    c = Client()
    c.run_gui()
