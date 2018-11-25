# -*- coding: utf-8 -*-

"""Module containing various sets to represent objects.

These sets are basically default, ordered dictionaries.  They also have some additional methods to gorup and display objects.

Available classes:
    ContainersSet: a set of containers (container as key, list of objects as values).
    ObjectSet: a list of objects.

"""

from collections import OrderedDict, defaultdict

from evennia.utils.utils import list_to_string

class OrderedDefaultDict(OrderedDict, defaultdict):

    """A defaultdict retaining key ordering like OrdereedDict."""

    def __init__(self, default_factory, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

class ContainerSet(OrderedDefaultDict):

    """A defaultdict retaining key ordering like OrdereedDict.

    This class is used to store containers when getting or dropping objects.  Like a default dictionary, it has a factory (a list).  Like an OrderedDict, it retains the order in which new keys are added.  It also has additional methods that can be useful whe storing containers:
        objects: return a flattened list of objects in all containers.

    """

    def __init__(self, *args, **kwargs):
        super(ContainerSet, self).__init__(list, *args, **kwargs)
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

    def names(self, looker):
        """Return the grouped names (singular or plural) as a list of str.

        Args:
            looker (Object): the looker.

        Returns:
            names (list of str): the list of names.

        """
        dictionary = OrderedDefaultDict(list)
        for obj in self:
            singular = obj.key
            dictionary[singular].append(obj)

        # Now create a list of names
        names = []
        for objects in dictionary.values():
            names.append(objects[0].get_numbered_name(len(objects), looker))

        return names

    def wrapped_names(self, looker):
        """
        Return a wrapped list of names.

        This method uses `list_to_string` to combine all names.

        Args:
            looker (Object): the looker.

        Returns:
            names (str): the list of names, wrapped for friendly display.

        """
        return list_to_string(self.names(looker), endsep="and")
