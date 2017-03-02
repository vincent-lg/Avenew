"""
This file ocntains the CmdRoom and sub-commands.

"""

from textwrap import dedent

from commands.command import Command

from commands.edit_cmdset import EditCommand

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

        self.caller.db.editing = {
                "object": location,
                "attr": "desc",
        }

        self.caller.cmdset.add("commands.edit_cmdset.EditCmdSet",
                permanent=True)
        command = self.caller.cmdset.all()[-1].commands[-1]
        command.display_desc(self.caller, self.caller.location.db.desc)
