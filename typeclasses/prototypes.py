"""
Prototypes classes.

Avenew uses a system of prototypes defined as objects, instead of
having prototypes defined as dictionaries.  Having prototypes as
objects in the database means it is possible to use most builder
commands to manipulate them, including the '@call' command (event
system), '@desc', enhanced '@' to edit the object and so on.

"""

from evennia import DefaultObject
from evennia.contrib.events.utils import register_events
from evennia.utils.create import create_object
from evennia.utils.search import search_tag

from typeclasses.characters import Character

@register_events
class PChar(DefaultObject):

    """PChar (character prototype).

    This prototype is used to create several characters based on a
    similar prototype.  This is most useful for NPCs (Non-Playing
    Characters).  The 'prototype' attribute on the character allows
    to identify of which prototype the character was created.
    Extensive tags are used to quickly identify the characters created
    on a PChar.

    """

    _events = Character._events

    @property
    def characters(self):
        """Return the list of characters with the PChar's key."""
        return search_tag(self.key, category="pchar")

    def at_rename(self, old_name, new_name):
        """The key (name) of the prototype is changed."""
        print "Changing the key", old_name, new_name
        for character in search_tag(old_name, category="pchar"):
            character.tags.remove(old_name, category="pchar")
            character.tags.add(new_name, category="pchar")

    def create(self, location=None):
        """Create a character on this prototype."""
        character = create_object("typeclasses.characters.Character",
                key="somebody", location=location)
        character.tags.add(self.key, category="pchar")
        character.db.prototype = self
        return character
