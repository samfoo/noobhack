import unittest

from game.dungeon import Dungeon, Level, Map
from game.events import dispatcher

class MapTest(unittest.TestCase):
    def test_init(self):
        m = Map()
        self.assertEqual(1, len(m.levels))
        self.assertNotEqual(None, m.current) 
        self.assertEqual(0, len(m.links))

    def test_cannot_add_links_to_levels_that_dont_exist(self):
        m = Map()
        self.assertRaises(ValueError, m._link, 1, (5, 5), 2, (5, 5))

    def test_can_add_link_between_existing_levels(self):
        m = Map()
        first = m.levels[1][0]
        first.downs.add((5,5))
        second = Level(2)
        second.ups.add((10,10))
        m._add(2, second)
        m._link(1, (5, 5), 2, (10, 10))
        self.assertEqual(1, len(m.links))
        self.assertEqual(1, len(m.links[(1, 2)]))

        self.assertTrue(((5, 5), (10, 10)) in m.links[(1, 2)])

    def test_move_down_to_level_that_doesnt_exist_yet(self):
        m = Map()
        m.move(1, 2, (5, 5), (10, 10))
        second = Level(2)
        second.ups.add((10, 10))
        self.assertEqual(second, m.levels[2][0])

    def test_move_down_then_back_up(self):
        m = Map()
        m.current.features.add("samfoo")
        m.move(1, 2, (5, 5), (10, 10))
        m.move(2, 1, (10, 10), (5, 5))
        self.assertEqual(2, len(m.levels))
        self.assertEqual(1, len(m.links))
        self.assertEqual(m.levels[1][0], m.current)
        self.assertTrue("samfoo" in m.current.features)

    def test_move_down_then_back_up_then_down_a_different_link(self):
        m = Map()
        m.move(1, 2, (5, 5), (10, 10))
        m.move(2, 1, (10, 10), (5, 5))
        m.move(1, 2, (6, 6), (7, 7))

        self.assertEqual(2, len(m.levels))
        self.assertEqual(2, len(m.levels[2]))
        self.assertEqual(1, len(m.links))
        self.assertEqual(2, len(m.links[(1,2)]))
        self.assertEqual(m.levels[2][1], m.current)

        m.move(2, 1, (7,7), (6,6))
        self.assertEqual(2, len(m.levels))
        self.assertEqual(2, len(m.levels[2]))
        self.assertEqual(1, len(m.links))
        self.assertEqual(2, len(m.links[(1,2)]))
        self.assertEqual(m.levels[1][0], m.current)

    def test_moving_up_to_a_branched_level(self):
        m = Map()
        first = m.current
        first.features.add("first")
        m.move(1, 2, (1, 1), (2, 2))
        second_a = m.current
        second_a.features.add("second a")
        m.move(2, 3, (3, 3), (4, 4)) 
        third_a = m.current
        third_a.features.add("third a")
        m.move(3, 2, (4, 4), (3, 3))
        m.move(2, 1, (2, 2), (1, 1))
        m.move(1, 2, (5, 5), (10, 10))
        second_b = m.current
        second_b.features.add("second b")
        m.move(2, 1, (10, 10), (5, 5))

        self.assertEqual(first, m.current)
        self.assertEqual(3, len(m.levels))
        self.assertEqual(2, len(m.links))
        self.assertEqual(2, len(m.links[(1,2)]))
        self.assertEqual(1, len(m.links[(2,3)]))

    def test_teleport_down(self):
        m = Map()
        first = m.current
        m.teleport(1, 3)

        self.assertEqual(2, len(m.levels))
        self.assertEqual(0, len(m.links))
        self.assertNotEqual(first, m.current)

    def test_teleport_down_then_walk_back_up(self):
        m = Map()
        first = m.current
        m.teleport(1, 3)

        m.move(3, 2, (3, 3), (2, 2))
        m.move(2, 1, (5, 5), (10, 10))

        self.assertEqual(3, len(m.levels))
        self.assertEqual(1, len(m.levels[1]))
        self.assertEqual(2, len(m.links))
        self.assertEqual(1, len(m.links[(1,2)]))
        self.assertEqual(1, len(m.links[(2,3)]))

    def test_teleport_down_then_walk_back_up_different_branch(self):
        m = Map()
        m.move(1, 2, (1, 1), (2, 2))
        m.current.branch = "mines"
        m.move(2, 1, (2, 2), (1, 1))
        self.assertEqual("main", m.current.branch)
        m.move(1, 2, (5, 5), (6, 6))
        where_i_should_end_up = m.current
        m.teleport(2, 3)
        m.move(3, 2, (8, 8), (9, 9))
        self.assertEquals(where_i_should_end_up, m.current)

if __name__ == "__main__":
    unittest.main()
