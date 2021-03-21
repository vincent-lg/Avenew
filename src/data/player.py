# Copyright (c) 2020-20201, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

"""Player entity.

A player is a character with a name, and it can be linked to an account.

"""

from datetime import datetime
import pickle
from pony.orm import Optional, Required
from typing import Sequence

from context.stack import ContextStack
from data.character import Character
from data.decorators import lazy_property

class Player(Character):

    """Playing Character (PC)."""

    first_name = Required(str)
    last_name = Required(str)
    account = Required("Account")
    created_on = Required(datetime, default=datetime.utcnow)
    binary_context_stack = Optional(bytes)

    @lazy_property
    def context_stack(self):
        """Return the stored or newly-build context stack."""
        stored = self.binary_context_stack
        if stored:
            return pickle.loads(stored)

        # Create a new context stack
        stack = ContextStack(self)

        # Add the static command layer as first layer
        stack.add_command_layer("static")
        return stack

    @property
    def full_name(self):
        """Return the player's full name."""
        return f"{self.first_name} {self.last_name}"

    def after_insert(self):
        """
        Hook called before the player is inserted.

        We take this opportunity to add the player name as a singular name.

        """
        self.names.singular = self.full_name

    def get_hashable_name(self, group_for: 'db.Character'):
        """
        Return a hashable name to indicate future grouping.

        By default, this method returns the singular name
        for this object (that is, the `get_name_for`  method with
        only one object, `self`).  However, this can be altered,
        to change the way object names are grouped.
        In this case, we return the player ID, because that is unique
        (and we don't want to group player names).

        Args:
            group_for (Character): the character to whom the list of objects
                    will be displayed.

        Returns:
            name (str): the hashable name.

        """
        return self.id

    def get_name_for(self, group_for: 'db.Character',
            group: Sequence['CanBeNamed']):
        """
        Return the singular or plural name for this object.

        This method is called to pluralize an object name, or to get
        the singular name if the object couldn't be grouped.

        Args:
            group_for (Character): the character to whom the list
                    of objects will be displayed.
            group (list of objects): the objects in the same group.
                    This list contains `self` and thus,
                    is at least one object in length.

        Returns:
            name (str): the singular or plural name to display, depending.

        """
        return self.full_name
