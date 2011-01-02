"""
I'm chock full of classes and methods and constants and whatnot that keep track
of the state of the dungeon while a game is being played. That is to say: which
levels are where, what features the levels have, where it's entrances and exits
are, etc.
"""

import re

from noobhack.game import shops 

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

class Map:
    """
    Ahh, the map. The nethack text client, unfortunately doesn't always give us
    the best clues about what level or branch we're on. Instead we have to make
    our best guess. To make matters worst: Level teleports and trap doors add 
    to the confusion and the dungeon becomes a set of graphs that connect at 
    some point, but figuring out what those points are and tracking everything
    is really complex (see the mostrosity that is `move`).

    The way we keep track of connections is two-fold:

        1. We keep track of links between levels. The links between dlvl 1 and 
        dlvl 2, for example, are all kept in the links hash under the key
        `(1, 2)`. When the player travels from dlvl 1 to dlvl2, we know what
        her position was before she arrived and her position after she arrived.
        All of these together form a link. E.g. `{(1, 2): ((1, 2), (3, 4))}`
        would be a link from dlvl 1 to 2, where the top position is `(1, 2)` 
        and the bottom position is `(3, 4)`.

        2. Each level keeps track of it's own entrances and exits (ups and 
        downs)

    With this information we can contruct a sparse graph of the entire dungeon.
    As we see new levels and new stairwells, the links are automatically 
    created.
    """

    def __init__(self):
        self.levels = {1: [Level(1)]} 
        self.links = {}
        self.current = self.levels[1][0]

    def _add(self, at_dlvl, level):
        """
        Add a dungeon level. This doesn't check to see if a dungeon level
        exists or is part of the interpreted graph. Generally, `move` should be
        used instead.

        :param at_dlvl: int dungeon level to add the level at.
        :param level: The `Level` to add.
        """

        dlvl = self.levels.get(at_dlvl, []) 
        dlvl.append(level)
        self.levels[at_dlvl] = dlvl 

    def _guess_teleported(self, to_dlvl):
        """
        Attempts to find a "best guess" level that we've already seen that was
        teleported to.
        """

        if self.levels.has_key(to_dlvl) and \
           len(self.levels[to_dlvl]) == 1 and \
           self.levels[to_dlvl][0].branch == self.current.branch:
            # If we teleported/droped into a level that we've already been
            # to, our work is done, just set current to this level.
            return self.levels[to_dlvl][0]

        elif self.levels.has_key(to_dlvl) and \
                len(self.levels[to_dlvl]) > 1:
            # We might have been to this level before, we don't know. Check
            # to see if any of the levels on this dlvl are the same branch
            # as the current level (maybe we teleported there).
            possibles = self.levels[to_dlvl]
            found = [l for l in possibles if l.branch == self.current.branch]
            if len(found) == 1:
                return found[0]
            else:
                return None

        else:
            # We've never seen this place before for sure.
            return None

    def is_orphan(self, level):
        """
        Return whether the level is an orphan or not. An orphan is a level with
        no levels above that connect to it.
        """

        return level in self.orphans(level.dlvl)

    def orphans(self, dlvl):
        """
        Return a list of all orphans on a particular dlvl.
        """

        levels = self.levels[dlvl]
        return [level for level in levels if len(level.ups) == 0]

    def children(self, level):
        """
        Return a list of all children of a level. Children are those levels 
        one level below and directly connected to the parent via stairwells.
        """

        dlvl = level.dlvl
        links = self.links.get((dlvl, dlvl + 1), set())
        return [
            self.levels_for_link(dlvl, link[0], dlvl+1, link[1])[1] 
            for 
                link in links 
            if 
                link[0] in level.downs
        ]

    def first(self):
        """
        Return the starting level.
        """

        return self.levels[1][0]

    def branch(self, branch):
        """
        Mark the current level as a branch.
        """

        self.current.branch = branch

    def teleport(self, from_dlvl, to_dlvl):
        """
        Transition from one dungeon level to another by teleport.
        """

        guess = self._guess_teleported(to_dlvl)

        if from_dlvl > to_dlvl and guess is None:
            # We're moving up, so there's one extra heuristic we can do:
            # Moving up means that we can only ever be in either our
            # current branch *or* the main dungeon branch. We've 
            # eliminated the possibility that we're in our current 
            # branch, but maybe we're in the main branch.
            guess = [l for l in self.levels[to_dlvl] if l.branch == "main"]
            if len(guess) > 0:
                guess = guess[0]
            else:
                guess = None

        if guess is not None:
            self.current = guess
        else:
            # We've (hopefully) never been here before, and (hopefully)
            # are on the same branch, or (hopefully) will get a message
            # telling us the current level is a different branch.
            new = Level(to_dlvl, self.current.branch)
            self._add(to_dlvl, new)
            self.current = new

    def move(self, from_dlvl, to_dlvl, from_pos, to_pos):
        """
        Transition from one dungeon level to another.

        Here be dragons.
        """

        # If the positions are provided, we've got and explicit link
        # between two levels (we traveled there by stairs). It's simple
        # enough to check and see if we've been to this level before by
        # checking to see if the link exists.
        if from_dlvl < to_dlvl:
            # Heading down...
            above, below = from_dlvl, to_dlvl
            above_pos, below_pos = from_pos, to_pos
        else:
            # ... or heading up
            above, below = to_dlvl, from_dlvl
            above_pos, below_pos = to_pos, from_pos

        if (above_pos, below_pos) in self.links.get((above, below), set()):
            # There's already a link, we just need to get the levels.
            above_lvl, below_lvl = self.levels_for_link(above, 
                                                        above_pos, 
                                                        below, 
                                                        below_pos)
            if from_dlvl < to_dlvl:
                self.current = below_lvl
            else:
                self.current = above_lvl
        else:
            new = Level(to_dlvl, self.current.branch)

            if from_dlvl < to_dlvl:
                # Heading down is easy enough...
                self.current.downs.add(above_pos)
                new.ups.add(below_pos)

                # If there was no link, we couldn't have been here before...
                self._add(to_dlvl, new)
                self.current = new
            else:
                # ... but heading up might be trickier. We might be on a branch
                # which teleported us down and have just arrived at a level 
                # which we've never gone down to before... crap.

                if not self.is_orphan(self.current):
                    # There's already a link from our current level to some
                    # level above it. We're not using that link, so we must be
                    # going up to a different (new) level. I think this case
                    # only happens with sokoban.
                    self._add(to_dlvl, new)
                else:
                    # Try to find any parents above me that are childless that
                    # I might be traveling to.
                    possibles = [l for l in self.levels.get(above, []) if len(self.children(l)) == 0 and l.branch == self.current.branch] 
                    if len(possibles) == 0:
                        # There are no levels above me that could possibly be a
                        # parent, so this must be going from one orphan to 
                        # another and we're fine creating a new level.
                        self._add(to_dlvl, new)
                    else: 
                        # There was a level above me that could be my parent.
                        # Hopefully only one, because we can't tell the
                        # difference between them.
                        new = possibles[0]

                new.downs.add(above_pos)
                self.current.ups.add(below_pos)
                self.current = new

            # There's no link, so create it.
            self._link(above, above_pos, below, below_pos)

    def levels_for_link(self, above, above_pos, below, below_pos):
        """
        Given two dungeon levels and two positions, return the levels (above,
        and below) which form this link.

        :param above: the dungeon level above
        :param above_pos: a tuple (x, y) position of the above (down) stairs
        :param below: the dungeon level below
        :param below_pos: a tuple (x, y) position of the below (up) stairs

        :return: a tuple of the Level objects, (above, below)
        """

        possibles = self.links.get((above, below), set())
        if (above_pos, below_pos) in possibles:
            aboves = self.levels.get(above, [])
            belows = self.levels.get(below, [])
            above_lvl = [l for l in aboves if above_pos in l.downs][0]
            below_lvl = [l for l in belows if below_pos in l.ups][0]

            return above_lvl, below_lvl
        else:
            return None 

    def _link(self, above, above_pos, below, below_pos):
        """
        Add a link between two dungeon levels.
        """

        aboves = self.levels.get(above, [])
        belows = self.levels.get(below, [])
        if len([l for l in aboves if above_pos in l.downs]) == 0 or \
           len([l for l in belows if below_pos in l.ups]) == 0:
            raise ValueError("Adding a link to non-existant levels not allowed")

        current = self.links.get((above, below), set())
        current.add((above_pos, below_pos))
        self.links[(above, below)] = current

class Level:
    """
    A level is a single dungeon level. This can be thought of as "mines, level 
    3", or "main, level 5". There can be multiple levels of the same dlvl, but
    they must be on different branches.
    """
    codemap = {
        "oracle": "o",
        "rogue": "r",
        "altar (chaotic)": "ac",
        "altar (neutral)": "an",
        "altar (lawful)": "al",
        "angry watch": "w",
        "zoo": "z",
        "barracks": "b",
        "shop": "s",
        "vault": "v",
        "beehive": "h",
        "chest": "c",
    }

    def __init__(self, dlvl, branch="main"):
        self.features = set()
        self.shops = set()
        self.ups = set()
        self.downs = set()
        self.breadcrumbs = set()
        self.dlvl = dlvl
        self.branch = branch 

    def short_codes(self):
        """
        Return the list of short codes (useful for displaying information about
        a level when space is limited).
        """

        codes = [self.codemap[f] for f in self.features if self.codemap.has_key(f)]
        return sorted(codes)

    def __eq__(self, other):
        if other is None or other.__class__ is not Level:
            return False

        return self.dlvl == other.dlvl and \
                self.features == other.features and \
                self.ups == other.ups and \
                self.downs == other.downs and \
                self.branch == other.branch

class Dungeon:
    """
    The dungeon keeps track of various dungeon states that are helpful to know.
    It remembers where shops are, remembers where it heard sounds and what they
    mean, and probably some other stuff that I'll think of in the future.
    """

    def __init__(self):
        self.graph = Map()
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
        dispatcher.add_event_listener("trap-door", 
                                      self._level_teleport_handler)
        dispatcher.add_event_listener("move", self._bread_crumbs_handler)

    def _bread_crumbs_handler(self, _, cursor):
        self.current_level().breadcrumbs.add(cursor)

    def _shop_type_handler(self, _, shop_type):
        if "shop" not in self.current_level().features:
            self.current_level().features.add("shop")
        self.current_level().shops.add(shops.types[shop_type]) 

    def _branch_change_handler(self, _, branch):
        self.graph.branch(branch)

    def _level_feature_handler(self, _, feature):
        self.current_level().features.add(feature)

    def _level_teleport_handler(self, _):
        self.went_through_lvl_tel = True 

    def _level_change_handler(self, _, level, from_pos, to_pos):
        if self.level == level:
            # This seems like it's probably an error. The brain, or whoever is
            # doing the even dispatching should know not to dispatch a level
            # change event when, in fact, we clearly have not changed levels.
            return

        if abs(self.level - level) > 1 or \
           self.went_through_lvl_tel:
            self.graph.teleport(self.level, level)
            self.went_through_lvl_tel = False
        else:
            self.graph.move(self.level, level, from_pos, to_pos)

        # Update our current position
        self.level = level

    def current_level(self):
        return self.graph.current
