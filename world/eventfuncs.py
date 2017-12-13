# -*- coding: utf-8 -*-

"""
Module containing the Avenew event funcs (event functions).
"""

import datetime

from evennia.utils import gametime as gtime

class GTime(datetime.datetime):

    """Extended datetime, with a 'season' property."""

    @property
    def season(self):
        """Return the game time season."""
        Y = self.year
        date = datetime.date
        seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
               ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
               ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
               ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
               ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))
        ]

        today = self.date()
        return next(season for season, (start, end) in seasons if start <= today <= end)


def gametime():
    """Return the current game time as a datetime object.

    This returns a datetime opbject with an additional property: `season`.  It returns the current reason as a string (like "winter").

    """
    return GTime.fromtimestamp(gtime.gametime(absolute=True))
