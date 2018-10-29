# -*- coding: utf-8 -*-

"""Module containing various sets to represent objects.

These sets are basically default, ordered dictionaries.  They also have some additional methods to gorup and display objects.

Available classes:
    ContainersSet: a set of containers (container as key, list of objects as values).
    ObjectSet: a list of objects.

"""

from collections import OrderedDict, defaultdict


class ContainerSet(OrderedDict, defaultdict):

    """A defaultdict retaining key ordering like OrdereedDict.

    This class is used to store containers when getting or dropping objects.  Like a default dictionary, it has a factory (a list).  Like an OrderedDict, it retains the order in which new keys are added.  It also has additional methods that can be useful whe storing containers:
        objects: return a flattened list of objects in all containers.

    """

    def __init__(self, *args, **kwargs):
        super(ContainerSet, self).__init__(*args, **kwargs)
        self.default_factory = list
        self._remaining = ObjectSet()

    @property
    def remaining(self):
        """Return the remaining objects."""
        return self._remaining

    @remaining.setter
    def remaining(self, new_list):
        """Set a new list, force it to be an ObjectSet."""
        self._remaining[:] = new_list

    def objects(self):
        """Return the flattened list of objects."""
        return ObjectSet(obj for objects in self.values() for obj in objects)


class ObjectSet(list):

    """A list to represent a list of objects, with additional methods."""

    pass
