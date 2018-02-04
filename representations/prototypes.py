# -*- coding: utf-8 -*-

"""Module containing the representation of the prototype classes."""

from evennia.utils.evtable import EvTable

from representations.base import BaseRepr

FORMOBJ = """
.-------------------------------------------------------------------------.
| Key: xxxxxxxxxxxx1xxxxxxxxxxxxxx  Types: xx2xxxxxxxxxxxxxxxxxxxxxxxxxxx |
|                                                                         |
| Desc: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx3xxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|                                                                         |
| Mass: xx4xxxx KG                                                        |
|                                                                         |
.-------------------------------------------------------------------------.
"""

class PObjRepr(BaseRepr):

    """The object prototype representation."""

    fields = {
            "key": str,
            "mass": float,
    }
    to_display = ["name", "types", "desc", "mass"]
    form = FORMOBJ

    def get_desc(self, caller):
        return self.obj.db.desc

    def get_mass(self, caller):
        return self.obj.db.mass
