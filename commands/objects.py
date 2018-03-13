# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

from textwrap import wrap

from evennia.utils.utils import crop, inherits_from

from commands.command import Command

## Constants
CATEGORY = "Manipulation des objets"

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
            self.msg("|yQue voulez-vous ramasser ?|n")
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
            self.msg("Hmm, il faudrait peut-être demander la permission avant d'essayer de faire cela !")
            return

        # It needs to have a type handler anyway
        types = []
        if hasattr(obj, "types"):
            types = obj.types.can("use")

        if not types:
            self.msg("Que voulez-vous faire avec {} ?".format(obj.get_display_name(self.caller)))
            return

        types[0].use(self.caller)


class CmdAddress(Command):

    """
    Address a notification that you have received.

    If you have a phone or computer and it receives notifications (like a
    new message), you can use the |hADDRESS|n command to directly open
    this notification and answer to it.  The classical example if, you have a
    phone in your pocket, and it starts ringing or vibrating.  You can look at
    it to see what's going on.  On the phone screen will be your recent
    noticiations.  Each notification has a number, and you can enter
    |hADDRESS <number>|n which will start using the phone and open in the desired
    application.  You can also use |nADDRESS|n without argument to just see the
    notifications on the devices you currently have.
    """

    key = "address"
    help_category = CATEGORY

    def access(self, srcobj, access_type="cmd", default=False):
        if srcobj.cmdset.has("computer"):
            return False

        return super(CmdAddress, self).access(srcobj, access_type, default)

    def func(self):
        """Execute the command."""
        location = self.caller.location
        contents = self.caller.contents + getattr(location, "contents", [])
        notifications = []
        for obj in contents:
            if not hasattr(obj, "types"):
                continue

            for type in obj.types:
                if hasattr(type, "notifications"):
                    notifications.extend(type.notifications.all())

        # If there's no argument, display the list of notifications
        if not self.args.strip():
            if not notifications:
                self.msg("Il semble que vous n'ayiez aucune notification sur aucun de vos appareils.")
                return

            msg = "Notifications en attente :"
            i = 0
            for notification in notifications:
                i += 1
                title = crop(notification.title, 35, "...")
                name = crop(notification.obj.get_display_name(self.caller), 17, "...")
                content = "\n    ".join(wrap(notification.content, 74))
                msg += "\n{:>2}  {:<35}, {:<17} ({})".format(i, title, name, notification.ago)
                if content:
                    msg += "\n    " + content

            self.msg(msg)
            return

        # An argument has been entered
        args = self.args.strip()
        if not args.isdigit():
            self.msg("Entrez un nombre pour répondre à cette notification.")
            return

        # Get the notifications
        args = int(args)
        try:
            assert args > 0
            notification = notifications[args - 1]
        except (AssertionError, IndexError):
            self.msg("Le nombre entré est invalide.")
            return

        # Try to see if the device can be used
        obj = notification.obj
        if not obj.types.can("use"):
            self.msg("Vous ne pouvez adresser cette notification sur {}.".format(obj.get_display_name(self.caller)))
            return

        notification.address(self.caller)
