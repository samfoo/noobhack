def shop_entered_callback(dungeon, input, matches):
    type_of_shop = matches.groups()[0]
    dungeon.add_shop(type_of_shop)

def death_callback(dungeon, input, matches):
    dungeon.delete()

def level_changed_callback(dungeon, input, matches):
    level = int(matches.groups()[0])
    dungeon.set_current_level(level)

