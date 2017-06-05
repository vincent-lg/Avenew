"""Test the GPS and coordinate finder."""

from logic.gps import GPS
from tests.road import TestRoad
from typeclasses.rooms import Room
from typeclasses.vehicles import Crossroad

class TestGPS(TestRoad):

    """Test the GPS and coordinate finder."""

    def test_simple(self):
        """Test consistency of several simple street numbers."""
        coordinates = [
            (-1, -1, 3),
            (12, -1, 3),
            (16, -8, 3),
            (16, 18, 3),
            (25, 20, 3),
            (37, 5, 3),
        ]

        for choice in coordinates:
            street = Crossroad.get_street(*choice)
            if street[0] is None:
                print "error", choice

            left = street[2]["left"]["coordinates"]
            for number in street[2]["left"]["numbers"]:
                gps = GPS(self.a1, "{} {}".format(number, street[1]))
                gps.find_path()
                self.assertEqual(gps.path[-1][2], left)
            right = street[2]["right"]["coordinates"]
            for number in street[2]["right"]["numbers"]:
                gps = GPS(self.a1, "{} {}".format(number, street[1]))
                gps.find_path()
                self.assertEqual(gps.path[-1][2], right)
