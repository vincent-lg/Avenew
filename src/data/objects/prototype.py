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

"""ObjectPrototype entity, an object prototype."""

import typing as ty

from pony.orm import Required, Set, select

from data.base import db, PicklableEntity
from data.decorators import lazy_property
from data.handlers import (
        AttributeHandler, BlueprintHandler, DescriptionHandler,
        NameHandler, TagHandler,
)
from data.objects.types.handler import TypeHandler

class ObjectPrototype(PicklableEntity, db.Entity):

    """Object prototype entity, to define objects."""

    barcode = Required(str, unique=True, index=True)
    objects = Set("Object", reverse="prototype")

    @lazy_property
    def db(self):
        return AttributeHandler(self)

    @lazy_property
    def tags(self):
        return TagHandler(self)

    @lazy_property
    def blueprints(self):
        return BlueprintHandler(self)

    @lazy_property
    def names(self):
        return NameHandler(self)

    @lazy_property
    def description(self):
        return DescriptionHandler(self)

    @lazy_property
    def types(self):
        return TypeHandler(self)

    def create_at(self, location: 'db.Room'):
        """
        Create an object at this location.

        Args:
            location (Room): the object's intended location.

        Returns:
            object (Object): the new object.

        """
        # Find the barcode (needs optimization).
        existing = select(o.barcode for o in self.objects)
        x = 1
        found = False
        while not found:
            barcode = f"{self.barcode}_{x}"
            if barcode not in existing:
                found = True
            x += 1

        obj = self.objects.create(barcode=barcode)

        obj.location = location

        # Subscribe to names
        obj.names.register(self.names.singular)
        obj.names.register(self.names.plural)

        # Add object types
        for obj_type in self.types:
            obj.types.add(obj_type)

        return obj
