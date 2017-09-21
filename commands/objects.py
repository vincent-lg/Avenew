"""
Commands to manipualte objects.
"""

from textwrap import wrap

from evennia.utils.utils import crop, inherits_from

from commands.command import Command

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
    help_category = "Object manipulation"

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
    help_category = "Object manipulation"

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
                self.msg("You don't seem to have waiting notifications on any of your devices.")
                return

            msg = "Waiting notifications:"
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
            self.msg("Enter a number to address this notification.")
            return

        # Get the notifications
        args = int(args)
        try:
            assert args > 0
            notification = notifications[args - 1]
        except (AssertionError, IndexError):
            self.msg("Invalid notification number.  Enter |hADDRESS|n without argument to see your current notifications.")
            return

        # Try to see if the device can be used
        obj = notification.obj
        if not obj.types.can("use"):
            self.msg("You cannot address this notification on {}.".format(obj.get_display_name(self.caller)))
            return

        notification.address(self.caller)
