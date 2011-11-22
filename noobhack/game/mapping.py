class Branch:
    def __init__(self, start):
        self.current = self.start = start

    def __iter__(self):
        return Branch(self.start)

    def __len__(self):
        return len([l for l in self])

    def subbranches(self):
        # Check me out!
        # I'm probably not performant. Oh well...
        this_branch = self.start.branch

        # TODO: Can a level have connections to more than one dungeon branch?
        roots = [l.branches()[0] for l
                 in self
                 if l.has_a_branch()]

        return [Branch(r) for r in roots]

    def next(self):
        # Go down the stairs (if they exist) to the next level below this one
        # on the same branch.
        if self.current == None:
            raise StopIteration
        else:
            current = self.current
            potential_nexts = [l for l 
                               in current.stairs.values() 
                               if l.branch == current.branch
                                 and l.dlvl > current.dlvl]
            if len(potential_nexts) > 0:
                self.current = potential_nexts[0]
            else:
                self.current = None

            return current

class Level(object):
    """
    A single dungeon level. This can be thought of as "mines, level 3", or 
    "main, level 5". There can be multiple levels of the same dlvl, but
    they should generally be in different branches. Dungeons have stairs to
    other levels.

    Levels also are responsible for keeping track of various interesting things
    about themselves. What features they contain, breadcrumbs of what squares
    have been stepped on, etc.
    """

    def __init__(self, dlvl, branch="main"):
        self.dlvl = dlvl
        self.branch = branch 
        self.stairs = {}

        # Level features
        self.breadcrumbs = set()
        self.features = set()
        self.shops = set()

    def change_branch_to(self, branch):
        self.branch = branch
        if self.branch != "sokoban":
            links = self.stairs.values()
            for child in [c for c in links if c.dlvl > self.dlvl]:
                child.change_branch_to(branch)

    def add_stairs(self, level, position):
        self.stairs[position] = level

    def stairs_at(self, pos):
        return self.stairs.get(pos, None)

    def has_stairs_at(self, pos):
        return self.stairs_at(pos) != None

    def branches(self):
        return [l for l in self.stairs.values() if l.branch != self.branch]

    def has_a_branch(self):
        return len(self.stairs) > 1 or \
                (len(self.stairs.values()) > 0 and \
                 self.stairs.values()[0].branch != self.branch)

    def is_a_junction(self):
        below = [l for l in self.stairs.values() if l.dlvl > self.dlvl]
        above = [l for l in self.stairs.values() if l.dlvl < self.dlvl]
        return len(below) > 1 or len(above) > 1

class Map:
    def __init__(self, level, x, y):
        self.current = level 
        self.levels = set([self.current])
        self.location = (x, y) 

    def move(self, x, y):
        self.location = (x, y)
        self.current.breadcrumbs.add((x, y))

    def level_at(self, branch, dlvl):
        maybe_level = [l for l 
                       in self.levels 
                       if l.dlvl == dlvl 
                           and l.branch == branch]
        if len(maybe_level) == 1:
            return maybe_level[0]
        else: 
            return None

    def change_branch_to(self, branch):
        self.current.change_branch_to(branch)

    def is_there_a_level_at(self, branch, dlvl):
        return self.level_at(branch, dlvl) is not None

    def _link(self, new_level, pos):
        self.current.add_stairs(new_level, self.location)
        new_level.add_stairs(self.current, pos)

    def _add(self, new_level, pos):
        self.levels.add(new_level)
        self._link(new_level, pos)

    def _handle_existing_level(self, to_dlvl, to_pos):
        has_stairs_to_other_lower = [l for l 
                                     in self.current.stairs.values() 
                                     if l.dlvl == to_dlvl]

        if len(has_stairs_to_other_lower) > 0:
            # If the existing level has stairs to it, and we're at a different
            # location than those stairs then the stairs at our current 
            # location *must* be a different level.
            other_level = has_stairs_to_other_lower[0]
            other_level.change_branch_to("not sure")

            new_level = Level(to_dlvl, "not sure")
            self._add(new_level, to_pos)
            self.current = new_level
        else:
            # Otherwise, if there are no stairs to the lower level, we just
            # assume that the stairs we're presently at lead to it.
            existing_level = self.level_at(self.current.branch, to_dlvl)
            self._link(existing_level, to_pos)
            self.current = existing_level

    def main(self):
        return Branch(min(self.levels, key=lambda x: x.dlvl))

    def branches(self):
        def group_min(groups, l):
            existing_min = groups.get(l.branch, l)
            if l.dlvl <= existing_min.dlvl:
                groups[l.branch] = l

        branch_roots = reduce(group_min, self.levels)
        return [Branch(root) for root in branch_roots]

    def travel_by_stairs(self, to_dlvl, to_pos):
        if self.current.has_stairs_at(self.location):
            # If the current level already has stairs at our current position,
            # then use them.
            self.current = self.current.stairs_at(self.location)
        elif self.is_there_a_level_at(self.current.branch, to_dlvl):
            # If there's a level in this branch at the dlvl that we're 
            # traveling to, but there's no current stairs link, it means that
            # we just haven't traveled by stairs between those levels. Adding
            # the link is all that's necessary.
            self._handle_existing_level(to_dlvl, to_pos)
        else:
            # If the current level doesn't have stairs at our current position,
            # create a new level and attach them.
            new_level = Level(to_dlvl, self.current.branch)
            self._add(new_level, to_pos)
            self.current = new_level

        self.location = to_pos

    def travel_by_teleport(self, to_dlvl, to_pos):
        levels_in_current_branch = \
                [l for l in self.levels if l.branch == self.current.branch]
        maybe_level = [l for l in levels_in_current_branch if l.dlvl == to_dlvl]
        if len(maybe_level) == 1:
            # We've already been to the level and can just set it as the
            # current and be done with it.
            self.current = maybe_level[0]
        else:
            # We haven't already been to the level and need to create it, but 
            # leave it unlinked to anything as of yet.
            new_level = Level(to_dlvl, self.current.branch)
            self.current = new_level
            self.levels.add(new_level)
