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
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.bag1)
        self.assertEqual(self.bag1.tags.get(category="eq"), "left_hand")

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
        # bag2 can go in bag1, but bag1 can't go in bag2 afterward
        can = self.char3.equipment.can_get(self.bag2)
        self.assertTrue(can)
        self.char3.equipment.get(can)
        self.assertFalse(self.char3.equipment.can_get(self.bag1, filter=[self.bag2]))

    def test_drop(self):
        """Try to drop objects."""
        # Move bag1 into char3, apple1 and apple2 into bag1
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        self.apple1.location = self.bag1
        self.apple2.location = self.bag1
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.bag1)

        # Try to drop apple2 on the floor
        can = self.char3.equipment.can_drop(self.apple2, filter=[])
        self.assertTrue(can)
        self.assertIn(self.room1, can)
        self.char3.equipment.drop(can)
        self.assertEqual(self.apple2.location, self.room1)
        self.assertNotIn(self.apple2, self.bag1.contents)

        # Get apple2 back and try to drop bag1
        self.apple2.location = self.bag1
        can = self.char3.equipment.can_drop(self.bag1, filter=[])
        self.assertTrue(can)
        self.assertIn(self.room1, can)
        self.char3.equipment.drop(can)
        self.assertEqual(self.bag1.location, self.room1)
        self.assertNotIn(self.bag1, self.char3.contents)
        self.assertEqual(self.apple1.location, self.bag1)
        self.assertEqual(self.apple2.location, self.bag1)
        self.assertFalse(self.bag1.tags.get(category="eq"))

        # Get bag1 back, and try to drop into bag2
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        can = self.char3.equipment.can_drop(self.bag1, filter=[self.bag2])
        self.assertTrue(can)
        self.assertIn(self.bag2, can)
        self.char3.equipment.drop(can)
        self.assertEqual(self.bag1.location, self.bag2)
        self.assertNotIn(self.bag1, self.char3.contents)
        self.assertEqual(self.apple1.location, self.bag1)
        self.assertEqual(self.apple2.location, self.bag1)
        self.assertFalse(self.bag1.tags.get(category="eq"))

        # Get bag1 back. Try to drop bag2 into bag1, it should fail
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        can = self.char3.equipment.can_drop(self.bag2, filter=[self.bag1])
        self.assertFalse(can)

        # Cases that should fail
        # bag1 can't be dropped into bag1
        self.assertFalse(self.char3.equipment.can_drop(self.bag1, filter=[self.bag1]))
        # char3 can't drop char3
        self.assertFalse(self.char3.equipment.can_drop(self.char3))
        # Force-wear bag1 on head, dropping it shouldn't work
        self.bag1.location = self.char3
        self.bag1.tags.clear(category="eq")
        self.bag1.tags.add("head", category="eq")
        self.assertFalse(self.char3.equipment.can_drop(self.bag1))
