from noobhack.game.dungeon import Dungeon, Level, Map, looks_like_sokoban, looks_like_mines

def test_sokoban_a():
    display = [
        "-------- ------",
        "|<|@..=---....|",
        "|^|-.00....0..|",
        "|^||..00|.0.0.|",
        "|^||....|.....|",
        "|^|------0----|",
        "|^|    |......|",
        "|^------......|",
        "|..^^^^0000...|",
        "|..-----......|",
        "----   --------",
    ]

    assert looks_like_sokoban(display)

def test_sokoban_b():
    display = [
        "------  ----- ",
        "|....|  |...| ",
        "|.0..----.0.| ",
        "|.0......0..| ",
        "|..--->---0.| ",
        "|---------.---",
        "|..^^^<|.....|",
        "|..----|0....|",
        "--^|   |.0...|",
        " |^-----.0...|",
        " |..^^^^0.0..|",
        " |??----------",
        " ---- ",
    ]

    assert looks_like_sokoban(display)

def test_not_mines_even_with_headstone():
    display = [
        "-----",
        "|...-",
        "|.|.|",
        "|^..|",
        "|.[<|",
        "---.-",
    ]

    assert not looks_like_mines(display)

def test_not_mines_even_with_strip():
    display = [
        "--        ", 
        "    ----  ",
    ]
    assert not looks_like_mines(display)

