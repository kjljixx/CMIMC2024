import bot.gen1
import bot.greedy_bot_move
import bot.random_bot_move
import bot.strategy
from hex_func import *
import importlib
import os
from os.path import abspath, dirname
import json
import bot
from pathlib import Path

os.chdir(dirname(abspath(__file__)))

# Setting

WRITE = True
NGAME = 1
DEBUG = True

# file path

directory_path = Path(__file__).parent
bot_path = directory_path / "bot"
bot_mod = "bot."
save_path = directory_path / "games"

# create save path if not exist
if not os.path.exists(save_path):
    os.makedirs(save_path)

# generate bot list
bot_list = {
    # name: getattr(
    #     importlib.import_module(bot_mod + os.path.splitext(name)[0]),
    #     os.path.splitext(name)[0],
    # )
    # for name in os.listdir(bot_path)
    # if os.path.isfile(os.path.join(bot_path, name))
}
bot_list = {"pass":bot.greedy_bot_move.greedy_bot_move, "p":bot.strategy.strategy, "m":bot.gen1.strategy}
print("Bots:", list(bot_list.keys()))
# Running

total_scores = [0, 0, 0]

for n in range(NGAME):
    gameid = str(time.time())
    path = os.path.join(save_path, gameid + ".json")

    res = run_game(bot_list)
    res["id"] = gameid

    for i in range(3):
        total_scores[i] = total_scores[i] + res["scores"][i]

    if WRITE:
        with open(path, "w") as writer:
            json.dump(res, writer)
    if n % 10 == 0:
        print(total_scores)
print(total_scores)
