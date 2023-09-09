from player import Player


class Game:
    def __init__(self, identifier):
        self.id = identifier
        self.active = True
        self.questions = {}
        self.players_actions = {}
        self. ready = False

    def add_player(self, player):
        self.players_actions[player.id] = {"name": player.name, "reply": False, "answer": None, "result": None}
        print(f"player added: {self.players_actions[player.id]}")

    def add_player_reply(self, p_id, answer):
        self.players_actions[p_id]['reply'] = True
        self.players_actions[p_id]['answer'] = answer

    def is_all_player_answered(self):
        for p in self.players_actions.values():
            if not p['reply']:
                print(p)
                return False
        return True

    def get_player_answer(self, p_id):
        if not self.players_actions[p_id]['reply']:
            print(f"no reply yet fo player {p_id}")
        return self.players_actions[p_id]['answer']

    def play(self, correct_answer):
        if self.is_all_player_answered():
            self.ready = True
            for p_id, p in self.players_actions.items():
                if p['answer'] == correct_answer:
                    p['result'] = True
                else:
                    p['result'] = False
            print("round played")
        else:
            print("not all players replyed")

    def reset_game(self):
        for p in self.players_actions.values():
            p['reply'] = False
            p['answer'] = None
            p['result'] = None

    def remove_player(self, p_id):
        p = self.players_actions.pop(p_id)
        print(f"player removed: {p}")

    def __str__(self):
        s = str(self.__dict__)
        return s


if __name__ == "__main__":
    game = Game(1)
    game.add_player(Player(1, "zvi"))
    game.add_player(Player(2, "gal"))
    game.add_player(Player(3, "tom"))
    game.add_player_reply(1, 2)
    game.add_player_reply(2, 2)
    game.play(2)
    game.add_player_reply(3, 3)
    game.play(2)
    print(game)
    game.reset_game()
    game.play(1)
    game.add_player_reply(2, 3)
    game.add_player_reply(1, 2)
    game.add_player_reply(3, 2)
    game.play(2)
    print(game)
