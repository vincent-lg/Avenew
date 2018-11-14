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

from collections import OrderedDict
from Queue import Queue

from evennia.utils.utils import inherits_from

from logic.character.limbs import Limb
from logic.character import limbs as LIMBS
from logic.object.sets import ContainerSet, ObjectSet
from world.log import character as log


class EquipmentHandler(object):

    """Equipment handler for characters.

    This handler supports equipping, getting, dropping, removing objects.
    It includes a set of easy-to-use methods to handle containers.

    """

    def __init__(self, character):
        self.character = character

    @property
    def limbs(self):
        """Return the ordered dictionary of key: limb."""
        ret = OrderedDict()
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

        for limb in limbs:
            ret[limb.key] = limb

        return ret

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
        limbs = self.limbs.values()
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

    def all(self, only_visible=False, looker=None):
        """Return all objects, include these contained.

        No type checking is performed at this level.  Only the object's
        contents are returned as they are.

        Args:
            only_visible (bol, optional): only return visible objects (that
                    is, those with a 'view' lock matching the character).
                    False by default.
            looker (object, optional): the looker.  If not set, it defaults
                    to the character who owns this equipment.  When you set
                    `only_visible` to True, the lock is performed on
                    the looker.

        Returns:
            objects (list of Object): list of objects found in the character,
            recursively checking for contents.

        """
        def _explore_contents(to_update, objects):
            for obj in objects:
                to_update.append(obj)
                _explore_contents(to_update, obj.contents)

        objs = []
        looker = looker or self.character
        for obj in self.character.contents:
            if obj is not None:
                if only_visible and not obj.access(looker, "view"):
                    # this is not visible to the character, skip
                    continue

                objs.append(obj)
                for content in obj.contents:
                    if content in objs:
                        # Protect against infinite recursion
                        continue

                    objs.append(content)
                    _explore_contents(objs, content.contents)

        return objs

    def nested(self, looker=None, only_show=None):
        """
        Return the nested dictioanry of owned objects.

        The returned dictionary should look something like:

        {
            LeftHand: (0, [BlackBag]),
            BlackBag: (1, [Apple, Apple, Apple]),
            RedBag: (2, [Pear, Pear]),
        }

        In other words, the keys should be a limb or an object, and the
        value should be a tuple: the depth of this container (0 for a limb)
        and a list of objects contained in this container.  Notice that
        sub-containers aren't listed (that's why the RedBag object isn't
        listed in the BlackBag content), they have separate key/value
        pairs in the dictionary.

        Args:
            looker (object, optional): the looker.  If it's not set, use the
                    character who owns this equipment.
            only_show (list of objects, optional): return only these
                    objects with their containers.

        Returns:
            nested (dict): a dictionary of nested objects.

        """
        looker = looker or self.character
        only_show = only_show or []
        limbs = self.limbs
        nested = ContainerSet()
        nested.default_factory = ObjectSet
        objs = self.all(only_visible=True, looker=looker)

        # If only_show, apply a filter
        for obj in list(only_show):
            while obj.location and obj.location != self.character:
                obj = obj.location
                only_show.append(obj)

        for obj in objs:
            depth = 0
            if obj != self.character and only_show and obj not in only_show:
                continue

            parent = obj
            while parent != self.character:
                depth += 1
                parent = parent.location
                if parent is None:
                    obj = None
                    break

            if obj is None:
                continue

            # If a first level object, try to get the limb
            if obj.location == self.character:
                limb_key = obj.tags.get(category="eq")
                if limb_key is None:
                    log.warning("Character {}(#{}): the object {}(#{}) was found in the inventory without a proper container or limb attached to it".format(
                            self.character.key, self.character.id, obj.key, obj.id))
                    continue

                if limb_key not in limbs:
                    log.warning("Character {}(#{}): the object {}(#{}) was found in the inventory at first level with an incorrect limb key: {!r}".format(
                            self.character.key, self.character.id, obj.key, obj.id, limb_key))
                    continue

                limb = limbs[limb_key]
                parent = limb
                if not obj.contents:
                    continue
            else:
                parent = obj.location
                if obj.contents:
                    continue

            nested[(parent, depth - 1)].append(obj)

        return nested

    def format_equipment(self, looker, show_covered=False):
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

    def format_inventory(self, looker=None, only_show=None):
        """
        Return the formatted inventory as a string.

        The inventory is composed of every owned object, starting from the
        character's first level equipment (what she is wearing) and
        recursively examining each object's contents.

        Args:
            looker (object, optional): the looker.  If not set, default to
            only_show (list of objects, optional): list of objects to filter
                    the inventory.
                    the character who owns this equipment.

        Return:
            inventory (str): the formatted inventory.

        """
        looker = looker or self.character
        nested = self.nested(looker=looker, only_show=only_show)
        string = ""
        last_parent = None
        for (parent, depth), objects in nested.items():
            indent_m1 = (depth - 1) * 2 * " "
            indent = depth * 2 * " "
            indent_p1 = (depth + 1) * 2 * " "
            if last_parent is not None and getattr(parent, "location", None) and last_parent != parent.location and parent.location != self.character:
                string += "\n" + indent_m1 + "[Back inside " + parent.location.get_display_name(looker) + ", you also see]:"

            if getattr(parent, "location", None) == self.character:
                if objects:
                    string += "\n" + indent_p1 + ("\n" + indent_p1).join(objects.names(looker))
                continue

            if isinstance(parent, Limb):
                string += "\n" + "[" + parent.name + "]:\n  "
                parent = objects[0]
                del objects[:]
            else:
                string += "\n" + indent

            string += parent.get_display_name(looker)
            if objects or depth == 0:
                string += " [containing]"
            if objects:
                string += "\n" + indent_p1 + ("\n" + indent_p1).join(objects.names(looker))
            last_parent = parent

        if string.strip():
            return string.lstrip("\n")
        else:
            return "You aren't carrying anything."

    def can_get(self, object_or_objects, filter=None):
        """Return the objects the character can get.

        Args:
            object_or_objects (Object or list of Object): the object(s) to pick up.
            filter (list of objects, optional): a list of containers, only
                    use these containers if present.

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
        can_hold = self.can_hold() if filter is None else False
        can_get = ContainerSet()
        if inherits_from(object_or_objects, "evennia.objects.objects.DefaultObject"):
            objects = [object_or_objects]
        else:
            objects = object_or_objects

        # Look for potential containers (even if there is a filter)
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
            # If there is a filter, check it, `container` should be in it
            if filter is not None and container not in filter:
                continue

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

    def can_drop(self, object_or_objects, filter=None):
        """Return the objects the character can drop.

        Args:
            object_or_objects (Object or list of Object): the object(s) to drop.
            filter (list of objects, optional): a list of containers, only
                    use these containers if present.

        Return:
            objects (dictionary of Object:container): the list of objects the
                    character can pick up.  Note that the container can be
                    a room (Room object), if the object can be put into the
                    room.

        Object types are checked at this moment.  Rather, browsing through
        the extended object content, if one object can drop, checks whether
        it can drop these objects.  This method will spread the objects
        on several containers if it has to.

        """
        can_drop = ContainerSet()
        if inherits_from(object_or_objects, "evennia.objects.objects.DefaultObject"):
            objects = [object_or_objects]
        else:
            objects = object_or_objects

        # Look for potential containers (even if there is a filter)
        containers = {}
        extended = self.character.location.contents + self.all()
        for obj in extended:
            if hasattr(obj, "types"):
                types = obj.types.can("get")
                if types:
                    containers[obj] = types[0]

        # Try to drop all objects
        to_drop = []
        for container, type in containers.items():
            # If there is a filter, check it, `container` should be in it
            if filter is not None and container not in filter:
                continue

            in_it = []
            for obj in objects:
                if obj in to_drop:
                    continue

                # Try to put the object into the container
                if type.can_get(in_it + [obj]):
                    can_drop[container].append(obj)
                    in_it.append(obj)
                    to_drop.append(obj)

            if all(obj in to_drop for obj in objects):
                break

        # The remaining objects are dropped into the room if a filter isn't present
        remaining = [obj for obj in objects if obj not in to_drop]
        while not filter and remaining:
            can_drop[self.character.location].append(remaining.pop(0))

        can_drop.remaining = remaining
        return can_drop

    def drop(self, objects_and_containers):
        """
        Drop the specified objects.

        The `can_drop` method should have been called beforehand, and this
        method should process dropting the objects and putting them in the
        various containers without error.

        Args:
            objects_and_containers (dict): the objects to drop, the result
                    of the `can_drop` method.  No error is assumed to happen
                    at this point.

        """
        for container, objects in objects_and_containers.items():
            for obj in objects:
                obj.location = container

    def can_wear(self, obj, limb=None):
        """
        Return whether the character can wear this object.

        Args:
            obj (Object): the object to wear.
            limb (Limb, optional): the limb on which to wear this object.

        Returns:
            limb (Limb or None): the limb on which the object can be worn,
                    or None to indicate a failure.

        """
        types = obj.types.can("wear")
        if not types:
            return

        # If obj is already worn, return None
        if obj.tags.get(category="eq"):
            return

        idents = [ident for type_obj in types for ident in type_obj.db.get("wear_on", [])]

        # If a limb is specified, check that it is present in this list
        if limb:
            if limb.key not in idents and limb.group not in idents:
                return

            if self.limbs[limb.key]: # Something is already worn on this limb
                return

            return limb

        ident = idents[0]
        for limb, obj in self.first_level:
            if obj is None:
                if limb.key == ident or limb.group == ident:
                    return limb

    def wear(self, obj, limb):
        """
        Wear an object.

        The parameter should have been the ones returned by `can_wear`,
        called beforehand.  At this point, both the object and limb aren't
        checked for errors.

        Args:
            obj (Object): the object to wear.
            limb (Limb): the limb on which to wear this object.

        """
        obj.location = self.character
        obj.tags.add(limb.key, category="eq")
