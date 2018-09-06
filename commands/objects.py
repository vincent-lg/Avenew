# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

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
      |yget 5 apples into lunch sack|n

    Finally, you can also take objects from a container (usually, a chest or
    furniture).  Just specify the name of the container after the |yfrom|n keyword:
      |yget coin from chest|n

    You can combine all these syntaxes if needed.

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

        # Extract from and into
        # Extract the quantity, if specified
        quantity = 1
        words = self.args.strip().split(" ")




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
    """

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
            objs = self.search(self.args.strip(), candidates=candidates, quiet=True)
            if objs:
                obj = objs[0]
                if not hasattr(obj, "types"):
                    self.msg("|r{} isn't a phone or computer with notifications.|n".format(obj.get_display_name(self.caller)))
                    return

                for type in obj.types:
                    if hasattr(type, "notifications"):
                        notifications.extend(type.notifications.all())
            else:
                self.msg("|rCan't find that:|n {}".format(self.args.strip())
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
