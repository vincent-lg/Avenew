# -*- coding: utf-8 -*-

"""Module containing the representation of the object classes."""

from evennia.utils.evtable import EvTable

from representations.base import BaseRepr

FORM = """
.-------------------------------------------------------------------------.
| Name: xxxxxxxxxxxx1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
| Plural: xxxxxxxxxxxx2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
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

class ObjectRepr(BaseRepr):

    """The object representation."""

    fields = {
            "key": str,
            "plural": str,
            "mass": float,
    }
    to_display = ["name", "plural", "desc", "mass"]
    form = FORM

    def get_desc(self, caller):
        return self.obj.db.desc

    def get_mass(self, caller):
        return self.obj.db.mass
