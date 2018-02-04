# -*- coding: utf-8 -*-

"""
Container types.
"""

from auto.types.base import BaseType

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
            self.db["max_mass"] = 3
        else:
            prototype = self.obj.db.prototype
            type = prototype.types.get("container")
            self.db["max_mass"] = type.db.get("max_mass", 3)
