import requests
import html
import random

import constants
from firefox_db import Database


QUESTIONS_PATH_WEB = "https://opentdb.com/api.php?amount={}&category={}&difficulty={}&type=multiple"


class TriviaOpenDb:

    def __init__(self, cat, diff, number_of_questions=10, next_question=None):
        self.category = cat
        self.difficulty = diff
        self.number_of_questions = number_of_questions
        if next_question is None:
            self.my_questions_path = QUESTIONS_PATH_WEB.format(number_of_questions,
                                                               trivia_categories_dict[self.category],
                                                               trivia_difficulty_dict[self.difficulty])
            # print(self.my_questions_path)
            self.questions = TriviaOpenDb.load_trivia_game(self.my_questions_path)
            # print(self.questions)
            self.next_question = 0
        else:
            self.next_question = next_question

    def get_next_question(self):
        try:
            key = list(self.questions.keys())[self.next_question]
            struct = self.questions[key]
            question = struct['question']
            answers = struct['answers']
            self.next_question += 1
            return key, question, answers
        except IndexError:
            # print("no more questions")
            return None, None, None

    def get_correct_answer(self, question):
        for q in self.questions.values():
            if q['question'] == question:
                correct = q['correct_answer']
                return correct, q['answers'][correct-1], constants.NUMBER_OF_QUESTIONS
        return -1, 0, ""

    def add_player_answer(self, game_id, player_name, question_id, player_value):
        pass

    @staticmethod
    def decode_html_entities(json_dict):
        if isinstance(json_dict, list):
            return [TriviaOpenDb.decode_html_entities(itm) for itm in json_dict]
        elif isinstance(json_dict, dict):
            return {key: TriviaOpenDb.decode_html_entities(value) for key, value in json_dict.items()}
        elif isinstance(json_dict, str):
            return html.unescape(json_dict)
        else:
            return json_dict

    @staticmethod
    def load_trivia_game(db_path):
        json_dict = TriviaOpenDb.decode_html_entities(requests.get(db_path).json())
        dict_questions = dict()
        for i in range(1, len(json_dict["results"]) + 1):
            dict_questions[i] = json_dict['results'][i - 1]
        q_list = list(dict_questions.items())
        random.shuffle(q_list)
        trivia_dict = {}
        for itm in q_list:
            answers = [itm[1]["correct_answer"]] + itm[1]["incorrect_answers"]
            random.shuffle(answers)
            correct = answers.index(itm[1]["correct_answer"]) + 1
            trivia_dict[itm[0]] = {"question": itm[1]['question'], "answers": answers, "correct_answer": correct}

        return trivia_dict

    @staticmethod
    def run_game():
        score = 0
        key, question, answers = t.get_next_question()
        i = 1
        while question is not None:
            print(f"{i}. {question}")
            j = 1
            for answer in answers:
                print(f"   {j}. {answer}")
                j = j + 1
            reply = int(input("Enter you answer: "))
            correct_ans,  correct_answer_txt, max_number_of_questions = t.get_correct_answer(question)
            if reply == correct_ans:
                score += 5
                print("correct")
            else:
                # correct_ans, correct_score = t.get_correct_answer(question)
                print(f"incorrect === correct answer is {correct_answer_txt}")
            i += 1
            key, question, answers = t.get_next_question()
        return score


class TriviaOpenDbFirebase(TriviaOpenDb):
    def __init__(self, game_id, player_name):
        # print("init TriviaOpenDbFirebase")
        game_dict = Database.get_by_key("games", game_id)
        print(game_dict['players'])
        super().__init__(game_dict['category'], game_dict['difficulty'],
                         game_dict['number_questions'], len(game_dict['players'][player_name]))
        self.questions = game_dict['questions']
        self.players = game_dict['players'][player_name]
        # print(self.players)

    def get_next_question(self):
        try:
            key = self.next_question
            print(key)
            print(self.questions)
            struct = self.questions[key]
            question = struct['question']
            answers = struct['answers']
            self.next_question += 1
            return key, question, answers
        except IndexError:
            print("no more questions")
            return None, None, None

    def get_correct_answer(self, question):
        # print(self.questions)
        # print(type(self.questions))
        for q in self.questions[1:]:
            if q['question'] == question:
                correct = q['correct_answer']
                return correct, q['answers'][correct-1], constants.NUMBER_OF_QUESTIONS
        return -1, "", -1


trivia_categories_dict = {'Animals': 27,
                          'Book': 10,
                          "General knowledge": 9,
                          "History": 23,
                          "Music": 12,
                          "Science computers": 18,
                          "Sports": 21,
                          "Vehicles": 28
                          }

trivia_difficulty_dict = {"0": "easy", "1": "medium", "2": "hard"}


if __name__ == "__main__":
    get_category = True
    category = "Book"
    difficulty = 0
    while get_category:
        for item in trivia_categories_dict.keys():
            print(item)
        category = input("enter trivia category: ")
        try:
            trivia_categories_dict[category]
            get_category = False
        except KeyError:
            print("illegal category")

    get_difficulty = True
    while get_difficulty:
        for item in trivia_difficulty_dict.items():
            print(item)
        difficulty = input("enter trivia difficulty (number): ")
        try:
            trivia_difficulty_dict[difficulty]
            get_difficulty = False
        except KeyError:
            print("illegal difficulty")

    t = TriviaOpenDb(category, difficulty, constants.NUMBER_OF_QUESTIONS)
    print("game score: ", TriviaOpenDb.run_game())
