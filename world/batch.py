# Batch-code that creates a demonstration world.

#HEADER

from textwrap import dedent
from evennia.utils import create, search
from typeclasses.objects import Object
from typeclasses.rooms import Room

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

# Get the room#2 (limbo)
center = Room.objects.get(id=2)

#CODE
# Rooms and exits
center.key = "A parking lot"
center.db.desc = describe("""
    This is really a new place, isn't it?  Not much to be
    seen, as it is.
""")

sidewalk = get_room(0, -1, 0)
sidewalk.key = "A sidewalk"
sidewalk.db.desc = describe("""
    This is a piece of sidewalk, really beautiful.
""")
sidewalk2 = get_room(-1, -1, 0)
sidewalk2.key = "A sidewalk"
sidewalk.db.desc = describe("""
    This is another piece of sidewalk, really beautiful.
""")
get_exit(sidewalk, "west", sidewalk2)
get_exit(sidewalk2, "east", sidewalk)
