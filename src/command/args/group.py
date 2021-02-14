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

"""Argument group, containing branches."""

from typing import Optional, Union

from command.args.base import ArgSpace
from command.args.branch import Branch
from command.args.error import ArgumentError
from command.args.result import DefaultResult, Result

class Group:

    """
    Command argument group, to have several branches.

    A group in command arguments is meant to represent a set of argument
    branches.  An argument branch is a set of arguments, and a branch
    can either be verified or not.  A group in turn can contain
    several branches and help choose which one to execute through
    a partial parsing.  The group can then decide to propagate
    any error it meets, to use the one working branch or
    to generate an error of its own.

    """

    space = ArgSpace.UNKNOWN
    in_namespace = True

    def __init__(self, parser, optional=False):
        self.parser = parser
        self.branches = []
        self.optional = optional
        self.msg_error = "Specify something."

    def add_branch(self):
        """Add and return a new branch."""
        branch = Branch(self)
        self.branches.append(branch)
        return branch

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
        # Parse the several branches.  The aim is to select one
        # branch... or none at all.
        success = []
        for branch in self.branches:
            result = branch.parse(character, string, begin, end)
            if isinstance(result, Result):
                success.append((branch, result))

        # If there's more than one success, retrieve the most limited one.
        if len(success) > 1:
            success = max(success, key=lambda tup: len(tup[0].arguments))[1]
        elif len(success) == 1:
            success = success[0][1]

        if success:
            return success

        return ArgumentError(self.msg_error)

    def add_to_namespace(self, result, namespace):
        """Add the result to the namespace."""
        other = result.namespace
        for key, value in other:
            setattr(namespace, key, value)
