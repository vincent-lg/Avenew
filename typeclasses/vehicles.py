"""
Vehicles

"""

import pdb
from math import sqrt
from random import choice
import sys

from evennia import DefaultObject

# Constants
DIRECTIONS = {
    0: "East",
    1: "South-east",
    2: "South",
    3: "South-west",
    4: "West",
    5: "North-west",
    6: "North",
    7: "North-east",
    8: "Down",
    9: "Up",
}

class Crossroad(DefaultObject):

    """A crossroad, used to set up the route system.

    A crossroad is like a simplified room.  It can't be travelled or
    seen by players, and is only used by the vehicle system to lead
    them, much like tracks for a train.  A crossroad is set at a given
    position (given its X, Y and Z coords) and can have several
    possible "exits" pointing to other crossroads.  These exits are
    fixed in direction, and must be straight (a road with turns
    would need a crossroad to map the turning point, even though
    players may not be aware of it).

    """

    @classmethod
    def get_complex(cls):
        """Return the entire complex as a dictionary of coordinates.

        This method SHOULD NOT be used in cases when performances
        count, specifically in background tasks, such as moving a
        vehicle.  It should only be called for building tasks, and
        if possible, be optimized.  It will query all crossroads and
        cache them, which may amount to some building.  It will also
        try to create an accurate map with crossroads and routes.

        Returns:
            A dictionary containing, as keys, the coordinates
            (x, y, z) and as values, another dict containing the
            type of object and some additional information.

        Example:
            complex = Crossroad.get_complex()
            at = complex.get((0, 0, 0))
            # at is None if nothing is there
            # It might contain a dictionary to indicate a road or crossroad
            if at:
                type = at["type"]
                # type can be 'road' or 'crossroad'
                if type == "road":
                    directions = at["directions"]
                    # The directions in which open crossroads stand
                elif type == "crossroad":
                    crossroad = at["crossroad"]

        """
        crossroads = cls.objects.all()
        reverse = {
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
        m_coords = {
            0: (1, 0, 0),
            1: (1, -1, 0),
            2: (0, -1, 0),
            3: (-1, -1, 0),
            4: (-1, 0, 0),
            5: (-1, 1, 0),
            6: (0, 1, 0),
            7: (1, 1, 0),
            8: (0, 0, -1),
            9: (0, 0, 1),
        }

        # Building the map
        map = {}
        for crossroad in crossroads:
            x, y, z = crossroad.x, crossroad.y, crossroad.z
            if any(c is None for c in (x, y, z)):
                continue

            map[(x, y, z)] = {
                    "type": "crossroad",
                    "crossroad": crossroad,
            }

            # Now, look for all routes
            for direction, exit in crossroad.db.exits.items():
                # Trace the straight street until next crossroad
                exit = exit["crossroad"]
                d_x, d_y, d_z = exit.x, exit.y, exit.z
                contrary = reverse[direction]
                t_x, t_y, t_z = x, y, z
                m_x, m_y, m_z = m_coords[direction]
                while (t_x, t_y) != (d_x, d_y):
                    t_x += m_x
                    t_y += m_y
                    t_z += m_z
                    if (t_x, t_y, t_z) not in map:
                        map[(t_x, t_y, t_z)] = {
                                "type": "road",
                                "crossroads": [
                                    (crossroad, direction),
                                ],
                        }
                    else:
                        present = map[(t_x, t_y, t_z)]
                        if present["type"] == "road":
                            present["crossroads"].append((crossroad, direction))

                    # Add a check to make sure we're still on track

        return map

    @classmethod
    def get_crossroad_at(cls, x, y, z):
        """
        Return the crossroad at the given location or None if not found.

        Args:
            x (int): the X coord.
            y (int): the Y coord.
            z (int): the Z coord.

        Return:
            The crossroad at this location (Room) or None if not found.

        """
        crossroads = cls.objects.filter(
                db_tags__db_key=str(x), db_tags__db_category="coordx").filter(
                db_tags__db_key=str(y), db_tags__db_category="coordy").filter(
                db_tags__db_key=str(z), db_tags__db_category="coordz")
        if crossroads:
            return crossroadss[0]

        return None

    def _get_x(self):
        """Return the X coordinate or None."""
        x = self.tags.get(category="coordx")
        return int(x) if isinstance(x, str) else None
    def _set_x(self, x):
        """Change the X coord."""
        old = self.tags.get(category="coordx")
        if old is not None:
            self.tags.remove(old, category="coordx")
        self.tags.add(str(x), category="coordx")
    x = property(_get_x, _set_x)

    def _get_y(self):
        """Return the Y coordinate or None."""
        y = self.tags.get(category="coordy")
        return int(y) if isinstance(y, str) else None
    def _set_y(self, y):
        """Change the Y coord."""
        old = self.tags.get(category="coordy")
        if old is not None:
            self.tags.remove(old, category="coordy")
        self.tags.add(str(y), category="coordy")
    y = property(_get_y, _set_y)

    def _get_z(self):
        """Return the Z coordinate or None."""
        z = self.tags.get(category="coordz")
        return int(z) if isinstance(z, str) else None
    def _set_z(self, z):
        """Change the Z coord."""
        old = self.tags.get(category="coordz")
        if old is not None:
            self.tags.remove(old, category="coordz")
        self.tags.add(str(z), category="coordz")
    z = property(_get_z, _set_z)

    def at_object_creation(self):
        self.db.exits = {}

    def refresh_tag(self, name):
        """Reset the tag if not present."""
        name = name.lower()
        if not self.tags.get(name, category="road"):
            self.tags.add(name, category="road")

    def refresh_tags(self):
        """Refresh all tags."""
        for info in self.db.exits.values():
            name = info.get("name")
            if name:
                self.refresh_tag(name)

    def add_exit(self, direction, crossroad, name):
        """
        Add a new exit in the given direction.

        Args:
            direction (int): the direction (0 for east, 1 for south-east...)
            crossroad (Crossroad): the destination (another crossroad)
            name (str): name of the exit (like "eight street")

        If there already was a crossroad in this direction, replace it.
        The given crossroad has to be logically set (if you give a
        direction of 0, the crossroad should be straight to the east
        of the configured position).

        """
        # Check the geographical logic
        # Get the distance between self and crossroad
        x, y, z = self.x, self.y, self.z
        d_x, d_y, d_z = crossroad.x, crossroad.y, crossroad.z
        distance = sqrt((d_x - x) ** 2 + (d_y - y) ** 2)
        self.db.exits[direction] = {
                "crossroad": crossroad,
                "distance": distance,
                "name": name,
        }
        self.refresh_tag(name)

    def del_exit(self, direction):
        """
        Delete the exit in the given direction.

        This method doesn't delete the crossroad in this direction.
        It simply removes the current exit to it, you can link it
        again if you want.

        Args:
            direction (int): the direction (0 for east, 1 for south-east...)

        """
        name = None
        if direction in self.db.exits:
            info = self.db.exits.pop(direction)
            name = info.get(name)

        if name and self.tags.get(name, category="road"):
            self.tags.remove(name, category="road")


class Vehicle(DefaultObject):

    """
    A vehicle driven on a road complex.

    A vehicle may contain one or more rooms, that will, in turn,
    contain characters, objects and more.  A vehicle has, itself,
    a specific position (stored in .db.coords, as a tuple (x, y, z))
    and can be set on a route.  A vehicle doesn't travel from room to
    room, it is not contained in a room, except when it is "parked"
    and characters can enter or leave it.
    A vehicle also has a direction (0 => east, 1 => southeast, 2 = south...)
    and a speed.

    The route complex is set using crossroads (see the Crossroad class
    above).  A crossroad is the point of the road when it can offer
    several "exits"..  A crossroad is merely a simplified room.  Each
    crossroad stores the possible destinations from there.  A crossroad
    with no exits is a dead-end:  vehicles can drive there, but unless
    they turn around, they can't go forward.  Vehicles store the
    previous crossroad and next crossroad to help them navigate
    effectively.

    """

    to_edit = {
            "name": "key",
            "speed": {
                    "attr": "db.speed",
                    "type": "int",
                    "valid": lambda speed: speed >= 0,
            },
    }

    def at_object_creation(self):
        self.db.coords = (None, None, None)
        self.db.driver = None
        self.db.direction = 0
        self.db.speed = 0
        self.db.constant_speed = 0
        self.db.desired_speed = 0
        self.db.previous_crossroad = None
        self.db.next_crossroad = None

    def msg_contents(self, msg):
        """Send a message to all the vehicle's content (presumably rooms)."""
        for object in self.contents:
            object.msg_contents(msg)

    def control_panel(self, looker):
        """Return the control panel of the vehicle."""
        speed = int(round(self.db.speed))
        n_direction = self.db.direction
        direction = DIRECTIONS[n_direction]
        previous = self.db.previous_crossroad
        next = self.db.next_crossroad
        street = previous.db.exits[n_direction]["name"]
        string = "{{{{{:>2}}} {} - {}".format(speed, direction, street)
        if self.locks.check_lockstring(looker, "perm(Builders)"):
            x, y, z = self.db.coords
            x = int(round(x))
            y = int(round(y))
            z = int(round(z))
            string += ", {},{},{} from {} to {}".format(x, y, z,
                    previous.key, next.key)

        return string

    def move(self):
        """
        Move the vehicle.

        This method is called by the system every 3 seconds.
        "Fake" vehicles (without any rooms) move automatically.
        Vehicles with drivers move too.

        """
        if self.db.driver or not self.contents:
            if self.contents:
                control = self.control_panel(self.db.driver)

            distance = self.vary_speed()
            self.go_on(distance)
            if self.contents:
                new_control = self.control_panel(self.db.driver)
                if control != new_control:
                    self.db.driver.msg(new_control)

    def go_on(self, distance):
        """Move distance in set direction.

        Args:
            distance (flat, optional): the distance to move.

        If the next crossroad is on the path, moves right onto it.

        """
        x, y, z = self.db.coords
        direction = self.db.direction
        previous = self.db.previous_crossroad
        next = self.db.next_crossroad
        if previous is None or next is None:
            return

        n_x, n_y, n_z = next.x, next.y, next.z

        # If the vehicle is in a crossroad, select logical exit or
        # raise a RuntimeError
        #mypdb = pdb.Pdb(stdout=sys.__stdout__)
        #mypdb.set_trace()
        if (x, y, z) == (n_x, n_y, n_z):
            destinations = [(direction, exit["crossroad"]) for \
                    direction, exit in next.db.exits.items()]
            destinations = [(dir, dest) for dir, dest in destinations \
                    if dest is not previous]
            if len(destinations) == 0:
                return
            if len(destinations) > 1:
                destinations = [choice(destinations)]

            self.db.previous_crossroad = next
            self.db.next_crossroad = destinations[0][1]
            self.change_direction(destinations[0][0])
            next = self.db.next_crossroad
            n_x, n_y, n_z = next.x, next.y, next.z
            direction = self.db.direction

        between = sqrt((n_x - x) ** 2 + (n_y - y) ** 2)
        if between <= distance:
            # The vehicle has moved in the crossroad (not checking Z)
            self.db.coords = (n_x, n_y, n_z)
        else:
            if between <= distance * 2 and self.db.constant_speed > 16:
                self.db.constant_speed = 16
            elif self.db.constant_speed != self.db.desired_speed:
                self.db.constant_speed = self.db.desired_speed

            # Do move in the specified direction
            if direction == 0: # East
                x += distance
            elif direction == 1: # South-east
                x += 1 / sqrt(2) * distance
                y -= 1 / sqrt(2) * distance
            elif direction == 2: # South
                y -= distance
            elif direction == 3: # South-wast
                x -= 1 / sqrt(2) * distance
                y -= 1 / sqrt(2) * distance
            elif direction == 4: # West
                x -= distance
            elif direction == 5: # North-wast
                x -= 1 / sqrt(2) * distance
                y += 1 / sqrt(2) * distance
            elif direction == 6: # North
                y += distance
            elif direction == 7: # North-east
                x += 1 / sqrt(2) * distance
                y += 1 / sqrt(2) * distance
            else:
                raise ValueError("invalid direction {}".format(direction))

            x = round(x, 3)
            y = round(y, 3)
            z = round(z, 3)
            self.db.coords = (x, y, z)

    def vary_speed(self):
        """Change the speed and warn passengers."""
        if self.db.constant_speed is None:
            self.db.constant_speed = 0
        if self.db.desired_speed is None:
            self.db.desired_speed = 0

        old = self.db.speed
        constant = self.db.constant_speed
        diff = constant - old
        if diff > 0:
            # The vehicle doesn't move as quickly as the constant speed
            if diff < 4:
                self.db.speed = constant
            else:
                self.db.speed += 4
        elif diff < 0:
            # The vehicle moves faster than the constant speed
            if diff > -15:
                self.db.speed = constant
            else:
                self.db.speed -= 15

        return self.speed_to_distance(self.db.speed)

    def change_direction(self, direction):
        """Have the vehicle change direction.

        This method will display a message if appropriate.

        """
        old_direction = self.db.direction
        self.db.direction = direction
        previous = self.db.previous_crossroad
        road = previous.db.exits[direction]["name"]
        diff = direction - old_direction
        msg = ""
        side = "left" if diff < 0 else "right"
        if diff == 0:
            msg = "You go foward and take {road}."
        elif diff in (-1, 1):
            msg = "You slightly turn to the {side} on {road}."
        elif diff in (-2, 2):
            msg = "You veer off to the {side} on {road}."
        elif diff in (-3, 3):
            msg = "You take a very sharp turn to the {side} on {road}."
        elif diff in (4, -4):
            msg = "An illegal U turn and you're going back on {road}."

        if msg:
            self.msg_contents(msg.format(side=side, road=road))


    @staticmethod
    def speed_to_distance(speed):
        return speed / 16.0
