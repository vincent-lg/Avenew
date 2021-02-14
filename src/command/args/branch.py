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

"""Argument branch."""

from typing import Optional, Union

from command.args.base import ARG_TYPES
from command.args.error import ArgumentError
from command.args.namespace import Namespace

from command.args.result import Result

NOT_SET = object()

class Branch:

    """
    Argument branch, a suite of arguments.

    A branch should be checked in sequence to be valid.  However, some
    arguments in a branch can be optional.

    """

    def __init__(self, optional=False):
        from command.args.args import CommandArgs, _NOT_SET
        self.optional = optional
        self.arguments = []
        self._args = CommandArgs()

    def __repr__(self):
        return f"<ArgBranch>"

    def add_argument(self, arg_type: str, *args, dest: Optional[str] = None,
            optional=False, default=NOT_SET, **kwargs):
        """
        Add a new argument to the parser.

        Args:
            arg_type (str): the argument type.
            dest (str, optional): the attribute name in the namespace.
            optional (bool, optional): is this argument optional?

        Additional keyword arguments are sent to the argument class.

        """
        from command.args.args import _NOT_SET
        default = _NOT_SET if default is NOT_SET else default
        arg_class = ARG_TYPES.get(arg_type)
        if arg_class is None:
            raise KeyError(f"invalid argument type: {arg_type!r}")

        dest = dest or arg_type
        argument = arg_class(*args, dest=dest, optional=optional,
                default=default, **kwargs)
        self._args.arguments.append(argument)
        return argument

    def parse(self, character: 'db.Character', string: str, begin: int = 0,
            end: Optional[int] = None) -> Union[Result, ArgumentError]:
        """
        Parse the argument.

        Args:
            character (Character): the character running the command.
            string (str): the string to parse.
            begin (int): the beginning of the string to parse.
            end (int, optional): the end of the string to parse.

        Returns:
            result (Result or ArgumentError).

        """
        namespace = self._args.parse(character, string, begin, end)
        if isinstance(namespace, Namespace):
            result = Result(0, None, "")
            result.namespace = namespace
        else:
            result = namespace

        return result
