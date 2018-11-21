# -*- coding: utf-8 -*-

"""Test for the character equipment."""

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest

class TestEquipment(EvenniaTest):

    """Test chracter equipment, inclding object manipulation."""

    def setUp(self):
        super(TestEquipment, self).setUp()
        self.char3 = create_object("typeclasses.characters.Character", key="char3", location=self.room1)
        self.apple1 = create_object("typeclasses.objects.Object", key="an apple 1", location=self.room1)
        self.apple2 = create_object("typeclasses.objects.Object", key="an apple 2", location=self.room1)
        self.apple3 = create_object("typeclasses.objects.Object", key="an apple 3", location=self.room1)
        self.bag1 = create_object("typeclasses.objects.Object", key="a black bag", location=self.room1)
        self.bag1.types.add("container")
        self.bag2 = create_object("typeclasses.objects.Object", key="a pink purse", location=self.room1)
        self.bag2.types.add("container")

    def test_all(self):
        """Test all the stats with general functions."""
        # By default, char3 has a HUMAN list of limbs.
        limbs = self.char3.equipment.limbs

        # By default, the number of equiped objects should be 0
        self.assertEqual(0, len(
                [(l, o) for l, o in self.char3.equipment.first_level.items() if o is not None]))
        self.assertEqual(len(limbs), len(
                [(l, o) for l, o in self.char3.equipment.first_level.items() if o is None]))

        # A human character should have two free hands
        self.assertEqual(2, self.char3.equipment.hm_can_hold())

    def test_get(self):
        """Try to get several objects."""
        can = self.char3.equipment.can_get(self.apple1)
        self.assertEqual(1, len(can))
        self.assertIn(self.apple1, can.objects())
        self.assertNotIn(self.apple2, can.objects())
        self.assertNotIn(self.apple3, can.objects())
        self.assertEqual(can.remaining, [])

        # Try to get two apples (should be possible)
        can = self.char3.equipment.can_get([self.apple1, self.apple2])
        self.assertEqual(2, len(can))
        self.assertIn(self.apple1, can.objects())
        self.assertIn(self.apple2, can.objects())
        self.assertNotIn(self.apple3, can.objects())
        self.assertEqual(can.remaining, [])

        # Getting three apples should give the same result as getting two
        # (the third apple is ignored)
        can = self.char3.equipment.can_get([self.apple1, self.apple2, self.apple3])
        self.assertEqual(2, len(can))
        self.assertIn(self.apple1, can.objects())
        self.assertIn(self.apple2, can.objects())
        self.assertNotIn(self.apple3, can.objects())
        # Except can.remaining should contain apple3
        self.assertEqual(1, len(can.remaining))
        self.assertIn(self.apple3, can.remaining)

        # Now pick up the bag
        can = self.char3.equipment.can_get([self.bag1])
        self.char3.equipment.get(can)
        self.assertIn(self.bag1, self.char3.equipment.all())

        # If we try to pick up an apple now, it should go in the bag
        can = self.char3.equipment.can_get([self.apple1, self.apple2])
        self.char3.equipment.get(can)
        self.assertIn(self.bag1, self.char3.equipment.all())
        self.assertIn(self.apple1, self.char3.equipment.all())
        self.assertIn(self.apple1, self.bag1.contents)
        self.assertIn(self.apple2, self.char3.equipment.all())
        self.assertIn(self.apple2, self.bag1.contents)

        # Picking up some objects shouldn't be allowed
        # bag1 is already held
        self.assertFalse(self.char3.equipment.can_get(self.bag1))
        # apple3 is now locked against getting
        self.apple3.locks.add("get:false()")
        self.assertTrue(self.char3.equipment.can_get(self.apple1))
        self.assertFalse(self.char3.equipment.can_get(self.apple3))
        # picking oneself up should be forbidden (infinite loop)
        self.assertFalse(self.char3.equipment.can_get(self.char3, check_lock=False))
