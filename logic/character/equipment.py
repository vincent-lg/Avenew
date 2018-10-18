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
from collections import defaultdict

from evennia.utils.utils import inherits_from

class EquipmentHandler(object):

    """Equipment handler for characters.

    This handler supports equipping, getting, dropping, removing objects.
    It includes a set of easy-to-use methods to handle containers.

    """

    def __init__(self, character):
        self.character = character

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

    def can_get(self, object_or_objects):
        """Return the objects the character can get.

        Args:
            object_or_objects (Object or list of Object): the object(s) to pick up.

        Return:
            objects (dictionary of Object:container): the list of objects the
                    character can pick up.  Note that the container can be
                    the character itself, if the object can be picked up in one of
                    the character's hands.

        Object types are checked at this moment.  Rather, browsing through
        the extended object content, if one object can get, checks whether
        it can get these objects.  This method will spread the objects
        on several containers if it has to.

        """
        can_get = defaultdict(list)
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

        return can_get

    def first_level(self):
        """Return the first-level of equipment for this character.

        The search will be performed in the character's content.  Depending
        on the character's skeleton, limbs will be attributed with
        containers.  If an object doesn't match a limb, it will be
        disregarded.

        Returns:
            limbs (dictionary of str:list of objects): a dictionary containing, as key, the name of the limb
                    and as value, a list of objects sorted by proximity (the first object in the list is the closest to the skin).

        """
        limbs = OrderedDict()
        skeleton_name = self.character.db.skeleton
        if not skeleton_name:
            return limbs

        skeleton = SKELETONS.get(skeleton_name)
        if skeleton is None:
            raise ValueError("Can't find the skeleton: '{}'".format(skeleton_name))

        # Get all contents, we'll filter afterward
        contents = self.character.contents
        for key, name, group in skeleton:
            objs = sorted([obj for obj in contents if obj.tags.get(key, category="eq")],
                    key=lambda obj: obj.tags.get(category="eq_pos"))
            limbs[name] = objs

        return limbs
