"""
Module containing the type handler.

The type handler is a handler on objects (under `obj.types`) allowing to have an object with
several types.  The specific data is stored in the object (or prototype) attributes.

"""

from collections import OrderedDict

from auto.types.high_tech import Phone

## Constants
TYPES = OrderedDict()
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
        return "Types: {}".format(names)

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
        """Return the type of this name or None."""
        types = [obj_type for obj_type in self._types if type(obj_type).name == name]
        return types[0] if types else None

    def add(self, name):
        """Add a new type for this object."""
        if name not in TYPES:
            raise KeyError("Unknown type: {}".format(name))

        if self._obj.tags.get(name, category="obj_type") is None:
            self._obj.tags.add(name, category="obj_type")
            self._find_types()

            # If the object has a prototype, create the type consistently
            if self._obj.db.prototype:
                new_type = self.get(name)
                new_type.create()

    def remove(self, name):
        """Remove a type."""
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
