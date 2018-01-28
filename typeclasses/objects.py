# -*- coding: utf-8 -*-

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

from auto.types.typehandler import TypeHandler
from typeclasses.shared import AvenewObject, SharedAttributeHandler

class Object(AvenewObject, EventObject):
    """
    Default objects.
    """

    @lazy_property
    def attributes(self):
        return SharedAttributeHandler(self)

    @lazy_property
    def types(self):
        return TypeHandler(self)

    def get_numbered_name(self, count, looker, **kwargs):
        """
        Return the numbered (singular, plural) forms of this object's key. This is by default called
        by return_appearance and is used for grouping multiple same-named of this object. Note that
        this will be called on *every* member of a group even though the plural name will be only
        shown once. Also the singular display version, such as 'an apple', 'a tree' is determined
        from this method.

        Args:
            count (int): Number of objects of this type
            looker (Object): Onlooker. Not used by default.
        Kwargs:
            key (str): Optional key to pluralize, use this instead of the object's key.
        Returns:
            singular (str): The singular form to display.
            plural (str): The determined plural form of the key, including the count.
        """
        key = kwargs.get("key", self.key)
        singular = key
        plural = "{} {}".format(count, self.attributes.get("plural", "things"))
        if not self.aliases.get(plural, category="plural_key"):
            # we need to wipe any old plurals/an/a in case key changed in the interrim
            self.aliases.clear(category="plural_key")
            self.aliases.add(plural, category="plural_key")
            # save the singular form as an alias here too so we can display "an egg" and also
            # look at 'an egg'.
            self.aliases.add(singular, category="plural_key")
        return singular, plural

    def return_appearance(self, looker):
        """Return the appearance depending on types."""
        for type in self.types:
            if hasattr(type, "return_appearance"):
                return type.return_appearance(looker)
