"""This file contains the commands for builders."""

from textwrap import dedent

from evennia import create_object
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import class_from_module

from commands.unixcommand import UnixCommand
from logic.geo import NAME_DIRECTIONS, coords_in, coords

class CmdEdit(MuxCommand):

    """
    Global editing command.

    To use this command, you have to specify the field you wish to
    edit, the object's name (or #ID) and the value after an equal
    sign.  For instance:

        @speed a porsche = 180

    Depending on the object, you will have different fields you can
    modify through this command.  If you have the object and want to
    know what you can edit, simply use this command without the first
    parameter:

        @ a porsche

    Use both the field name and object name without the equal sign
    and value to see the current value of this field:

        @speed #331

    """

    key = "@"
    locks = "cmd:id(1) or perm(Builders)"
    help_category = "Building"

    def func(self):
        """Main function for this command."""
        field_name, sep, obj_name = self.lhs.partition(" ")
        field_name = field_name.lower()
        if field_name.endswith("/del"):
            field_name = field_name[:-4]
            self.switches = ["del"]

        if not obj_name:
            obj_name = field_name
            field_name = ""

        if not obj_name:
            self.msg("Specify at least an object's name or #ID.")
            return

        # Search for the actual object
        obj = self.caller.search(obj_name)
        if not obj:
            return

        # Get the representation value for this object type
        repr = getattr(type(obj), "repr", None)
        if repr is None:
            self.msg("This object has no representation to describe it.")
            return

        repr = class_from_module(repr)
        repr = repr(obj)
        if self.rhs:
            value = self.rhs
            if hasattr(repr, "set_" + field_name):
                getattr(repr, "set_" + field_name)(self.caller, value)
            else:
                self.msg("You cannot modify this field name {} in {}.".format(
                        field_name, obj.get_display_name(self.caller)))
        elif "del" in self.switches:
            if hasattr(repr, "clear_" + field_name):
                getattr(repr, "clear_" + field_name)(self.caller)
            else:
                self.msg("You cannot clear this field name {} in {}.".format(
                        field_name, obj.get_display_name(self.caller)))
        else:
            if hasattr(repr, "get_" + field_name):
                getattr(repr, "get_" + field_name)(self.caller)
            elif field_name in repr.fields:
                value = getattr(obj, field_name)
                self.caller.msg("Current value {} = {} for {}.".format(
                        field_name, value, obj.get_display_name(self.caller)))
            else:
                self.msg("You cannot see this field name {} in {}.".format(
                        field_name, obj.get_display_name(self.caller)))

class CmdNew(UnixCommand):

    """
    Create a new object.

    You can use this command to create multiple objects, like rooms,
    exits, vehicles, and so on.  The first parameter after the
    |w@new|n command is the type to create: |w@new room|n, for
    instance, will create a room.  Different types have different
    expectations.  Read the help above to see the available options
    for each type.

    Examples:
      |w@new room n|n

    """

    key = "@new"
    locks = "cmd:id(1) or perm(Builders)"
    help_category = "Building"

    def init(self):
        """Configure the parser and sub-commands."""
        subparsers = self.parser.add_subparsers()

        # @new room
        room = subparsers.add_parser("room", help="add a room",
                epilog=dedent(self.create_room.__doc__).strip())
        room.add_argument("exit", nargs="?",
                help="the exit in which to create the room")
        room.add_argument("-c", "--coordinates", type=coords,
                help="the new room's coordinates (X Y Z)")
        room.set_defaults(func=self.create_room)

    def func(self):
        self.opts.func(self.opts)

    def create_room(self, args):
        """
        Create a room with given exit or coordinates.

        When using the |w@new room|n command, you have to specify the coordinates of
        the room to create.  This is usually done by providing an exit name as
        parameter: the room where you are, or the position you are in (if in
        road building mode) will be used to infer coordinates.  You can also set
        the |w-c|n option, spcifying coordinates for the new room.

        Examples:
          |w@new room e|n
          |w@new room sw|n
          |w@new room -c 5,10,-15|n

        """
        self.msg(str(args))


class CmdPlant(UnixCommand):

    '''
    Plant a tree or plant.

    This command is used to plant a tree or plant in the room you are in.

    Examples:
      plant orange -a 8
      plant strawberry --hidden
      plant potato --hidden --age 5

    '''

    key = "plant"

    def init(self):
        "Add the arguments to the parser."
        # 'self.parser' inherits `argparse.ArgumentParser`
        self.parser.add_argument("key",
                help="the key of the plant to be planted here")
        self.parser.add_argument("-a", "--age", type=int,
                default=1, help="the age of the plant to be planted")
        self.parser.add_argument("--hidden", action="store_true",
                help="should the newly-planted plant be hidden to players?")

    def func(self):
        "func is called only if the parser succeeded."
        # 'self.opts' contains the parsed options
        key = self.opts.key
        age = self.opts.age
        hidden = self.opts.hidden
        self.msg("Going to plant '{}', age={}, hidden={}.".format(
                key, age, hidden))
