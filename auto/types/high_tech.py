"""
High-tech device types.
"""

from evennia.contrib.random_string_generator import RandomStringGenerator

from auto.types.base import BaseType

## Constants
PHONE_GENERATOR = RandomStringGenerator("phone number", r"[0-9]{3}-[0-9]{4}")

# Classes
class Phone(BaseType):

    """
    Definition of the phone type.

    A phone is an object that has a phone number, and can be reached
    through it.  It also supports several commands to phone, text,
    or do more advanced things (like accessing the network, playing,
    listening to music and so on).

    """

    name = "phone"

    def create(self):
        """
        The type has just been added.
        """
        db = self.db
        if "number" not in db:
            number = PHONE_GENERATOR.get()
            db["number"] = number
            self.obj.tags.add(number.replace("-", ""), category="phone number")
