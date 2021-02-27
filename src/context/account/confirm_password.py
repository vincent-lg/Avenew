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

"""Confirm password context, displayed when one wishes to confirm a new password."""

from context.session_context import SessionContext
import settings

class ConfirmPassword(SessionContext):

    """
    Context to confirm a new password for a new account.

    Input:
        <identical password>: valid password, move to account.email.
        <different passwords>: go back to account.create_password.
        /: slash, go back to account.create_password.

    """

    text = """
        Vous avez choisi un mot de passe pour ce compte. Veuillez l'entrer
        à nouveau, afin d'être sûr qu'il s'agisse bien de votre choix.
        Si vous voulez changer de mot de passe, entrez / pour revenir
        à l'écran précédent.
    """
    prompt = "Confirmez votre mot de passe :"

    async def input(self, password):
        """The user entered something."""
        original = self.session.options.get("password", "")

        if not original:
            await self.msg(
                "Comment êtes-vous arrivés à cette étape ? Quelque chose "
                "d'inattendu s'est produit, il vaut mieux entrer de nouveau "
                "votre mot de passe."
            )
            await self.move("account.create_password")
            return

        # Check that the passwords aren't different
        if original != password:
            await self.msg(
                "Oops, il semble que vous n'ayez pas entré le même mot "
                "de passe cete fois. Mieux vaut réessayer."
            )
            await self.move("account.create_password")
            return

        # That's the correct password
        await self.msg("Merci d'avoir confirmé votre mot de passe.")
        await self.move("account.email")
