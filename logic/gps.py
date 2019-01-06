# -*- coding: utf-8 -*-

"""Module containing the GPS class."""

from itertools import count
from math import fabs, sqrt
from queue import PriorityQueue
import re

from evennia.typeclasses.tags import Tag

from logic.geo import coords_in, distance_between
from typeclasses.rooms import Room
from typeclasses.vehicles import Crossroad
from world.log import logger

# Constants
RE_ADDRESS = re.compile(r"^(?P<num>[0-9 ]*)?\s*(?P<road>.*?)(,\s*(?P<city>.*))?$")
RE_NUMBER = re.compile(r"(\d+)")
UNIQUE = count()
log = logger("gps")

class GPS(object):

    """Class to represent a GPS query.

    A GPS query is a link between two points (often represented as
    addresses).  It will attempt to find the shortest path between
    these two points and optionally guide a vehicle.

    """

    def __init__(self, origin=None, destination=None):
        self.origin = origin
        self.destination = destination
        self.address = ""
        self.path = []
        if isinstance(origin, str):
            self.origin = self.find_address(origin)
        if isinstance(destination, str):
            self.destination = self.find_address(destination, is_dest=True)

    def find_address(self, address, is_dest=False):
        """Find and return the address.

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
        crossroads = Crossroad.get_crossroads_road(road, city)
        log.debug("Searching for number={}, road={}, city={}".format(
                number, road, city))

        # Recording the address
        if is_dest:
            if city:
                self.address = "{} {} in {}".format(number, road, city)
            else:
                self.address = "{} {}".format(number, road)

        if not crossroads:
            log.debug("Cannot find a matching crossroad")
            raise ValueError("cannot find the address '{} {}, {}', " \
                    "no match found".format(number, road, city))

        # Get the first crossroad and start counting from there
        beginning = crossroads[0]

        # Look for the distance
        current = beginning
        found = False
        current_number = 0
        visited = []
        while not found:
            before = visited[-1] if visited else None
            infos = [
                    (k, v) for (k, v) in current.db.exits.items() if \
                    v["name"].lower() == road and v["crossroad"] is not before]
            if current in visited or not infos:
                log.debug("  The expected road number can't be found")
                raise ValueError("the expected road number ({}) on " \
                        "{} can't be found".format(number, road))

            infos.sort(key=lambda tup: tup[1]["crossroad"].id)
            direction, info = infos[0]
            crossroad = info["crossroad"]
            distance = distance_between(current.x, current.y, 0,
                    crossroad.x, crossroad.y, 0)
            end_number = (distance - 1) * info.get("interval", 1) * 2
            if current_number + end_number >= number:
                end = current
                found = True

                # If the destination is closer to the end crossroad, choose it instead
                remaining = number - current_number - 1
                distance = 1 + remaining // info.get("interval", 1) // 2
                projected = end.db.exits[direction]["coordinates"][distance - 1]

                # If the number is odd, look for the other side of the street
                if number % 2 == 1:
                    shift = (direction - 2) % 8
                else:
                    shift = (direction + 2) % 8

                if remaining > end_number / 2:
                    log.debug("We actually are closer from #{}.".format(
                            crossroad.id))
                    opp_direction = (direction + 4) % 8
                    if crossroad.db.exits.get(opp_direction, {}).get("crossroad") is current:
                        log.debug("There's a reverse road, use it.")
                        end = crossroad
                        direction = opp_direction

                break

            # The number is further ahead, go on
            visited.append(current)
            current = crossroad
            current_number += end_number

        # If not end, the address couldn't be found
        if end is None:
            log.debug("The expected road number can't be found")
            raise ValueError("the expected road number ({}) on " \
                    "{} can't be found".format(number, road))

        log.debug("Found end=#{}, direction={}, distance={}".format(
                end.id, direction, distance))
        projected = coords_in(projected[0], projected[1],
                projected[2], shift)
        room = Room.get_room_at(*projected)
        if room:
            log.debug("Found room {} at {} {} {}".format(room, room.x,
                    room.y, room.z))
            projected = room

        # If is_dest, add the path
        if is_dest:
            self.path.append((end, direction, projected))

        return end

    def find_path(self):
        """Find the path between origin and destination."""
        start = self.origin
        goal = self.destination
        log.debug("Finding the shortest path between #{} and #{}".format(
                start.id, goal.id))

        # A* algorithm to find the path
        frontier = PriorityQueue()
        frontier.put((0, next(UNIQUE), start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        while not frontier.empty():
            current = frontier.get()[2]
            if current is goal:
                break

            for direction, info in current.db.exits.items():
                next_cr = info["crossroad"]
                new_cost = cost_so_far[current] + distance_between(current.x, current.y, 0, next_cr.x, next_cr.y, 0)
                if next_cr not in cost_so_far or new_cost < cost_so_far[next_cr]:
                    cost_so_far[next_cr] = new_cost
                    priority = new_cost + sqrt(
                            (next_cr.x - goal.x) ** 2 + (next_cr.y - goal.y) ** 2)
                    frontier.put((priority, next(UNIQUE), next_cr))
                    came_from[next_cr] = (current, direction)

        path = []
        while current is not start:
            old = current
            current, direction = came_from[current]
            path.append((current, direction, old))
            log.debug("  From #{} to #{}, direction={}".format(
                    current.id, old.id, direction))

        path.reverse()
        self.path = path + self.path

        # There's a possibility the path may be shortened on hop -2
        if len(self.path) > 1:
            if (self.path[-2][1] + 4) % 8 == self.path[-1][1]:
                log.debug("The before last hop can be removed.")
                self.path[-2] = self.path[-2][:2] + (self.path[-1][2], )
                del self.path[-1]

    @staticmethod
    def extract_address(string):
        """Extract the address from the string.

        The string could be formatted in different ways.

        Args:
            string (str): the string containing the address.

        Returns:
            (number, road, city): a tuple containing three str objects.

        """
        string = string.lower()
        tags = Tag.objects.filter(db_category__in=("road", "city"))
        roads = []
        cities = []
        for tag in tags:
            if tag.db_category == "road":
                if tag.db_key not in roads:
                    roads.append(tag.db_key)
            else:
                if tag.db_key not in cities:
                    cities.append(tag.db_key)

        # Extract the number
        match = RE_NUMBER.search(string)
        if match:
            number = match.group(1)
        else:
            number = "1"

        # Extract the name of the city
        city = ""
        for name in cities:
            if name.lower() in string:
                city = name
                break

        # Find the road name
        road = ""
        for name in roads:
            if name.lower() in string:
                road = name
                break

        return (number, road, city)
