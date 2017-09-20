"""
Abstract type.
"""

from evennia.utils.utils import lazy_property

class BaseType(object):

    """
    All types should inherit from this class.

    You can override the following methods.  Note that they are called
    ONLY if the type is defined on an object, and not on a prototype:
        at_type_creation: the type has been added to an object.
        at_server_start: the server starts, useful to re-do some actions.

    """

    name = "unknown"

    def __init__(self, handler, obj):
        self.handler = handler
        self.obj = obj

    @lazy_property
    def db(self):
        """Return the storage (saver dict) for this type."""
        return self.handler.db(type(self).name)

    def at_type_creation(self):
        """
        The type has just been added to an object.

        Override this method to create custom behavior dependent on
        the type itself.

        """
        pass

    def at_server_start(self):
        """The server has restarted.

        Override this hook to re-do some custom actions for this type
        when the server restarts.  Notice that this hook will not be
        called if the type is defined on a prototype.

        """
        pass

