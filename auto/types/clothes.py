# -*- coding: utf-8 -*-

"""
Clothes types.
"""

from auto.types.base import BaseType
from logic.object.sets import ObjectSet

class Clothes(BaseType):

    """
    Definition of the clothes type.

    Clothes are objects that are typically meant to be worn on one or several
    body parts (limbs).  Often, clotehes are coupled with containers to make
    clothes that can hold things in their "pocket".

    """

    name = "clothes"
    can_wear = True

    def at_type_creation(self, prototype=False):
        """Copy some attributes in prototype."""
        if prototype:
            self.db["wear_on"] = []
        else:
            prototype = self.obj.db.prototype
            type = prototype.types.get("clothes")
            self.db["wear_on"] = type.db.get("wear_on", [])
