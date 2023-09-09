from client_communication import ClientCommunication
from trivia_questions import trivia_difficulty_dict, trivia_categories_dict
from player import Player
import time
import constants

menu_options = {"Login": "1",
                "Sign in": "2",
                "Start new game": "3",
                "Continue game": "4",
                "Logout": "8",
                "Exit": "9"}


class Client:

    def __init__(self):
        # self.user_name = input("Enter player name: ")
        # self.user_pass = ''
        self.communication = ClientCommunication()
        self.player = None

    def redraw(self, game, p):
        pass

    def draw_menu(self):
        if self.player is None:
            print("Menu:")
        else:
            print(f"Menu ({self.player.name})")

        for key, value in menu_options.items():
            print(f"{value}. {key}")

    @staticmethod
    def draw_signin_menu():
        print("Sign in:")
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
                print("illegal value")
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

    def login(self):
        if self.player is None:
            name, password = Client.draw_login_menu()
            cmd, data = self.communication.send_response("login", [name, password])
            if eval(data[0]):
                print(f"login successfully")
                self.player = Player(name, password, int(data[1]))
            else:
                print("incorrect user name or password")
        else:
            print("you already logged in")

    def logout(self):
        if self.player is not None:
            cmd, data = self.communication.send_response("logout", [self.player.name])
            if data[0] == 'ok':
                print("logout successfully")
                self.player = None
        else:
            print("you are not logged in")

    def signin(self):
        if self.player is None:
            name, password = Client.draw_signin_menu()
            cmd, data = self.communication.send_response("signin", [name, password])
            if eval(data[0]):
                print(f"signin successfully")
            else:
                print("user already exists")
        else:
            print("you already logged in")

    def start_new_game(self):
        if self.player is not None:
            print("Start new Trivia Game")
            # category = input(f"Choose trivia game category\n{list(trivia_categories_dict.keys())}: ")
            # difficulty = input(f"Choose trivia game difficulty\n{list(trivia_difficulty_dict.keys())}: ")
            category = Client.get_field_value_with_checks("Choose trivia game category",
                                                          list(trivia_categories_dict.keys()))
            difficulty = Client.get_field_value_with_checks("Choose trivia game difficulty",
                                                            list(trivia_difficulty_dict.keys()))
            number_of_questions = 3
            cmd, data = self.communication.send_response("start",
                                                         [self.player.name, category, difficulty,
                                                          number_of_questions])
            game_id = data[0]
            print(f"game_id={game_id}")

            question_id, question, answers = self.get_next_question(game_id)
            # i = 1
            while question_id is not None:
                print(f"{question_id}. {question}")
                j = 1
                for answer in answers:
                    print(f"   {j}. {answer}")
                    j = j + 1
                # p_reply = int(input("Enter you answer: "))
                p_reply = Client.get_field_value_with_checks("Enter you answer: ",
                                                             ["1", "2", "3", "4"])
                cmd, params = self.communication.send_response("check_answer",
                                                               [game_id, question_id, question, p_reply])
                is_correct = eval(params[0])
                correct_ans_txt = params[1]
                if is_correct:
                    print("correct")
                else:
                    print(f"incorrect, correct answer: {correct_ans_txt}")
                # i += 1
                question_id, question, answers = self.get_next_question(game_id)

            cmd, params = self.communication.send_response("game_score", [game_id, self.player.name])
            game_score = params[0]
            print(f"game score: {game_score}")
            time.sleep(2)
        else:
            print("Login to play game")

    def continue_game(self):
        if self.player is not None:
            # get my active games and shoe for selection
            cmd, params = self.communication.send_response("active_games", [self.player.name])
            active_games = eval(params[0])
            active_games_list = []
            if len(active_games) > 0:
                print("Games to continue...")
                print("Game Id  Category           Difficulty Number of questions")
                for item in active_games:
                    prms = item.split("*")
                    g_id = prms[0]
                    cat = prms[1]
                    diclt = prms[2]
                    noq = prms[3]
                    diff_val = constants.DIFFICULT_DICT[diclt]
                    print(f"{str(g_id).ljust(9, ' ')}{cat.ljust(19, ' ')}{diff_val.ljust(11, ' ')}{str(noq)}")
                    active_games_list.append(g_id)
                found = False
                selected_game_id = ""
                while not found:
                    selected_game_id = input("Select game id to continue:")
                    if selected_game_id in active_games_list:
                        found = True
                    else:
                        print("illegal game Id")
                print(f"Continue Trivia Game {selected_game_id}")
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

    def run(self):
        ans = ''
        while True:
            # os.system('cls')
            self.draw_menu()
            can_continue = False
            while not can_continue:

                ans = input("Enter you selection: ")
                if ans in list(menu_options.values()):
                    can_continue = True
                else:
                    print("illegal menu option")
            if ans == menu_options["Login"]:
                self.login()
            elif ans == menu_options["Sign in"]:
                self.signin()
            elif ans == menu_options["Logout"]:
                self.logout()
            elif ans == menu_options["Start new game"]:
                self.start_new_game()
            elif ans == menu_options["Continue game"]:
                self.continue_game()
            elif ans == menu_options["Exit"]:
                print("exiting game")
                break
        self.communication.client.close()


if __name__ == "__main__":
    c = Client()
    c.run()
