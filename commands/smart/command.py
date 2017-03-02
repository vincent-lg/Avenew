"""
Module containing the SmartCommand.

SmartCommands are commands (inherited from the Command class)
but they handle features to help parsing, through the "params"
class attribute.  See the class documentation for more information.

"""

from commands.command import Command
from commands.smart.parameters.pipe import ParamPipe

class SmartCommand(Command):

    """Base class for a SmartCommand.

    A SmartCommand is an evennia Command with additional
    features.  Its main purpose is to help parsing of parameters
    using an extended definition of expected arguments.  For
    instance, the 'pk' command, to set the player-kill flag,
    could define a single parameter:  either 'on' or 'off'.
    More complex commands, like 'get', could require additional
    parameters:  first (optionally) a number, then an object
    name, then, optionally, the FROM keyword and a different
    object name.  This would result in more complex parameters
    that the SmartCommand will more easily interpret.

    """

    params = None

    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)
        if type(self).params is None:
            type(self).params = ParamPipe()
            self.setup()

    def setup(self):
        """Create the parameters using methods of self.params.

        (See the 'commands.parameters.pipe.ParamPipe for details.)

        """
        pass

    def func(self):
        """Actual function, parsing of parameters.

        DO NOT OVERRIDE this function in an inherited class.
        This method has two purposes:
        1.  To parse the parameters and display an error message if needed.
        2.  To call the 'execute' method where the command mechanism is.

        Therefore, you should override the 'execute' method,
        not the 'func' one.

        The parameters are parsed from self.args.  The result
        is then stored in attributes of 'self'.  For instance:
            class Roll(SmartCommand):
                '''Roll a dice X times.

                Usage:
                    roll [number]

                Roll a dice 1 or more times.  You can specify the
                number as an argument.  If no argument is specified,
                roll the dice only once.

                '''
                key = "roll"
                def setup(self):
                    self.params.add("number", default=1)

                def execute(self):
                    msg = "You roll a dice {} times.".format(self.number)
                    self.caller.msg(msg)

        In the MUD client:
            > roll 5
            You roll the dice 5 times.
            > roll
            You roll the dice 1 times.
            > roll ok
            This is not a valid number.

        """
        try:
            self.params.parse(self)
        except ValueError, err:
            self.caller.msg("|r{}|n".format(err))
        else:
            self.execute()

    def execute(self):
        """Execute the actual command.

        This method is called after parsing of parameters
        (if it occurred without error).  You can (and should)
        override this method in command classes.

        """
        pass
