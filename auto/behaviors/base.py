# -*- coding: utf-8 -*-

"""Module containing the abstract Behavior class."""

from evennia.utils.utils import lazy_property

class Behavior(object):

    """Abstract class for behaviors."""

    name = "unknown"

    def __init__(self, handler, character):
        self.handler = handler
        self.character = character

    @lazy_property
    def db(self):
        """Return the storage (saver dict) for this behavior."""
        return self.handler.db(type(self).name)

    def at_behavior_creation(self, prototype=False):
        """
        The behavior has just been added to a character or pchar.

        Override this method to create custom behavior dependent on
        the type itself.

        """
        pass
