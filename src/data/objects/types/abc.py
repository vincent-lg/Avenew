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

"""Module containing the abstract object type."""

from abc import ABCMeta, abstractmethod
from typing import Union

from data.base import db

TYPES = {} # Dictionary of object types

class MetaType(ABCMeta):

    """Metaclass for object types."""

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if (name := cls.name) is not None:
            TYPES[name] = cls


class AbstractType(metaclass=MetaType):

    """
    Abstract type.

    Each object type should inherit from this class and implement the
    abstract methods.

    """

    name = None # The object name, should be unique across types.

    def __init__(self, obj: Union['db.Object', 'db.ObjectPrototype']):
        if isinstance(obj, db.Object):
            self.obj = obj
            self.prototype = obj.prototype
        elif isinstance(obj, db.ObjectPrototype):
            self.obj = None
            self.prototype = obj
        else:
            raise ValueError("invalid object")

    @property
    def db(self):
        """Return the attribute handler for the type storage."""
        if (handler := getattr(self, "cached_db_handler", None)):
            return handler

        from data.handlers import AttributeHandler
        obj = self.obj or self.prototype
        category = "object" if self.obj else "prototype"
        if obj is None:
            raise ValueError("the object is not set")

        handler = AttributeHandler(obj)
        handler.subset = f"type.{category}:{obj.id}.{self.name}"
        self.cached_db_handler = handler
        return handler

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
