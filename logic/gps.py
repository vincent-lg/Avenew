"""
Module containing the GPS class.

"""

from math import fabs as abs
from Queue import PriorityQueue
import re

from logic.geo import coords_in
from typeclasses.rooms import Room
from typeclasses.vehicles import Crossroad
from world.log import logger

# Constants
RE_ADDRESS = re.compile(r"^(?P<num>[0-9 ]*)?\s*(?P<road>.*?)(,\s*(?P<city>.*))?$")
log = logger("gps")

class GPS(object):

    """
    Class to represent a GPS query.

    A GPS query is a link between two points (often represented as
    addresses).  It will attempt to find the shortest path between
    these two points and optionally guide a vehicle.

    """

    def __init__(self, origin=None, destination=None):
        self.origin = origin
        self.destination = destination
        self.path = []
        if isinstance(origin, str):
            self.origin = self.find_address(origin)
        if isinstance(destination, str):
            self.destination = self.find_address(destination, in_path=True)

    def find_address(self, address, in_path=False):
        """
        Find and return the address.

        Args:
            address (str): the address to be found.

        The address could be in different formats:
            "89 North Star"
            "89 North Star, Los Alfaques"
            "North Star, Los Alfaques"

        """
        log.debug("Try to locate {}".format(address))
        match = RE_ADDRESS.search(address)
        if not match:
            raise ValueError("the specified address {} doesn't match".format(
                    repr(address)))

        # Extract the number
        number = match.group("num").replace(" ", "")
        if number:
            number = int(number)
        else:
            number = 1

        # Extract the road name
        road = match.group("road").lower().strip()

        # Extract the city name
        city = match.group("city")

        # Try to find all the crossroads serving this street
        if city:
            city = city.lower().strip()
            crossroads = Crossroad.objects.filter(
                    db_tags__db_key=road, db_tags__db_category="road").filter(
                    db_tags__db_key=city, db_tags__db_category="city")
        else:
            crossroads = Crossroad.objects.filter(
                    db_tags__db_key=road, db_tags__db_category="road")

        log.debug("Searching for number={}, road={}, city={}".format(
                number, road, city))
        if not crossroads:
            log.debug("Cannot find a matching crossroad")
            raise ValueError("cannot find the address '{} {}, {}', " \
                    "no match found".format(number, road, city))

        # Get the first crossroad and start counting from there
        beginning = crossroads[0]

        # Look for the distance
        next = beginning
        found = [next]
        distance = 0
        expected = int(number / 4)
        if expected < 1:
            expected = 1

        end = None
        while distance < expected:
            log.debug("  Current distance={} ({}), current crossroad=#{}".format(
                    distance, expected, next.id))
            infos = [(dir, info) for (dir, info) in next.db.exits.items() if \
                    info["name"].lower() == road and info["crossroad"] not in found]
            if not infos:
                log.debug("  The expected road number can't be found")
                raise ValueError("the expected road number ({}) on " \
                        "{} can't be found".format(number, road))

            direction, info = infos[0]
            next_distance = info["distance"] - 1
            if distance + next_distance >= expected:
                # Try to find the right coordinates
                end = next
                expected -= distance
                break

            # The number is further ahead, go on
            next = info["crossroad"]
            distance += next_distance
            found.append(next)

        # If not end, the address couldn't be found
        if end is None:
            log.debug("The expected road number can't be found")
            raise ValueError("the expected road number ({}) on " \
                    "{} can't be found".format(number, road))

        log.debug("Found end=#{}, direction={}, distance={}".format(
                end.id, direction, distance))
        projected = coords_in(end.x, end.y, end.z,
                direction, distance=expected)

        # If the number is odd, look for the other side of the street
        if number % 2 == 1:
            shift = (direction - 2) % 8
        else:
            shift = (direction + 2) % 8

        projected = coords_in(projected[0], projected[1],
                projected[2], shift)
        room = Room.get_room_at(*projected)
        if room:
            log.debug("Found room {} at {} {} {}".format(room, room.x,
                    room.y, room.z))
            projected = room

        # If in_path, add the path
        if in_path:
            self.path.append((end, direction, projected))

        return end

    def find_path(self):
        """Find the path between origin and destination."""
        start = self.origin
        goal = self.destination

        # A* algorithm to find the path
        def heuristic(a, b):
            # Manhattan distance on a square grid
            return abs(a.x - b.x) + abs(a.y - b.y)

        # Feeding the frontier
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break

            for direction, info in current.db.exits.items():
                next = info["crossroad"]
                new_cost = cost_so_far[current] + info["distance"]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = (current, direction)

        path = []
        while current != start:
           old = current
           current, direction = came_from[current]
           path.append((current, direction, old))

        path.reverse()
        self.path = path + self.path
