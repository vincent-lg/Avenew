# -*- coding: utf-8 -*-

"""
Module containing the type handler.

The type handler is a handler on objects (under `obj.types`) allowing to have an object with
several types.  The specific data is stored in the object (or prototype) attributes.

"""

from collections import OrderedDict

from evennia.utils.utils import inherits_from

from auto.types.clothes import Clothes
from auto.types.container import Container
from auto.types.high_tech import Computer, Phone

## Constants
# You can change the type order here, it will be reflected in the type list of every object.
TYPES = OrderedDict()
TYPES["clothes"] = Clothes
TYPES["computer"] = Computer
TYPES["container"] = Container
TYPES["phone"] = Phone

## Classes
class TypeHandler(object):

    """
    Type handler for objects with prototypes.

    A type handler can be set on an object or a prototype.  The object
    (or prototype) tags will be used to determine the active types
    and create them.

    """

    def __init__(self, obj):
        self._obj = obj
        self._types = []
        self._find_types()

    def __repr__(self):
        return "<TypeHandler for {}>".format(self._obj)

    def __str__(self):
        names = [type(type_obj).name for type_obj in self._types]
        return ", ".join(names)

    def __iter__(self):
        return iter(self._types)

    def __contains__(self, name):
        return name in [type(type_obj).name for type_obj in self._types]

    def _find_types(self):
        """Build the list of tyupes."""
        sorted_types = list(TYPES.keys())
        current_names = [type(type_obj).name for type_obj in self._types]
        types = self._types
        for name, obj_type in TYPES.items():
            if name in current_names:
                continue

            if self._obj.tags.get(name, category="obj_type"):
                types.append(obj_type(self, self._obj))

        types.sort(key=lambda type_obj: sorted_types.index(type(type_obj).name))

    def get(self, name):
        """Return the type of this specified name or None.

        Args:
            name (str): the name of the type to find.

        Returns:
            type: the type or None if not found.

        """
        types = [obj_type for obj_type in self._types if type(obj_type).name == name]
        return types[0] if types else None

    def add(self, name, recursive=True):
        """Add a new type for this object.

        Args:
            name (str): name of the type to add.
            recursive (bool, optional): should the objects of this prototype
                    have this type added too?

        Note:
            The `recursive` keyword argument is proably to keep untouched.
            If you add a type to a prototype with objects, the same
            type is added to these objects, but the recursivity should
            stop here.

            The type shouldn't be already present in this object's
            (or prototype's) type list.

        Raises:
            KeyError: the type name couldn't be found.

        """
        if name not in TYPES:
            raise KeyError("Unknown type: {}".format(name))

        if self._obj.tags.get(name, category="obj_type") is None:
            self._obj.tags.add(name, category="obj_type")
            self._find_types()

            # If the object has a prototype, create the type consistently
            if inherits_from(self._obj, "typeclasses.prototypes.PObj"):
                new_type = self.get(name)
                new_type.at_type_creation(prototype=True)
                if recursive:
                    # This is a prototype, add the type to its objects
                    for obj in getattr(self._obj, "objs", []):
                        obj.types.add(name, recursive=False)
            elif self._obj.db.prototype:
                new_type = self.get(name)
                new_type.at_type_creation(prototype=False)

    def remove(self, name):
        """Remove a type.

        Args:
            name (str): name of the type to remove.

        Raises:
            KeyError: the type name isn't valid.

        """
        if name not in TYPES:
            raise KeyError("Unknown type: {}".format(name))

        if self._obj.tags.get(name, category="obj_type"):
            self._obj.tags.remove(name, category="obj_type")

        self._types[:] = [type_obj for type_obj in self._types if type(type_obj).name != name]

    def db(self, name):
        """
        Return a saver dict stored in the object attribute.

        This is useful in order to store independent data for a type.
        All types have a `db` property that points to a different storage
        area, but they can also call the type handler's `db` method if
        they want to share data between types.

        Args:
            name (str): name of the storage.

        Returns:
            storage (dict): the saver dict.

        """
        if not self._obj.attributes.has("_type_storage"):
            self._obj.db._type_storage = {}
        storage = self._obj.db._type_storage

        # Create the specific storage area if necessary
        if name not in storage:
            storage[name] = {}

        return storage[name]

    def has(self, name):
        """
        Return a list of types that have this attribute/method name.

        Args:
            name (str): the name of the behavior.

        Returns:
            types (list): the list of types that support this behavior name.

        Note:
            A type supports a behavior if it has a method or attribute with
            the same name.

        """
        types = []
        for type in self._types:
            if hasattr(type, name):
                types.append(type)

        return types

    def can(self, name):
        """
        Return a list of types that can handle this behavior.

        Args:
            name (str): the name of the behavior.

        Returns:
            types (list): the list of types that support this behavior name.

        Note:
            A type supports a behavior if it has a class attribute with "can_{name}".
            For instance, `obj.types.can("use")` will return
            a list with the computer type if it is present on the
            handler, since the computer type has a `can_use` class attribute.
            Note that this class attribute can be a method too.

        """
        types = []
        for type in self._types:
            if getattr(type, "can_{}".format(name), None):
                types.append(type)

        return types
