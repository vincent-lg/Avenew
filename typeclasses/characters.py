# -*-coding:Utf-8 -*

"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.utils.utils import lazy_property
from evennia.contrib.ingame_python.typeclasses import EventCharacter
from evennia.contrib.ingame_python.utils import register_events

from auto.behaviors.behaviorhandler import BehaviorHandler
from logic.character.stats import StatsHandler
from logic.geo import get_direction
from typeclasses.shared import AvenewObject

# Constants
MAP = r"""
Crossroad

   Map                        Roads

        N                     {fn}
  NW    {fl}    NE
    {ell}   {fl}   {erl}                 {ern}
     {ell}  {fl}  {erl}                  {eln}
      {ell} {fl} {erl}
       {ell}{fl}{erl}                    {rn}
W{ll}{ll}{ll}{ll}{ll}{ll}{ll}*{rl}{rl}{rl}{rl}{rl}{rl}{rl}E             {ln}
       {hll}{bl}{hrl}
      {hll} {bl} {hrl}                   {hrn}
     {hll}  {bl}  {hrl}                  {hln}
    {hll}   {bl}   {hrl}
  SW    {bl}    SE
        S                     {bn}
"""

PRE_TURN = """
Before the driven vehicle turn into a crossroad.
This event is called on the character driving a vehicle, when this
vehicle is close from a crossroad where it will have to turn.  This
event can be called to set taxi drivers or other automatic NPCs on a
driving mission.

Variables you can use in this event:
    character: the character connected to this event.
    vehicle: the vehicle driven by the character.
    crossroad: the crossroad on which the vehicle is about to arrive.
"""

POST_TURN = """
After the driven vehicle has turned into a road.
This event is called on the character driving a vehicle, when this
vehicle has just turned from a crossroad onto a road.  This
event can be called to set taxi drivers or other automatic NPCs on a
driving mission.

Variables you can use in this event:
    character: the character connected to this event.
    vehicle: the vehicle driven by the character.
    crossroad: the crossroad on which the vehicle has just turned.
"""

# Classes
@register_events
class Character(AvenewObject, EventCharacter):
    """
    The character, representing an account-character (connected) or
    NPC (non-connected).
    """

    _events = {
        "pre_turn": (["character", "vehicle", "crossroad"], PRE_TURN),
        "post_turn": (["character", "vehicle", "crossroad"], POST_TURN),
    }
    repr = "representations.character.CharacterRepr"

    @lazy_property
    def behaviors(self):
        """Return the behavior handler for this character."""
        return BehaviorHandler(self)

    @lazy_property
    def stats(self):
        """Return the stat handler for this character."""
        return StatsHandler(self)

    def at_before_say(self, message, **kwargs):
        """
        Before the object says something.

        This hook is by default used by the 'say' and 'whisper'
        commands as used by this command it is called before the text
        is said/whispered and can be used to customize the outgoing
        text from the object. Returning `None` aborts the command.

        Args:
            message (str): The suggested say/whisper text spoken by self.
        Kwargs:
            whisper (bool): If True, this is a whisper rather than
                a say. This is sent by the whisper command by default.
                Other verbal commands could use this hook in similar
                ways.
            receivers (Object or iterable): If set, this is the target or targets for the say/whisper.

        Returns:
            message (str): The (possibly modified) text to be spoken.

        """
        # Escape | and {} (color codes and mapping)
        message = message.replace("|", "||")
        return super(Character, self).at_before_say(message)

    def at_say(self, speech, **kwargs):
        """Say something."""
        if kwargs.get("whisper"):
            msg_self = "Vous chuchotez à {all_receivers}: {speech}"
            msg_receivers = "{object} vous chuchote: {speech}"
            msg_location = None
        else:
            msg_self = "Vous dites : {speech}"
            msg_receivers = ""
            msg_location = "{object} dit : {speech}"
        super(Character, self).at_say(speech, msg_self=msg_self,
                msg_location=msg_location, msg_receivers=msg_receivers)

    def display_turns(self, vehicle, crossroad):
        """Called to display the list of available exits."""
        if vehicle.has_message("turns"):
            return

        vehicle.add_message("turns")
        direction = vehicle.db.direction
        exits = crossroad.db.exits
        sessions = self.sessions.get()
        if sessions:
            if any(session.protocol_flags.get(
                    "SCREENREADER", False) for session in sessions):
                # One session on the driver has SCREENREADER turned on
                msg = ""
                for dir, exit in exits.items():
                    if msg:
                        msg += "\n"

                    name = get_direction(dir)["name"].capitalize()
                    msg += "  {:<10} - {}".format(name, exit["name"])
            else:
                # Create the diagram to represent the crossroad
                msg = MAP.format(
                        fl="|" if 6 in exits else " ",
                        fn="N  - " + exits[6]["name"] if 6 in exits else "",
                        erl="/" if 7 in exits else " ",
                        ern="NE - " + exits[7]["name"] if 7 in exits else "",
                        ell="\\" if 5 in exits else " ",
                        eln="NW - " + exits[5]["name"] if 5 in exits else "",
                        rl="-" if 0 in exits else " ",
                        rn="E  - " + exits[0]["name"] if 0 in exits else "",
                        ll="-" if 4 in exits else " ",
                        ln="W  - " + exits[4]["name"] if 4 in exits else "",
                        hrl="\\" if 1 in exits else " ",
                        hrn="SE - " + exits[1]["name"] if 1 in exits else "",
                        hll="/" if 3 in exits else " ",
                        hln="SW - " + exits[3]["name"] if 3 in exits else "",
                        bl="|" if 2 in exits else " ",
                        bn="S  - " + exits[2]["name"] if 2 in exits else "",
                )

            self.msg(msg)

    def pre_turn(self, vehicle, crossroad):
        """Called to have the driver make a decision regarding turning."""
        from world.log import main as log
        log.debug("Calling pre_turn X={} Y={} direciton={} crossroad={} {}".format(round(vehicle.db.coords[0], 3), round(vehicle.db.coords[1], 3), vehicle.db.direction, vehicle.db.next_crossroad, crossroad))

        # Call the 'pre_turn' event on the driver
        self.callbacks.call("pre_turn", self, vehicle, crossroad)

        # Call the pre_turn behavior on driver
        if "driver" in self.behaviors:
            self.behaviors["driver"].pre_turn(self, vehicle)
