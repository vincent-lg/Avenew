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

    def __init__(self, prototype: 'db.ObjectPrototype'):
        self.prototype = prototype

    @property
    def db(self):
        """Return the attribute handler for the type storage."""
        if (handler := getattr(self, "cached_db_handler", None)):
            return handler

        from data.handlers import AttributeHandler
        if self.prototype is None:
            raise ValueError("the object prototype is not set")

        handler = AttributeHandler(self.prototype)
        handler.subset = f"type.{self.prototype.id}.{self.name}"
        self.cached_db_handler = handler
        return handler

    @abstractmethod
    def on_create(self):
        """
        Method called when this type is added to an object.

        Therefore, it's not called afterward, should the type be modified.
        This method can be used to add attributes to the object type
        in a flexible way, keeping in mind that later updates might
        not be applied and these later attributes might not exist.

        """
        pass
