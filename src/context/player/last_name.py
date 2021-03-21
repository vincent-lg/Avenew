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

"""Last name context, to create a new player's last name."""

from textwrap import dedent

from context.session_context import SessionContext
from context.player._constants import Mood, Pronoun
from data.constants import Pronoun
import settings

SCREEN = """
L'agent{e} continue :
""".strip("\n")

OOC = """
TIP : vous devez à présenter entrer le nom de famille fictif de votre
      futur personnage.
""".strip("\n")

class FirstName(SessionContext):

    """
    Context to enter the player's new first name.

    Input:
        <valid>: valid first name, move to player.last_name.
        <invalid>: invalid name, gives reason and stays here.

    """

    prompt = "Entrez le nom de famille de votre nouveau personnage :"

    async def greet(self):
        """Return the text to be entering when refreshing this context."""
        mood = self.session.options.get("agent_mood")
        pronoun = self.session.options.get("agent_pronoun")
        e = "e" if pronoun is Pronoun.SHE else ""
        if mood is Mood.SOBER:
            question = dedent("""
                Merci. Pourriez-vous me donner votre nom de famille à présent ?
            """.strip("\n"))
        elif mood is Mood.BUSINESSLIKE:
            question = dedent("""
                Bien noté. Votre nom de famille, s'il vous plaît ?
            """.strip("\n"))
        elif mood is Mood.TIRED:
            question = dedent("""
                Merci. Quel est votre nom de famille ?
            """.strip("\n"))
        elif mood is Mood.BRUTAL:
            question = dedent("""
                Bien. Nom de famille s'il vous plaît ?
            """.strip("\n"))
        elif mood is Mood.POLITE:
            question = dedent("""
                Merci bien. Pourriez-vous me donner votre nom de famille
                à présent, s'il vous plaît ?
            """.strip("\n"))
        else:
            raise ValueError(f"mood not supported: {mood}")

        screen = SCREEN.format(e=e)

        # Add the question
        screen += '\n"' + question.strip() + '"'

        # Add the OOC tip.
        screen += "\n\n" + OOC

        return screen

    async def input(self, last_name):
        """The user entered something."""
        pronoun = self.session.options.get("agent_pronoun")
        e = "e" if pronoun is Pronoun.SHE else ""
        # Check that the name isn't a forbidden name
        if last_name.lower() in settings.FORBIDDEN_CHARACTER_NAMES:
            await self.msg(
                f"Le nom {name!r} est interdit. Veuillez "
                "en choisir un différent."
            )
            return

        await self.msg(
                f"L'agent{e} hoche la tête et écrit quelques mots sur un "
                "calepin tiré de sa poche."
        )
        self.session.options["last_name"] = last_name
        await self.move("player.pronoun")
