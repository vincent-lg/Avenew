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

"""Pronoun context, to create a new player's pronoun."""

from textwrap import dedent

from context.session_context import SessionContext
from context.player._constants import Mood, Pronoun
from data.constants import Pronoun
import settings

SCREEN = """
L'agent{e} continue :
""".strip("\n")

OOC = """
TIP : vous devez à présent entrer le pronom identifiant votre personnage.
      Notez que ce choix est volontairement aussi flexible que possible :
      il vous est simplement demandé de choisir parmi les pronoms "il",
      "elle" ou "iel" (complètement neutre). Il ne s'agit pas du genre
      de votre personnage et vous pourrez modifier ce pronom une fois en jeu
      si nécessaire. Cela aura surtout un impact sur les messages et
      les titres choisis par les autres pour vous adresser la parole.
""".strip("\n")

class PronounCtx(SessionContext):

    """
    Context to enter the player's pronoun.

    Input:
        <valid>: valid pronoun, moves to "player.age".
        <invalid>: invalid pronoun, gives list and stays here.

    """

    prompt = "Entrez le pronom de votre futur personnage :"

    async def greet(self):
        """Return the text to be displayed when refreshing this context."""
        mood = self.session.options.get("agent_mood")
        pronoun = self.session.options.get("agent_pronoun")
        e = "e" if pronoun is Pronoun.SHE else ""
        question = dedent("""
            Parfait. Pourriez-vous me donner le pronom par lequel
            vous êtes identifié(e) ?
        """.strip("\n"))

        screen = SCREEN.format(e=e)

        # Add the question
        screen += '\n"' + question.strip() + '"'

        # Add the OOC tip.
        screen += "\n\n" + OOC

        return screen

    async def input(self, pronoun):
        """The user entered something."""
        # Check that the pronoun is a valid choice.
        choices = {member.subject: member for member in Pronoun}
        pronoun = pronoun.lower()
        if pronoun in choices:
            member = choices[pronoun]
            self.session.options["pronoun"] = member
            pronoun = self.session.options.get("agent_pronoun")
            e = "e" if pronoun is Pronoun.SHE else ""
            await self.msg(
                    f"L'agent{e} hoche la tête et écrit quelques mots sur un "
                    "calepin tiré de sa poche."
            )
            await self.move("player.age")
        else:
            await self.msg(
                    f"""Désolé, ce pronom n'est pas valide. Les choix """
                    f"""possibles sont : "{'", "'.join(choices)}"."""
            )
