"""Module containing utilities for the batch code."""

from textwrap import dedent
from evennia.utils import create, search

from logic.geo import direction_between
from typeclasses.objects import Object
from typeclasses.rooms import Room
from typeclasses.vehicles import Crossroad, Vehicle

# Constants
ROOM_TYPECLASS = "typeclasses.rooms.Room"
EXIT_TYPECLASS = "typeclasses.exits.Exit"
CROSSROAD_TYPECLASS = "typeclasses.vehicles.Crossroad"
ALIASES = {
        "east": ["e"],
        "south-east": ["se", "s-e"],
        "south": ["s"],
        "south-west": ["sw", "s-w"],
        "west": ["w"],
        "north-west": ["nw"],
        "north": ["n"],
        "north-east": ["ne", "n-e"],
        "down": ["d"],
        "up": ["u"],
}

# Functions
def get_room(x, y, z):
    """Get or create the given room."""
    room = Room.get_room_at(x, y, z)
    if room:
        return room

    # Create the room
    room = create.create_object(ROOM_TYPECLASS, "Nowhere")
    room.x = x
    room.y = y
    room.z = z
    return room

def get_exit(room, direction, destination, name=None, aliases=None):
    """Get or create the exit from room to destination."""
    name = name or direction
    exits = [o for o in room.contents if o.destination and o.name == name]
    if exits:
        return exits[0]

    # Create the exit
    aliases = aliases or ALIASES.get(name, [])
    exit = create.create_object(EXIT_TYPECLASS, name, room,
                   aliases=aliases, destination=destination)
    return exit

def describe(text):
    """Return the STR description.

    Simple new lines are replaced with spaces.  Double line breaks
    are considered as paragraphs.  The text is run through the dedent
    function.

    """
    lines = []
    for line in text.split("\n\n"):
        line = dedent(line.strip("\n"))
        line = line.replace("\n", " ")
        lines.append(line)

    return "\n".join(lines)

def get_crossroad(x, y, z):
    """Return or create the given crossroad."""
    crossroad = Crossroad.get_crossroad_at(x, y, z)
    if crossroad:
        return crossroad

    # Create the crossroad
    crossroad = create.create_object("typeclasses.vehicles.Crossroad", "")
    crossroad.x = x
    crossroad.y = y
    crossroad.z = z
    return crossroad

def add_road(origin, destination, name, back=True):
    """Add a road between crossroad origin and destination.

    Args:
        origin (Crossroad): the origin of the road.
        destination (Crossroad): the destination of the road.
        name (str): the name of the road to add.
        back (optional, bool): should we create a back road?

    A back road will create the same road from destination to origin
    (using the reverse direction).

    """
    x, y, z = origin.x, origin.y, origin.z
    d_x, d_y, d_z = destination.x, destination.y, destination.z
    direction = direction_between(x, y, 0, d_x, d_y, 0)
    reverse = direction_between(d_x, d_y, 0, x, y, 0)
    if direction is None:
        raise ValueError("Between {} {} and {} {} ({}), the direction " \
                "can't be found.".format(x, y, d_x, d_y, name))

    if not direction in origin.db.exits:
        coordinates = origin.add_exit(direction, destination, name)
    else:
        coordinates = origin.db.exits[direction]["coordinates"]

    if back and reverse not in destination.db.exits:
        destination.add_exit(reverse, origin, name, coordinates)
