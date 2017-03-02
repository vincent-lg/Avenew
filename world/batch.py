# Batch-code that creates a demonstration world.

#HEADER

from textwrap import dedent
from evennia.utils import create, search
from typeclasses.objects import Object
from typeclasses.rooms import Room

# Constants
ROOM_TYPECLASS = "typeclasses.rooms.Room"
EXIT_TYPECLASS = "typeclasses.exits.Exit"
ROOM_LOCKSTRING = "control:id(1) or perm(Wizards); " \
                          "delete:id(1) or perm(Wizards); " \
                          "edit:id(1) or perm(Wizards)"

# Functions
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
center.key = "A magnificient hotel"
center.db.desc = describe("""
    You are standing in front of a magnificient hotel.  A few marble
    steps lead to the heavy wooden doors, into a hall that, judging
    from outside, is gigantic, to say the least.

    Behind you, to the south, is a large alleyway leading to a parking
    lot and, still beyond, a busy street.
""")

# Create the hotel hall
hall = create.create_object(ROOM_TYPECLASS, "A splendid hall")
hall.db.desc = describe("""
    This is a magnificent hotel hall, surrounded by plants and a
    large counter in the far corner.  A set of heavy doors leading
    south outside of the hall, while corridors lead further into
    this hotel.
""")
hall.locks.add(ROOM_LOCKSTRING)
create.create_object(EXIT_TYPECLASS, "north", center,
                   aliases=["n", "hall", "hotel"],
                   locks=ROOM_LOCKSTRING,
                   destination=hall)
create.create_object(EXIT_TYPECLASS, "south", hall,
                   aliases=["s", "out", "outside"],
                   locks=ROOM_LOCKSTRING,
                   destination=center)
