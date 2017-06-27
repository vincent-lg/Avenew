"""
Module used to handle simple but frequent calculations over directions.

It also handles a basic representation of coordinates in 2 or 3 dimensions.

"""

from math import fabs

## Constants
NAME_DIRECTIONS = {
        "east": 0,
        "southeast": 1,
        "south": 2,
        "southwest": 3,
        "west": 4,
        "northwest": 5,
        "north": 6,
        "northeast": 7,
        "down": 8,
        "up": 9,

        # Aliases
        "e": 0,
        "se": 1,
        "s": 2,
        "sw": 3,
        "w": 4,
        "nw": 5,
        "n": 6,
        "ne": 7,
        "d": 8,
        "u": 9,
}

NAME_OPP_DIRECTIONS = {
        0: "east",
        1: "southeast",
        2: "south",
        3: "southwest",
        4: "west",
        5: "northwest",
        6: "north",
        7: "northeast",
        8: "down",
        9: "up"
}

OPP_DIRECTIONS = {
        0: 4,
        1: 5,
        2: 6,
        3: 7,
        4: 0,
        5: 1,
        6: 2,
        7: 3,
        8: 9,
        9: 8,
}

ALIAS_DIRECTIONS = {
        0: ["e"],
        1: ["se", "s-e"],
        2: ["s"],
        3: ["sw", "s-w"],
        4: ["w"],
        5: ["nw", "n-w"],
        6: ["n"],
        7: ["ne", "n-e"],
        8: ["d"],
        9: ["u"],
}

## Functions
def coords_in(x, y, z, direction, distance=1):
    """Return the tuple of coords in the given direction.

    The direction should be given as an integer, 0 for east, 1 for
    southeast, 2 for south and so on.

    Args:
        x (int): the X coordinate.
        y (int): the Y coordinate.
        z (int): the Z coordinate.
        direction (int): the direction.
        distance (optional): the distance in coords.

    Returns:
        The tuple of x, y and z of new coordinates.

    """
    if direction == 0: # East
        x += distance
    elif direction == 1: # South-east
        x += distance
        y -= distance
    elif direction == 2: # South
        y -= distance
    elif direction == 3:
        x -= distance
        y -= distance
    elif direction == 4: # West
        x -= distance
    elif direction == 5: # North-west
        x -= distance
        y += distance
    elif direction == 6: # North
        y += distance
    elif direction == 7: # North-east
        x += distance
        y += distance
    elif direction == 8: # Down
        z -= distance
    elif direction == 9: # Up
        z += distance
    else:
        raise ValueError("the specified direction {} is invalid.".format(
                direction))

    return x, y, z

def direction_between(x1, y1, z1, x2, y2, z2):
    """Find the exact direction between two sets of coords.

    If the first set is 0, 0, 0 and the second 0, 1, 0, then returns
    6 (that is, north).  If there is no perfect direction between
    them, return None.

    """
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    if dx > 0 and dy == 0 and dz == 0: # East
        return 0
    elif dx > 0 and dy == -dx and dz == 0: # Southeast
        return 1
    elif dx == 0 and dy < 0 and dz == 0: # South
        return 2
    elif dx < 0 and dy == dx and dz == 0: # Southwest
        return 3
    elif dx < 0 and dy == 0 and dz == 0: # West
        return 4
    elif dx < 0 and dy == -dx and dz == 0: # Northwest
        return 5
    elif dx == 0 and dy > 0 and dz == 0: # North
        return 6
    elif dx > 0 and dy == dx and dz == 0: # Northeast
        return 7
    elif dx == 0 and dy == 0 and dz < 0:
        return 8
    elif dx == 0 and dy == 0 and dz > 0:
        return 9
    else:
        return None

def distance_between(x1, y1, z1, x2, y2, z2):
    """
    Return the relative distance between two coordinates.

    IMPORTANT: the relative distance between two points will not be
    absolutely measured.  Instead, the greatest difference between
    axis will be returned.  It means that the relative distance between
    0 0 0 and 2 2 0 is 2, not sqrt(4).

    """
    dx = int(fabs(x2 - x1))
    dy = int(fabs(y2 - y1))
    dz = int(fabs(z2 - z1))
    return max(dx, dy, dz)

def coords(string, allow_float=False):
    """
    Return, if found, a tuple of numbers.

    Args:
        string (str): the string containing the "X Y Z".
        allow_float (bool, optional): allow floating coordinates?

    Returns:
        The tuple containing the three numbers (X, Y, Z) extracted
        from the string.

    Raises:
        ValueError: the format cannot be used.

    """
    # Remove beginning or ending parenthesis if necessary
    string = string.lstrip("(").rstrip(")")

    # string could be X,Y,Z
    if "," in string:
        coords = string.split(",")
    else:
        coords = string.split(" ")

    if len(coords) != 3:
        raise ValueError("wrong number of coordinates, must be X Y Z")

    converter = float if allow_float else int
    try:
        x = converter(coords[0].strip())
    except ValueError:
        raise ValueError("wrong value for X: {}".format(coords[0]))

    try:
        y = converter(coords[1].strip())
    except ValueError:
        raise ValueError("wrong value for Y: {}".format(coords[1]))

    try:
        z = converter(coords[2].strip())
    except ValueError:
        raise ValueError("wrong value for Z: {}".format(coords[2]))

    return (x, y, z)

def get_direction(direction):
    """
    Return information on the provided direction.

    Args:
        direction (int): a direction number (between 0 and 9).

    Returns:
        A dictionary containing the name of the direction, aliases, and
        opposite directions.

    """
    name = NAME_OPP_DIRECTIONS[direction]
    aliases = ALIAS_DIRECTIONS[direction]
    opp_direction = OPP_DIRECTIONS[direction]
    opp_name = NAME_OPP_DIRECTIONS[opp_direction]
    opp_aliases = ALIAS_DIRECTIONS[opp_direction]
    return {
            "name": name,
            "aliases": aliases,
            "opposite_direction": opp_direction,
            "opposite_name": opp_name,
            "opposite_aliases": opp_aliases,
    }
