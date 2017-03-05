"""
This file ocntains the CmdRoom and sub-commands.

"""

from textwrap import dedent

from commands.command import Command

from evennia.utils.eveditor import EvEditor

class CmdRoom(Command):

    """
    Manipulate rooms.

    Sub-commands:
        name [new name]: Display or change the room's name

    """

    key = "room"
    locks = "cmd:id(1) or perm(Builders)"

    def func(self):
        caller = self.caller
        location = caller.location

        # Check permissions
        if not location.access(self.caller, "edit"):
            self.caller.msg("|rYou cannot edit this room.|n")
            return

        string = dedent("""
            You are in room '{room.name}' (#{room.id})

            Available sub-commands:
                name [new name]: Check or change the room's name
                desc: edit the room's description

        """.strip("\n")).format(room=location)

        caller.msg(string)


class CmdRoomName(Command):

    """
    Display or change the room's name.

    Syntax:
        room name
        room name <new name of the room>

    Aliases:
        rname
        rn

    """

    key = "room name"
    aliases = ["rname", "rn"]
    locks = "cmd:id(1) or perm(Builders)"

    def func(self):
        caller = self.caller
        location = caller.location

        # Check permissions
        if not location.access(self.caller, "edit"):
            self.caller.msg("|rYou cannot edit this room.|n")
            return

        args = self.args.lstrip()
        if args:
            location.name = args
            caller.msg("The name of the room has been updated.")
        caller.msg("Current name of the room #{}: {}.".format(
                location.id, location.name))

def _desc_load(caller):
    return caller.db.evmenu_target.db.desc or ""

def _desc_save(caller, buf):
    """
    Save line buffer to the desc prop. This should
    return True if successful and also report its status to the user.
    """
    caller.db.evmenu_target.db.desc = buf
    caller.msg("Saved.")
    return True

def _desc_quit(caller):
    caller.attributes.remove("evmenu_target")
    caller.msg("Exited editor.")

class CmdRoomDesc(Command):

    """
    Open a line editor to edit the room's description.

    Syntax:
        room describe

    Alias:
        room desc
        rdesc
        rd

    """

    key = "room describe"
    aliases = ["room desc", "rdesc", "rd"]
    locks = "cmd:id(1) or perm(Builders)"

    def func(self):
        """Open the line editor to edit the description."""
        location = self.caller.location

        # Check permissions
        if not location.access(self.caller, "edit"):
            self.caller.msg("|rYou cannot edit this room.|n")
            return

        self.caller.db.evmenu_target = self.caller.location
        # launch the editor
        EvEditor(self.caller, loadfunc=_desc_load, savefunc=_desc_save, quitfunc=_desc_quit, key="desc", persistent=True)
