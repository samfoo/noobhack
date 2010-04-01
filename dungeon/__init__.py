def load(filename=".dungeon.nh"):
    # TODO: Probably should implement this at some point.
    return None

class Dungeon:
    def __init__(self):
        self.current = 0 
        self.levels = {} 

    def dungeon_add_shop(self, shop_type):
        shops = self.levels[self.current]["shops"]
        if not shop_type in shops:
            shops.append(shop_type)

    def set_current_level(self, level):
        self.current = level
        if not self.levels.has_key(self.current):
            self.levels[self.current] = {"shops": []}

    def delete(self):
        # TODO: Probably should implement this at some point.
        pass

    def save(self, filename=".dungeon.nh"):
        # TODO: Probably should implement this at some point.
        pass
