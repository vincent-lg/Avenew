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

"""Phone object type."""

from data.objects.types.abc import AbstractType

class Clothing(AbstractType):

    """Phone object type."""

    name = "clothing"

    def update_prototype(self):
        """
        Called when the object prototype is added or updated.

        This method is called when the type is added to the object
        prototype (using `prototype.types.add(...)`) and each time the
        server starts, when the object prototype's types are first
        loaded (which might not happen right away).  Therefore,
        it is a good place to set default attributes, using the
        `if_necessary` property:

            with self.db.if_necessary as update:
                update.modifier = 3
                update.protection = 5

        In the previous example, these attributes will only be created
        if they don't already exist.

        """
        with self.db.if_necessary as update:
            update.protection = 35
            update.color = 8

    def update_object(self, prototype: 'AbstractType'):
        """
        Called when the object is created or updated.

        This method is called when the type is added to the object
        itself, which happens automatically when an object is created
        on a prototype (`prototype.create_at(...)`), and each time the
        server starts, when the object types are first loaded
        (which might not happen right away).  Therefore,
        it is a good place to set default attributes, using the
        `if_necessary` property:

            with self.db.if_necessary as update:
                update.max_modifier = prototype.db.modified
                update.default_protection = prototype.db.protection

        In the previous example, these attributes will only be created
        if they don't already exist.
        You have the guarantee that the specified `prototype`, holding
        the types on the prototype itself, has already been updated
        at this point.

        Args:
            prototype (AbstractType): the type object corresponding
                    to the same type on the object prototype, which
                    allows to transfer attributes quickly.

        """
        with self.db.if_necessary as update:
            update.max_protection = prototype.db.protection
            update.cur_color = prototype.db.color
