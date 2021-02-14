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

"""Handler to add types to objects and object prototypes."""

import typing as ty

from pony.orm import commit, select

from data.base import db
from data.handlers.tags import TagHandler
from data.objects.types.abc import TYPES
from data.objects.types.abc import AbstractType
import settings

class TypeHandler(TagHandler):

    """Type handler, using a tag handler behind the scenes."""

    subset = "type"

    def __init__(self, owner):
        super().__init__(owner)
        self.cached_types = {}

    def __iter__(self):
        """
        Return the types for the owner.
        """
        links = self._get_all_tags()

        # Get the types
        types = {}
        for link in links:
            name = link.tag.name
            cached = self.cached_types.get(name)
            if cached is not None:
                types[name] = cached
                continue

            # Create the type object
            obj_class = TYPES.get(name)
            if obj_class is None:
                raise ValueError(f"unknown type: {name}")

            obj_type = obj_class(self._TagHandler__owner)
            self.cached_types[name] = obj_type
            types[name] = obj_type

        return iter(tuple(types.values()))

    def __contains__(self, name_or_type: ty.Union[str, AbstractType]):
        """Return whether this instance contains this tag."""
        if isinstance(name_or_type, AbstractType):
            name = name_or_type.name
        else:
            name = name_or_type
        return super().__contains__(name)

    def has(self, name_or_type: ty.Union[str, AbstractType]) -> bool:
        """
        Return whether this type is present in this object.

        Args:
            name_or_type (str or AbstractType): the type.

        Returns:
            present (bool): whether this object is of this type.

        """
        if isinstance(name_or_type, AbstractType):
            name = name_or_type.name
        else:
            name = name_or_type
        return super().get(name)

    def get(self, name_or_type: ty.Union[str, AbstractType],
            create: ty.Optional[bool] = False) -> AbstractType:
        """
        Return the abstract type with the specified name.

        If `create` is set to `True`, create the type if doesn't exist.

        Args:
            name_or_type (str or AbstractType): the type to get.

        Returns:
            type (AbstractType): the object type.

        Raises:
            ValueError: if the type doesn't exist and `create` is False.

        """
        if isinstance(name_or_type, AbstractType):
            name = name_or_type.name
        else:
            name = name_or_type
        cached = self.cached_types.get(name)
        if cached:
            return cached

        owner = self._TagHandler__owner
        obj_class = TYPES.get(name)
        if obj_class is None:
            raise ValueError(f"unknown type: {name}")

        obj_type = obj_class(owner)
        self.cached_types[name] = obj_type

        # Try to query it.
        if name in self:
            return obj_type
        elif create:
            # Add the object type.
            self.add(name)
            return obj_type

    def add(self, name_or_type: ty.Union[str, AbstractType]):
        """
        Add the object type to this instance.

        If this object already has this type, do nothing.

        Args:
            name_or_type (str or ObjectType): the type to add.

        """
        if isinstance(name_or_type, AbstractType):
            name = name_or_type.name
        else:
            name = name_or_type

        super().add(name)
        obj_type = self.get(name)

        # Update it.
        owner = self._TagHandler__owner
        if isinstance(owner, db.ObjectPrototype):
            obj_type.update_prototype()

            # Add the type to objects.
            for sub_obj in owner.objects:
                sub_obj.types.add(name)
        elif isinstance(owner, db.Object):
            prototype = owner.prototype
            if name not in prototype.types:
                self.remove(name)
                raise ValueError(
                        f"type {name} cannot be added to this "
                        "object, because the object prototype doesn't "
                        "have it set"
                )

            parent = prototype.types.get(name, create=True)
            obj_type.update_object(parent)
        else:
            raise ValueError(
                    "the owner is neither object prototype nor object"
            )

    def remove(self, name_or_type: ty.Union[str, AbstractType]):
        """
        Remove the type from the instance.

        If the type isn't present, do nothing.

        Args:
            name_or_type (str or AbstractType): the type to remove.

        """
        if isinstance(name_or_type, AbstractType):
            name = name_or_type.name
        else:
            name = name_or_type
        return super().remove(name)
