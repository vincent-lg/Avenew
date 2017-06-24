"""Module containing the abstract Behavior class."""

class Behavior(object):

    """Abstract class for behaviors."""

    @classmethod
    def call(cls, name, *args, **kwargs):
        """
        Call the behavior's method, if it exists.

        Args:
            name (str): the name of the behavior.

        """
        if hasattr(cls, name):
            return getattr(cls, name)(*args, **kwargs)
