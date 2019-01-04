# -*- coding: utf-8 -*-

"""
This file contains the CmdRoad.
"""

from math import sqrt
import pdb
from random import choice
import sys
import time
from textwrap import dedent

from evennia.commands.cmdset import CmdSet
from evennia.utils.create import create_object

from commands.command import Command
from logic.geo import *
from logic.gps import GPS
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
                "y": location.y,
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
            self.caller.cmdset.remove("commands.road.RoadCmdSet")
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

        # Look for a room at this location
        crossroad = Crossroad.get_crossroad_at(x, y, z)
        room = Room.get_room_at(x, y, z)
        closest, street, exits = Crossroad.get_street(x, y, z)
        if crossroad:
            text = dedent("""
                Crossroad #{id} ({x} {y} {z})
                You are at the crossroad #{id}.
            """.format(id=crossroad.id, x=x, y=y, z=z).strip("\n"))
            if crossroad.db.exits:
                text += "\nAvailable roads:"
                for direction, exit in crossroad.db.exits.items():
                    direction = directions[direction]
                    name = exit["name"]
                    destination = exit["crossroad"]
                    distance = int(round(exit["distance"], 1))
                    slope = exit["slope"]
                    text += "\n    {}, {} (#{}), distance {}, slope {}.".format(
                            direction, name, destination.id, distance, slope)
            else:
                text += "\n" + dedent("""
                    This crossroad has no configured route yet.
                    Use the |yroad|n command to create roads from here.
                """.strip("\n"))

            self.caller.msg(text)
        elif closest:
            name = street
            text = dedent("""
                {name} ({x}, {y}, {z})
                This is {name}.  It is connected:
            """.format(name=name, x=x, y=y, z=z).strip("\n"))
            crossroads = Crossroad.get_crossroads_with(x, y, z)
            for crossroad in crossroads:
                infos = [v for v in crossroad.db.exits.values() if \
                        (x, y, z) in v["coordinates"]]
                if not infos:
                    continue

                info = infos[0]
                direction = info["direction"]
                distance = int(round(sqrt((
                        crossroad.x - x) ** 2 + (crossroad.y - y) ** 2)))
                text += "\n    {}, at #{}, distance {}, slope {}.".format(
                        opposed[direction], crossroad.id, distance,
                        info["slope"])

            # Display the coordinates on either side
            left = exits["left"]
            left_direction = left["direction"]
            left_numbers = "-".join([str(n) for n in left["numbers"]])
            if left["room"]:
                left = left["room"].key
            else:
                left = " ".join([str(c) for c in left["coordinates"]])
            right = exits["right"]
            right_direction = right["direction"]
            right_numbers = "-".join([str(n) for n in right["numbers"]])
            if right["room"]:
                right = right["room"].key
            else:
                right = " ".join([str(c) for c in right["coordinates"]])
            text += "\n    {}, {} {}: {}".format(directions[left_direction],
                    left_numbers, street.lower(), left)
            text += "\n    {}, {} {}: {}".format(directions[right_direction],
                    right_numbers, street.lower(), right)
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
        cross/add

    This command can be used to create a crossroad where you are in
    road building mode.

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

        # Check that there is no crossroad here
        already = Crossroad.get_crossroad_at(x, y, z)
        if already:
            self.caller.msg("A crossroad already exists here.")
            return

        if not self.args.strip().lower() == "/add":
            self.msg(self.args)
            return

        # Create the crossroad
        crossroad = create_object("vehicles.Crossroad", key="",
                nohome=True)

        # Set the coordinates
        crossroad.x = x
        crossroad.y = y
        crossroad.z = z
        self.caller.msg("The crossroad (#{}) has been created here.".format(
                crossroad.id))
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
    name of the street to be created.  Accounts will see this name,
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
        crossroad = Crossroad.get_crossroad_at(x, y, z)
        if crossroad is None:
            self.caller.msg("There is no crossroad here.")
            return

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
        if direction_between(x, y, 0, destination.x, destination.y,
                0) != direction:
            self.msg("The specified crossroad (#{}) isn't in that " \
                    "direction.".format(destination.id))
            return

        # Finally, check that there is a name
        if not name.strip():
            self.caller.msg("Specify a name for this road.")
            return

        # Everything seems okay, add the exit
        coords = crossroad.add_exit(direction, destination, name)
        destination.add_exit(OPP_DIRECTIONS[direction], crossroad, name,
                        coordinates=coords)
        self.caller.msg("There now is a road from this crossroad " \
               "leading to the crossroad {} (#{}), called {}.".format(
               destination.key, destination.id, name))


class CmdVehicle(Command):

    """
    Create a vehicle where you stand in road building mode.

    Usage:
        vehicle <name of the vehicle>

    This command can be used to create a vehicle at the crossrsoad where
    you stand in road building mode.  You can put a plus sign (+)
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
        crossroad = Crossroad.get_crossroad_at(x, y, z)
        if crossroad is None:
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


class CmdCompass(Command):

    """
    Use a compass to locate a crossroad.

    Usage:
        compass <crossroad ID>

    This will attempt to find the 2D direction between where you are
    and the specified crossroad.

    """

    key = "compass"
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

        cid = self.args.strip()
        if not cid:
            self.msg("Specify the crossroad ID.")
            return

        if cid.startswith("#"):
            cid = cid[1:]

        if not cid.isdigit():
            self.msg("Invalid crossroad ID.")
            return

        try:
            crossroad = Crossroad.objects.get(id=int(cid))
        except Crossroad.DoesNotExist:
            self.caller.msg("The crossroad of ID {} doesn't exist.".format(cid))
            return

        # Try to obtain the 2D direction
        direction = direction_between(x, y, 0, crossroad.x, crossroad.y, 0)
        if direction is None:
            self.msg("The crossroad #{} isn't in any straight " \
                    "direction from here.".format(crossroad.id))
            return

        self.msg("The crossroad #{} is in direction {}.".format(
                crossroad.id, NAME_OPP_DIRECTIONS[direction]))


class CmdGPS(Command):

    """
    Use the GPS to find a path.

    Usage:
        gps <address of destination>

    This will attempt to find the path between your current location and
    the specified address.

    Example:
        gps 5 north star

    """

    key = "GPS"
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
        crossroad = Crossroad.get_crossroad_at(x, y, z)
        if crossroad is None:
            self.msg("You are not standing at a crossroad, cannot use the GPS.")
            return

        address = self.args.strip()
        if not address:
            self.msg("Enter the address of the destination.")
            return

        # Try to find the address
        t1 = time.time()
        try:
            gps = GPS(crossroad, address)
            t2 = time.time()
        except ValueError as e:
            e = str(e)
            self.msg(e[0].upper() + e[1:] + ".")
            return

        # Now get the path
        t3 = time.time()
        gps.find_path()
        t4 = time.time()
        tt1 = round(t2 - t1, 4)
        tt2 = round(t4 - t3, 4)
        text = dedent("""
            Searching address: {}.
            Address found in {} seconds.
            GPS found path in {} seconds.
            Shortest path in {} hops:
        """.strip("\n").format(address, tt1, tt2, len(gps.path)))

        directions = {
                0: "to the east",
                1: "to the south-east",
                2: "to the south",
                3: "to the south-west",
                4: "to the west",
                5: "to the north-west",
                6: "to the north",
                7: "to the north-east",
                8: "downward",
                9: "upward",
        }

        # Display all the hops
        i = 1
        for origin, direction, destination in gps.path:
            direction = directions[direction]
            if isinstance(origin, tuple):
                o_x, o_y, o_z = origin
                origin = "X={} Y={} Z={}".format(*origin)
            elif isinstance(origin, Room):
                o_x, o_y, o_z = origin.x, origin.y, origin.z
                origin = origin.key
            else:
                o_x, o_y, o_z = origin.x, origin.y, origin.z
                origin = "#{}".format(origin.id)

            if isinstance(destination, tuple):
                d_x, d_y, d_z = destination
                destination = "X={} Y={} Z={}".format(*destination)
            elif isinstance(destination, Room):
                d_x, d_y, d_z = destination.x, destination.y, destination.z
                destination = destination.key
            else:
                d_x, d_y, d_z = destination.x, destination.y, destination.z
                destination = "#{}".format(destination.id)

            distance = distance_between(o_x, o_y, 0, d_x, d_y, 0)
            text += "\n{:>2} {}, from {} to {}, distance {}.".format(
                    i, direction, origin, destination, distance)
            i += 1

        self.msg(text)


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
        self.add(CmdCompass())
        self.add(CmdGPS())
