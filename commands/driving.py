"""
Driving command set and commands.
"""

from evennia import default_cmds
from evennia.utils.utils import inherits_from

from commands.command import Command
from logic.geo import distance_between
from typeclasses.vehicles import Crossroad, log

# Commands
class CmdDrive(Command):

    """
    Begin or stop driving a vehicle.

    Usage:
        drive

    This command is both used to begin driving a vehicle when you
    are in the front seat, or to stop driving if the vehicle has
    stopped moving.  Entering the |wdrive|n command to stop driving
    will stop the vehicle in the middle of the street, which isn't
    often a good idea.  Instead, you can use the |wpark|n command,
    which will try to park the vehicle neatly on the side of
    the street you are currently driving in.  Once parked, you can
    |wleave|n the vehicle.

    While driving, you can use several short commands to control
    speed, direction and driving mode.  Read the |wdriving|n help
    file (by typing |whelp driving|n) for more information.

    """

    key = "drive"
    help_category = "Driving"

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("It seems you are not in a vehicle.")
            return

        vehicle = room.location
        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg(
                    "Are you, or are you not, in a vehicle?  Hard to say...")
            return

        # We can only control the steering wheel from the front seat
        if room is not vehicle.contents[0]:
            self.msg("You aren't in the front seat of {}.".format(
                    vehicle.key))
            return

        # Are we already driving this vehicle
        if vehicle.db.driver is self.caller:
            vehicle.db.driver = None
            self.msg("You let go of the steering wheel.")
            room.msg_contents("{driver} lets go of the streering wheel.",
                    exclude=[self.caller], mapping=dict(driver=self.caller))
            self.caller.cmdset.remove("commands.driving.DrivingCmdSet")
            return

        # Or someone else could be riving
        if vehicle.db.driver:
            self.msg("Someone else is at the wheel.")
            return

        # All is good, allow 'self.caller' to drive
        vehicle.db.driver = self.caller
        self.msg("You grip the steering wheel and stretch your legs " \
                "to reach the pedals.")
        room.msg_contents("{driver} grips the steering wheel and stretches " \
                "his legs to reach the pedals.", exclude=[self.caller],
                mapping=dict(driver=self.caller))

        # If the vehicle is in a room, leave it.
        if vehicle.location is not None:
            vehicle.location = None
            self.msg("You start the engine and begin to drive {} " \
                    "on the street.".format(vehicle.key))
            vehicle.msg_contents("The engine of {vehicle} starts.",
                    exclude=[self.caller], mapping=dict(vehicle=vehicle))

        self.caller.cmdset.add("commands.driving.DrivingCmdSet",
                permanent=True)


class CmdPark(Command):

    """
    Park the vehicle you are driving.

    Usage:
        park
        park left

    This command can be used to park the vehicle you are driving,
    right on the sidewalk.  The vehicle's speed has to be really
    reduced.  You will not be able to park anywhere.  When you have
    arrived at your destination, after reducing speed (using the
    |wspeed|n command), you can |wpark|n, then use the |wdrive|n
    command to stop driving.  Then, you can |wleave|n the vehicle.

    By default, you will try to park on the right side of the street.
    You can also type |wpark left|n to park instead on the left side
    of the street.

    """

    key = "park"
    help_category = "Driving"

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("It seems you are not in a vehicle.")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg(
                    "Are you, or are you not, in a vehicle?  Hard to say...")
            return

        # Make sure we are currently driving
        if vehicle.db.driver is not self.caller:
            self.msg("You aren't driving {}.".format(vehicle.key))
            return

        # Check the speed
        if vehicle.db.speed > 10:
            self.msg("You are still driving too fast.")
            return

        # Get both sides of the current coordinate
        x, y, z = vehicle.db.coords

        # The Z coordinate could be invalid at this point, if there's a slope.
        previous = vehicle.db.previous_crossroad
        direction = vehicle.db.direction
        distance = distance_between(int(round(x)), int(round(y)), 0,
                previous.x, previous.y, 0)

        if (x, y) != (previous.x, previous.y):
            street = previous.db.exits[direction]

            try:
                assert distance > 0
                x, y, z = street["coordinates"][distance - 1]
            except AssertionError:
                x, y, z = previous.x, previous.y, previous.z
            except IndexError:
                log.warning("Cannot find the Z coordinate for vehicle " \
                        "#{}, trying to park at {} {}.".format(
                        vehicle.id, x, y))

                self.msg("It seems you can't park here.")
                return
        else:
            self.msg("Now, you cannot park in the middle of a crossroad.")
            return

        # Get the matching street
        log.debug("Parking #{} on {} {} {}".format(vehicle.id, x, y, z))
        closest, name, streets = Crossroad.get_street(x, y, z)
        if not streets:
            self.msg("You don't find any free spot to park.")
            return

        # Park on the left or right
        left = self.args.lower().strip() == "left"

        if left:
            side_direction = (direction - 2) % 8
        else:
            side_direction = (direction - 2) % 8
        spot = streets.get(side_direction)
        log.debug("  Parking #{} on the {} side, found {}".format(vehicle.id, "left" if left else "right", spot))

        # If there's no room there
        if spot and spot["room"] is None:
            self.msg("You don't find any free spot to park.")
            return

        room = spot["room"]
        vehicle.location = room
        vehicle.stop()
        numbers = "-".join(str(n) for n in spot["numbers"])
        self.caller.msg("You park {} on the {side} side.".format(
                vehicle.key, side="left" if left else "right"))
        self.caller.location.msg_contents("{driver} parks {vehicle} on the {side} side.",
                exclude=[self.caller], mapping=dict(driver=self.caller,
                vehicle=vehicle, side="left" if left else "right"))
        vehicle.msg_contents("{vehicle} pulls up in front of {numbers} {street}",
                mapping=dict(vehicle=vehicle, numbers=numbers, street=name))


class CmdSpeed(Command):

    """
    Change the desired speed of your vehicle when you are driving.

    Usage:
        speed <miles per hour>

    This command can be used to change the speed of your vehicle while
    you're driving.  You don't have to enter it to speed up or brake
    at every road, crossroad, traffic light and such: what you are
    changing using this command is your desired speed.  It usually
    reflects the maximum speed you will drive to, assuming no need
    for braking occurs.  When you stop for any reason, and then begin
    driving again, your speed will increase until it reaches the
    desired speed you have specified.  This speed will, however, depend
    on your driving mode: by default, you will obey traffic rules as
    much as you can, stop for traffic lights and slow down for crossroads.
    You can change your driving mode (usually, to drive faster), but
    be aware that this will increase the probability of crashing your
    vehicle.  If you decide to ignore traffic lights, for instance, you
    may end up crashing into another vehicle at the next crossroad.
    It will depend on your driving skill, your reflexes in handling
    unexpected situations will be greatly solicitated if you decide
    to drive in such a way.

    To change your desired speed without affecting your driving mode,
    use this command |yspeed|n, followed by the number of desired
    mile per hour.

    Example:
        |yspeed 25|n

    If you want to gently brake and park, you can use |yspeed 0|n
    to gently brake, and then, when the vehicle has stopped, the |ypark|n
    command.

    """

    key = "speed"
    help_category = "Driving"

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("It seems you are not in a vehicle.")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg(
                    "Are you, or are you not, in a vehicle?  Hard to say...")
            return

        # Make sure we are currently driving
        if vehicle.db.driver is not self.caller:
            self.msg("You aren't driving {}.".format(vehicle.key))
            return

        # If the vehicle is parked, un-park it
        if vehicle.location is not None:
            vehicle.location = None

        # Change the speed
        current = vehicle.db.speed
        desired = self.args.strip()

        try:
            desired = int(desired)
            assert desired >= 0
        except (ValueError, AssertionError):
            self.msg("Sorry, this is not a valid speed.")
        else:
            vehicle.db.desired_speed = desired
            self.msg("You're now planning to drive at {} MPH.".format(desired))

            # Display a message to the vehicle if the speed changes
            if current < desired:
                vehicle.msg_contents("{} begins to speed up.".format(
                        vehicle.key))
            elif current > desired:
                vehicle.msg_contents("{} begins to slow down.".format(
                        vehicle.key))


# Command set
class CmdTurn(Command):

    """
    Prepare to turn in a direction.

    If you are driving a vehicle, you can use this command to prepare to turn.  When the vehicle approaches a crossroad, the possibility should be displayed to you, much like the obvious exits in a room.  The vehicle isn't in the middle of the crossroad yet, just a short distance away, and you can turn without slowing down too much.  However, if you wait too long to turn, then the vehicle will stop in the middle of the crossroad, and you will need to speed up again after you have turned.

    To use this command, you can either use the full name of the turn, or aliases.  Aliases are much quicker to type, and once you get used to driving in the game, you will find using them is much better, particularly if your client doesn't support macro.  Here are all the directions and possible syntaxes:

    +------------|---------------------------------------------+
    | Directions | Commands                                    ||
    +------------|---------------------------------------------+
    | Forward    | |wgo forward|n      | |wforward|n    | |wgo f|n    | |yf|n  |
    | Easy right | |wturn easy right|n | |weasy right|n | |wturn er|n | |wer|n |
    | Easy left  | |wturn easy left|n  | |weasy left|n  | |wturn el|n | |wel|n |
    | Right      | |wturn right|n      | |wright|n      | |wturn r|n  | |wtr|n |
    | Left       | |wturn left|n       | |wleft|n       | |wturn l|n  | |wtl|n |
    | Hard right | |wturn hard right|n | |whard right|n | |wturn hr|n | |whr|n |
    | Hard left  | |wturn hard left|n  | |whard left|n  | |wturn hl|n | |whl|n |
    | Behind     | |wgo behind|n       | |wbehind|n     | |wgo b|n    | |wb|n  |
    +------------||---------------------------------------------+

    In other words, a little before arriving to a crossroad with
    an exit on the left, you could prepare to turn in this direction
    by entering either |wturn left|n, or |wleft|n, or simply |wl|n.

    """

    key = "turn"
    aliases = ["go", "forward", "f", "easy right", "er", "easy left", "el",
            "right", "tr", "left", "tl", "hard right", "hr", "hard left", "hl",
            "behind", "b"]
    help_category = "Driving"

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("It seems you are not in a vehicle.")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg(
                    "Are you, or are you not, in a vehicle?  Hard to say...")
            return

        # Make sure we are currently driving
        if vehicle.db.driver is not self.caller:
            self.msg("You aren't driving {}.".format(vehicle.key))
            return

        # Proceed to turn
        name = self.raw_string.strip().lower()
        direction = vehicle.db.direction

        # Different choices
        if name in ("go", "forward", "go f", "f"):
            turn = 0
            msg = "You prepare to go forward on the next open crossroad."
        elif name in ("turn easy right", "easy right", "turn er", "er"):
            turn = 1
            msg = "You prepare to do an easy right on the next open crossroad."
        elif name in ("turn easy left", "easy left", "turn el", "el"):
            turn = 7
            msg = "You prepare to do an easy left on the next open crossroad."
        elif name in ("turn right", "right", "turn r", "tr"):
            turn = 2
            msg = "You prepare to turn right on the next open crossroad."
        elif name in ("turn left", "left", "turn l", "tl"):
            turn = 6
            msg = "You prepare to turn left on the next open crossroad."
        elif name in ("turn hard right", "hard right", "turn hr", "hr"):
            turn = 3
            msg = "You prepare to do a hard right on the next open crossroad."
        elif name in ("turn hard left", "hard left", "turn hl", "hl"):
            turn = 5
            msg = "You prepare to do a hard left on the next open crossroad."
        elif name in ("go behind", "behind", "go b", "b"):
            turn = 4
            msg = "You prepare to do some scarcely-legal U turn."
        else:
            self.msg("In what direction do you want to turn?")
            return

        vehicle.db.expected_direction = (direction + turn) % 8
        self.msg(msg)


class DrivingCmdSet(default_cmds.CharacterCmdSet):

    """
    Driving command set.

    This command set contains additional commands that are active
    when one drives a vehicle.  These commands aren't automatically
    active when one climbs into a vehicle, the user should use the
    'drive' command.  Doing so will give him/her additional commands,
    like control of the speed, the direction and basic information
    on the vehicle he/she is driving, like a constant glimpse of the
    control panel.  The user should use 'drive' again to release the
    steering wheel, something that shouldn't be done when the car
    is still rolling.

    """

    def at_cmdset_creation(self):
        """Populates the cmdset with commands."""
        self.add(CmdPark())
        self.add(CmdSpeed())
        self.add(CmdTurn())
