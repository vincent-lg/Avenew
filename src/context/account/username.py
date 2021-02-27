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

"""New account context, displayed when one wishes to create a new account."""

from context.session_context import SessionContext
from data.account import Account
import settings

class Username(SessionContext):

    """
    Context called when the user wishes to create a new account.

    Input:
        <new username>: valid username, move to account.create_password.
        <invalid>: invalid username, gives reason and stays here.
        /: slash, go back to connection.home.

    """

    text = """
        Nouvel utilisateur, bienvenue sur Avenew !

        Vous souhaitez donc vous créer un compte. La premièrre étape est
        de choisir un nom d'utilisateur (ou nom de compte). Il est préférable,
        pour des raisons de sécurité, que ce nom soit différent du nom
        de vos personnages. Votre compte utilisateur permet juste de
        regrouper plusieurs personnages ensemble. Votre nom de compte est
        différent de votre nom de personnage. Personne en jeu ne verra votre
        nom de compte, si ce n'est les administrateurs qui ne communiqueront
        pas cette information à d'autres joueurs. Ainsi, si quelqu'un souhaite
        jouer avec vos personnages, il lui faudra deviner le nom de compte et
        le mot de passe, ce qui rend le cas hautement improbable.

        Tout comme le mot de passe, il est conseillé de ne pas communiquer
        votre nom de compte, même à des joueurs dont vous êtes proches. Le
        nom de compte pourra être modifié par la suite, toujours pour des
        raisons de sécurité. Il vous sera demandé à chaque connexion.
    """
    prompt = "Entrez votre nouveau nom de compte :"

    async def input(self, username):
        """The user entered something."""
        username = username.lower().strip()

        # Check that the name isn't too short
        if len(username) < settings.MIN_USERNAME:
            await self.msg(
                f"Le nom de compte {username!r} est invalide. Il doit "
                f"comprendre au moins {settings.MIN_USERNAME} caractères."
            )
            return

        # Check that the username isn't a forbidden name
        if username in settings.FORBIDDEN_USERNAMES:
            await self.msg(
                f"Le nom de compte {username!r} est un nom interdit. "
                "Vous ne pouvez créer un compte avec ce nom."
            )
            return

        # Check that nobody is using this username
        account = Account.get(username=username)
        if account:
            await self.msg(
                f"Le nom d'utilisateur {username!r} existe déjà. "
                "Choisissez-en un différent."
            )
            return

        await self.msg(f"Votre nouveau nom de compte : {username!r}.")
        self.session.options["username"] = username
        await self.move("account.create_password")
