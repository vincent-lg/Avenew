"""
Driving command set and commands.
"""

from evennia import default_cmds
from evennia.utils.utils import inherits_from
from commands.command import Command

# Commands
class CmdDrive(Command):

    """
    Begin or stop driving a vehicle.

    Usage:
        drive

    This command is both used to begin driving a vehicle when you
    are in the front seat, or to stop driving if the vehicle has
    stopped moving.  Entering the |ydrive|n command to stop driving
    will stop the vehicle in the middle of the street, which isn't
    often a good idea.  Instead, you can use the |ypark|n command,
    which will try to park the vehicle neatly on the right side of
    the street you are currently driving in.  Once parked, you can
    |yleave|n the vehicle.

    While driving, you can use several short commands to control
    speed, direction and driving mode.  Read the |ydriving|n help
    file (by typing |yhelp driving|n) for more information.

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
            self.caller.cmdset.delete()
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
        self.caller.cmdset.add("commands.driving.DrivingCmdSet",
                permanent=True)


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
        #self.add(CmdPark())
        self.add(CmdSpeed())
