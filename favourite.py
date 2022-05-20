import requests
import json

from data.config import BOT_TOKEN
from data.settings import API_VERSION


# rename game name for use in the url
def rename(game_name: str) -> str:
    game_name = game_name.lower()
    game_name = game_name.replace(": ", "-")
    game_name = game_name.replace(" ", "-")
    return game_name


# general view for url https://gamestatus.info/back/api/gameinfo/game/*renamed-game-name*
def get_json(game_name: str) -> dict:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
    }
    url = "https://gamestatus.info/back/api/gameinfo/game/" + rename(game_name)
    r = requests.get(url, headers=headers, params={"format": "json"})

    return json.loads(r.text)


# return game's crack status. False - not cracked, True - cracked
def get_crack_status(game_name: str) -> bool:
    json_dict = get_json(game_name)
    if json_dict["crack_date"] is None:
        return False
    else:
        return True


# send message to peer_id
def message_send(peer_id: str, text_message: str) -> None:
    url = "https://api.vk.com/method/messages.send?"
    params = {
        "user_id": int(peer_id),
        "message": text_message,
        "random_id": 0,
        "access_token": BOT_TOKEN,
        "v": API_VERSION
    }
    requests.get(url, params=params)


def main():
    with open("json/uncracked_games.json", "r") as file:
        uncracked_game_list = json.load(file)

    for game in uncracked_game_list:
        if get_crack_status(game):
            uncracked_game_list.remove(game)
            with open("json/favourite_dict.json", "r") as file:
                fav_dict = json.load(file)
            for peer_id in fav_dict.keys():
                if game in fav_dict[peer_id]:
                    fav_dict[peer_id].remove(game)
                    with open("json/favourite_dict.json", "w") as file:
                        json.dump(fav_dict, file)
                    message_send(peer_id, game + " была взломана!")

    with open("json/uncracked_games.json", "w") as file:
        json.dump(uncracked_game_list, file)

