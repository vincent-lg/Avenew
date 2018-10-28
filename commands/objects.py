# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

from collections import defaultdict
from textwrap import wrap

from evennia.utils.utils import crop, inherits_from

from commands.command import Command

## Constants
CATEGORY = "Object manipulation"

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
            self.msg("|yWhat do you want to pick up?|n")
            return

        # Extract the quantity, if specified
        quantity = 1
        words = self.args.strip().split(" ")
        if words[0].isdigit():
            quantity = int(words.pop(0))
        elif words[0] == "*":
            quantity = -1
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
            self.msg("|yYou should at least specify an object name to pick up.|n")
            return

        # Try to find the from object (higher priority since we need it in the next search)
        from_obj = self.caller.location
        if from_text:
            candidates = self.caller.location.contents + self.caller.equipment.all()
            from_objs = self.caller.search(from_text, quiet=True, candidates=candidates)
            if from_objs:
                from_obj = from_objs[0]
            else:
                self.msg("|rYou can't find that: {}.|n".format(from_text))
                return

        # Try to find the object
        objs = self.caller.search(obj_text, quiet=True, candidates=from_obj.contents)
        if objs:
            # Alter the list depending on quantity
            if quantity == 0:
                quantity = 1
            objs = objs[:quantity]
        else:
            self.msg("|rYou can't find that: {}.|n".format(obj_text))
            return

        # Try to put the objects in the caller
        can_get = self.caller.equipment.can_get(objs)
        if can_get:
            self.caller.equipment.get(can_get)
            gotten = [obj for objects in can_get.values() for obj in objects]
            for obj in gotten:
                self.msg("You pick up: {}.".format(obj.get_display_name(self.caller)))
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
