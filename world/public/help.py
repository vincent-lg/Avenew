# Batch-code file containing the standard help files
# Generate with: @batchcode public.help

#HEADER
from world.batch import get_help_entry

#CODE
get_help_entry("vehicle", """
    In Avenew One, you can drive a vehicle using a set of commands discussed here.
    Although vehicles can access areas you can not walk to, they're primarily used
    to earn some time.  Cars, for instance, offer a convenient shortcut from
    across town, although you could walk.  Typical vehicles would be cars,
    trucks, motorcycles.  More atypical vehicles are still to be expected
    however.

    To drive a vehicle you own, or a public vehicle you have access to, you first
    need to be near it.  You will see it in the room description.  Vehicles are
    grouped by type and brand so as not to overflow you with data, but you can
    easily search for a specific vehicle.  You have to climb into it, using the
    |yenter|n command.  This command takes a single argument: the name (or a
    portion of the name) of the
    vehicle in which you want to climb.  You can also supply the number plate,
    to avoid confusion.  Note that the vehicle might be locked, in which case,
    you will need to use the |yunlock|n command.  You will not be able to
    unlock every vehicle in a parking lot, you will need the keys or a similar
    item.  Public vehicles are usually unlocked, which means you can enter into
    them freely.  On the other hand, it also means anyone can do the same, so
    you shouldn't rely too much on this mean of transportation.

    Once in the front seat of the vehicle, you have to use the |ydrive|n command
    to grip the steering wheel.  This will not be possible if someone else is
    already driving.  You will use the same command to release the steering wheel
    when you want to stop driving.  If you are parked and you use the |ydrive|n
    command, you will start the engine and drive the few yards necessary to
    be on the street.

    You now have to accelerate.  You can control the speed using the |yspeed|n
    command.  Specify your desired speed in miles per hour.  Notice that this
    is more like your maximum cruising speed.  You will not have to manually
    brake at every obstacle.  You will just try to drive as close from your
    cruising speed as possible.  If you want to stop, simply use |yspeed 0|n
    to slowly reduce speed.

    A little before you arrive at a crossroad at the end of the street, you will
    get notified about what exits are available in this crossroad.  This is
    much like obtaining the obvious exits when you look at a room.  However,
    you must choose a turn relatively quickly.  If you don't and the vehicle
    enters the crossroad, you will either go forward if possible, or stop in
    the middle of the crossroad.  In the latter case, you will need to turn and
    then change your speed again with the |yspeed|n command.  To prepare to
    turn when you get notified about the available exits, you can use the
    |yturn|n command.  This, however, is not the easiest solution: you can
    use direction names to turn, like |ynortheast|n or even the alias |yne|n.
    This is quite easier to type and quicker, not mentioning that since
    standard exits have the same name, you can use your client aliases or
    macros if available.

    Once you arrive at your desired destination, first slow down using the
    |yspeed|n command.  To park, you can use the |ypark|n command.  Your
    vehicle should be relatively slow or you won't be able to use this command.
    The |ypark|n command will attempt to park your vehicle on the right side of
    the street.  If you prefer to park on the left, use the absolute direction
    name or alias, like |ypark south|n or |ypark e|n.

    Finally, you can just climb out of your vehicle using the |yleave|n command.
    Once more, you might have to unlock the vehicle as some will automatically
    lock when you are driving to avoid possible thefts.  Once outside, you
    might want to |ylock|n your vehicle to prevent others from climbing
    into them and driving away.

    """, aliases=["driving", "driver"])
