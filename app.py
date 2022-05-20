import requests

import json
import threading
import time

from vkbottle import Bot, PhotoMessageUploader, Text, Keyboard, KeyboardButtonColor
from vkbottle.bot import Message

import favourite
from search import search_game
from data.settings import FAVOURITE_UPDATING_TIME
from data.config import BOT_TOKEN

bot = Bot(BOT_TOKEN)
photo_message_uploader = PhotoMessageUploader(bot.api, generate_attachment_strings=True)


def keyboard_bot(game_name):
    keyboard = (Keyboard(one_time=False, inline=True))
    keyboard.add(Text("Добавить в избранное", {"favourite": game_name}), color=KeyboardButtonColor.PRIMARY)
    return keyboard.get_json()


def call_favourite():
    while True:
        favourite.main()
        time.sleep(FAVOURITE_UPDATING_TIME)


async def get_photo(game_name):
    with open("json/photo.json", "r") as file:
        photo_list = json.load(file)
    try:
        return photo_list[game_name]
    except KeyError:
        path = requests.get(favourite.get_json(game_name)["full_image"]).content
        photo_list[game_name] = await photo_message_uploader.upload(file_source=path)
        with open("json/photo.json", "w") as file:
            json.dump(photo_list, file)
        return photo_list[game_name]


@bot.on.private_message(text="Добавить в избранное")
async def add_favourite(message: Message):
    with open("json/favourite_dict.json", "r") as file:
        fav_dict = json.load(file)
    for peer_id in fav_dict.keys():
        if json.loads(message.payload)["favourite"] not in fav_dict[peer_id]:
            await message.answer("Вы внесли игру в избранное!")
            fav_dict[str(message.peer_id)].append(json.loads(message.payload)["favourite"])
            with open("json/favourite_dict.json", "w") as file:
                json.dump(fav_dict, file)
        else:
            await message.answer("Вы уже внесли игру в избранное!")


@bot.on.private_message()
async def game_request(message: Message):
    try:
        if search_game(message.text) is True:
            await message.answer("Игра взломана.", attachment=await get_photo(favourite.rename(message.text)))
        else:
            await message.answer("Игра не взломана.", attachment=await get_photo(favourite.rename(message.text)),
                                 keyboard=keyboard_bot(favourite.rename(message.text)))
    except KeyError:
        await message.answer("Не знаю такой игры, возможно ты неправильно ввёл название?")


if __name__ == '__main__':
    threading.Thread(target=call_favourite).start()
    bot.run_forever()
