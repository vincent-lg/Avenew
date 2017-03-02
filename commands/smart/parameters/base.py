"""Module containing the Parameter base class."""

class Parameter(object):

    """Base class of any parameters.

    A parameter is responsible for interpreting a string using
    the 'parse' method.  It can be mandatory or optional, with
    or without default value.  It is responsible for extracting
    a very specific information from a string (for instance, a
    number).

    """

    key = None

    def __init__(self):
        self.default = None
        self.attribute = type(self).key

    def __repr__(self):
        return "<Parameter {}>".format(repr(self.attribute))

    def parse(self, command, args):
        """Parse the 'args' parameter (a string).

        Expected arguments:
            self -- the parameter object
            command -- the SmartCommand object
            args -- the string argument (str)

        If parsing is successful, this method should write an
        attribute in the command object.  If parsing fails but
        the parameter is defined as optional, will retrieve the
        default value and write it in the command object.  If
        the parameter is mandatory, however, it will raise a
        ValueError exception (to be customized).

        """
        pass
