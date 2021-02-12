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

"""IFFALSE assembly expression, a conditional GOTO if the MRV is False."""

from scripting.assembly.abc import BaseExpression
from scripting.assembly.exceptions import MoveCursor

class IfFalse(BaseExpression):

    """
    IFFALSE assembly expression.

    Args:
        None.

    This expression's only role is to jump to another line if
    the most recent value (MRV) in the stack is False,
    doing nothing otherwise.

    """

    name = "IFFALSE"

    @classmethod
    async def process(cls, script, stack, cursor, pop=True):
        """
        Process this expression.

        Args:
            script (Script): the script object.
            stack (LifoQueue): the current stack.
            cursor (int): the new cursor position.
            pop (bool, optional): should the boolean be popped?

        """
        value = stack.get(block=False)
        if not value:
            if not pop:
                stack.put(value, block=False)

            raise MoveCursor(cursor)
