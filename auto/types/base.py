"""
Abstract type.
"""

class BaseType(object):

    """
    All types should inherit from this type.
    """

    name = "unknown"

    def __init__(self, handler, obj):
        self.handler = handler
        self.obj = obj

    @property
    def db(self):
        """Return the storage (saver dict) for this type."""
        return self.handler.db(type(self).name)

    def create(self):
        """
        The type has just been added.

        Override this method to create custom behavior dependent on
        the type itself.

        """
        pass
