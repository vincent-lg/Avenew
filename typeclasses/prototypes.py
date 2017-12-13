# -*- coding: utf-8 -*-

"""
Prototypes classes.

Avenew uses a system of prototypes defined as objects, instead of
having prototypes defined as dictionaries.  Having prototypes as
objects in the database means it is possible to use most builder
commands to manipulate them, including the '@call' command (event
system), '@desc', enhanced '@' to edit the object and so on.

"""

from evennia import DefaultObject
from evennia.contrib.ingame_python.utils import register_events
from evennia.utils.create import create_object
from evennia.utils.search import search_tag
from evennia.utils.utils import lazy_property

from auto.types.typehandler import TypeHandler
from typeclasses.characters import Character
from typeclasses.objects import Object
from typeclasses.rooms import Room

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

    _events = Character._events.copy()
    _events.update(Character.__bases__[0]._events)

    @property
    def characters(self):
        """Return the list of characters with the PChar's key."""
        return search_tag(self.key, category="pchar")

    def at_rename(self, old_name, new_name):
        """The key (name) of the prototype is changed."""
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


@register_events
class PObj(DefaultObject):

    """PObj (object prototype).

    This prototype is used to create several objects based on a
    similar prototype.  The 'prototype' attribute on the object allows
    to identify of which prototype the object was created.
    Extensive tags are used to quickly identify the characters created
    on a PChar.

    """

    _events = Object._events.copy()
    _events.update(Object.__bases__[0]._events)

    @lazy_property
    def types(self):
        return TypeHandler(self)

    @property
    def objs(self):
        """Return the list of objects with the PObj's key."""
        return search_tag(self.key, category="pobj")

    def at_rename(self, old_name, new_name):
        """The key (name) of the prototype has changed."""
        for obj in search_tag(old_name, category="pobj"):
            obj.tags.remove(old_name, category="pobj")
            obj.tags.add(new_name, category="pobj")

    def create(self, location=None, key=None):
        """Create an object on this prototype."""
        key = key or "something"
        obj = create_object("typeclasses.objects.Object",
                key=key, location=location)
        obj.tags.add(self.key, category="pobj")
        obj.db.prototype = self

        # Add the types
        for type_obj in self.types:
            name = type(type_obj).name
            obj.types.add(name)

        return obj


@register_events
class PRoom(DefaultObject):

    """PRoom (room prototype).

    This prototype is used to create several rooms based on a
    similar prototype.  The 'prototype' attribute on the room allows
    to identify of which prototype the room was created.
    Extensive tags are used to quickly identify the rooms created
    on a PRoom.

    Attributes are shared across rooms of the same prototype.  They
    can override specific attributes, but if they don't, they will
    just have the same as their prototype.  It also applies to
    descriptions (since room descriptions are stored in an attribute).

    """

    _events = Room._events.copy()
    _events.update(Room.__bases__[0]._events)

    @property
    def rooms(self):
        """Return the list of rooms of this prototype."""
        return search_tag(self.key, category="proom")

    def at_rename(self, old_name, new_name):
        """The key (name) of the prototype has changed."""
        for room in search_tag(old_name, category="proom"):
            room.tags.remove(old_name, category="proom")
            room.tags.add(new_name, category="proom")

    def create(self, key=None):
        """Create a room on this prototype."""
        key = key or self.key
        room = create_object("typeclasses.rooms.Room", key=key)
        room.tags.add(self.key, category="proom")
        room.db.prototype = self
        return room
