# -*- coding: utf-8 -*-

"""Module containing the event help strings for characters."""

CAN_DELETE = """
Can the character be deleted?
This event is called before the character is deleted.  You can use
'deny()' in this event to prevent this character from being deleted.
If this event doesn't prevent the character from being deleted, its
'delete' event is called right away.

Variables you can use in this event:
    character: the character connected to this event.
"""

CAN_MOVE = """
Can the character move?
This event is called before the character moves into another
location.  You can prevent the character from moving
using the 'deny()' eventfunc.

Variables you can use in this event:
    character: the character connected to this event.
    origin: the current location of the character.
    destination: the future location of the character.
"""

CAN_PART = """
Can the departing charaacter leave this room?
This event is called before another character can move from the
location where the current character also is.  This event can be
used to prevent someone to leave this room if, for instance, he/she
hasn't paid, or he/she is going to a protected area, past a guard,
and so on.  Use 'deny()' to prevent the departing character from
moving.

Variables you can use in this event:
    departing: the character who wants to leave this room.
    character: the character connected to this event.
"""

CAN_SAY = """
Before another character can say something in the same location.
This event is called before another character says something in the
character's location.  The "something" in question can be modified,
or the action can be prevented by using 'deny()'.  To change the
content of what the character says, simply change the variable
'message' to another string of characters.

Variables you can use in this event:
    speaker: the character who is using the say command.
    character: the character connected to this event.
    message: the text spoken by the character.
"""

DELETE = """
Before deleting the character.
This event is called just before deleting this character.  It shouldn't
be prevented (using the `deny()` function at this stage doesn't
have any effect).  If you want to prevent deletion of this character,
use the event `can_delete` instead.

Variables you can use in this event:
    character: the character connected to this event.
"""

GREET = """
A new character arrives in the location of this character.
This event is called when another character arrives in the location
where the current character is.  For instance, a puppeted character
arrives in the shop of a shopkeeper (assuming the shopkeeper is
a character).  As its name suggests, this event can be very useful
to have NPC greeting one another, or accounts, who come to visit.

Variables you can use in this event:
    character: the character connected to this event.
    newcomer: the character arriving in the same location.
"""

MOVE = """
After the character has moved into its new room.
This event is called when the character has moved into a new
room.  It is too late to prevent the move at this point.

Variables you can use in this event:
    character: the character connected to this event.
    origin: the old location of the character.
    destination: the new location of the character.
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

PUPPETED = """
When the character has been puppeted by an account.
This event is called when an account has just puppeted this character.
This can commonly happen when an account connects onto this character,
or when puppeting to a NPC or free character.

Variables you can use in this event:
    character: the character connected to this event.
"""

SAY = """
After another character has said something in the character's room.
This event is called right after another character has said
something in the same location..  The action cannot be prevented
at this moment.  Instead, this event is ideal to create keywords
that would trigger a character (like a NPC) in doing something
if a specific phrase is spoken in the same location.
To use this event, you have to specify a list of keywords as
parameters that should be present, as separate words, in the
spoken phrase.  For instance, you can set an event tthat would
fire if the phrase spoken by the character contains "menu" or
"dinner" or "lunch":
    @call/add ... = say menu, dinner, lunch
Then if one of the words is present in what the character says,
this event will fire.

Variables you can use in this event:
    speaker: the character speaking in this room.
    character: the character connected to this event.
    message: the text having been spoken by the character.
"""

TIME = """
A repeated event to be called regularly.
This event is scheduled to repeat at different times, specified
as parameters.  You can set it to run every day at 8:00 AM (game
time).  You have to specify the time as an argument to @call/add, like:
    @call/add here = time 8:00
The parameter (8:00 here) must be a suite of digits separated by
spaces, colons or dashes.  Keep it as close from a recognizable
date format, like this:
    @call/add here = time 06-15 12:20
This event will fire every year on June the 15th at 12 PM (still
game time).  Units have to be specified depending on your set calendar
(ask a developer for more details).

Variables you can use in this event:
    character: the character connected to this event.
"""

UNPUPPETED = """
When the character is about to be un-puppeted.
This event is called when an account is about to un-puppet the
character, which can happen if the account is disconnecting or
changing puppets.

Variables you can use in this event:
    character: the character connected to this event.
"""

