"""
This file ocntains the CmdRoom and sub-commands.

"""

from textwrap import dedent

from django.conf import settings
from evennia.utils.create import create_object
from evennia.utils.eveditor import EvEditor

from commands.command import Command
from commands.smart.command import SmartCommand
from logic.geo import *
from typeclasses.rooms import Room

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

    def func(self):
        """Open the line editor to edit the description."""
        location = self.caller.location
        self.caller.db.evmenu_target = self.caller.location
        # Launch the editor
        EvEditor(self.caller, loadfunc=_desc_load,
                savefunc=_desc_save, quitfunc=_desc_quit, key="desc",
                persistent=True)


class CmdRoomAdd(SmartCommand):

    """
    Add a new room.

    Syntax:
        room add <direction>

    This command can be used to create new rooms.  You have to
    specify the name of the exit to be created (can be an alias,
    like |ye|n for |yeast|n).  The exit to this room and back will
    be created.  The coordinates of the new room will be changed
    accordingly.

    Alias:
        radd

    """

    key = "room add"
    aliases = ["radd"]
    locks = "cmd:id(1) or perm(Builders)"

    def setup(self):
        """Setup the command's arguments."""
        self.params.add("direction")

    def execute(self):
        """Open the line editor to edit the description."""
        name = self.direction.name
        indice = self.direction.indice
        opp_name = self.direction.opp_name
        opp_indice = self.direction.opp_indice

        # Typeclasses
        room_typeclass = settings.BASE_ROOM_TYPECLASS
        exit_typeclass = settings.BASE_EXIT_TYPECLASS

        # Perform additional checks if the room has valid coordinates
        here = self.caller.location
        if all(c is None for c in (here.x, here.y, here.z)):
            coords = (None, None, None)
            msg_coords = "without valid coordinates"
        else:
            coords = coords_in(here.x, here.y, here.z, indice)
            msg_coords = "with coordinates X={} Y={} Z={}".format(*coords)

            # Check that there is no room at the future location
            if Room.get_room_at(*coords):
                self.msg("There already is a room at this location " \
                        "(X={}, Y={}, Z={}).".format(*coords))
                return

        # Check that there is no exit in this direction
        if [o for o in here.contents if o.destination and o.key == name]:
            self.msg("There already is an exit in this direction.")
            return

        # Create the room
        room = create_object(room_typeclass, key="Nowhere")
        room.x = coords[0]
        room.y = coords[1]
        room.z = coords[2]
        self.msg("The room {} (#{}) has been created {}.".format(
                room.key, room.id, msg_coords))

        # Create the exits
        aliases = ALIAS_DIRECTIONS[indice]
        opp_aliases = ALIAS_DIRECTIONS[opp_indice]
        exit = create_object(exit_typeclass, key=name,
                location=here, destination=room, aliases=aliases)
        self.msg("The {} exit has been created between {} and {}.".format(
                name, here.key, room.key))
        opp_exit = create_object(exit_typeclass, key=opp_name,
                location=room, destination=here, aliases=opp_aliases)
        self.msg("The {} exit has been created between {} and {}.".format(
                opp_name, room.key, here.key))
