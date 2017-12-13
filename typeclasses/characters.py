# -*-coding:Utf-8 -*

"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.contrib.ingame_python.typeclasses import EventCharacter
from evennia.contrib.ingame_python.utils import register_events

from behaviors import BEHAVIORS

# Constants
MAP = r"""
Crossroad

   Map                        Roads

        {f}                     {fn}
  {el}    {fl}    {er}
    {ell}   {fl}   {erl}                 {ern}
     {ell}  {fl}  {erl}                  {eln}
      {ell} {fl} {erl}
       {ell}{fl}{erl}                    {rn}
{l}{ll}{ll}{ll}{ll}{ll}{ll}{ll}*{rl}{rl}{rl}{rl}{rl}{rl}{rl}{r}             {ln}
       {hll}{bl}{hrl}
      {hll} {bl} {hrl}                   {hrn}
     {hll}  {bl}  {hrl}                  {hln}
    {hll}   {bl}   {hrl}
  {hl}    {bl}    {hr}
        {b}                     {bn}
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
class Character(EventCharacter):
    """
    The character, representing an account-character (connected) or
    NPC (non-connected).
    """

    _events = {
        "pre_turn": (["character", "vehicle", "crossroad"], PRE_TURN),
        "post_turn": (["character", "vehicle", "crossroad"], POST_TURN),
    }

    @property
    def behaviors(self):
        """Return the list of active behaviors."""
        tags = self.tags.get(category="behavior")
        if tags is None:
            tags = []
        elif isinstance(tags, basestring):
            tags = [tags]

        # Place the behaviors in a list
        behaviors = []
        for name in tags:
            if name in BEHAVIORS:
                behaviors.append(BEHAVIORS[name])

        return behaviors

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

    def display_turns(self, vehicle, crossroad):
        """Called to display the list of available exits."""
        if vehicle.has_message("turns"):
            return

        vehicle.add_message("turns")
        direction = vehicle.db.direction
        exits = dict([((k - direction) % 8, v) for k, v in crossroad.db.exits.items()])
        names = {
                0: "Forward",
                1: "Easy right",
                2: "Right",
                3: "Hard right",
                4: "Behind",
                5: "Hard left",
                6: "Left",
                7: "Easy left",
        }

        sessions = self.sessions.get()
        if sessions:
            if any(session.protocol_flags.get(
                    "SCREENREADER", False) for session in sessions):
                # One session on the driver has SCREENREADER turned on
                msg = ""
                for dir, exit in exits.items():
                    if msg:
                        msg += "\n"

                    name = names[dir]
                    msg += "  {:<10} - {}".format(name, exit["name"])
            else:
                # Create the diagram to represent the crossroad
                msg = MAP.format(
                        f="F" if 0 in exits else " ",
                        fl="|" if 0 in exits else " ",
                        fn="F  - " + exits[0]["name"] if 0 in exits else "",
                        er="ER" if 1 in exits else "  ",
                        erl="/" if 1 in exits else " ",
                        ern="ER - " + exits[1]["name"] if 1 in exits else "",
                        el="EL" if 7 in exits else "  ",
                        ell="\\" if 7 in exits else " ",
                        eln="EL - " + exits[7]["name"] if 7 in exits else "",
                        r="R" if 2 in exits else " ",
                        rl="-" if 2 in exits else " ",
                        rn="R  - " + exits[2]["name"] if 2 in exits else "",
                        l="L" if 6 in exits else " ",
                        ll="-" if 6 in exits else " ",
                        ln="L  - " + exits[6]["name"] if 6 in exits else "",
                        hr="HR" if 3 in exits else "  ",
                        hrl="\\" if 3 in exits else " ",
                        hrn="HR - " + exits[3]["name"] if 3 in exits else "",
                        hl="HL" if 5 in exits else "  ",
                        hll="/" if 5 in exits else " ",
                        hln="HL - " + exits[5]["name"] if 5 in exits else "",
                        b="B" if 4 in exits else " ",
                        bl="|" if 4 in exits else " ",
                        bn="B  - " + exits[4]["name"] if 4 in exits else "",
                )

            self.msg(msg)

    def pre_turn(self, vehicle, crossroad):
        """Called to have the driver make a decision regarding turning."""
        from world.log import main as log
        log.debug("Calling pre_turn X={} Y={} direciton={} crossroad={} {}".format(round(vehicle.db.coords[0], 3), round(vehicle.db.coords[1], 3), vehicle.db.direction, vehicle.db.next_crossroad, crossroad))

        # Call the 'pre_turn' event on the driver
        self.callbacks.call("pre_turn", self, vehicle, crossroad)

        # Call the pre_turn behavior
        for behavior in self.behaviors:
            behavior.call("pre_turn", self, vehicle)
        log.debug("  Decided to turn {}".format(vehicle.db.expected_direction))
