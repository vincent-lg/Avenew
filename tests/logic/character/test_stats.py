# -*- coding: utf-8 -*-

"""Test for the character stats."""

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest

class TestStats(EvenniaTest):

    """Test chracter stats."""

    def setUp(self):
        super(TestStats, self).setUp()
        self.char3 = create_object("typeclasses.characters.Character", key="char3", location=self.room1)

    def test_all(self):
        """Test all the stats with general functions."""
        for name, (value, _min, _max) in self.char3.stats.defaults.items():
            stat = getattr(self.char3.stats, name)
            self.assertEqual(stat, value)
            self.assertEqual(stat.current, value)
            self.assertEqual(stat.base, value)
            self.assertEqual(stat.mod, 0)
            self.assertEqual(stat.min, _min)
            self.assertEqual(stat.max, _max)

            # Mathematical checks
            self.assertNotEqual(stat, value + 1)
            self.assertTrue(stat < value + 1)
            self.assertTrue(stat <= value)
            self.assertTrue(stat > value - 1)
            self.assertTrue(stat >= value)

            # Try to change the stat's value without being specific (should fail)
            with self.assertRaises(TypeError):
                setattr(self.char3.stats, name, value)

    def test_pvit(self):
        """Test the physical vitality/health"""
        def die(character):
            character.db.dead = True
        type(self.char3).die = die
        def live(character):
            character.db.dead = False
        type(self.char3).live = live
        stat = self.char3.stats.p_vit
        self.assertEqual(stat, 100)

        # Play with the modifier
        stat.base = 50
        stat.mod = 10
        self.assertEqual(stat, 60)
        stat.mod = 80
        self.assertEqual(stat, 100)
        stat.mod = -20
        self.assertEqual(stat, 30)
        stat.base = 100
        stat.mod = 0
        self.assertEqual(stat, 100)

        # Try to change the min value (it should fail)
        with self.assertRaises(AttributeError):
            stat.min = 5

        # Try to modify the maximum
        stat.max = 150
        stat.mod = 60
        self.assertEqual(stat, 150)
        stat.base = 120
        stat.mod = 0
        self.assertEqual(stat, 120)
        stat.max = 100
        self.assertEqual(stat.base, 100)

        # Try to see the character die
        self.char3.live()
        stat.base = 0
        self.assertTrue(self.char3.db.dead)
        stat.base = 10
        self.assertFalse(self.char3.db.dead)

        # Die with a modifier
        stat.mod = -10
        self.assertTrue(self.char3.db.dead)
        stat.mod = 0
        self.assertFalse(self.char3.db.dead)
