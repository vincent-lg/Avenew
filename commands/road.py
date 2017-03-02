"""
This file contains the CmdRoad.
"""

from math import sqrt
import pdb
from random import choice
import sys
from textwrap import dedent

from evennia.commands.cmdset import CmdSet
from evennia.utils.create import create_object
from evennia.utils.spawner import spawn

from commands.command import Command
from logic.geo import *
from typeclasses.rooms import Room
from typeclasses.vehicles import Crossroad

# Commands
class CmdStartRoad(Command):

    """
    Enter into road building.

    Syntax:
        @road

    Type |yq|n to exit the road building mode.

    """

    key = "@road"
    locks = "cmd:id(1) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location
        if any(c is None for c in (location.x, location.y, location.z)):
            self.caller.msg("You are not in a room with valid coordinates.")
            return

        if caller.db._road_building:
            self.caller.msg("You already are in road building mode.  " \
                    "|yQuit|n to quit.")
            return

        caller.db._road_building = {
                "x": location.x,
                "y":  location.y,
                "z": location.z,
        }

        self.caller.cmdset.add("commands.road.RoadCmdSet",
                permanent=True)
        self.caller.msg(dedent("""
            You now are in road building mode.
            Move around the exits as usual, |ylook|n, use |ycross|n
            to create a crossroad, |yroad|n to create a road in
            that crossroad, |yvehicle|n to create a vehicle.  Don't
            hesitate to look at the |yhelp|n files.  Type |yq|n
            to exit this mode.
        """.strip("\n")))


class CmdLook(Command):

    """
    Look around your character.

    Usage:
        look

    This command is used to look around you.  In road building mode,
    you will see where you are (the coordinates, wherher you are
    standing at a crossroad, on a road on nowhere).

    """

    key = "look"
    aliases = ["l"]

    def func(self):
        """Execute the command."""
        building = self.caller.db._road_building
        if not building:
            self.caller.msg("Closing the building mode...")
            self.caller.cmdset.delete()
            return

        directions = {
                0: "To the east",
                1: "To the south-east",
                2: "To the south",
                3: "To the south-west",
                4: "To the west",
                5: "To the north-west",
                6: "To the north",
                7: "To the north-east",
                8: "Downward",
                9: "Upward",
        }
        opposed = {
                0: "To the west",
                1: "To the north-west",
                2: "To the north",
                3: "To the north-east",
                4: "To the east",
                5: "To the south-east",
                6: "To the south",
                7: "To the south-west",
                8: "Upward",
                9: "Downward",
        }

        x = building["x"]
        y = building["y"]
        z = building["z"]
        complex = Crossroad.get_complex()

        # Look for a room at this location
        room = Room.get_room_at(x, y, z)
        entry = complex.get((x, y, z))
        type = entry["type"] if entry else ""
        if type == "road":
            name = "A unknown street"
            if entry["crossroads"]:
                first = entry["crossroads"][0][0]
                direction = entry["crossroads"][0][1]
                name = first.db.exits[direction]["name"]

            text = dedent("""
                {name} ({x}, {y}, {z})
                This is {name}.  It is connected to:
            """.format(name=name, x=x, y=y, z=z).strip("\n"))
            for crossroad, direction in entry["crossroads"]:
                distance = int(round(sqrt((
                        crossroad.x - x) ** 2 + (crossroad.y - y) ** 2)))
                text += "\n    {}, at {}, distance {}.".format(
                        opposed[direction], crossroad.key, distance)
            self.caller.msg(text)
        elif type == "crossroad":
            crossroad = entry["crossroad"]
            text = dedent("""
                {crossroad} #{id} ({x} {y} {z})
                You are at the {crossroad} crossroad (#{id}).
            """.format(crossroad=crossroad.key, id=crossroad.id,
                    x=x, y=y, z=z).strip("\n"))
            if crossroad.db.exits:
                text += "\nAvailable roads:"
                for direction, exit in crossroad.db.exits.items():
                    direction = directions[direction]
                    name = exit["name"]
                    destination = exit["crossroad"]
                    distance = int(round(exit["distance"], 1))
                    text += "\n    {}, {} (#{}), distance {}.".format(
                            direction, name, destination.id, distance)
            else:
                text += "\n" + dedent("""
                    This crossroad has no configured route yet.
                    Use the |yroad|n command to create roads from here.
                """.strip("\n"))

            self.caller.msg(text)
        elif room:
            text = dedent("""
                {title} ({x} {y} {z})
                You are in the room {title}.
                You could have a road or even a crossroad here, but
                it's not recommended to add one.
            """.format(title=room.key, x=x, y=y, z=z).strip("\n"))
            self.caller.msg(text)
        else:
            text = dedent("""
                Nowhere ({x} {y} {z})
                You aren't in any room, on any route or on any crossroad.
                You can create a crossroad right here using the |ycross|n
                command.
                You will then have to specify possible exits (streets) from
                that crossroad.
            """.format(x=x, y=y, z=z).strip("\n"))
            self.caller.msg(text)


class CmdMove(Command):

    """
    Move using exits.
    """

    key = "move"
    aliases = list(NAME_DIRECTIONS.keys())
    autohelp = False

    def func(self):
        """Execute the command."""
        building = self.caller.db._road_building
        if not building:
            self.caller.msg("Closing the building mode...")
            self.caller.cmdset.delete()
            return

        x = building["x"]
        y = building["y"]
        z = building["z"]

        # Check that the direciton is valid
        name = self.raw_string.strip().lower()
        if name not in NAME_DIRECTIONS:
            self.caller.msg("In what direction do you wish to move?")
            return

        direction = NAME_DIRECTIONS[name]
        x, y, z = coords_in(x, y, z, direction)
        self.caller.db._road_building["x"] = x
        self.caller.db._road_building["y"] = y
        self.caller.db._road_building["z"] = z
        self.caller.execute_cmd("look")


class CmdQuit(Command):

    """
    Quit the road building mode.

    Syntax:
        quit

    Leave the road building mode.

    """

    key = "quit"
    aliases = ["q"]

    def func(self):
        """Execute the command."""
        self.caller.msg("Quitting the road building mode.")
        self.caller.cmdset.delete()
        del self.caller.db._road_building


class CmdCross(Command):

    """
    Create a crossroad where you are.

    Syntax:
        cross <name of the crossroad to create>

    This command can be used to create a crossroad where you are in
    road building mode.  You will need to specify a name for the
    crossroad: this name won't be visible by players, and will
    just serve as a reference to you and other builders.  It doesn't
    have to be unique.  It's usually short and indicate what road
    it can join.  Following a given convention, the crossroad named
    3-8 could be joining third street with eighth avenue.

    Aliases:
        cr

    """

    key = "cross"
    aliases = ["cr"]
    help_category = "road building"

    def func(self):
        """Execute the command."""
        building = self.caller.db._road_building
        if not building:
            self.caller.msg("Closing the building mode...")
            self.caller.cmdset.delete()
            return

        x = building["x"]
        y = building["y"]
        z = building["z"]

        command = self.args.strip()
        if not command:
            self.caller.msg("Specify the name of this crossroad.")
            return

        # Check that there is no crossroad here
        complex = Crossroad.get_complex()
        entry = complex.get((x, y, z))
        if entry and entry["type"] == "crossroad":
            self.caller.msg("A crossroad already exists here.")
            return

        # Create the crossroad
        crossroad = create_object("vehicles.Crossroad", key=command,
                nohome=True)

        # Set the coordinates
        crossroad.tags.add(str(x), category="coordx")
        crossroad.tags.add(str(y), category="coordy")
        crossroad.tags.add(str(z), category="coordz")
        self.caller.msg("The crossroad {} (#{}) has been created here.".format(
                crossroad.key, crossroad.id))
        self.caller.msg("Use the |yroad|n command to create roads " \
                "from this crossroad.")

class CmdRoad(Command):

    """
    Create a road from the crossroad where you are.

    Syntax:
        road <direction> <destination ID> <name of the road>

    This command is used to create a road originating from the
    crossroad where you are in road building mode.  A crossroad can
    have one, two or more roads connected to it.  You must provide as
    first argument the direction of the road, for instance |yeast|n
    (you can use short names, like |ye|n).  The second argument should
    be the ID of the crossroad you want to connect to.  You have
    access to the ID when you use the |ycross|n command, or when you
    walk around in road building mode.  The third argument is the
    name of the street to be created.  Players will see this name,
    when turning onto this road or a little before, when deciding
    where to go.  It will also show on the control panel of the
    vehicle, as a constant reminder.

    Example:
        road east 8 First street

    Assuming #8 is a crossroad that is directly east from here.
    It will also create a return route (from #8 to here).

    Aliases:
        r

    """

    key = "road"
    aliases = ["r"]
    help_category = "road building"

    def func(self):
        """Execute the command."""
        building = self.caller.db._road_building
        x = building["x"]
        y = building["y"]
        z = building["z"]

        # Check that there is a crossroad here
        complex = Crossroad.get_complex()
        entry = complex.get((x, y, z))
        if entry is None or entry["type"] != "crossroad":
            self.caller.msg("There is no crossroad here.")
            return

        crossroad = entry["crossroad"]
        command, s, remaining = self.args.strip().partition(" ")

        # The first parameter is a direction
        direction = NAME_DIRECTIONS.get(command.lower())
        if direction is None:
            self.caller.msg("The direction {} doesn't exist.".format(
                    command))
            return

        # The second parameter should be an ID
        id, s, name = remaining.partition(" ")

        # Check that this refer to a crossroad
        if id.startswith("#"):
            id = id[1:]

        try:
            destination = Crossroad.objects.get(id=id)
        except (Crossroad.DoesNotExist, ValueError):
            self.caller.msg("The crossroad of ID {} doesn't exist.".format(id))
            return

        # Before continuing, check that the crossroad is in this direction
        if direction_between(x, y, z, destination.x, destination.y,
                destination.z) != direction:
            self.msg("The specified crossroad (#{}) isn't in that " \
                    "direction.".format(destination.id))
            return

        # Finally, check that there is a name
        if not name.strip():
            self.caller.msg("Specify a name for this road.")
            return

        # Everything seems okay, add the exit
        crossroad.add_exit(direction, destination, name)
        destination.add_exit(OPP_DIRECTIONS[direction], crossroad, name)
        self.caller.msg("There is now a road from this crossroad " \
               "leading to the crossroad {} (#{}), called {}.".format(
               destination.key, destination.id, name))


class CmdVehicle(Command):

    """
    Create a vehicle where you stand in road building mode.

    Usage:
        vehicle <name of the vehicle>

    This command can be used to create a vehicle at the crossrsoad where
    you stand in road building mode.  You can put an plus sign (+)
    before the name of the vehicle, to force a room to be created
    inside of it.  If the sign isn't present, the vehicle is created
    with no room, which makes it a "fake" vehicle that will be
    automatically controlled by the system.

    Example:
        vehicle dodge pick-up ford

    Aliases:
        v

    """

    key = "vehicle"
    aliases = ["v"]
    help_category = "road building"

    def func(self):
        """Execute the command."""
        building = self.caller.db._road_building
        x = building["x"]
        y = building["y"]
        z = building["z"]

        # Check that there is a crossroad here
        complex = Crossroad.get_complex()
        entry = complex.get((x, y, z))
        if entry is None or entry["type"] != "crossroad":
            self.caller.msg("There is no crossroad here.")
            return

        with_room = False
        command = self.args.strip()
        if command.startswith("+"):
            command = command[1:]
            with_room = True

        if not command.strip():
            self.caller.msg("Specify the name of the vehicle you want " \
                    "to create.")
            return

        # Create the vehicle
        vehicle = create_object("vehicles.Vehicle", key=command,
                nohome=True)
        vehicle.db.coords = (x, y, z)

        # Set the vehicle in a random direction
        crossroad = entry["crossroad"]
        direction, destination = choice(crossroad.db.exits.items())
        destination = destination["crossroad"]
        vehicle.db.previous_crossroad = crossroad
        vehicle.db.next_crossroad = destination
        vehicle.db.direction = direction
        self.caller.msg("The vehicle {} (#{}) has been created.".format(
                vehicle.key, vehicle.id))

        # Create the room
        if with_room:
            room = create_object("rooms.VehicleRoom",
                    key="Inside of the vehicle", location=vehicle)
            self.caller.msg("The room #{} has been added in the " \
                    "vehicle.".format(room.id))


# Command set
class RoadCmdSet(CmdSet):

    key = "road building"
    priority = 102

    def at_cmdset_creation(self):
        self.add(CmdLook())
        self.add(CmdMove())
        self.add(CmdQuit())
        self.add(CmdCross())
        self.add(CmdRoad())
        self.add(CmdVehicle())
