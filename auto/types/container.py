# -*- coding: utf-8 -*-

"""
Container types.
"""

from auto.types.base import BaseType
from logic.object.sets import ObjectSet

class Container(BaseType):

    """
    Definition of the container type.

    A container is an object that can contain others.  It can be a pair
    of jeans, a bag, a chest, a furniture, and more.

    """

    name = "container"

    def at_type_creation(self, prototype=False):
        """Copy some attributes in prototype."""
        if prototype:
            self.db["mass_max"] = 3
        else:
            prototype = self.obj.db.prototype
            type = prototype.types.get("container")
            self.db["mass_max"] = type.db.get("mass_max", 3)

    def can_get(self, objects):
        """Return whether this container can get the specified objects.

        Args:
            objects (list of Object): list of objects to put in this container.

        """
        return True
        mass = self.mass
        mass_max = self.db.get("mass_max")
        if mass_max is None:
            raise ValueError("{} has no mass_max".format(self.obj))

        return True

    def return_appearance(self, looker):
        """Return the appearance of the phone."""
        if self.obj.contents:
            objects = ObjectSet()
            visible = [o for o in self.obj.contents if o.access(looker, "view")]
            for obj in visible:
                objects.append(obj)
            if objects:
                return "\n\nÀ l'intérieur, vous voyez :\n  " + "\n  ".join([name for name in objects.names(looker)])

        return "\n\nThere is nothing inside."
