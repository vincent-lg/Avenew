"""This file contains the commands for builders."""

from textwrap import dedent

from evennia import create_object
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.create import create_object
from evennia.utils.utils import class_from_module, inherits_from

from evennia.contrib.unixcommand import UnixCommand
from logic.geo import NAME_DIRECTIONS, coords_in, coords, get_direction
from typeclasses.prototypes import PRoom
from typeclasses.rooms import Room
from typeclasses.vehicles import Crossroad

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
        operation = "get"
        if field_name.endswith("/add"):
            field_name = field_name[:-4]
            operation = "add"
        elif field_name.endswith("/del"):
            field_name = field_name[:-4]
            operation = "del"
        elif self.rhs:
            operation = "set"

        if not obj_name:
            obj_name = field_name
            field_name = ""

        if not obj_name:
            self.msg("Specify at least an object's name or #ID.")
            return

        # Search for the actual object
        objs = self.caller.search(obj_name, quiet=True)
        if not objs or len(objs) > 1:
            obj = self.caller.search(obj_name, global_search=True)
            if not obj:
                return
        else:
            obj = objs[0]

        # Get the representation value for this object type
        repr = getattr(type(obj), "repr", None)
        if repr is None:
            self.msg("This object has no representation to describe it.")
            return

        repr = class_from_module(repr)
        repr = repr(obj)
        repr.process(self.caller, field_name, self.rhs, operation)


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

    def init_parser(self):
        """Configure the parser and sub-commands."""
        subparsers = self.parser.add_subparsers()

        # @new room
        room = subparsers.add_parser("room", help="add a room",
                epilog=dedent(self.create_room.__doc__).strip())
        room.add_argument("exit", nargs="?",
                help="the exit in which to create the room")
        room.add_argument("-h", "--help", action="store_true",
                help="display the help")
        room.add_argument("-c", "--coordinates", type=coords,
                help="the new room's coordinates (X Y Z)")
        room.add_argument("-p", "--prototype", nargs="+", default=None,
                help="the prototype key on which to build this room")
        room.add_argument("-r", "--road", default=["AUTO"], nargs="+",
                help="the road name, AUTO to find it automatically or NONE")
        room.set_defaults(func=self.create_room)
        room.set_defaults(parser=room)

    def func(self):
        if self.opts.help:
            self.msg(self.opts.parser.format_help())
        else:
            self.opts.func(self.opts)

    def create_room(self, args):
        """
        Create a room with given exit or coordinates.

        When using the |w@new room|n command, you have to specify the coordinates of
        the room to create.  This is usually done by providing an exit name as
        parameter: the room where you are, or the position you are in (if in
        road building mode) will be used to infer coordinates.  You can also set
        the |w-c|n option, spcifying coordinates for the new room.

        The |w-r|n or |w--road|n option can be used to change the road that
        the newly-created room will be connected to.  By default, this option
        is set to |wAUTO,|n meaning the proper address will be determined based
        on the name of the street you currently are.  You can set this to |wNONE|n
        to disable automatic road lookup, or give it a full road name, like
        |wfirst street|n.

        Examples:
          |w@new room e|n
          |w@new room sw|n
          |w@new room -c 5,10,-15|n
          |w@new room west -r NONE|n
          |w@new room n -r gray street|n

        """
        # Default parameters are set to None and modified by the context of the caller
        exit = direction = x = y = z = n_x = n_y = n_z = origin = road = None
        road_name = " ".join(args.road)
        prototype = None
        if args.prototype:
            prototype = " ".join(args.prototype)

            # Try to find the prototype
            try:
                prototype = PRoom.objects.get(db_key=prototype)
            except PRoom.DesNotExist:
                self.msg("The prototype {} doesn't exist.".format(prototype))
                return

        # Do some common checks
        info = {}
        if args.exit:
            if args.exit not in NAME_DIRECTIONS:
                self.msg("Invalid direction name: {}.".format(args.exit))
                return
            direction = NAME_DIRECTIONS[args.exit]
            info = get_direction(direction)
            exit = info["name"]

        # If caller is in road building mode, use its location
        building = self.caller.db._road_building
        if building:
            x = building["x"]
            y = building["y"]
            z = building["z"]
            room = Room.get_room_at(x, y, z)
            closest, street, exits = Crossroad.get_street(x, y, z)

            # If in a room in road building mode, take this room as the origin
            if room:
                origin = room
            elif closest and args.exit:
                if direction in exits:
                    entry = exits[direction]
                    if entry["room"]:
                        self.msg("There's already a room {} from here: {}.".format(
                                args.exit, entry["room"].key))
                        return

                    n_x, n_y, n_z = entry["coordinates"]
                    entry["name"] = street
                    road = entry
                else:
                    self.msg("This direction ({}) isn't a side of this road: {}.".format(
                            exit, street))
                    return
            elif closest:
                self.msg("You are in road building mode on {}, you must provide " \
                        "an exit name.".format(street))
                return
            else:
                self.msg("You are in road building mode, but not on a valid road.")
                return
        elif inherits_from(self.caller.location, "typeclasses.rooms.Room"):
            # The caller is in a room
            origin = self.caller.location
            x, y, z = origin.x, origin.y, origin.z
            if any(c is None for c in (x, y, z)):
                self.msg("You are in a room without valid coordinates.")
                return

            # Try to identify whether the new room would be a road
            if direction is not None:
                n_x, n_y, n_z = coords_in(x, y, z, direction)
            elif args.coordinates:
                n_x, n_y, n_z = args.coordinates

            if road_name == "AUTO":
                roads = origin.tags.get(category="road")
                roads = roads or []
                roads = [roads] if isinstance(roads, basestring) else roads
                for name in roads:
                    # Get all coordinates for this road
                    coordinates = Crossroad.get_road_coordinates(name,
                            include_road=False, include_crossroads=False)
                    if (n_x, n_y, n_z) in coordinates:
                        road = {
                                "name": name,
                                "numbers": coordinates[(n_x, n_y, n_z)],
                        }
                        break
            elif road_name != "NONE":
                # Look for the road name
                coordinates = Crossroad.get_road_coordinates(road_name,
                        include_road=False, include_crossroads=False)
                if (n_x, n_y, n_z) in coordinates:
                    road = {
                            "name": road_name,
                            "numbers": coordinates[(n_x, n_y, n_z)],
                    }
                else:
                    self.msg("Cannot find the road named '{}'.".format(
                            road_name))

        # Check that the new coordinates are not already used
        already = Room.get_room_at(n_x, n_y, n_z)
        if already is not None:
            self.msg("A room ({}) already exists here, X+{} Y={} Z={}.".format(
                    already.key, n_x, n_y, n_z))
            return

        # Create the new room
        if prototype:
            room = prototype.create()
        else:
            room = create_object("typeclasses.rooms.Room", "Nowhere")
        room.x = n_x
        room.y = n_y
        room.z = n_z
        self.msg("Creating a new room: {}(#{}) (X={}, Y={}, Z={}).".format(
                room.key, room.id, n_x, n_y, n_z))
        if road:
            name = road["name"]
            numbers = road["numbers"]
            self.msg("Adding addresses {} {} to the new room.".format(
                    "-".join(str(n) for n in numbers), name))
            room.add_address(numbers, name)

        # Create the exits if needed
        if exit and origin:
            if any(e.name == exit for e in origin.exits):
                self.msg("There already is an exit {} in the room {}.".format(
                        exit, origin.key))
            else:
                aliases = info["aliases"]
                create_object("typeclasses.exits.Exit", exit, origin,
                               aliases=aliases, destination=room)
                self.msg("Created {} exit from {} to {}.".format(
                        exit, origin.key, room.key))

        # Creating the back exit
        if info and origin:
            back = info["opposite_name"]
            if any(e.name == back for e in room.exits):
                self.msg("There already is an exit {} in the room {}.".format(
                        back, room.key))
            else:
                aliases = info["opposite_aliases"]
                create_object("typeclasses.exits.Exit", back, room,
                               aliases=aliases, destination=origin)
                self.msg("Created {} exit from {} to {}.".format(back, room.key, origin.key))
