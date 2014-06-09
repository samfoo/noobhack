import os

import cPickle as pickle

def load(save_file):
    if os.path.exists(save_file):
        save = open(save_file, "r")
        try:
            return pickle.load(save)
        finally:
            save.close()
    else:
        raise RuntimeError(
            "NetHack is trying to restore a game file, but noobhack " + 
            "doesn't have any memory of this game. While noobhack will " +
            "still work on a game it doesn't know anything about, there " +
            "will probably be errors. If you'd like to use noobhack, " +
            "run nethack and quit your current game, then restart " + 
            "noobhack."
        )

def save(save_file, player, dungeon):
    save = open(save_file, "w")
    try:
        pickle.dump((player, dungeon), save)
    finally:
        save.close()

def delete(save_file):
    if os.path.exists(save_file):
        os.remove(save_file)

