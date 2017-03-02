"""
Module containing the ParamPipe class.

A ParamPipe object is created for every SmartCommand.  In it
is defined the list of expected parameters to be used.  The
'add' method is probably the most useful one, and you should
use it in the 'setup' method of your class inheriting
'SmartCommand'.

"""

from commands.smart.parameters.list import DICT_PARAM

class ParamPipe(object):

    """A parameter pipe, defined in every SmartCommand.

    A parameter pipe (ParamPipe) is used to store a list of
    parameters with various rules:  type, default value,
    mandatory presence and grouping should eventually be
    supported.  A ParamPipe object is created for every
    SmartCommand which can add parameters to it.  When a
    SmartCommand is called, it uses the 'parse' method of
    ParamPipe to 'parse' a string into a list of interpreted
    parameters.

    Parameers are defined in the same package
    ('commands.parameters').  The 'add' method is used to add
    new parameters to the pipe.  Further customization is still
    possible, using the returned parameter object.

    """

    def __init__(self):
        self._parameters = []
        self._groups = []

    def add(self, ptype, default=None):
        """Add a new parameter.

        Expected arguments:
            ptype -- the type of parameter (str)
            default -- the default value of this parameter if not specified

        If 'default' is left to None, or set to None, the
        created parameter will assume it's mandatory (it has to
        be specified).  Use a different default value to
        specify 'no value' (an empty string, for isntance).

        """
        pclass = DICT_PARAM.get(ptype)
        if pclass is None:
            raise ValueError("the parameter type {} doesn't exist".format(
                    repr(ptype)))

        # Create the parameter object
        parameter = pclass()
        parameter.default = default
        self._parameters.append(parameter)
        return parameter

    def parse(self, command):
        """Parse the specified args.

        This is a very simple implementation for the time being.

        """
        args = command.args
        for parameter in self._parameters:
            args = parameter.parse(command, args)
