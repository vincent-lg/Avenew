# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

from collections import defaultdict
import re
from textwrap import wrap

from evennia.utils.utils import crop, inherits_from

from commands.command import Command
from logic.object.sets import ObjectSet

## Constants
CATEGORY = "Object manipulation"
RE_D = re.compile(r"^\d+$")

class CmdGet(Command):
    """
    Pick up something.

    Usage:
      get [quantity] <object name> [from <container>] [into <container>]

    Pick up one or more objects at your feet.  The easiest usage is to simply
    specify an object name as argument:
      |yget apple|n

    You can also pick up several objects at once:
      |yget 3 apples|n

    Or get all of them:
      |yget * apples|n

    By default, the objects you pick up will be sorted in your inventory, which is
    defined by what you are carrying as containers.  If you have a pair of jeans
    on, you will have pockets... but they won't be too large either.  If you don't
    have any more room in your containers, you will try to pick up the objects with
    your free hands, assuming they are not too heavy for you.  You can also specify
    in which container to store the objects you have picked up:
      |yget 5 apples into lunchbox|n

    Finally, you can also take objects from a container (usually, a chest or
    furniture).  Just specify the name of the container after the |yfrom|n keyword:
      |yget coin from chest|n

    You can combine all these syntaxes if needed:
      |yget 5 apples from basket into lunchbox|n

    See also: drop, hold, put, wear, remove.

    """

    key = "get"
    aliases = ["grab"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gWhat do you want to pick up?|n")
            return

        # Extract the quantity, if specified
        quantity = 1
        words = self.args.strip().split(" ")
        if RE_D.search(words[0]):
            quantity = int(words.pop(0))
        elif words[0] == "*":
            quantity = None
            del words[0]

        # Extract from and into
        obj_text = from_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "from":
                from_text = " ".join(words[i + 1:])
                del words[i:]
            elif word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gYou should at least specify an object name to pick up.|n")
            return

        # Try to find the from object (higher priority since we need it in the next search)
        from_objs = [self.caller.location]
        if from_text:
            candidates = self.caller.location.contents + self.caller.equipment.all()
            from_objs = self.caller.search(from_text, quiet=True, candidates=candidates)
            if not from_objs:
                self.msg("|rYou can't find that: {}.|n".format(from_text))
                return

        # Try to find the object
        from_obj_contents = [content for obj in from_objs for content in obj.contents]
        objs = self.caller.search(obj_text, quiet=True, candidates=from_obj_contents)
        if objs:
            # Alter the list depending on quantity
            if quantity == 0:
                quantity = 1
            objs = objs[:quantity]
        else:
            self.msg("|rYou can't find that: {}.|n".format(obj_text))
            return

        # Try to find the into objects
        into_objs = None
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True)
            if not into_objs:
                self.msg("|rYou can't find that: {}.|n".format(into_text))
                return

        # Try to put the objects in the caller
        can_get = self.caller.equipment.can_get(objs, filter=into_objs)
        if can_get:
            # Messages to display
            ot_kwargs = {"char": self.caller}
            objs = can_get.objects()
            my_msg = "You get "
            my_msg += objs.wrapped_names(self.caller)
            ot_msg = "{char} gets {objs}"
            ot_kwargs["objs"] = objs
            if from_text:
                from_objs = ObjectSet(from_objs)
                my_msg += " from " + from_objs.wrapped_names(self.caller)
                ot_msg += " from {from_objs}"
                ot_kwargs["from_objs"] = from_objs
            if into_text:
                my_msg += ", and drop {} into ".format("it" if len(can_get.objects()) < 2 else "them")
                my_msg += ObjectSet(into_objs).wrapped_names(self.caller)
            my_msg += "."
            ot_msg += "."
            self.msg(my_msg)
            self.caller.location.msg_contents(ot_msg, exclude=[self.caller], mapping=ot_kwargs)
            self.caller.equipment.get(can_get)
        else:
            self.msg("|rIt seems you cannot get that.|n")


class CmdDrop(Command):
    """
    Drop something.

    Usage:
      drop [quantity] <object name> [from <container>] [into <container>]

    Drop some object.  The most simple usage is to specify the object name
    to drop on the floor:
      |ydrop apple|n

    You can also drop several objects at once:
      |ydrop 3 apples|n

    Or drop all of them:
      |ydrop * apples|n

    By default, the objects you want to drop will be searched in your inventory,
    that is, everything you are wearing and what they contain.  You don't have to
    specify the origin of the objects: if the apples you try to drop, in the same
    example, can be found in your inventory, then you don't need to specify the
    container in which to look for.  But sometimes, it is useful to specify one
    container from which the objects should be searched.  To do so, specify the
    container name after the |yfrom|n keyword:
      |ydrop 5 apples from lunchbox|n

    Finally, you can also drop objects into one or more specific containers.  This
    syntax is most helpful to put clothes in a drawer for instance, or place a jar
    in a cupboard.  To drop in a specific container, use the |yinto|n keyword
    followed by your container name:
      |ydrop coin into chest|n

    You can combine all these syntaxes if needed:
      |ydrop 5 apples from basket into lunchbox|n

    See also: get, hold, put, wear, remove.

    """

    key = "drop"
    aliases = ["put"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gWhat do you want to drop?|n")
            return

        # Extract the quantity, if specified
        quantity = 1
        words = self.args.strip().split(" ")
        if RE_D.search(words[0]):
            quantity = int(words.pop(0))
        elif words[0] == "*":
            quantity = None
            del words[0]

        # Extract from and into
        obj_text = from_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "from":
                from_text = " ".join(words[i + 1:])
                del words[i:]
            elif word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gYou should at least specify an object name to drop.|n")
            return

        # Try to find the from object (higher priority since we need it in the next search)
        if from_text:
            candidates = caller.equipment.all(only_visible=True)
            from_objs = self.caller.search(from_text, quiet=True, candidates=candidates)
            from_obj_contents = [content for obj in from_objs for content in obj.contents]
            if not from_obj_contents:
                self.msg("|rYou can't find that: {}.|n".format(from_text))
                return
        else:
            from_obj_contents = caller.equipment.all(only_visible=True)

        # Try to find the object
        objs = self.caller.search(obj_text, quiet=True, candidates=from_obj_contents)
        if objs:
            # Alter the list depending on quantity
            if quantity == 0:
                quantity = 1
            objs = objs[:quantity]
        else:
            self.msg("|rYou can't find that: {}.|n".format(obj_text))
            return

        # Try to find the into objects
        into_objs = []
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True)
            if not into_objs:
                self.msg("|rYou can't find that: {}.|n".format(into_text))
                return

        # Try to put the objects in the containers
        can_drop = self.caller.equipment.can_drop(objs, filter=into_objs)
        if can_drop:
            # Messages to display
            ot_kwargs = {"char": self.caller}
            objs = can_drop.objects()
            my_msg = "You drop " + objs.wrapped_names(self.caller)
            ot_msg = "{char} drops {objs}"
            ot_kwargs["objs"] = objs
            if from_text:
                from_objs = ObjectSet(from_objs)
                my_msg += " from " + from_objs.wrapped_names(self.caller)
                ot_msg += " from {from_objs}"
                ot_kwargs["from_objs"] = from_objs
            if into_text:
                into_objs = ObjectSet(into_objs)
                my_msg += ", and put {} into ".format("it" if len(objs) < 2 else "them")
                my_msg += into_objs.wrapped_names(self.caller)
                ot_msg = "{char} puts {objs} into {into_objs}"
                ot_kwargs["into_objs"] = into_objs
            my_msg += "."
            ot_msg += "."
            self.msg(my_msg)
            self.caller.location.msg_contents(ot_msg, exclude=[self.caller], mapping=ot_kwargs)
            self.caller.equipment.drop(can_drop)
        else:
            self.msg("|rIt seems you cannot drop that.|n")


class CmdUse(Command):

    """
    Use an object given in argument.

    Usage:
        use <object name>

    This command allows you to use an object with an obvious usage, like a phone
    or computer.  More specific commands are available for more specific actions.
    To use a phone that you have near at hand, for instance, just enter
    |huse|n followed by the name of the phone to use.

    Example:
        use computer

    """

    key = "use"
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        # Search for this object
        obj = self.caller.search(self.args)
        if not obj:
            return

        # First, check that what is being used isn't a character
        if inherits_from(obj, "typeclasses.characters.Character"):
            self.msg("Wow, perhaps you should ask permission before trying that!")
            return

        # It needs to have a type handler anyway
        types = []
        if hasattr(obj, "types"):
            types = obj.types.can("use")

        if not types:
            self.msg("What do you want to do with {}?".format(obj.get_display_name(self.caller)))
            return

        types[0].use(self.caller)


class CmdAnswer(Command):

    """
    Answer to the most recent notification you have received.

    If you have a phone or computer and it receives notifications (like a
    new message), you can use the |yanswer|n command to directly open
    this notification and answer to it.  Obviously, the most common use case is when
    somebody calls you.  You will then hear the phone ring and can answer to it by
    entering |yanswer|n.

    If you have more than one devices, you can specify part of the name of the device
    as an argument, to choose only the most recent notification from this device.
    For example:
      |yanswer orange phone|n

    """

    key = "answer"
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        candidates = self.caller.contents + self.caller.location.contents
        notifications = []
        if self.args.strip():
            # Filter based on the object's name
            objs = self.caller.search(self.args.strip(), candidates=candidates, quiet=True)
            if objs:
                obj = objs[0]
                if not hasattr(obj, "types"):
                    self.msg("|r{} isn't a phone or computer with notifications.|n".format(obj.get_display_name(self.caller)))
                    return

                for type in obj.types:
                    if hasattr(type, "notifications"):
                        notifications.extend(type.notifications.all())
            else:
                self.msg("|rCan't find that:|n {}".format(self.args.strip()))
                return

        else:
            for obj in candidates:
                if not hasattr(obj, "types"):
                    continue

                for type in obj.types:
                    if hasattr(type, "notifications"):
                        notifications.extend(type.notifications.all())

        if not notifications:
            self.msg("It seems like you have no unread notification on any of your devices.")
            return
        notification = notifications[-1]

        # Try to see if the device can be used
        obj = notification.obj
        if not obj.types.can("use"):
            self.msg("You cannot address this notification on {}.".format(obj.get_display_name(self.caller)))
            return

        notification.address(self.caller)


class CmdEquipment(Command):
    """
    Display your equipment.

    Usage:
      equipment

    This command displays your equipment, that is, everything you are wearing or
    holding in your hands.  You will see all you are wearing, even if it's hidden by
    some other worn objects.  For instance, even if you have shoes on, and socks
    beneath them, you will see both shoes and socks, whereas if someone looks at you,
    she will only see your shoes, which maybe is a good thing.

    See also: inventory, get, drop, wear, remove, empty, hold.

    """

    key = "equipment"
    aliases = ["eq"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        self.msg(self.caller.equipment.format_equipment(looker=self.caller, show_covered=True))


class CmdInventory(Command):
    """
    Display your inventory.

    Usage:
      inventory [object name]

    This command displays your inventory, that is, the list of what you are wearing
    and what they contain, if they contain anything.  Usually, when you pick up
    something, it will end up in one of your hands.  However, if you have some
    pocket or a backpack or similar, what you pick up will probably end up in there,
    assuming there is room.  A container can contain other containers, too, so that
    you can have a backpack containing a plastic bag containing apples.  In this
    case, when you type |yinventory|n, you will see your backpack, inside of it the
    plastic bag, and inside of it your apples.  This command is useful to list
    everything you are carrying, even if it's hidden in various containers.

    You can also specify an object name to filter based on this name.  This allows
    to use |yinventory|n as a request: find where are my apples.  Following the same
    example, you could use |yinventory apples|n and it will only display your apples
    and where they are, not displaying you the rest of your inventory.  Notice that
    containers that contain your apples are still displayed for clarity.  This will
    help you retrieve something you have lost, something you know you are carrying but
    can't remember where.  In a way, it's a bit like patting your pockets and
    looking into all your bags to find something, but it will be much quicker.

    Remember that you do not need to specify the containers to use your objcts:
    following the same example, of your backpack containing a plastic bag containg
    your apples, if you want to eat one, you just need to enter |yeat apple|n.
    The system will find them automatically, no need to get them manually from the
    plastic bag.

    See also: equipment, get, drop, wear, remove, empty, hold.

    """

    key = "inventory"
    aliases = ["i"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        only_show = None
        if self.args.strip():
            candidates = self.caller.equipment.all(only_visible=True, looker=self.caller)
            only_show = self.caller.search(self.args, candidates=candidates, quiet=True)
            if not only_show:
                self.msg("You don't carry that.")
                return

        inventory = self.caller.equipment.format_inventory(only_show=only_show)
        self.msg(inventory)


class CmdWear(Command):
    """
    Wear an object from your inventory.

    Usage:
      wear <object name>[, <body part>]

    This command allows you to wear an object that you have in your inventory.
    Something you aren't already wearing.  For instance, let's say you pick up
    a shirt: when using the |yget|n command, it will go either in one of your
    containers (like a bag) or in your hands.  To wear it, you need to use the
    |ywear|n command:
      |ywear shirt|n

    You can also specify the body part on which to wear this object.  Some objects
    can be worn on different body parts.  In this case, specify the body part after
    a comma:
      |ywear pink sock, right foot|n

    If the object can be worn on various body parts but you don't specify it, the
    system will try to guess on which body part to wear this object.

    See also: equipment, get, drop, remove, empty, hold.

    """

    key = "wear"
    aliases = []
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        if "," in self.args:
            obj_name, body_part = self.args.rsplit(",", 1)
            obj_name = obj_name.strip()
            body_part = body_part.strip()
        else:
            obj_name = self.args.strip()
            body_part = ""

        # First, try to find the object to wear
        objs = self.caller.search(obj_name, quiet=True, candidates=self.caller.equipment.all(only_visible=True))
        # Filter, removing already-worn objects
        objs = [obj for obj in objs if self.caller.equipment.can_wear(obj)]

        if not objs:
            self.msg("|gYou don't find that: {}.|n".format(obj_name))
            return

        obj = objs[0]

        # Check the body parts
        first_level = self.caller.equipment.first_level
        prefered_limbs = []
        if body_part:
            for limb in first_level.keys():
                if limb.name.startswith(body_part):
                    prefered_limbs.append(limb)

            if not prefered_limbs:
                self.msg("|gCan't find this body part: {}.|n".format(body_part))
                return

        if prefered_limbs:
            for limb in prefered_limbs:
                if self.caller.equipment.can_wear(obj, limb):
                    limb.msg_wear(doer=self.caller, obj=obj)
                    self.caller.equipment.wear(obj, limb)
                    return
            self.msg("|rYou can't wear {} anywhere.|n".format(obj.get_display_name(self.caller)))
            return

        # Choose the first match
        limb = self.caller.equipment.can_wear(obj)
        if limb:
            limb.msg_wear(doer=self.caller, obj=obj)
            self.caller.equipment.wear(obj, limb)
        else:
            self.msg("|rYou can't wear {} anywhere.|n".format(obj.get_display_name(self.caller)))


class CmdRemove(Command):
    """
    Stop wearing an object.

    Usage:
      remove <object name> [into <container>]

    Stop weearing (remove) some object that you are wearing, that is, something
    that is visible in your equipment (see the |yequipment|n command).  If you are
    wearing a shirt, for instance, and would like to stop wearing it:
      |yremove shirt|n

    You can also specify a container in which to drop this object when it is
    removed.  By default, the system will try to find the container on you (in your
    pockets or bags) but you can help it, to order your posessions in a better way:
      |yremove shirt into backpack|n

    See also: get, drop, hold, wear, empty.

    """

    key = "remove"
    aliases = []
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gWhat do you want to stop wearing?|n")
            return

        # Extract into
        words = self.args.strip().split(" ")
        obj_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gYou should at least specify an object name to remove.|n")
            return

        # Try to find the object
        objs = caller.search(obj_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
        if not objs:
            self.msg("|rYou can't find that: {}.|n".format(obj_text))
            return
        obj = objs[0]

        # Try to find the into objects
        into_obj = None
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True)
            if not into_objs:
                self.msg("|rYou can't find that: {}.|n".format(into_text))
                return
            into_obj = into_objs[0]

        can_remove = caller.equipment.can_remove(obj, container=into_obj)
        if can_remove:
            caller.equipment.remove(obj, can_remove)
            caller.msg("You stop wearing {obj}.".format(obj=obj.get_display_name(caller)))
            caller.location.msg_contents("{caller} stops wearing {obj}.", mapping=dict(caller=caller, obj=obj), exclude=[caller])
        else:
            self.msg("|rYou can't stop wearing {}.|n".format(obj.get_display_name(self.caller)))


class CmdHold(Command):
    """
    Hold an object in your hand.

    Usage:
      hold <object name>

    Hold an object.  If the object you specify is in your inventory but not in
    your hand, you will hold it, assuming you have a free hand.  This is useful
    to quickly hold weapons and use them, rather than having to check your inventory
    to find it.
      |yhold baton|n

    See also: get, drop, wear, remove, empty.

    """

    key = "hold"
    aliases = []
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gWhat do you want to hold?|n")
            return

        # Try to find the object
        obj_text = self.args.strip()
        objs = caller.search(obj_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
        objs = [obj for obj in objs if not obj.tags.get(category="eq")]
        if not objs:
            self.msg("|rYou can't find that: {}.|n".format(obj_text))
            return

        obj = objs[0]

        can_hold = caller.equipment.can_hold(obj)
        if can_hold:
            can_hold[0].msg_hold(doer=self.caller, obj=obj)
            caller.equipment.hold(obj, can_hold[0])
        else:
            self.msg("|rYou can't hold {}.|n".format(obj.get_display_name(self.caller)))


class CmdEmpty(Command):

    """
    Empty a container.

    Usage:
      empty <container> [into <other container>]

    Empty a container, like a bag.  The simple usage of this command is to empty a
    container right on the floor:
      |yempty backpack|n

    All the container content will be dropped to the floor.  Alternatively, you can
    specify another container in which to empty the first one.  To do so, specify
    the second container after the |yinto|n keyword:
      |yempty purse into backpack|n

    Notice that the original container will still be at the same place, it will
    just be empty, assuming this command succeeds.

    See also: get, drop, hold, wear, remove.

    """

    key = "empty"
    aliases = ["dump"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gWhat do you want to empty?|n")
            return

        # Extract into
        words = self.args.strip().split(" ")
        obj_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gYou should at least specify an object name to empty.|n")
            return

        # Try to find the object
        objs = caller.search(obj_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
        objs = [content for obj in objs for content in obj.contents]
        if not objs:
            self.msg("|rYou can't find that: {}.|n".format(obj_text))
            return

        # Try to find the into objects
        into_objs = []
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
            if not into_objs:
                self.msg("|rYou can't find that: {}.|n".format(into_text))
                return

        # Try to put the objects in the containers
        can_drop = caller.equipment.can_drop(objs, filter=into_objs)
        if can_drop:
            # Messages to display
            ot_kwargs = {"char": self.caller}
            objs = can_drop.objects()
            my_msg = "You drop " + objs.wrapped_names(self.caller)
            ot_msg = "{char} drops {objs}"
            ot_kwargs["objs"] = objs
            if into_text:
                into_objs = ObjectSet(into_objs)
                my_msg += ", and put {} into ".format("it" if len(objs) < 2 else "them")
                my_msg += into_objs.wrapped_names(self.caller)
                ot_msg = "{char} puts {objs} into {into_objs}"
                ot_kwargs["into_objs"] = into_objs
            my_msg += "."
            ot_msg += "."
            self.msg(my_msg)
            self.caller.location.msg_contents(ot_msg, exclude=[self.caller], mapping=ot_kwargs)
            self.caller.equipment.drop(can_drop)
        else:
            self.msg("|rIt seems you cannot drop anything from that.|n")
