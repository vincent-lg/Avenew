# -*- coding: utf-8 -*-

"""
Module containing the behavior handler.

The behavior handler is a handler on characters (under `char.behaviors`)
allowing to add, remove, and trigger specific behaviors.  Call to
behaviors is generally hard-coded in the `Character` (or subsequent) class.

"""

from evennia.utils.utils import inherits_from

from auto.behaviors.driver import Driver

BEHAVIORS = {
    "driver": Driver,
}

class BehaviorHandler(object):

    """
    Behavior handler for characterss with behaviors.

    Behaviors can be set on character and character prototypes (`pchar`).
    When a character is created on a `pchar`, it copies its behaviors.

    You will use the following methods most of the time:
        add(...): add a behavior to the character.
        remove(...): remove a behavior from the character.
        get(...): get the specified behavior for this character.

    """

    def __init__(self, character):
        self._character = character
        self._behaviors = []
        self._find_behaviors()

    def __repr__(self):
        return "<BehaviorHandler for {}>".format(self._character)

    def __str__(self):
        names = [type(behavior).name for behavior in self._behaviors]
        return ", ".join(names)

    def __iter__(self):
        return iter(self._behaviors)

    def __contains__(self, name):
        return name in [type(behavior).name for behavior in self._behaviors]

    def __getitem__(self, name):
        """Return the behavior."""
        return [behavior for behavior in self._behaviors if type(behavior).name == name][0]

    def _find_behaviors(self):
        """Build the list of behaviors."""
        names = [type(behavior).name for behavior in self._behaviors]
        behaviors = self._behaviors
        for name, behavior in BEHAVIORS.items():
            if name in names:
                continue

            if self._character.tags.get(name, category="behavior"):
                behaviors.append(behavior(self, self._character))

        self._behaviors.sort(key=lambda behavior: type(behavior).name)

    def get(self, name):
        """Return the behavior of this specified name or None.

        Args:
            name (str): the name of the behavior to find.

        Returns:
            behavior: the behavior or None if not found.

        """
        behaviors = [behavior for behavior in self._behaviors if type(behavior).name == name]
        return behaviors[0] if behaviors else None

    def add(self, name, recursive=True):
        """Add a new behavior for this character.

        Args:
            name (str): name of the behavior to add.
            recursive (bool, optional): should the objects of this character prototype
                    have this behavior added too?

        Note:
            The `recursive` keyword argument is proably to keep untouched.
            If you add a behavior to a character prototype with characters, the same
            behavior is added to these characters, but the recursivity should
            stop here.

            The behavior shouldn't be already present in this character's
            (or pchar's) behavior list.

        Raises:
            KeyError: the behavior name couldn't be found.

        """
        if name not in BEHAVIORS:
            raise KeyError("Unknown behavior: {}".format(name))

        if self._character.tags.get(name, category="behavior") is None:
            self._character.tags.add(name, category="behavior")
            self._find_behaviors()

            # If the character has a prototype, create the behavior consistently
            if inherits_from(self._character, "typeclasses.prototypes.PChar"):
                new_behavior = self.get(name)
                new_behavior.at_behavior_creation(prototype=True)
                if recursive:
                    # This is a prototype, add the behavior to its characters
                    for char in getattr(self._character, "characters", []):
                        char.behaviors.add(name, recursive=False)
            elif self._character.db.prototype:
                new_behavior = self.get(name)
                new_behavior.at_behavior_creation(prototype=False)

    def remove(self, name):
        """Remove a behavior.

        Args:
            name (str): name of the behavior to remove.

        Raises:
            KeyError: the behavior name isn't valid.

        """
        if name not in BEHAVIORS:
            raise KeyError("Unknown behavior: {}".format(name))

        if self._character.tags.get(name, category="behavior"):
            self._character.tags.remove(name, category="behavior")

        self._behaviors[:] = [behavior for behavior in self._behaviors if type(behavior).name != name]

    def db(self, name):
        """
        Return a saver dict stored in the object attribute.

        This is useful in order to store independent data for a behavior.
        All behaviors have a `db` property that points to a different storage
        area, but they can also call the behavior handler's `db` method if
        they want to share data between behaviors.

        Args:
            name (str): name of the storage.

        Returns:
            storage (dict): the saver dict.

        """
        if not self._character.attributes.has("_behavior_storage"):
            self._character.db._behavior_storage = {}
        storage = self._character.db._behavior_storage

        # Create the specific storage area if necessary
        if name not in storage:
            storage[name] = {}

        return storage[name]
