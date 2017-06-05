"""Parent test for road-related tests."""

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest

from world.batch import *

class TestRoad(EvenniaTest):

    """Test complex.

    This parent class creates a simple road complex with some
    features that are expected to still work in various tests.

    """

    def setUp(self):
        super(TestRoad, self).setUp()
        self.parking = create_object("typeclasses.rooms.Room", key="A parking lot")
        self.parking.x = 0
        self.parking.y = 0
        self.parking.z = 3
        self.a1 = get_crossroad(-8, 3, 1)
        self.b1 = get_crossroad(-8, -1, 2)
        self.b2 = get_crossroad(-4, -1, 3)
        self.b3 = get_crossroad(1, -1, 3)
        self.b4 = get_crossroad(16, -1, 3)
        self.b5 = get_crossroad(32, -1, 3)
        self.b6 = get_crossroad(35, -1, 3)
        self.b7 = get_crossroad(35, 5, 3)
        self.b8 = get_crossroad(40, 5, 3)
        self.b9 = get_crossroad(40, -5, 3)
        self.b10 = get_crossroad(35, -5, 3)
        self.a2 = get_crossroad(16, 20, 3)
        self.a3 = get_crossroad(32, 20, 3)
        self.c1 = get_crossroad(-8, -8, 2)
        self.c2 = get_crossroad(1, -8, 3)
        self.d1 = get_crossroad(5, -12, 3)
        self.d2 = get_crossroad(16, -12, 3)
        add_road(self.a1, self.b1, "Port avenue")
        add_road(self.a1, self.b2, "Sunrise street")
        add_road(self.b1, self.b2, "First street")
        add_road(self.b2, self.b3, "First street")
        add_road(self.b3, self.b4, "First street")
        add_road(self.b4, self.b5, "First street")
        add_road(self.b4, self.a2, "North star")
        add_road(self.b5, self.b6, "First street")
        add_road(self.b6, self.b7, "Central Plaza")
        add_road(self.b7, self.b8, "Central Plaza")
        add_road(self.b8, self.b9, "Central Plaza")
        add_road(self.b9, self.b10, "Central Plaza")
        add_road(self.b10, self.b6, "Central Plaza")
        add_road(self.a2, self.a3, "North star")
        add_road(self.a3, self.b5, "North star")
        add_road(self.b1, self.c1, "First avenue")
        add_road(self.c1, self.c2, "Second street")
        add_road(self.c2, self.b3, "Second avenue")
        add_road(self.c2, self.d1, "Gray street")
        add_road(self.d1, self.d2, "Gray street")
        add_road(self.d2, self.b4, "Third avenue")
