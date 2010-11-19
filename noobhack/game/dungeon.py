import game.shops 

from events import dispatcher

class Level:
    def __init__(self):
        self.features = set()
        self.exits = set()

class Dungeon:
    """
    The dungeon keeps track of various dungeon states that are helpful to know.
    It remembers where shops are, remembers where it heard sounds and what they
    mean, and probably some other stuff that I'll think of in the future.
    """

    def __init__(self):
        self.graph = {"dungeon:1": Level()}
        self.level = "dungeon:1"
        dispatcher.add_event_listener("level-change", 
                                      self._level_change_handler)
        dispatcher.add_event_listener("level-feature",
                                      self._level_feature_handler)
        dispatcher.add_event_listener("shop-type",
                                      self._shop_type_handler)

    def _shop_type_handler(self, event, shop_type):
        if "shop" in self.current_level().features:
            # Remove the generic shop now that we know what type of shop it is.
            self.current_level().features.remove("shop")
        self.current_level().features.add("shop (%s)" % \
                                          game.shops.types[shop_type]) 

    def _level_feature_handler(self, event, feature):
        self.graph[self.level].features.add(feature)

    def _level_change_handler(self, event, branch, level, teleported=False):
        key = "%s:%d" % (branch, level)
        if not teleported:
            self.graph[self.level].exits.add(key)

        if not self.graph.has_key(key):
            self.graph[key] = Level()

        self.level = key

    def current_level(self):
        return self.graph[self.level]
