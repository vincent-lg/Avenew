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

"""Home, the first active node in the login/chargen process."""

from context.session_context import SessionContext
from data.account import Account

class Home(SessionContext):

    """
    Context displayed just after MOTD.

    Input:
        new: the user wishes to create a new account.
        <existing account>: the user has an account and wishes to connect.

    """

    prompt = "Entrez votre nom d'utilisateur :"
    text = """
        Si vous possédez déjà un compte sur Avenew, entrez à présent son nom.
        Si ce n'est pas le cas, entrez 'nouveau' pour créer un compte.
    """

    async def input_nouveau(self):
        """The user has input 'new' to create a new account."""
        await self.move("account.username")

    async def input(self, username: str):
        """The user entered something else."""
        username = username.lower()
        account = Account.get(username=username)
        if account is None:
            await self.msg(
                    f"Le compte {username!r} n'a pas pu être trouvé. Si vous "
                    "souhaitez le créer, entrez la commande 'nouveau', sinon "
                    "essayez un autre nom."
            )
            return

        self.session.options["account"] = account
        await self.move("connection.password")
