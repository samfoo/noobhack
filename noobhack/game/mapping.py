class Level(object):
    def __init__(self, dlvl, branch="main"):
        self.dlvl = dlvl
        self.branch = branch 
        self.stairs = {}

    def change_branch_to(self, branch):
        self.branch = branch
        for child in [c for c in self.stairs.values() if c.dlvl > self.dlvl]:
            child.change_branch_to(branch)

    def add_stairs(self, level, position):
        self.stairs[position] = level

    def stairs_at(self, pos):
        return self.stairs.get(pos, None)

    def has_stairs_at(self, pos):
        return self.stairs_at(pos) != None

    def __repr__(self):
        return repr([self.dlvl, self.branch, self.stairs])

class Map:
    def __init__(self, level, x, y):
        self.current = level 
        self.levels = set([self.current])
        self.location = (x, y) 

    def move(self, x, y):
        self.location = (x, y)

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
            existing_level = self.level_at(self.current.branch, to_dlvl)
            self.current.add_stairs(existing_level, self.location)
            existing_level.add_stairs(self.current, to_pos)
            self.current = existing_level
        else:
            # If the current level doesn't have stairs at our current position,
            # create a new level and attach them.
            new_level = Level(to_dlvl, self.current.branch)
            self.current.add_stairs(new_level, self.location)
            new_level.add_stairs(self.current, to_pos)
            self.current = new_level
            self.levels.add(new_level)

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
