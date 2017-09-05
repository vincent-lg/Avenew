"""
Test for the computer type.
"""

from evennia.commands.default.tests import CommandTest
from evennia.utils.create import create_object

from auto.types.high_tech import APPS, load_apps
from commands.objects import CmdUse

class TestComputer(CommandTest):

    """Test for the computer type.

    This set of tests uses a smart phone (an object with computer and phone type).

    """

    def setUp(self):
        """Create the prototype and smart phone."""
        super(TestComputer, self).setUp()
        self.prototype = create_object("typeclasses.prototypes.PObj", key="smartphone")
        self.prototype.types.add("phone")
        self.prototype.types.add("computer")
        load_apps()
        self.prototype.types.get("computer").apps.add("text")
        self.smartphone = self.prototype.create(key="phone")

    def use(self):
        """Put the smart phone object in use."""
        self.user = create_object("typeclasses.characters.Character", key="user", location=self.room1)
        self.smartphone.location = self.user
        return self.call(CmdUse(), "phone", caller=self.user)
    
    def test_start_using(self):
        """Build and use a smart phone."""
        print self.use()
        print "smart", list(self.smartphone.types.get("computer").apps)
        self.assertTrue(len(list(self.smartphone.types)) == 2)

