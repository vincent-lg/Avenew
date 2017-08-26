"""
Comsystem command module.

Contrary to the Evennia default comm system, channels in Avenew are
available to logged-in characters only, not to accounts through the OOC
mode (there's not much of an OOC mode in Avenew).  The default commands
are therefore removed from the AccountCmdSet, while the new commands are
added into the CharacterCmdSet.

"""

from django.utils.translation import ugettext as _
from evennia import SESSION_HANDLER
from evennia.commands.default.comms import find_channel
from evennia.commands.default.muxcommand import MuxCommand
from evennia.comms.channelhandler import CHANNELHANDLER
from evennia.comms.models import ChannelDB, Msg
from evennia.comms.channelhandler import CHANNELHANDLER
from evennia.locks.lockhandler import LockException
from evennia.utils import create, utils, evtable
from evennia.utils.logger import tail_log_file
from evennia.utils.utils import make_iter, class_from_module

from commands.command import Command

class CmdConnect(Command):
    """
    Connect to a channel.
    """

    key = "+"
    help_category = "Comms"
    locks = "cmd:not pperm(channel_banned)"
    auto_help = False

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args
        if not args:
            self.msg("Which channel do you want to connect to?")
            return

        channelname = self.args
        channel = find_channel(caller, channelname)
        if not channel:
            return

        # check permissions
        if not channel.access(caller, 'listen'):
            self.msg("%s: You are not allowed to listen to this channel." % channel.key)
            return

        # If not connected to the channel, try to connect
        if not channel.has_connection(caller):
            if not channel.connect(caller):
                self.msg("%s: You are not allowed to join this channel." % channel.key)
                return
            else:
                self.msg("You now are connected to the %s channel. " % channel.key.lower())
        else:
            self.msg("You already are connected to the %s channel. " % channel.key.lower())


class CmdDisconnect(Command):
    """
    Disconnect from a channel.
    """

    key = "-"
    help_category = "Comms"
    locks = "cmd:not pperm(channel_banned)"
    auto_help = False

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args
        if not args:
            self.msg("Which channel do you want to disconnect from?")
            return

        channelname = self.args
        channel = find_channel(caller, channelname)
        if not channel:
            return

        # If connected to the channel, try to disconnect
        if channel.has_connection(caller):
            if not channel.disconnect(caller):
                self.msg("%s: You are not allowed to disconnect from this channel." % channel.key)
                return
            else:
                self.msg("You stop listening to the %s channel. " % channel.key.lower())
        else:
            self.msg("You are not connected to the %s channel. " % channel.key.lower())


class CmdChannel(MuxCommand):

    """
    Manipulate channels.

    Usage:
      channel                            - display the list of channels.
      channel/join <name>                - connect to the channel.
      channel/leave <name>               - disconnect from the channel.

    This command and its switches are used to connect to, disconnect
    from, obtain information about, and modify settings of channels.  To
    connect to a channel, use the |wchannel/join|n command, followed
    by the name of the channel.  For instance: |wchannel/join public|n.
    You can use the plus symbol as a shortcut: |w+public|n .

    To talk on a channel, simply use its name as a command followed by
    your message.  To send |whello|n on the public channel, for instance:
    |wpublic hello|n . You will find other information when using
    |whelp <channel name>|n, like |whelp public|n .

    To disconnect from a channel and stop receiving messages from it,
    use the |channel/leave|n command, followed by the name of the channel.
    For instance: |wchannel/leave public|n .  You can also use the
    minus symbol as a shortcut: |w-public|n .

    """

    key = "channel"
    aliases = ["channels"]
    help_category = "Comms"
    locks = "cmd:not pperm(channel_banned)"

    def func(self):
        """Body of the command."""
        caller = self.caller

        # If there's an argument, it's a channel name
        args = self.args
        channel = None
        if self.args.strip():
            channel = find_channel(caller, self.args)
            if not channel:
                return

            # Check permissions
            if not channel.access(caller, 'listen'):
                self.msg("%s: You are not allowed to listen to this channel." % channel.key)
                return

        if "join" in self.switches:
            if not channel:
                self.msg("Which channel do you want to join?")
                return

            # If not connected to the channel, try to connect
            if not channel.has_connection(caller):
                if not channel.connect(caller):
                    self.msg("%s: You are not allowed to join this channel." % channel.key)
                    return
                else:
                    self.msg("You now are connected to the %s channel. " % channel.key.lower())
            else:
                self.msg("You already are connected to the %s channel. " % channel.key.lower())
        elif "leave" in self.switches:
            if not channel:
                self.msg("Which channel do you want to leave?")
                return

            # If connected to the channel, try to disconnect
            if channel.has_connection(caller):
                if not channel.disconnect(caller):
                    self.msg("%s: You are not allowed to disconnect from this channel." % channel.key)
                    return
                else:
                    self.msg("You stop listening to the %s channel. " % channel.key.lower())
            else:
                self.msg("You are not connected to the %s channel. " % channel.key.lower())
        else:
            channels = sorted(ChannelDB.objects.all(), key=lambda chan: chan.key)
            channels = [chan for chan in channels if chan.access(
                    caller, 'listen')]
            if channels:
                puppets = [session.puppet for session in SESSION_HANDLER.values() \
                        if session.puppet]
                table = evtable.EvTable("Channel", "Descriptions", "Nb")
                for channel in channels:
                    nb = len([obj for obj in channel.subscriptions.all() \
                            if obj in puppets])
                    table.add_row(channel.key, channel.db.desc, nb)
                self.msg(unicode(table))
            else:
                self.msg("There's currently no channel here... odd...")


class ChannelCommand(Command):
    """
    {channelkey} channel

    {channeldesc}

    Usage:
      {lower_channelkey} <message>
      {lower_channelkey}/history [start]
      {lower_channelkey}/me <message>
      {lower_channelkey}/who

    Switch:
      history: View 20 previous messages, either from the end or
          from <start> number of messages from the end.
      me: Perform an emote on this channel.
      who: View who is connected to this channel.

    Example:
      {lower_channelkey} Hello World!
      {lower_channelkey}/history
      {lower_channelkey}/history 30
      {lower_channelkey}/me grins.
      {lower_channelkey}/who
    """
    # ^note that channeldesc and lower_channelkey will be filled
    # automatically by ChannelHandler

    # this flag is what identifies this cmd as a channel cmd
    # and branches off to the system send-to-channel command
    # (which is customizable by admin)
    is_channel = True
    key = "general"
    help_category = "Channel Names"
    obj = None
    arg_regex = ""

    def parse(self):
        """
        Simple parser
        """
        # cmdhandler sends channame:msg here.
        channelname, msg = self.args.split(":", 1)
        self.history_start = None
        self.switch = None
        if msg.startswith("/"):
            try:
                switch, msg = msg[1:].split(" ", 1)
            except ValueError:
                switch = msg[1:]
                msg = ""

            self.switch = switch.lower().strip()

        # If /history
        if self.switch == "history":
            try:
                self.history_start = int(msg) if msg else 0
            except ValueError:
                # if no valid number was given, ignore it
                pass

        self.args = (channelname.strip(), msg.strip())

    def func(self):
        """
        Create a new message and send it to channel, using
        the already formatted input.
        """
        channelkey, msg = self.args
        caller = self.caller
        channel = ChannelDB.objects.get_channel(channelkey)
        admin_switches = ("destroy", "emit", "lock", "locks", "desc", "kick")

        # Check that the channel exist
        if not channel:
            self.msg(_("Channel '%s' not found.") % channelkey)
            return

        # Check that the caller is connected
        if not channel.has_connection(caller):
            string = _("You are not connected to channel '%s'.")
            self.msg(string % channelkey)
            return

        # Check that the caller has send access
        if not channel.access(caller, 'send'):
            string = _("You are not permitted to send to channel '%s'.")
            self.msg(string % channelkey)
            return

        # Get the list of connected to this channel
        puppets = [session.puppet for session in SESSION_HANDLER.values() \
                if session.puppet]
        connected = [obj for obj in channel.subscriptions.all() if obj in puppets]

        # Handle the various switches
        if self.switch == "me":
            if not msg:
                self.msg("What do you want to do on this channel?")
            else:
                msg = "{} {}".format(caller.key, msg)
                channel.msg(msg, online=True)
        elif self.switch == "who":
            keys = [obj.key for obj in connected]
            keys.sort()
            string = "Connected to the {} channel:".format(channel.key)
            string += ", ".join(keys) if keys else "(no one)"
            string += "."
            self.msg(string)
        elif channel.access(caller, 'control') and self.switch in admin_switches:
            if self.switch == "destroy":
                confirm = yield("Are you sure you want to delete the channel {}? (Y?N)".format(channel.key))
                if confirm.lower() in ("y", "yes"):
                    channel.msg("Destroying the channel.")
                    channel.delete()
                    CHANNELHANDLER.update()
                    self.msg("The channel was destroyed.")
                else:
                    self.msg("Operation cancelled, do not destroy.")
            elif self.switch == "emit":
                if not msg:
                    self.msg("What do you want to say on this channel?")
                else:
                    channel.msg(msg, online=True)
            elif self.switch in ("lock", "locks"):
                if msg:
                    try:
                        channel.locks.add(msg)
                    except LockException, err:
                        self.msg(err)
                        return
                    else:
                        self.msg("Channel permissions were edited.")

                string = "Current locks on {}:\n  {}".format(channel.key, channel.locks)
                self.msg(string)
            elif self.switch == "desc":
                if msg:
                    channel.db.desc = msg
                    self.msg("Channel description was updated.")

                self.msg("Description of the {} channel: {}".format(
                        channel.key, channel.db.desc))
            elif self.switch == "kick":
                if not msg:
                    self.msg("Who do you want to kick from this channel?")
                else:
                    to_kick = caller.search(msg, candidates=connected)
                    if to_kick is None:
                        return

                    channel.disconnect(to_kick)
                    channel.msg("{} has been kicked from the channel.".format(to_kick.key))
                    to_kick.msg("You have been kicked from the {} channel.".format(channel.key))
        elif self.history_start is not None:
            # Try to view history
            log_file = channel.attributes.get("log_file", default="channel_%s.log" % channel.key)
            send_msg = lambda lines: self.msg("".join(line.split("[-]", 1)[1]
                                                    if "[-]" in line else line for line in lines))
            tail_log_file(log_file, self.history_start, 20, callback=send_msg)
        elif self.switch:
            self.msg("{}: Invalid switch {}.".format(channel.key, self.switch))
        elif not msg:
            self.msg(_("Say what?"))
            return
        else:
            if caller in channel.mutelist:
                self.msg("You currently have %s muted." % channel)
                return
            channel.msg(msg, senders=self.caller, online=True)

    def get_extra_info(self, caller, **kwargs):
        """
        Let users know that this command is for communicating on a channel.

        Args:
            caller (TypedObject): A Character or Account who has entered an ambiguous command.

        Returns:
            A string with identifying information to disambiguate the object, conventionally with a preceding space.
        """
        return _(" (channel)")

    def get_help(self, caller, cmdset):
        """
        Return the help message for this command and this caller.

        By default, return self.__doc__ (the docstring just under
        the class definition).  You can override this behavior,
        though, and even customize it depending on the caller, or other
        commands the caller can use.

        Args:
            caller (Object or Account): the caller asking for help on the command.
            cmdset (CmdSet): the command set (if you need additional commands).

        Returns:
            docstring (str): the help text to provide the caller for this command.

        """
        docstring = self.__doc__
        channel = ChannelDB.objects.get_channel(self.key)
        if channel and channel.access(caller, 'control'):
            # Add in the command administration switches
            docstring += HELP_COMM_ADMIN.format(lower_channelkey=self.key.lower())

        return docstring


# Help entry for command administrators
HELP_COMM_ADMIN = r"""

    Administrator switches:
      {lower_channelkey}/kick <username>: kick a user from a channel.
      {lower_channelkey}/desc [description]: see or change the channel description.
      {lower_channelkey}/lock [lockstring]: see or change the channel permissions.
      {lower_channelkey}/emit <message>: admin emit to the channel.
      {lower_channelkey}/destroy: destroy the channel.
"""
