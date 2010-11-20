import game.shops 

from game.events import dispatcher

messages = {
    "trap-door": set(("A trap door opens up under you!",))
}

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
    
    Would indicate that we're in the mines.
    """

    def indices(row):
        # Find the indices of all double dashes in the string.
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

    return False

class Map:
    def __init__(self):
        self.levels = {1: [Level(1)]} 
        self.links = {}
        self.current = self.levels[1][0]

    def _add(self, at, level):
        """
        Add a dungeon level. This doesn't check to see if a dungeon level
        exists or is part of the interpreted graph. Generally, `move` should be
        used instead.

        :param at: int dungeon level to add the level at.
        :param level: The `Level` to add.
        """

        dlvl = self.levels.get(at, []) 
        dlvl.append(level)
        self.levels[at] = dlvl 

    def _guess_teleported(self, from_dlvl, to_dlvl):
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

    def branch(self, branch):
        self.current.branch = branch

    def teleport(self, from_dlvl, to_dlvl):
        """
        Transition from one dungeon level to another by teleport.
        """

        guess = self._guess_teleported(from_dlvl, to_dlvl)

        if from_dlvl > to_dlvl and guess is None:
            # We're moving up, so there's one extra heuristic we can do:
            # Moving up means that we can only ever be in either our
            # current branch *or* the main dungeon branch. We've 
            # eliminated the possibility that we're in our current 
            # branch, but maybe we're in the main branch.
            guess = [l for l in self.levels[to_dlvl] if l.branch == "main"]

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
            above_lvl, below_lvl = self._get_levels_for_link(above, 
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
                # which teleported us down and have just arrived back at a
                # level which we've never gone down to before... crap.

                # So how do we know if we're at a level that we've already been
                # to? Strictly speaking, we *can't* know; at least not for 
                # sure. However, we can guess that if we're coming up a branch,
                # and we arrive at some dlvl that we've been to and we've been
                # to the same branch or the main branch at that dlvl: then 
                # we've been here before.
                possibles = [l for l in self.levels.get(above, []) if l.branch == self.current.branch or l.branch == "main"]
                if len(possibles) == 0:
                    self._add(to_dlvl, new)
                else: 
                    new = possibles[0]

                new.downs.add(above_pos)
                self.current.ups.add(below_pos)
                self.current = new

            # There's no link, so create it.
            self._link(above, above_pos, below, below_pos)

    def _get_levels_for_link(self, above, above_pos, below, below_pos):
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
    def __init__(self, dlvl, branch="main"):
        self.features = set()
        self.shops = set()
        self.ups = set()
        self.downs = set()
        self.dlvl = dlvl
        self.branch = branch 

    def __str__(self):
        return "Dlvl(%s):%d(%s)" % (self.branch, \
                                    self.dlvl, \
                                    ",".join([f[0] for f in self.features]))

    def __repr__(self):
        return "<level(%s): %s>" % (self.branch, repr({
            "ups": list(self.ups),
            "downs": list(self.downs),
        }))

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
        self.fell_through_trap = False
        self.went_through_lvl_tel = False

        dispatcher.add_event_listener("level-change", 
                                      self._level_change_handler)
        dispatcher.add_event_listener("branch-change",
                                      self._branch_change_handler)
        dispatcher.add_event_listener("level-feature",
                                      self._level_feature_handler)
        dispatcher.add_event_listener("shop-type",
                                      self._shop_type_handler)

    def _shop_type_handler(self, _, shop_type):
        if "shop" not in self.current_level().features:
            self.current_leve().features.add("shop")
        self.current_level().shops.add(game.shops.types[shop_type]) 

    def _branch_change_handler(self, _, branch):
        self.graph.branch(branch)

    def _level_feature_handler(self, _, feature):
        self.current_level().features.add(feature)

    def _level_change_handler(self, _, level, from_pos, to_pos):
        if self.level == level:
            # This seems like it's probably an error. The brain, or whoever is
            # doing the even dispatching should know not to dispatch a level
            # change event when, in fact, we clearly have not changed levels.
            return

        if self.went_through_lvl_tel or self.fell_through_trap:
            self.graph.teleport(self.level, level)
            self.went_through_lvl_tel = False
            self.fell_through_trap = False
        else:
            self.graph.move(self.level, level, from_pos, to_pos)

        # Update our current position
        self.level = level

    def current_level(self):
        return self.graph.current
