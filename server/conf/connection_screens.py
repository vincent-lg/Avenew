# -*- coding: utf-8 -*-
"""
Connection screen

Texts in this module will be shown to the user at login-time.

Evennia will look at global string variables (variables defined
at the "outermost" scope of this module and use it as the
connection screen. If there are more than one, Evennia will
randomize which one it displays.

The commands available to the user when the connection screen is shown
are defined in commands.default_cmdsets.UnloggedinCmdSet and the
screen is read and displayed by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_SCREEN = \
r"""Welcome to

              ,
            /'/
          /' /
       ,/'  /.     ,   ____     ,____     ____ .   . ,   ,
      /`--,/ |    /  /'    )   /'    )  /'    )|   |/   /
    /'    /  |  /' /(___,/'  /'    /' /(___,/' |  /|  /'
(,/'     (_,_|/(__(________/'    /(__(_________|/' |/(__

|gAvenew One|n, built on Evennia %s!""" \
 % (utils.get_evennia_version())
