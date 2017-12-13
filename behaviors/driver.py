# -*- coding: utf-8 -*-

"""Module containing the driver behavior."""

from math import sqrt

from evennia.utils.utils import inherits_from

from behaviors.behavior import Behavior
from logic.geo import distance_between, coords_in
from world.log import logger
log = logger("driver")

class Driver(Behavior):

    """Behavior giving a character the ability to drive, following a path."""

    @classmethod
    def pre_turn(cls, driver, vehicle):
        """Before turning."""
        prototype = driver.db.prototype
        directions = {
                0: "forward",
                1: "easy right",
                2: "right",
                3: "hard right",
                4: "behind",
                5: "hard left",
                6: "left",
                7: "easy left",
        }
        destinations = driver.db.destinations
        if destinations:
            location = driver.location
            direction = vehicle.db.direction
            previous, abs_direction, next = destinations[0]
            rel_direction = (abs_direction - direction) % 8
            name = directions[rel_direction]
            verb = "go" if rel_direction in (0, 4) else "turn"
            log.debug("#{}-{}: {} {} {}-{}, direction={}".format(
                    vehicle.id, prototype, verb, name, previous, next, abs_direction))
            driver.execute_cmd("{} {}".format(verb, name))

            # Find the final coordinates if necessary
            final = destinations[-1][2]
            if isinstance(final, (tuple, list)):
                final = tuple(final)
            else:
                final = (final.x, final.y, final.z)
            distance = distance_between(destinations[-1][0].x, destinations[-1][0].y,
                    0, final[0], final[1], 0)

            # Last turn, get ready to park
            if len(destinations) <= 2:
                if vehicle.db.expected is None:
                    expected = coords_in(destinations[-1][0].x, destinations[-1][0].y, final[2],
                            direction=destinations[-1][1], distance=distance)
                    log.debug("#{}-{}: expected {} to {}".format(vehicle.id, prototype, expected, final))
                    vehicle.db.expected_destination = expected
                    right_expected = coords_in(*expected, direction=(destinations[-1][1] + 2) % 8)
                    left_expected = coords_in(*expected, direction=(destinations[-1][1] - 2) % 8)
                    if right_expected == final:
                        log.debug("#{}-{}: planning to park on the right".format(vehicle.id, prototype))
                        vehicle.db.expected_side = "right"
                    elif left_expected == final:
                        log.debug("#{}-{}: planning to park on the left".format(vehicle.id, prototype))
                        vehicle.db.expected_side = "left"
                    else:
                        log.warning("#{}-{}: can't find on which side to park, left={}, right={}, expected={}".format(
                                vehicle.id, prototype, left_expected, right_expected, final))
                    vehicle.start_monitoring()
            del destinations[0]

    @classmethod
    def attempt_parking(cls, driver, vehicle, new_coords):
        """Called when the driver should be attempting to park."""
        expected = vehicle.db.expected_destination
        if expected:
            prototype = driver.db.prototype
            distance = sqrt((new_coords[0] - expected[0]) ** 2 + (new_coords[1] - expected[1]) ** 2)
            log.debug("#{}-{}: attempting to park, distance={}".format(vehicle.id, prototype, distance))
            if distance <= 0.5:
                side = vehicle.db.expected_side
                log.debug("#{}-{}: try to park on {} side".format(vehicle.id, prototype, side))
                driver.execute_cmd("park {}".format(side))
                if vehicle.location: # The vehicle is parked
                    vehicle.stop_monitoring()
            elif distance < 4 and vehicle.db.desired_speed > 5:
                driver.execute_cmd("speed 5")
                log.debug("#{}-{}: slow down to 5 MPH".format(vehicle.id, prototype))
            elif distance < 7 and vehicle.db.desired_speed > 10:
                driver.execute_cmd("speed 10")
                log.debug("#{}-{}: slow down to 10 MPH".format(vehicle.id, prototype))
