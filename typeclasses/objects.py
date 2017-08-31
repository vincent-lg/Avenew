"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""

from evennia.contrib.ingame_python.typeclasses import EventObject
from evennia.utils.utils import lazy_property

from typeclasses.shared import SharedAttributeHandler

class Object(EventObject):
    """
    Default objects.
    """

    @lazy_property
    def attributes(self):
        return SharedAttributeHandler(self)
