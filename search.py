from favourite import get_crack_status, rename
import json


def search_game(game_name):
    if get_crack_status(game_name=game_name):
        return True
    else:
        with open("json/uncracked_games.json", "r") as file:
            uncracked_game_list = json.load(file)
        if rename(game_name) not in uncracked_game_list:
            uncracked_game_list.append(rename(game_name))
            with open("json/uncracked_games.json", "w") as file:
                json.dump(uncracked_game_list, file)
        return False
