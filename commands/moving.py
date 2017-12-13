# -*- coding: utf-8 -*-

"""
Commands to move.
"""

from evennia.utils.utils import inherits_from

from commands.command import Command

class CmdEnter(Command):

    """
    Enter a vehicle or area.

    Usage:
        enter <what>

    This command allows you to enter, a vehicle or an area.  You
    cannot enter into everything you see laying around, of course.
    You might use this command to climb into a vehicle, however, if
    it is parked here.  You just have to provide the name of what to
    enter into (like part of the name of the vehicle).

    Example:
        enter car

    """

    key = "enter"

    def func(self):
        """Execute the command."""
        room = self.caller.location

        # Check that self.args isn't empty
        if not self.args.strip():
            self.msg("What do you want to enter?")
            return

        # Search in the room for the object
        obj = self.caller.search(self.args)
        if obj is None:
            return

        # Handle climbing into a vehicle
        if inherits_from(obj, "typeclasses.vehicles.Vehicle"):
            # Check that the vehicle contains rooms
            if not obj.contents:
                self.msg("{}'s doors are locked.".format(obj.key))
                return

            # Climb into the first VehicleRoom
            vroom = obj.contents[0]
            self.caller.msg("You climb into {}.".format(obj.key))
            room.msg_contents("{caller} climbs into {vehicle}.",
                    exclude=[self.caller], mapping=dict(
                    caller=self.caller, vehicle=obj))
            self.caller.move_to(vroom, quiet=True)
            vroom.msg_contents("{caller} enters the vehicle.",
                    exclude=[self.caller], mapping=dict(caller=self.caller))
        else:
            self.msg("Obviously, you cannot enter {}.".format(obj.key))


class CmdLeave(Command):

    """
    Leave a vehicle or area.

    Usage:
        leave

    This command allows you to leave, a vehicle or an area.  You might
    use this command to climb off a vehicle, if it is parked.

    """

    key = "leave"

    def func(self):
        """Execute the command."""
        room = self.caller.location

        # Handle climbing off a vehicle
        if inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            # Check that the vehicle is parked
            vehicle = room.location
            if vehicle is None or vehicle.location is None:
                self.msg("It seeems {} isn't parked.".format(vehicle.key))
                return

            # If caller is driving, stop driving
            if vehicle.db.driver is self.caller:
                vehicle.db.driver = None

            # Climb off the vehicle
            outside = vehicle.location
            self.caller.msg("You climb off {}.".format(vehicle.key))
            room.msg_contents("{caller} climbs off {vehicle}.",
                    exclude=[self.caller], mapping=dict(
                    caller=self.caller, vehicle=vehicle))
            self.caller.move_to(outside, quiet=True)
            outside.msg_contents("{caller} climbs off from {vehicle}.",
                    exclude=[self.caller], mapping=dict(
                    caller=self.caller, vehicle=vehicle))
        else:
            self.msg("Obviously, you cannot leave from {}.".format(room.key))
