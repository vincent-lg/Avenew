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

"""First Name context, to create a new player's first name."""

from random import choice
from textwrap import dedent

from context.session_context import SessionContext
from context.player._constants import Mood, Pronoun
from data.constants import Pronoun
import settings

ALLOWED_PRONOUNS = (Pronoun.SHE, Pronoun.HE)
SCREEN = """
Vous vous trouvez à l'arrière d'un taxi, roulant à vive allure sur une voie
express en direction de Sann Castigo, ville de la Californie bâtie sur les
côtes de l'océan Pacifique. Les approches d'une ville de taille imposante se
laissent observer par la fenêtre, la quantité de panneaux publicitaires
en étant l'un des plus importants. La vitesse du taxi commence à diminuer
au fur et à mesure que le trafic s'intensifie à l'approche de la bretelle
d'accès. À quelques centaines de mètres se trouve un point de sécurité, composé
de plusieurs voitures de police garées en travers de la route, laissant
une seule voie accessible et rendant le contrôle d'identité indispensable.
À présent à faible vitesse, votre taxi se dirige vers ce point de sécurité
et la vitre arrière s'abaisse automatiquement.
Un{e} agent{e} s'approche de votre véhicule, {approach}, sous l'œil attentif
de ses collègues et s'adresse à vous {voice} :
""".strip("\n")

OOC = """
TIP: vous devez entrer le prénom de votre nouveau personnage
     (pas nécessairement le vôtre !). Il vous sera demandé un nom de famille
     fictif pour votre personnage ensuite.
""".strip("\n")

class FirstName(SessionContext):

    """
    Context to enter the player's new first name.

    Input:
        <valid>: valid first name, move to player.last_name.
        <invalid>: invalid name, gives reason and stays here.

    """

    prompt = "Entrez le prénom de votre nouveau personnage :"

    async def greet(self):
        """Return the text to be entering when refreshing this context."""
        mood = choice(tuple(Mood))
        pronoun = choice(ALLOWED_PRONOUNS)
        e = "e" if pronoun is Pronoun.SHE else ""
        self.session.options["agent_mood"] = mood
        self.session.options["agent_pronoun"] = pronoun
        if mood is Mood.SOBER:
            approach = f"concentré{e} sur sa mission"
            voice = "d'une voix neutre"
            question = dedent("""
                Un instant, s'il vous plaît. Vous vous approchez de Sann
                Castigo, il y a quelques formalités à remplir, j'en ai peur.
                On surveille les nouveaux arrivés en ville, surtout en ce
                moment. Pouvez-vous me donner votre prénom ?
            """.strip("\n"))
        elif mood is Mood.BUSINESSLIKE:
            approach = "d'un pas rapide"
            voice = "d'une voix sèche"
            question = dedent("""
                Bien, contrôle d'identité s'il vous plaît. C'est la procédure.
                Votre prénom ?"
            """.strip("\n"))
        elif mood is Mood.TIRED:
            approach = "l'air fatigué"
            voice = "d'une voix lasse"
            question = dedent("""
                Bonjour, contrôle d'identité. On garde un œil sur les nouveaux
                arrivés en ville en ce moment. Quel est votre prénom ?
            """.strip("\n"))
        elif mood is Mood.BRUTAL:
            approach = "d'un pas brusque mais alerte"
            voice = "d'une voix brusque"
            question = dedent("""
                Contrôle d'identité. On veut pas d'histoire ici. Votre
                prénom s'il vous plaît ?
            """.strip("\n"))
        elif mood is Mood.POLITE:
            approach = "d'un air nonchalant"
            voice = "d'un ton poli, presque cordial"
            question = dedent("""
                Bienvenue à Sann Castigo. Excusez-moi d'interrompre votre
                voyage un instant, mais la procédure demande que l'on
                enregistre les nouveaux arrivants. Il y a eu pas mal de
                troubles, ces derniers temps. Enfin... puis-je avoir votre
                prénom s'il vous plaît ?
            """.strip("\n"))
        else:
            raise ValueError(f"mood not supported: {mood}")

        screen = SCREEN.format(e=e, approach=approach, voice=voice)

        # Add the question
        screen += '\n"' + question.strip() + '"'

        # Add the OOC tip.
        screen += "\n\n" + OOC

        return screen

    async def input(self, first_name):
        """The user entered something."""
        pronoun = self.session.options.get("agent_pronoun")
        e = "e" if pronoun is Pronoun.SHE else ""
        # Check that the name isn't a forbidden name
        if first_name.lower() in settings.FORBIDDEN_CHARACTER_NAMES:
            await self.msg(
                f"Le nom {name!r} est interdit. Veuillez "
                "en choisir un différent."
            )
            return

        await self.msg(
                f"L'agent{e} hoche la tête et écrit quelques mots sur un "
                "carnet tiré de sa poche."
        )
        self.session.options["first_name"] = first_name
        await self.move("player.last_name")
