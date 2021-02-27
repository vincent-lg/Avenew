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

"""Create password context, displayed when one wishes to create a new account."""

from context.session_context import SessionContext
import settings

class CreatePassword(SessionContext):

    """
    Context to create a new password for a new account.

    Input:
        <valid password>: valid password, move to account.confirm_password.
        <invalid password>: invalid password, gives reason and stays here.
        /: slash, go back to account.new.

    """

    text = """
        Puisque vous avez choisi votre nom d'utilisateur, veuillez maintenant
        entrer le mot de passe associé à ce compte. Il vous sera demandé à
        chaque connexion.

        Il est important de se souvenir que le nom d'utilisateur et le
        mot de passe peuvent protéger vos personnages. Les autres joueurs ne
        verront ni votre nom de compte (raison pour laquelle il est préférable
        que le nom de compte diffère du nom de votre personnage en jeu) ni,
        bien sûr, votre mot de passe.

        Essayez d'avoir un mot de passe sécurisé (incluant des minuscules,
        majuscules, chiffres et symboles) pour éviter que d'autres utilisent
        votre compte, et vos personnages.

        Entrez votre nouveau mot de passe :
    """

    async def input(self, password):
        """The user entered something."""
        # Check that the password isn't too short
        if len(password) < settings.MIN_PASSWORD:
            await self.msg(
                f"Ce mot de passe est invalide. Il devrait "
                f"au moins contenir {settings.MIN_PASSWORD} caractères. "
                "Veuillez réessayer."
            )
            return

        self.session.options["password"] = password
        await self.move("account.confirm_password")
