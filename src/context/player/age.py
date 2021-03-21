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

"""Age context, to create a new player's age."""

from textwrap import dedent

from context.session_context import SessionContext
from context.player._constants import Mood, Pronoun
from data.constants import Pronoun
import settings

SCREEN = """
L'agent{e} continue :
""".strip("\n")

OOC = """
TIP : vous devez à présenter entrer l'âge, approximatif, de votre nouveau
      personnage. Cette information est simplement un repère. Soyez
      conscient(e) qu'il n'est pas permis de jouer un personnage mineur
      (moins de 18 ans) et un tel choix sera systématiquement refusé.
""".strip("\n")

OK = """
L'agent{e} hoche la tête et écrit quelques mots sur un calepin avant de
reculer et vous faire signe de passer. La vitre arrière remonte automatiquement
tandis que le taxi se glisse entre deux voitures de police et accélère
de nouveau. La ville de Sann Castigo vous entoure à présent, bien que vous
n'ayiez pas bien le temps d'en voir grand-chose, outre de hauts immeubles
et quelques parcs. Le taxi ralentit enfin devant un bâtiment d'aspect
officiel et se gare contre le trottoir. Vous payez le chauffeur et
descendez de voiture, constatant que le taxi repart immédiatement,
sans doute à l'affût de nouveaux clients.

TIP : bienvenue dans la ville de Sann Castigo, bienvenue en jeu !
      À partir de cet instant, vous pouvez utiliser les commandes habituelles
      aux jeux de type "MUD" pour vous déplacer et faire des actions.
      Si vous n'avez jamais joué(e) à ce type de jeu, il vous est vivement
      conseillé de vous diriger au nord, dans l'hôtel de ville, en tapant
      "nord" (sans les guillemets) puis la touche ENTRÉE de votre clavier.
      Pour ceux ayant l'habitude des MUD, sachez que l'hôtel de ville vous
      proposera des informations et outils qui vous seront utiles pour
      commencer (notamment de l'argent, des vêtements et autre). Il n'est
      pas absolument nécessaire d'y aller tout de suite, vous pourrez y
      revenir plus tard, mais il pourrait être utile d'y faire un tour,
      quitte à y revenir après.
""".strip("\n")

class Age(SessionContext):

    """
    Context to enter the player's age.

    Input:
        <valid>: valid age, move to player.complete.
        <invalid>: invalid age, gives reason and stays here.

    """

    prompt = "Entrez l'âge de votre nouveau personnage :"

    async def greet(self):
        """Return the text to be displayed when refreshing this context."""
        mood = self.session.options.get("agent_mood")
        pronoun = self.session.options.get("agent_pronoun")
        ppronoun = self.session.options.get("pronoun")
        e = "e" if pronoun is Pronoun.SHE else ""
        pe = "e" if ppronoun is Pronoun.SHE else ""
        if mood is Mood.SOBER:
            question = dedent(f"""
                Merci. Pourriez-vous à présent me donner votre âge ?
                Vous n'êtes pas obligé{pe} de le préciser à l'année prêt.
            """.strip("\n"))
        elif mood is Mood.BUSINESSLIKE:
            question = dedent(f"""
                Parfait. Pourriez-vous à présent me donner votre âge ?
                Vous n'êtes pas obligé{pe} de le préciser à l'année prêt.
            """.strip("\n"))
        elif mood is Mood.TIRED:
            question = dedent(f"""
                Passionnant. Pourriez-vous à présent me donner votre âge ?
                Vous n'êtes pas obligé{pe} de le préciser à l'année prêt.
            """.strip("\n"))
        elif mood is Mood.BRUTAL:
            question = dedent(f"""
                Pourriez-vous à présent me donner votre âge ?
                Vous n'êtes pas obligé{pe} de le préciser à l'année prêt.
            """.strip("\n"))
        elif mood is Mood.POLITE:
            question = dedent(f"""
                Merci encore. Pourriez-vous à présent me donner votre âge ?
                Vous n'êtes pas obligé{pe} de le préciser à l'année prêt.
            """.strip("\n"))
        else:
            raise ValueError(f"mood not supported: {mood}")

        screen = SCREEN.format(e=e, pe=pe)

        # Add the question
        screen += '\n"' + question.strip() + '"'

        # Add the OOC tip.
        screen += "\n\n" + OOC

        return screen

    async def input(self, age):
        """The user entered something."""
        pronoun = self.session.options.get("agent_pronoun")
        e = "e" if pronoun is Pronoun.SHE else ""
        # Check that the age is valid.
        try:
            age = int(age)
        except ValueError:
            await self.msg(
                    f"Désolé, {age} n'est pas un âge valide."
            )
        else:
            if age < 0:
                await self.msg("Les âges négatifs ne sont pas autorisés.")
            elif age < 18:
                await self.msg(
                        "Les personnages mineurs ne sont pas autorisés."
                )
            elif age > 110:
                await self.msg(
                    "Il pourrait être préférable de choisir un âge moindre."
                )
            else:
                await self.msg(OK.format(e=e))
                self.session.options["age"] = age
                await self.move("player.complete")
