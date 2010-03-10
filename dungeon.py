import cPickle

class Level:
    def __init__(self):
        self.things = {} 

    def things_of_interest(self):
        return self.things

class Dungeon:
    def __init__(self):
        self.branches = {
        }

        self.location = "The Dungeons of Doom"
        self.level = 0

    def current_level(self):
        return self.branches[self.location][self.level]

    def change_level(self, location, level):
        self.location = location

        # Maybe we're on a new level (either by teleporting or by going down
        # some stairs), so we have to add it to our current known levels
        self.branches[location] = \
            [self.branches[location][i] or Level() for i in xrange(level-1)]

        self.level = level

    def save(self, filename=".dungeon.nh"):
        pass
