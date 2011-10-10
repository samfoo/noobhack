"""
I'm chock full of classes and methods and constants and whatnot that keep track
of the state of the dungeon while a game is being played. That is to say: which
levels are where, what features the levels have, where it's entrances and exits
are, etc.
"""

import re

from noobhack.game import shops 

from noobhack.game.mapping import Map
from noobhack.game.mapping import Level

from noobhack.game.events import dispatcher

messages = {
    "trap-door": set((
        "A trap door opens up under you!",
        "Air currents pull you down into a hole!",
        "There's a gaping hole under you!",
    )),
    "level-teleport": set((
        "You rise up, through the ceiling!",
        "You dig a hole through the floor.  You fall through...",
        "You activated a magic portal!",
    )),
}

def looks_like_sokoban(display):
    """
    Sokoban is a lot easier than the mines. There's no teleporting and we know
    exactly what the first level looks like (though there are two variations 
    and it's all revealed at once.

    Easy peasy.
    """

    first = [
        "--\\^\\|   \\|.0...\\|",
        "\\|\\^-----.0...\\|",
        "\\|..\\^\\^\\^\\^0.0..\\|",
        "\\|..----------",
        "----",
    ]

    second = [
        "\\|\\^\\|    \\|......\\|",
        "\\|\\^------......\\|",
        "\\|..\\^\\^\\^\\^0000...\\|",
        "\\|\\.\\.-----......\\|",
        "----   --------",
    ]

    def identify(pattern):
        i = 0
        for j in xrange(len(display)):
            line = display[j].strip()
            if re.match(pattern[i], line) is not None:
                if i == len(pattern) - 1:
                    # Found the last one, that means we're home free.
                    return True
                else:
                    # Found this one, but it's not the last one.
                    i += 1
        return False

    sokoban = identify(first)
    if not sokoban:
        sokoban = identify(second)

    return sokoban
            
def looks_like_mines(display):
    """
    Gnomish Mines:
    
    Since we don't get a message about being in the mines, we have to
    guess whether we're in the mines or not. There are some features
    unique to the mines that we can use to make a pretty educated
    guess that we're there. Easiest is that the walls are typically irregular
    in the mines:
    
    e.g.
    
         --   or  --   or  --    or  --
        --         --        --        --
    
    Would indicate that we're in the mines. The other thing that could indicate
    that it's the mines is passageways that are only one square wide.

    e.g.
             or   -
        |.|       .
                  -
    """

    def indices(row):
        """
        Find the indices of all double dashes in the string.
        """
        found = []
        i = 0
        try:
            while True: 
                occurance = row.index("--", i)
                found.append(occurance)
                i = occurance + 1
        except ValueError:
            pass

        return found

    def mines(first, second):
        """
        Look at adjacent rows and see if the have the right pattern shapes to
        be what might be the mines.
        """
        for index in first:
            for other_index in second:
                if index == other_index + 1 or \
                   other_index == index + 1 or \
                   index == other_index + 2 or \
                   other_index == index + 2:
                    return True
        return False

    scanned = [indices(row) for row in display]
    for i in xrange(len(scanned)):
        if i + 1 == len(scanned):
            break
        above, below = scanned[i], scanned[i+1]
        if mines(above, below):
            return True

    for column in ["".join(c).strip() for c in zip(*display)]:
        if column.find("-.-") > -1:
            return True

    return False

#class Level:
#    """
#    A level is a single dungeon level. This can be thought of as "mines, level 
#    3", or "main, level 5". There can be multiple levels of the same dlvl, but
#    they must be on different branches.
#    """
#    codemap = {
#        "oracle": "o",
#        "rogue": "r",
#        "altar (chaotic)": "ac",
#        "altar (neutral)": "an",
#        "altar (lawful)": "al",
#        "angry watch": "w",
#        "zoo": "z",
#        "barracks": "b",
#        "shop": "s",
#        "vault": "v",
#        "beehive": "h",
#        "chest": "c",
#    }
#
#    def __init__(self, dlvl, branch="main"):
#        self.features = set()
#        self.shops = set()
#        self.ups = set()
#        self.downs = set()
#        self.breadcrumbs = set()
#        self.dlvl = dlvl
#        self.branch = branch 
#
#    def __str__(self):
#        return "dlvl:%s branch:%s ups:%s downs:%s" % (self.dlvl, self.branch, str(self.ups), str(self.downs))
#
#    def short_codes(self):
#        """
#        Return the list of short codes (useful for displaying information about
#        a level when space is limited).
#        """
#
#        codes = [self.codemap[f] for f in self.features if self.codemap.has_key(f)]
#        return sorted(codes)
#
#    def __eq__(self, other):
#        if other is None or other.__class__ is not Level:
#            return False
#
#        return self.dlvl == other.dlvl and \
#                self.features == other.features and \
#                self.ups == other.ups and \
#                self.downs == other.downs and \
#                self.branch == other.branch
#
class Dungeon:
    """
    The dungeon keeps track of various dungeon states that are helpful to know.
    It remembers where shops are, remembers where it heard sounds and what they
    mean, and probably some other stuff that I'll think of in the future.
    """

    def __init__(self):
        self.graph = Map(Level(1), 0, 0)
        self.level = 1
        self.went_through_lvl_tel = False

    def listen(self):
        dispatcher.add_event_listener("level-change", 
                                      self._level_change_handler)
        dispatcher.add_event_listener("branch-change",
                                      self._branch_change_handler)
        dispatcher.add_event_listener("level-feature",
                                      self._level_feature_handler)
        dispatcher.add_event_listener("shop-type",
                                      self._shop_type_handler)
        dispatcher.add_event_listener("level-teleport",
                                      self._level_teleport_handler)
        dispatcher.add_event_listener("branch-port",
                                      self._branch_port_handler)
        dispatcher.add_event_listener("trap-door", 
                                      self._level_teleport_handler)
        dispatcher.add_event_listener("move", self._map_move_handler)
        dispatcher.add_event_listener("move", self._bread_crumbs_handler)

    def _map_move_handler(self, _, cursor):
        self.graph.move(*cursor)

    def _bread_crumbs_handler(self, _, cursor):
        # TODO: Implement
        #self.current_level().breadcrumbs.add(cursor)
        pass

    def _shop_type_handler(self, _, shop_type):
        if "shop" not in self.current_level().features:
            self.current_level().features.add("shop")
        self.current_level().shops.add(shops.types[shop_type]) 

    def _branch_change_handler(self, _, branch):
        self.graph.change_branch_to(branch)

    def _level_feature_handler(self, _, feature):
        self.current_level().features.add(feature)

    def _level_teleport_handler(self, _):
        self.went_through_lvl_tel = True 

    def _branch_port_handler(self, _, branch):
        # TODO: Implement
        #self.graph.branch_port(branch)
        pass

    def _level_change_handler(self, _, level, from_pos, to_pos):
        if self.level == level:
            # This seems like it's probably an error. The brain, or whoever is
            # doing the even dispatching should know not to dispatch a level
            # change event when, in fact, we clearly have not changed levels.
            return

        if abs(self.level - level) > 1 or self.went_through_lvl_tel:
            self.graph.travel_by_teleport(level, to_pos)
            self.went_through_lvl_tel = False
        else:
            self.graph.travel_by_stairs(level, to_pos)

        # Update our current position
        self.level = level

    def current_level(self):
        return self.graph.current
