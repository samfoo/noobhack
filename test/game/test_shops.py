import unittest 

from noobhack.game.shops import *

class SellIdentifyTest(unittest.TestCase):
    def test_sucker_penalty(self):
        self.assertEqual(
            set([("orcish dagger", 1, 12, "crude dagger")]),
            sell_identify("crude dagger", 1, True)
        )

    def test_appearance_identify(self):
        self.assertEqual(
            set([("orcish dagger", 2, 12, "crude dagger")]),
            sell_identify("crude dagger", 2)
        )

    def test_random_markdown(self):
        self.assertEqual(
            set([("death", 125, 5, None), ("wishing", 125, 5, None)]),
            sell_identify("wand", 125)
        )

class BuyIdentifyTest(unittest.TestCase):
    def test_sucker_penalty(self):
        self.assertEqual(
            set([("orcish dagger", 6, 12, "crude dagger")]),
            buy_identify(11, "crude dagger", 6, True)
        )

    def test_appearance_identify(self):
        self.assertEqual(
            set([("orcish dagger", 4, 12, "crude dagger")]),
            buy_identify(11, "crude dagger", 4)
        )

    def test_appearch_id_with_random_markup(self):
        self.assertEqual(
            set([("orcish dagger", 5, 12, "crude dagger")]),
            buy_identify(11, "crude dagger", 5)
        )

    def test_random_markup(self):
        self.assertEqual(
            set([("death", 666, 5, None), ("wishing", 666, 5, None)]),
            buy_identify(11, "wand", 666)
        )

    def test_charisma_modifier(self):
        self.assertEqual(
            set([("death", 1000, 5, None), ("wishing", 1000, 5, None)]),
            buy_identify(5, "wand", 1000)
        )

        self.assertEqual(
            set([("death", 750, 5, None), ("wishing", 750, 5, None)]),
            buy_identify(6, "wand", 750)
        )

        self.assertEqual(
            set([("death", 666, 5, None), ("wishing", 666, 5, None)]),
            buy_identify(8, "wand", 666)
        )

        self.assertEqual(
            set([("death", 500, 5, None), ("wishing", 500, 5, None)]),
            buy_identify(11, "wand", 500)
        )

        self.assertEqual(
            set([("death", 375, 5, None), ("wishing", 375, 5, None)]),
            buy_identify(16, "wand", 375)
        )

        self.assertEqual(
            set([("death", 334, 5, None), ("wishing", 334, 5, None)]),
            buy_identify(18, "wand", 334)
        )

        self.assertEqual(
            set([("death", 250, 5, None), ("wishing", 250, 5, None)]),
            buy_identify(19, "wand", 250)
        )

if __name__ == "__main__":
    unittest.main()
