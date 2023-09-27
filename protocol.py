import constants
from cipher import *


PROTOCOL_CLIENT_COMMANDS = {
    'login': ["name", "password"],
    'signin': ["name", "password"],
    'logout': ["name"],
    'start_game': ["player_name", "category", "difficulty", "number_of_questions"],
    'next_question': ["game_id"],
    'check_answer': ['game_id', "question_id", "question", "player_reply"],
    'game_score': ['game_id', 'player_name'],
    'active_games': ["player_name"],
    'continue_game': ['game_id', 'player_name'],
    'open_mp_game': ["player_name", "category", "difficulty", "number_of_questions"],
    'mp_games': ["player_name"],
    'join_mp_game': ['game_id', 'player_name'],
    'leave_mp_game': ['game_id', 'player_name'],
    'start_mp_game': ['game_id'],
    'close_mp_game': ['game_id'],
    'next_mp_question': ["game_id"],
    'games_history': ['player_id'],
    'mp_games_notify_game_manager': ["game_id", "player_name"],
    'notify_mp_answer': ['game_id', 'player_name', "question_id", "question", "player_reply"],
    'can_go_next': ["game_id"],
    'mp_game_result': ["game_id"],
    'exchange_key': ["client_ip_port", "public_key"],
    'remove_shared_key': ["client_ip_port"]
}
PROTOCOL_SERVER_COMMANDS = {
    "login_response": ["is_ok", "player_id"],
    "signin_response": ["is_ok", "player_id"],
    "logout_response": ["is_ok"],
    "connect_response": ["is_ok"],
    "player_response": ["player_id"],
    "start_game_response": ["game_id"],
    'next_question_response': ["question_id", "question", "list of answers"],
    'check_answer_response': ['is_correct', "correct answer"],
    'game_score_response': ['game_score'],
    'active_games_response': ['list_of_games'],
    'continue_game_response': ['game_id'],
    "open_mp_game_response": ["game_id"],
    'mp_games_response': ['list of games'],
    'join_mp_game_response': ['game_id'],
    'leave_mp_game_response': ['game_id'],
    'start_mp_game_response': ['is_ok'],
    'close_mp_game_response': ['is_ok'],
    'next_mp_question_response': ["question_id", "question", "list of answers"],
    'notify_mp_join': ['game_id', 'player_name'],
    'notify_mp_leave': ['game_id', 'player_name'],
    'games_history_response': ['list of games'],
    'mp_games_notify_game_manager_response': ['game_id'],
    'notify_mp_answer_response': ['is_notified'],
    'can_go_next_response':  ["is_ok"],
    "mp_game_result_response": ["header", "list of players results"],
    'exchange_key_response': ["public_key"],
    'remove_shared_key_response': ["is_ok"]
}


class Protocol:
    @staticmethod
    def is_valid(cmd, data):
        if cmd in PROTOCOL_CLIENT_COMMANDS.keys():
            d = data.split(constants.DELIMITER)
            if len(d) == len(PROTOCOL_CLIENT_COMMANDS[cmd]):
                return True
        if cmd in PROTOCOL_SERVER_COMMANDS.keys():
            d = data.split(constants.DELIMITER)
            if len(d) == len(PROTOCOL_SERVER_COMMANDS[cmd]):
                return True
        return False

    @staticmethod
    def build_message(cmd, params_list, key):
        full_msg = ""
        msg_data = f"{params_list[0]}"
        if len(params_list) > 1:
            for d in params_list[1:]:
                msg_data += constants.DELIMITER + f"{d}"
        if Protocol.is_valid(cmd, msg_data):
            full_msg = cmd + constants.DELIMITER + msg_data
        if key is not None:
            cipher = Cipher(key, constants.NONCE)
            encrypted_data = cipher.aes_encrypt(full_msg.encode())
            return encrypted_data
        else:
            return full_msg.encode()

    @staticmethod
    def parse_message(msg, key):
        if type(msg) is bytes:
            if key is not None:
                cipher = Cipher(key, constants.NONCE)
                msg = cipher.aes_decrypt(msg)
            else:
                msg = msg.decode()
        parts = msg.split(constants.DELIMITER)
        cmd = parts[0]
        data = parts[1]
        if len(parts) > 2:
            for part in parts[2:]:
                data += constants.DELIMITER + part
        if Protocol.is_valid(cmd, data):
            return cmd, data.split(constants.DELIMITER)
        return None, None
