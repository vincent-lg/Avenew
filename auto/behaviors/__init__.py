# -*- coding: utf-8 -*-

"""Package containing the character behaviors.

One character can be set to use several behavior.  A behavior is a set of
additional instructions that will render the character able to perform some
complex tasks.  This additional complexity is added in separate modules, as
it will be more flexible and independent.  All characters don't have these
inate abilities, but adding a behavior to a character is quite simple.

Behaviors:
    driver: Driving a vehicle to a specific destination.

"""

from auto.behaviors.behaviorhandler import BEHAVIORS
