class Level:
    def __init__(self):
        self.rooms = {} 

    def rooms_of_interest(self):
        return self.rooms

class Dungeon:
    def __init__(self):
        # TODO: Figure out what the others are.
        self.locations = {
            "dungeon": [],
            "mines": []
        }

        self.location = "dungeon"
        self.level = 0
