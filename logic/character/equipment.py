# -*- coding: utf-8 -*-

"""Module containing the EquipmentHandler for characters.

The EquipmentHandler centralizes operations on limbs and container objects.
Its main method are:
    character.equipment.can_get(object_or_objects)
    character.equipment.get(objects_and_containers)
    character.equipment.can_drop(object_or_objects, location)
    character.equipment.drop(object_and_containers, location)

Most methods can receive either a single object or a list of objects.

"""

from Queue import Queue

from evennia.utils.utils import inherits_from

from logic.character.limbs import Limb
from logic.character import limbs as LIMBS
from logic.object.sets import ContainerSet


class EquipmentHandler(object):

    """Equipment handler for characters.

    This handler supports equipping, getting, dropping, removing objects.
    It includes a set of easy-to-use methods to handle containers.

    """

    def __init__(self, character):
        self.character = character

    @property
    def limbs(self):
        """Return the list of limbs."""
        limbs = self.character.attributes.get("custom_limbs")
        if limbs is None:
            # Assume that `character.db.limbs` contain the name of the list.
            name = self.character.attributes.get("limbs", "HUMAN")
            if not name.isupper():
                raise ValueError("the character {!r} has an incorrect name of limbs: {!r}".format(self.character, name))
            if not hasattr(LIMBS, name):
                raise ValueError("the character {!r} has a name of limbs which can't be found in the limbs module: {!r}".format(self.character, name))

            limbs = getattr(LIMBS, name)

        # Check that the list of limbs is a list of Limb objects
        if not isinstance(limbs, list) or not all([isinstance(limb, Limb) for limb in limbs]):
            raise ValueError("the character {!r} has an incorrect list of limbs".format(self.character))

        return limbs

    @property
    def first_level(self):
        """Return the first-level of equipment for this character.

        The search will be performed in the character's content.  Depending
        on the character's list of limbs, limbs will be attributed with
        object or None.  If an object doesn't match a limb, it will be
        disregarded.

        Returns:
            limbs (list of (Limb, obj or None) tuples): a list containing
                    tuples, each tuple having the Limb object as first
                    argument, and the equiped object if any (or None)
                    corresponding to this limb as second argument.

        """
        limbs = self.limbs
        first_level = []
        # Get all contents, we'll filter afterward
        contents = self.character.contents
        for limb in limbs:
            objs = [obj for obj in contents if obj.tags.get(limb.key, category="eq")]
            first_level.append((limb, objs[0] if objs else None))

        return first_level

    def can_hold(self, exclude=None):
        """
        Return the limbs that can hold something.

        Args:
            exclude (Object or list of objects): the optional objects to exclude.

        Returns:
            limbs (list of Limb): the free limbs that can hold something.

        """
        can_hold = []
        first_level = self.first_level
        exclude = exclude or []
        if not isinstance(exclude, (list, tuple)):
            exclude = [exclude]

        for limb, obj in first_level:
            if limb.can_hold:
                if obj is not None and obj not in exclude:
                    continue
                can_hold.append(limb)

        return can_hold

    def hm_can_hold(self, exclude=None):
        """
        Return how many limbs can hold something.

        A character with empty hands will probably have this method
        return 2 (2 free hands).  If this character picks something
        in one hand, this will return 1 and so on.

        Args:
            exclude (Object or list of Object, optional): object or list
                    of objects to ignore, if any.

        Returns:
            number (int): the number of limbs that are free and can hold something.

        """
        return len(self.can_hold(exclude))

    def all(self):
        """Return all objects, include these contained.

        No type checking is performed at this level.  Only the object's
        contents are returned as they are.

        """
        objs = []
        explore = Queue()
        explore.put(self.character)
        while not explore.empty():
            obj = explore.get()
            if obj is not None:
                for content in obj.contents:
                    if content in objs:
                        # Protect against infinite recursion
                        continue

                    objs.append(content)
                    explore.put(content)

        return objs

    def format(self, looker, show_covered=False):
        """
        Return a formatted string of the things worn by the character.

        This method is to be used by the `equipment` command and related.
        It will retrieve the list of limbs and format the message accordingly.

        Args:
            looker (Object): the object (character) looking.
            show_covered (bool, optional): show the limbs that are covered
                    (`False` by default).

        Returns:
            formatted (str): the formatted list of limbs as a string.

        """
        # First, retrieve the list of first level
        first_level = self.first_level
        # We first check what should be hidden
        hidden = []
        if not show_covered:
            for limb, obj in first_level:
                hidden.extend(limb.cover)

        # Browse the list of limbs to display them, hiding what should be hidden
        string = ""
        for limb, obj in first_level:
            if limb.key in hidden:
                continue

            if obj is None:
                continue

            string += "\n  " + limb.name.ljust(20) + ": " + obj.get_display_name(looker)

        return string.lstrip("\n")

    def can_get(self, object_or_objects):
        """Return the objects the character can get.

        Args:
            object_or_objects (Object or list of Object): the object(s) to pick up.

        Return:
            objects (dictionary of Object:container): the list of objects the
                    character can pick up.  Note that the container can be
                    a limb (Limb object), if the object can be picked up in
                    one of the character's limbs if it can hold something.

        Object types are checked at this moment.  Rather, browsing through
        the extended object content, if one object can get, checks whether
        it can get these objects.  This method will spread the objects
        on several containers if it has to.

        """
        can_hold = self.can_hold()
        can_get = ContainerSet()
        if inherits_from(object_or_objects, "evennia.objects.objects.DefaultObject"):
            objects = [object_or_objects]
        else:
            objects = object_or_objects

        # Look for potential containers
        containers = {}
        extended = self.all()
        for obj in extended:
            if hasattr(obj, "types"):
                types = obj.types.can("get")
                if types:
                    containers[obj] = types[0]

        # Try to get all objects
        to_get = []
        for container, type in containers.items():
            in_it = []
            for obj in objects:
                if obj in to_get:
                    continue

                # Try to put the object into the container
                if type.can_get(in_it + [obj]):
                    can_get[container].append(obj)
                    in_it.append(obj)
                    to_get.append(obj)

            if all(obj in to_get for obj in objects):
                break

        # The remaining objects are picked up by the can_hold limbs, if possible
        remaining = [obj for obj in objects if obj not in to_get]
        while can_hold and remaining:
            limb = can_hold.pop(0)
            can_get[limb].append(remaining.pop(0))

        can_get.remaining = remaining
        return can_get

    def get(self, objects_and_containers):
        """
        Get the specified objects.

        The `can_get` method should have been called beforehand, and this
        method should process getting the objects and putting them in the
        various containers without error.

        Args:
            objects_and_containers (dict): the objects to get, the result
                    of the `can_get` method.  No error is assumed to happen
                    at this point.

        """
        for container, objects in objects_and_containers.items():
            for obj in objects:
                if isinstance(container, Limb):
                    # It's a first-level, a limb, either hold it or wear it
                    limb = container
                    obj.location = self.character
                    obj.tags.add(limb.key, category="eq")
                else:
                    obj.location = container
