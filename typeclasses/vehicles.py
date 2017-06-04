"""
Vehicles

"""

import pdb
from math import fabs, sqrt
from random import choice
import sys

from evennia import DefaultObject

from logic.geo import NAME_DIRECTIONS, coords_in, direction_between, distance_between
from typeclasses.rooms import Room

# Constants
DIRECTIONS = NAME_DIRECTIONS

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
            return crossroads[0]

        return None

    @classmethod
    def get_crossroads_road(cls, road, city=None):
        """
        Get the list of crossroads connected to a road.

        Args:
            road (str): the road's name.
            city (str, optional): the city name to filter search.

        Returns:
            The list of found crossroads directly connected.

        """
        road = road.lower().strip()
        if city:
            city = city.lower().strip()
            crossroads = cls.objects.filter(
                    db_tags__db_key=road, db_tags__db_category="road").filter(
                    db_tags__db_key=city, db_tags__db_category="city")
        else:
            crossroads = cls.objects.filter(
                    db_tags__db_key=road, db_tags__db_category="road")

        # Sort by crossroad ID
        crossroads = sorted(list(crossroads), key=lambda c: c.id)
        return crossroads

    @classmethod
    def get_crossroads_with(cls, x, y, z):
        """
        Return the crossroads with a street leading to that coordinate.

        Args:
            x (int): the X coord.
            y (int): the Y coord.
            z (int): the Z coord.

        Return:
            The list of crossroads having a direct path to this coordinate.

        """
        tag = "{} {} {}".format(x, y, z)
        crossroads = cls.objects.filter(
                db_tags__db_key=tag, db_tags__db_category="croad")

        return crossroads

    @classmethod
    def get_street(cls, x, y, z, city=None):
        """
        Return the street and additional information if found, or None.

        Args:
            x (int): the X coordinate.
            y (int): the Y coordinate.
            z (int): the Z coordinate.
            city (optional, str): the city's name to filter by.

        Returns:
            A tuple containing  the closest crossroad (or None), the
            street name (or an empty string), and a list with the
            additional street numbers perpendicular to the street.
            For instance, if the street is oriented from east to west,
            the sides of the street are on the north and south, and
            the rooms or their coordinates are returned in the dictionary.

        Example:
            (<Crossroad #3>, "First street", {
                    "left": {
                        "direction": 2, # south
                        "coordinate": (0, -1, 0),
                        "room": <Room In front of the market>,
                        "numbers": (21, 23),
                    },
                    "right": {
                        "direction": 6, # north
                        "coordinate": (0, 1, 0),
                        "room": <Room In front of the public library>,
                        "numbers": (22, 24),
                    },
            })

        """
        crossroads = cls.get_crossroads_with(x, y, z)
        if not crossroads:
            return (None, "no crossroad", [])

        closest = crossroads[0]

        # Find the street name
        infos = [
                v for v in closest.db.exits.values() if \
                (x, y, z) in v["coordinates"]]
        if not infos:
            raise RuntimeError("unexpected: the coordinates {} {} {} " \
                    "were found in crossroad #{}, but the road leading " \
                    "this way cannot be found".format(x, y, z, first.id))

        road = infos[0]["name"].lower()

        # Find the first crossroad to this road
        crossroads = Crossroad.get_crossroads_road(road, city)
        if not crossroads:
            return (None, "no first crossroad", [])

        first = current = crossroads[0]
        found = False
        number = 0
        visited = []
        while not found:
            before = visited[-1] if visited else None
            infos = [
                    (k, v) for (k, v) in current.db.exits.items() if \
                    v["name"].lower() == road and v["crossroad"] is not before]
            if current in visited or not infos:
                return (None, "can't find", [])

            infos.sort(key=lambda tup: tup[1]["crossroad"].id)
            direction, info = infos[0]
            crossroad = info["crossroad"]
            distance = distance_between(current.x, current.y, 0,
                    crossroad.x, crossroad.y, 0)
            end_number = (distance - 1) * info.get("interval", 2) * 2
            if (x, y, z) in info["coordinates"]:
                d_x, d_y = current.x, current.y
                distance = distance_between(x, y, 0, d_x, d_y, 0)
                end_number = distance * info.get("interval", 2) * 2
                found = True

            number += end_number
            visited.append(current)
            current = crossroad

        # We now try to find the immediate neighbors
        interval = info.get("interval", 2)
        left_direction = (direction - 2) % 8
        left_coords = coords_in(x, y, z, left_direction)
        left_room = Room.get_room_at(*left_coords)
        left_numbers = tuple(number + n for n in range(-interval * 2 + 1, 1, 2))
        right_direction = (direction + 2) % 8
        right_coords = coords_in(x, y, z, right_direction)
        right_room = Room.get_room_at(*right_coords)
        right_numbers = tuple(number + n for n in range(-(interval - 1) * 2, 1, 2))

        return (closest, info["name"], {
                "left": {
                        "direction": left_direction,
                        "coordinates": left_coords,
                        "room": left_room,
                        "numbers": left_numbers,
                },
                "right": {
                        "side": "right",
                        "direction": right_direction,
                        "coordinates": right_coords,
                        "room": right_room,
                        "numbers": right_numbers,
                },
        })

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

    def add_exit(self, direction, crossroad, name, coordinates=None,
            interval=2):
        """
        Add a new exit in the given direction.

        Args:
            direction (int): the direction (0 for east, 1 for south-east...)
            crossroad (Crossroad): the destination (another crossroad)
            name (str): name of the exit (like "eight street")
            coordinates (optional, list): coordinate replacements.
            interval (optional, int): change the default number interval.

        If there already was a crossroad in this direction, replace it.
        The given crossroad has to be logically set (if you give a
        direction of 0, the crossroad should be straight to the east
        of the configured position).  Otherwise, a ValueError will
        be raised.

        The number interval determines the number of numbers per
        coordinates of a road.  By default, it is 2 (meaning, on
        one coordinate are actually 2 numbers).

        """
        # Check the geographical logic
        x, y, z = self.x, self.y, self.z
        d_x, d_y, d_z = crossroad.x, crossroad.y, crossroad.z

        # Since the vertical distance will affect coordinates, we
        # need to make sure it's properly handled.
        if direction_between(x, y, 0, d_x, d_y, 0) != direction:
            raise ValueError("the direction between {} and {} doesn't " \
                    "match {}".format(self, crossroad, direction))

        # Get the distance between self and crossroad
        distance = sqrt((d_x - x) ** 2 + (d_y - y) ** 2)

        coordinates = coordinates or []
        slope = d_z - z
        if not coordinates:
            progress = 0
            current_slope = 0

            # Calculate in-between coordinates
            if slope <= -1 or slope >= 1:
                slope_frequency = int(distance / fabs(slope))
            else:
                slope_frequency = 0

            if slope < 0:
                slope_step = -1
            else:
                slope_step = 1

            while progress < distance:
                progress += 1
                if progress >= distance:
                    break

                if slope_frequency and progress % slope_frequency == 0:
                    current_slope += slope_step

                coords = coords_in(x, y, z, direction, distance=progress)
                if current_slope:
                    coords = coords[:2] + (coords[2] + current_slope, )
                coordinates.append(coords)

        # Create the tags of possible coordinates
        for coords in coordinates:
            tag = "{} {} {}".format(*coords)
            if not self.tags.get(tag, category="croad"):
                self.tags.add(tag, category="croad")

        self.db.exits[direction] = {
                "coordinates": coordinates,
                "crossroad": crossroad,
                "distance": distance,
                "direction": direction,
                "interval": interval,
                "name": name,
                "slope": slope,
        }

        # Add the tag for the street name itself
        name = name.lower()
        if not self.tags.get(name, category="road"):
            self.tags.add(name, category="road")

        return coordinates

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

            # Remove the coordinate tags
            for coords in info.get("coordinates", []):
                tag = "{} {} {}".format(*coords)
                if self.tags.get(tag, category="croad"):
                    self.tags.remove(tag, category="croad")

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
