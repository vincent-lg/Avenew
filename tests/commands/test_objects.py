# -*- coding: utf-8 -*-

"""Test the commands dealing with objects."""

from __future__ import absolute_import, unicode_literals
from evennia.commands.default.tests import CommandTest
from evennia.utils.create import create_object

from commands.objects import CmdDrop, CmdEmpty, CmdGet, CmdHold, CmdRemove, CmdWear

class TestObjects(CommandTest):

    """Test the account/character login menu."""

    def setUp(self):
        super(TestObjects, self).setUp()
        self.room3 = create_object("typeclasses.rooms.Room", key="room3")
        self.char3 = create_object("typeclasses.characters.Character", key="char3", location=self.room3)
        self.apple = create_object("typeclasses.prototypes.PObj", key="apple")
        self.apple.db.plural = "apples"
        self.apple1 = self.apple.create(location=self.room3, key="an apple")
        self.apple2 = self.apple.create(location=self.room3, key="an apple")
        self.apple3 = self.apple.create(location=self.room3, key="an apple")
        self.bag1 = create_object("typeclasses.objects.Object", key="a black bag", location=self.room3)
        self.bag1.types.add("container")
        self.bag2 = create_object("typeclasses.objects.Object", key="a pink purse", location=self.room3)
        self.bag2.types.add("container")
        self.hat = create_object("typeclasses.objects.Object", key="a purple hat", location=self.room3)
        self.hat.types.add("clothes")
        self.hat.types.get("clothes").db["wear_on"] = ["head"]
        self.sock = create_object("typeclasses.objects.Object", key="an orange sock", location=self.room3)
        self.sock.types.add("clothes")
        self.sock.types.get("clothes").db["wear_on"] = ["stockings"]
        self.msgs = []

    def call(self, *args, **kwargs):
        """Call and store the message for later references."""
        self.msgs.append(super(TestObjects, self).call(*args, **kwargs))

    def test_get(self):
        self.call(CmdGet(), "apple", caller=self.char3)
        self.assertEqual(1, 1)

        # The search should have sorted objects in order, so the apple is apple1
        self.assertEqual(self.apple1.location, self.char3)
        self.assertEqual(self.apple1.tags.get(category="eq"), "left_hand")

        # Drop apple1 again and pick up two apples
        self.apple1.tags.clear(category="eq")
        self.apple1.location = self.room3
        # The picked up apples should be apple2 and apple3
        self.call(CmdGet(), "2 apples", caller=self.char3)
        self.assertEqual(self.apple1.location, self.room3)
        self.assertEqual(self.apple2.location, self.char3)
        self.assertEqual(self.apple3.location, self.char3)
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.apple2)
        self.assertEqual(self.char3.equipment.first_level["right_hand"], self.apple3)

        # Trying to get 3 apples should do the same thing
        for apple in [self.apple1, self.apple2, self.apple3]:
            apple.location = self.room3
            apple.tags.clear(category="eq")
        self.call(CmdGet(), "3 apples", caller=self.char3)
        self.assertEqual(self.apple1.location, self.char3)
        self.assertEqual(self.apple2.location, self.char3)
        self.assertEqual(self.apple3.location, self.room3)
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.apple1)
        self.assertEqual(self.char3.equipment.first_level["right_hand"], self.apple2)

        # Trying to get * apples should do the same thing
        for apple in [self.apple1, self.apple2, self.apple3]:
            apple.location = self.room3
            apple.tags.clear(category="eq")
        self.call(CmdGet(), "* apples", caller=self.char3)
        self.assertEqual(self.apple1.location, self.char3)
        self.assertEqual(self.apple2.location, self.char3)
        self.assertEqual(self.apple3.location, self.room3)
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.apple1)
        self.assertEqual(self.char3.equipment.first_level["right_hand"], self.apple2)

        # When holding a bag, getting the apples should work
        for apple in [self.apple1, self.apple2, self.apple3]:
            apple.location = self.room3
            apple.tags.clear(category="eq")
        self.call(CmdGet(), "black bag", caller=self.char3)
        self.call(CmdGet(), "* apples", caller=self.char3)
        self.assertEqual(self.apple1.location, self.bag1)
        self.assertEqual(self.apple2.location, self.bag1)
        self.assertEqual(self.apple3.location, self.bag1)
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.bag1)
        self.assertIsNone(self.char3.equipment.first_level["right_hand"])

        # Try to get an apple from the bag
        self.bag1.location = self.room3
        self.bag1.tags.clear(category="eq")
        self.call(CmdGet(), "apple from black bag", caller=self.char3)
        self.assertEqual(self.apple1.location, self.char3)
        self.assertEqual(self.char3.equipment.first_level["left_hand"], self.apple1)

        # Try to get from/into
        for apple in [self.apple1, self.apple2, self.apple3]:
            apple.location = self.bag1
            apple.tags.clear(category="eq")
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        self.bag2.location = self.char3
        self.bag2.tags.add("right_hand", category="eq")
        self.call(CmdGet(), "* apples from black bag into pink purse", caller=self.char3)
        self.assertEqual(self.apple1.location, self.bag2)
        self.assertEqual(self.apple2.location, self.bag2)
        self.assertEqual(self.apple3.location, self.bag2)

    def test_drop(self):
        """Test the drop command."""
        # Try to drop a held apple
        self.apple1.location = self.char3
        self.apple1.tags.add("left_hand", category="eq")
        self.call(CmdDrop(), "apple", caller=self.char3)
        self.assertEqual(self.apple1.location, self.room3)
        self.assertFalse(self.apple1.tags.get(category="eq"))

        # Same test, but with two apples
        self.apple1.location = self.char3
        self.apple1.tags.add("left_hand", category="eq")
        self.apple2.location = self.char3
        self.apple2.tags.add("right_hand", category="eq")
        self.call(CmdDrop(), "2 apples", caller=self.char3)
        self.assertEqual(self.apple1.location, self.room3)
        self.assertFalse(self.apple1.tags.get(category="eq"))
        self.assertEqual(self.apple2.location, self.room3)
        self.assertFalse(self.apple2.tags.get(category="eq"))

        # Try to drop all apples in a bag
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        for apple in (self.apple1, self.apple2, self.apple3):
            apple.tags.clear(category="eq")
            apple.location = self.bag1
        self.call(CmdDrop(), "* apples", caller=self.char3)
        self.assertEqual(self.apple1.location, self.room3)
        self.assertEqual(self.apple2.location, self.room3)
        self.assertEqual(self.apple3.location, self.room3)

        # Try to drop the apples into bag2
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        self.bag2.location = self.char3
        self.bag2.tags.add("right_hand", category="eq")
        for apple in (self.apple1, self.apple2, self.apple3):
            apple.tags.clear(category="eq")
            apple.location = self.bag1
        self.call(CmdDrop(), "* apples into purse", caller=self.char3)
        self.assertEqual(self.apple1.location, self.bag2)
        self.assertEqual(self.apple2.location, self.bag2)
        self.assertEqual(self.apple3.location, self.bag2)

        # Try to drop 2 apples from bag2 into bag1
        self.call(CmdDrop(), "2 apples into black bag from purse", caller=self.char3)
        self.assertEqual(self.apple1.location, self.bag1)
        self.assertEqual(self.apple2.location, self.bag1)
        self.assertEqual(self.apple3.location, self.bag2)

    def test_wear(self):
        """Test the wear command."""
        # Wear the hat when it's carried in one's hand
        self.hat.location = self.char3
        self.hat.tags.add("left_hand", category="eq")
        self.call(CmdWear(), "purple hat", caller=self.char3)
        self.assertEqual(self.hat.location, self.char3)
        self.assertEqual(self.hat.tags.get(category="eq"), "head")

        # Same thing, but put the hat in a bag
        self.bag1.location = self.char3
        self.bag1.tags.add("left_hand", category="eq")
        self.hat.location = self.bag1
        self.hat.tags.clear(category="eq")
        self.call(CmdWear(), "purple hat", caller=self.char3)
        self.assertEqual(self.hat.location, self.char3)
        self.assertEqual(self.hat.tags.get(category="eq"), "head")

        # Try to wear the sock on the right foot
        self.sock.location = self.bag1
        self.call(CmdWear(), "sock, right foot", caller=self.char3)
        self.assertEqual(self.sock.location, self.char3)
        self.assertEqual(self.sock.tags.get(category="eq"), "right_stocking")
