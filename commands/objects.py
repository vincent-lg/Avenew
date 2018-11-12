# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

from collections import defaultdict
import re
from textwrap import wrap

from evennia.utils.utils import crop, inherits_from, list_to_string

from commands.command import Command

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
        from_objs = [content for obj in from_objs for content in obj.contents]
        objs = self.caller.search(obj_text, quiet=True, candidates=from_objs)
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
            self.caller.equipment.get(can_get)
            self.msg("You get {}.".format(list_to_string(can_get.objects().names(self.caller), endsep="and")))
        else:
            self.msg("|rIt seems you cannot get that.|n")


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

    Aliases:
      eq

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

    Aliases:
      i

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
