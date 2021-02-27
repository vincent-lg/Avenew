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

"""New email context, displayed when one wishes to create an email address."""

from context.session_context import SessionContext
from data.account import Account
import settings

class Email(SessionContext):

    """
    Context to set the account email address.

    Input:
        <valid>: move to account.complete.
        <invalid>: invalid email address, gives reason and stays here.
        /: slash, go back to connection.create_password.

    """

    text = """
        À présent, veuillez entrer une adresse e-mail. Celle-ci sera
        associée à votre compte et ne sera pas visible par les autres joueurs.
        Elle n'est pas strictement obligatoire, vous pouvez n'entrer
        aucune adresse e-mail, aucune confirmation ne vous sera demandée.
        Cependant, avoir une adresse e-mail valide n'est pas sans avantage :

        *  Vous pourrez être averti de la communication en jeu (comme les
           SMS que vous recevrez pendant votre déconnexion). Cette option,
           comme toutes les autres, peut être désactivée tout en gardant
           une adresse e-mail valide ;
        *  En cas de rapport de bug ou de suggestion, les administrateurs
           seront en mesure de vous répondre directement. Bien que vous
           aurez accès à leur réponse dans tous les cas, le fait de la recevoir
           par e-mail vous permettra de mieux gérer ces notifications ;
        *  Si vous perdez le mot de passe d'accès à votre compte, il ne sera
           pas possible de renouveler votre mot de passe si vous n'avez pas
           d'adresse e-mail valide renseignée ;
        *  Si vous avez besoin d'entrer en contact (hors du jeu) avec l'équipe
           d'administration, l'adresse e-mail sera considérée comme la preuve
           que vous possédez bien ce compte. Si vous n'en avez pas associé,
           ces e-mails risquent d'avoir moins de crédibilité ;
        *  Les utilisateurs ayant précisés une adresse e-mail valide pourront
           être notifiés des nouveautés, incluant les corrections de bug,
           ajouts de commande, ajouts de nouveautés dans l'univers et
           évènements RP. Il est bien facile de manquer ces annonces (surtout
           les évènements RP), spécifier une adresse e-mail valide est une
           garantie d'avoir toutes les informations en temps et heure.

        En dernier recours, il est préférable de préciser une adresse e-mail
        valide ici ou de ne rien préciser du tout et appuyer sur ENTRÉE pour
        continuer. Il n'est pas encouragé de préciser une "fausse adresse
        e-mail", cela ne profite à personne.
    """
    prompt = "Entrez une adresse e-mail ou appuyer sur ENTRÉE :"

    async def input(self, email):
        """The user entered something."""
        # Very basic test to try and filter invalid email adresses
        email = email.strip()
        if email and "@" not in email:
            await self.msg(
                    f"Bon ! On dirait que {email!r} n'est pas une adresse "
                    "e-mail valide. Veuillez réessayer."
            )
            return

        account = Account.get(email=email)
        if account:
            await self.msg(
                    f"Désolé, l'adresse e-mail {email!r} est déjà utilisée "
                    "par un autre compte. Veuillez entrer une nouvelle "
                    "adresse e-mail."
            )
            return

        self.session.options["email"] = email
        await self.msg(
            f"Merci ! Votre adresse e-mail, {email}, a bien été associée "
            "à ce compte sur Avenew."
        )
        await self.move("account.complete")
