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


"""Wrapper context, to wrap a command layer in a chqaracter context."""

from command.layer import LAYERS
from context.character_context import CharacterContext

class Layer(CharacterContext):

    """Layer context, to wrap a command layer in a character context."""

    def __init__(self, character):
        super().__init__(character)
        self.layer = None
        self.layer_name = None

    def __str__(self):
        if (layer := self.layer):
            layer = layer.name
        else:
            layer = ""

        return f"{self.pyname}({layer})"

    def get_prompt(self):
        """Return the character prompt."""
        return "HP: 100   Man: 100   End: 100"

    async def handle_input(self, command: str):
        """Handle the user input, redirect to the command layer."""
        command = self.layer.find_command(command)
        if command is None:
            return

        # Otherwise, parse the command
        await command.parse_and_run()
        return True

    def cannot_find(self, command: str) -> str:
        """
        Error to send when the command cannot be found.

        This is called when the command cannot be found in this context,
        or anywhere in the command stack.

        Args:
            command (str): the command.

        """
        return self.layer.cannot_find(command)
