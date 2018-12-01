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
        self.hat = create_object("typeclasses.objects.Object", key="a purple hat", location=self.room1)
        self.hat.types.add("clothes")
        self.hat.types.get("clothes").db["wear_on"] = ["head"]

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
        # Force-wear bag1 on head, getting it shouldn't work
        self.bag1.location = self.char3
        self.bag1.tags.clear(category="eq")
        self.bag1.tags.add("head", category="eq")
        self.assertFalse(self.char3.equipment.can_get(self.bag1))

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

    def test_wear(self):
        """Test to wear an object."""
        # Place the hat in char3's left hand
        self.hat.location = self.char3
        self.hat.tags.add("left_hand", category="eq")
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.hat)

        # Try to wear hat1 on char3's head
        limb = self.char3.equipment.can_wear(self.hat)
        self.assertEqual(limb, self.char3.equipment.limbs["head"])
        self.char3.equipment.wear(self.hat, limb)
        self.assertEqual(self.hat.tags.get(category="eq"), "head")

        # Remove the hat, put it into bag1, and wear it again
        self.hat.location = self.bag1
        self.hat.tags.clear(category="eq")
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        limb = self.char3.equipment.can_wear(self.hat)
        self.assertEqual(limb, self.char3.equipment.limbs["head"])
        self.char3.equipment.wear(self.hat, limb)
        self.assertTrue(self.hat.location, self.char3)
        self.assertEqual(self.hat.tags.get(category="eq"), "head")

        # if hat is not in char3, it should fail
        self.hat.location = self.bag1
        self.hat.tags.clear(category="eq")
        self.bag1.location = self.room1
        self.bag1.tags.clear(category="eq")
        limb = self.char3.equipment.can_wear(self.hat)
        self.assertIsNone(limb)

        # Trying to wear char3 should fail
        self.assertIsNone(self.char3.equipment.can_wear(self.char3))

    def test_remove(self):
        """Test to remove (stop wearing)."""
        # Force-wear the hat ro ewmocw ir
        self.hat.location = self.char3
        self.hat.tags.add("head", category="eq")
        container = self.char3.equipment.can_remove(self.hat)
        self.assertEqual(container, self.char3.equipment.limbs["left_hand"])
        self.char3.equipment.remove(self.hat, container)
        self.assertIn(self.hat, self.char3.contents)
        self.assertEqual(self.hat.tags.get(category="eq"), "left_hand")

        # Take bag1 ine one hand and try the same thing
        self.hat.tags.clear(category="eq")
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        self.hat.location = self.char3
        self.hat.tags.add("head", category="eq")
        container = self.char3.equipment.can_remove(self.hat)
        self.assertEqual(container, self.bag1)
        self.char3.equipment.remove(self.hat, container)
        self.assertIn(self.hat, self.bag1.contents)
        self.assertIsNone(self.hat.tags.get(category="eq"))

        # Try to carry bag1 and bag2 and remove the hat with a filter
        self.bag2.location = self.char3
        self.bag2.tags.add("right_hand", category="eq")
        self.hat.location = self.char3
        self.hat.tags.add("head", category="eq")
        container = self.char3.equipment.can_remove(self.hat, self.bag2)
        self.assertEqual(container, self.bag2)
        self.char3.equipment.remove(self.hat, container)
        self.assertIn(self.hat, self.bag2.contents)
        self.assertIsNone(self.hat.tags.get(category="eq"))

        # Try the same thing with a limb as filter
        self.bag2.location = self.room1
        self.bag2.tags.clear(category="eq")
        self.hat.location = self.char3
        self.hat.tags.add("head", category="eq")
        container = self.char3.equipment.can_remove(self.hat, self.char3.equipment.limbs["right_hand"])
        self.assertEqual(container, self.char3.equipment.limbs["right_hand"])
        self.char3.equipment.remove(self.hat, container)
        self.assertIn(self.hat, self.char3.contents)
        self.assertEqual(self.hat.tags.get(category="eq"), "right_hand")

    def test_hold(self):
        """Test to hold something."""
        # Pick up the hat in one hand
        self.hat.location = self.char3
        self.hat.tags.add("left_hand", category="eq")
        limbs = self.char3.equipment.can_hold(self.hat, allow_worn=True)
        limb = limbs[0] if limbs else None
        self.assertEqual(limb, self.char3.equipment.limbs["right_hand"])
        self.char3.equipment.hold(self.hat, limb)
        self.assertEqual(self.hat.tags.get(category="eq"), "right_hand")

        # Try to hold something which is in a bag
        self.hat.location = self.bag1
        self.hat.tags.clear(category="eq")
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        limbs = self.char3.equipment.can_hold(self.hat, allow_worn=True)
        limb = limbs[0] if limbs else None
        self.assertEqual(limb, self.char3.equipment.limbs["right_hand"])
        self.char3.equipment.hold(self.hat, limb)
        self.assertEqual(self.hat.tags.get(category="eq"), "right_hand")
        self.assertEqual(self.hat.location, self.char3)
