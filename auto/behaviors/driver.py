# -*- coding: utf-8 -*-

"""Module containing the driver behavior."""

from math import sqrt

from evennia.utils.utils import inherits_from

from auto.behaviors.base import Behavior
from logic.geo import direction_between, distance_between, coords_in, get_direction
from logic.gps import GPS
from world.log import logger

log = logger("driver")

class Driver(Behavior):

    """Behavior giving a character the ability to drive, following a path.

    This behavior can be added to a PChar or character and will give the ability to
    drive.  Not all characters will know how to do that.  This behavior will
    store in a specific sub-attributes to know where it should go and what are
    the hops to reach it.  Give this behavior then add it through:

        character.behaviors.get("driver").drive_to("<address>")

    """

    name = "driver"

    def drive_to(self, address):
        """Plan to drive to a specific address.

        The character behind the call (it can't work with prototypes) is supposed to be in a
        vehicle and be driving it.  The address should be formatted correctly,
        "<number> <street> <city>" (use `extract_address` if the address is not
        formatted properly).  It will use the GPS to find the location and the
        hops (a hop being a link between crossroads).  This set of hops
        will then be edited each time the vehicle turns.

        """
        location = self.character.location
        vehicle = location.location
        msg_go = self.db.get("msg_go")
        desired_speed = self.db.get("desired_speed", 20)
        if msg_go:
            self.character.location.msg_contents(msg_go, mapping=dict(driver=self.character))

        # Find the address
        try:
            gps = GPS(vehicle.db.next_crossroad, address)
        except ValueError:
            log.debug("{} cannot find address {}".format(self.character, address))
            msg_cant_locate = self.db["msg_cant_locate"]
            if msg_cant_locate:
                location.msg_contents(msg_cant_locate, mapping=dict(driver=self.character))
        else:
            gps.find_path()
            log.debug("GPS: {}".format(gps.path))
            self.db["destinations"] = gps.path
            self.character.execute_cmd("speed {}".format(desired_speed))
            vehicle.clear_messages()

    def pre_turn(self, driver, vehicle):
        """Before turning."""
        destinations = self.db["destinations"]
        if destinations:
            location = driver.location
            direction = vehicle.db.direction
            previous, abs_direction, next = destinations[0]
            name = get_direction(abs_direction)["name"]
            log.debug("#{}-{}: turn {} {}-{}".format(
                    vehicle.id, self.character, name, previous, next))
            driver.execute_cmd("turn {}".format(name))

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
                if "expected" not in self.db:
                    expected = coords_in(destinations[-1][0].x, destinations[-1][0].y, final[2],
                            direction=destinations[-1][1], distance=distance)
                    side = get_direction(direction_between(expected[0], expected[1], 0, final[0], final[1], 0))["name"]
                    log.debug("#{}-{}: expected {} to {}, side={}".format(vehicle.id, self.character, expected, final, side))
                    self.db["expected"] = expected
                    self.db["side"] = side
                    vehicle.start_monitoring()
            del destinations[0]

    def attempt_parking(self, driver, vehicle, new_coords):
        """Called when the driver should be attempting to park."""
        expected = self.db["expected"]
        if expected:
            distance = sqrt((new_coords[0] - expected[0]) ** 2 + (new_coords[1] - expected[1]) ** 2)
            log.debug("#{}-{}: attempting to park, distance={}".format(vehicle.id, self.character, round(distance, 3)))
            if distance <= 0.5:
                side = self.db["side"]
                log.debug("#{}-{}: try to park on {} side".format(vehicle.id, self.character, side))
                driver.execute_cmd("park {}".format(side))
                if vehicle.location: # The vehicle is parked
                    vehicle.stop_monitoring()
            elif distance < 4 and vehicle.db.desired_speed > 5:
                driver.execute_cmd("speed 5")
                log.debug("#{}-{}: slow down to 5 MPH".format(vehicle.id, self.character))
            elif distance < 7 and vehicle.db.desired_speed > 10:
                driver.execute_cmd("speed 10")
                log.debug("#{}-{}: slow down to 10 MPH".format(vehicle.id, self.character))
