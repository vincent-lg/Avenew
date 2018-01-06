# -*- coding: utf-8 -*-

"""Module dcontaining the menu nodes of logged in account.

This menu allows to login to character, create a new one, delete
one and so on.

"""

import re
from textwrap import dedent

from django.conf import settings
from evennia import ChannelDB, ObjectDB
from evennia.utils import create, evmenu, logger
from evennia.utils.evmenu import EvMenu

from typeclasses.characters import Character
from world.utils import latinify

## Constants
RE_VALID_FIRST_NAME = re.compile(r"^[a-z -]{2,}$", re.I)
RE_VALID_LAST_NAME = re.compile(r"^[a-z -]{2,}$", re.I)

## Menu nodes
def choose_characters(account, command):
    """Log into one of this account's characters."""
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Appuyez sur ENTRER pour continuer.",
            "goto": "start",
        },
    )

    command = command.strip()

    # Search for a valid character
    session = account.db._session
    for i, character in enumerate(account.db._playable_characters):
        if command == str(i + 1):
            del account.db._session
            account.puppet_object(session, character)
            return "", None

    text = "|rImpossible de trouver ce personnage. Essayez à nouveau.|n"
    text += "\n" + _text_choose_characters(account)
    options = _options_choose_characters(account)
    return text, options

def create_character(account):
    """Display the introduction to the character creation."""
    text = dedent("""
        Vous vous trouvez à l'arrière d'un taxi, fonçant sur la voix express d'une
        autoroute. La vitesse ionitiale de votre véhicule diminue peu à peu, tandis
        que le flot de voitures, motos et camions signale l'approche d'une sortie
        importante. Le taxi s'engage sur une voie latérale et s'arrête à quelques
        mètres d'un cordon de sécurité, visiblement improvisé, barrant l'accès
        aux zones urbaines.

        Un officier de police se détache du groupe, faisant signe à votre conducteur
        de baisser la vitre arrière de votre côté. Ouvrant son carnet et se
        préparant à prendre note, il vous regarde attentivement :
            "Juste quelques questions avant de poursuivre votre route... on n'a pas
            besoin d'ennuis supplémentaires ici. Pour commencer, qui êtes-vous ?
            Donnez-moi votre prénom, s'il vous plaît.

        Entrez le prénom de votre nouveau personnage.
    """.strip("\n"))
    options = (
        {
            "key": "_default",
            "desc": "Entrez le prénom de votre nouveau personnage.",
            "goto": "create_first_name",
        },
    )

    return text, options

def create_first_name(account, command):
    """Prompt the new character for his/her first name."""
    command = command.strip()
    if not RE_VALID_FIRST_NAME.search(latinify(command)):
        text = dedent("""
            |rDésolé, ce prénom n'est pas valide.|n
            Un prénom correct peut comporter des lettres, caractères accentués et
            éventuellement des espaces. D'ici, vous pouvez :

                Entrer |yp|n pour revenir au choix de personnage.
                Ou entrer de nouveau le prénom de ce personnage.
        """.strip("\n"))
        options = (
            {
                "key": "p",
                "desc": "Revenir au choix de personnage.",
                "goto": "display_characters",
            },
            {
                "key": "_default",
                "desc": "Entrez de nouveau le prénom de votre personnage.",
                "goto": "create_first_name",
            },
        )
    else:
        first_name = " ".join(word.capitalize() for word in command.split(" "))
        account.db._first_name = first_name

        # Redirects to the creation of the last name
        text = dedent("""
            L'officier de police vous regarde d'un air vaguement curieux.
                "Bien... c'est déjà quelque chose. Pouvez-vous me donner votre nom de
                famille à présent ?"

            Entrez le nom de famille de votre nouveau personnage.
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Entrez le nom de famille de votre nouveau personnage.",
                "goto": "create_last_name",
            },
        )

    return text, options

def create_last_name(account, command):
    """Prompt the new character for his/her last name."""
    command = command.strip()

    last_name = " ".join(word.capitalize() for word in command.split(" "))
    first_name = account.db._first_name
    full_name = first_name + " " + last_name

    # Gets the characters with the same name
    characters = Character.objects.filter(db_key__iexact=full_name)
    if not RE_VALID_LAST_NAME.search(latinify(command)):
        text = dedent("""
            |rDésolé, ce nom de famille n'est pas valide.|n
            Un nom de famille doit comporter des lettres (éventuellement accentuées)
            et des espaces. D'ici vous pouvez :
                Entrer |yp|n pour revenir au choix de prénom.
                Ou entrez de nouveau le nom de famille de ce personnage.
        """.strip("\n"))
        options = (
            {
                "key": "p",
                "desc": "Revenir au choix du prénom de votre peresonnage.",
                "goto": "pre_first_name",
            },
            {
                "key": "_default",
                "desc": "Entrez à nouveau le nom de famille de votre personnage.",
                "goto": "create_last_name",
            },
        )
    elif len(characters) > 0:
        text = dedent("""
            |rUn personnage nommé {} existe déjà.  Vous pouvez :
                Entrer |yp|n pour revenir au choix de prénom.
                Ou entrez de nouveau le nom de famille de ce personnage.
        """.format(full_name).strip("\n"))
        options = (
            {
                "key": "p",
                "desc": "Revenir au choix du prénom de votre personnage.",
                "goto": "pre_first_name",
            },
            {
                "key": "_default",
                "desc": "Entrer à nouveau le nom de famille de votre personnage.",
                "goto": "create_last_name",
            },
        )
    else:
        account.db._full_name = full_name
        del account.db._first_name

        # Redirects to the gender selection.
        text = dedent("""
            L'officier de police hoche la tête et griffonne sur son carnet :
                "Pourrait être pire... Quel genre dois-je indiquer ?"

            Choisissez votre genre (|yF|n ou |yM|n).
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Entrez votre genre (F ou H).",
                "goto": "select_gender",
            },
        )

    return text, options

def select_gender(account, command):
    """Prompt the new character for his/her gender."""
    gender = command.strip().lower()
    if gender not in "mf":
        text = dedent("""
            L'officier de police se gratte la tête.
                "Pardon ? Je n'ai pas compris."

            Entrez |yF|n pour féminin ou |yM|n pour masculin.
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Entrez le genre de ce personnage.",
                "goto": "select_gender",
            },
        )
    else:
        female = True if gender == "f" else False
        title = "madame" if female else "monsieur"
        account.db._female = female

        text = dedent("""
            L'officier de police hoche la tête et griffonne sur son carnet :
                "Merci {title}. C'est presque fini. Il me faudrait juste savoir votre âge."

            Entrez l'âge de votre personnage.
        """.strip("\n")).format(title=title)
        options = (
            {
                "key": "_default",
                "desc": "Entrez l'âge de votre nouveau personnage.",
                "goto": "select_age",
            },
        )

    return text, options

def select_age(account, command):
    """Prompt the new character for his/her age."""
    age = command.strip()

    try:
        age = int(age)
    except ValueError:
        age = None

    if age is None:
        text = dedent("""
            L'officier de police se gratte la tête pensivement.
                "Désolé, je n'ai pas compris."

            Entrez l'âge de votre personnage à nouveau."
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Entrez l'âge de votre personnage.",
                "goto": "select_age",
            },
        )
    else:
        full_name = account.db._full_name
        female = account.db._female
        title = "madame" if female else "monsieur"
        options = (
            {
                "key": "_default",
                "desc": "Entrez l'âge de votre personnage.",
                "goto": "select_age",
            },
        )

        # There are invalid choices
        if age < 0:
            text = dedent("""
                L'officier de police recule d'un pas, apparemment surpris :
                    "Hmmm, me semble pas possible. Sans doute une erreur."

                Entrez l'âge de votre personnage.
            """.strip("\n"))
        elif age < 10:
            text = dedent("""
                L'officier de police vous considère avec surprise :
                    "Et où sont tes parents ? Me faut parler à un adulte responsable, désolé."

                Entrez l'âge de votre personnage.
            """.strip("\n"))
        elif age < 16:
            text = dedent("""
                L'officier de police vous fixe de haut en bas :
                    "Désolé, je ne peux autoriser que des adultes ici, à moins qu'ils
                    soient accompagnés. Ce n'est pas bien juste, mais ce sont les ordres.
                    Et le droit de conduire, c'est à 16 ans ici. Si tu as moins, me faudra
                    voir tes parents. Maintenant, tu as le droit de mentir aussi, mais
                    sois convaincant au moins."

                Entrez l'âge de votre personnage.
            """.strip("\n"))
        else:
            text = dedent("""
                L'officier de police écrit de nouveau dans son carnet, avant de le ranger :
                    Ça suffira. Bon séjour parmi nous, {title}."

                L'officier de police recule et vous fait signe de passer au travers
                du cordon de sécurité. Votre taxi reprend de la vitesse en entrant en ville.
                Au bout de quelques minutes, il ralentit et finit par s'immobiliser devant
                un hôtel semblant un peu décrépit, vu de l'extérieur. Vous descendez,
                payez le prix de la course et regardez le taxi s'éloigner avant d'étudier
                votre nouvel environnement.
            """.strip("\n")).format(title=title)

            # Create the character
            character = _create_character(full_name, account)
            character.db.female = female
            character.db.age = age
            del account.db._full_name
            del account.db._female

            # Connects on this character
            account.msg(text)
            session = account.db._session
            del account.db._session
            account.puppet_object(session, character)
            return "", None

    return text, options

## Transition nodes
def display_characters(account):
    """This node simply displays the character list.

    The input will be redirected to the 'choose_characters' menu
    node.  'display_characters' is useful to maintain a layer
    between a node and the character menu.

    """
    text = _text_choose_characters(account)
    options = _options_choose_characters(account)
    return text, options

def pre_first_name(account):
    """A menu node to pause before the choice of the first name."""
    text = dedent("""
        Un officier de police raye quelque chose dans son carnet :
            "Bon, recommençons du début alors. Pouvez-vous me donner votre prénom ?

        Entrez le prénom de votre nouveau personnage.
    """.strip("\n"))
    options = (
        {
            "key": "_default",
            "desc": "Entrez le prénom de votre nouveau personnage.",
            "goto": "create_first_name",
        },
    )

    return text, options

## Private functions
def _create_character(name, account):
    """Create a new character.

    Args:
        name (str): the name of the character to be created.
        account (Account): the account owning the character.

    Returns:
        The newly-created character.

    """
    # Look for default values
    permissions = settings.PERMISSION_ACCOUNT_DEFAULT
    typeclass = settings.BASE_CHARACTER_TYPECLASS
    home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)

    # Create the character
    character = create.create_object(typeclass, key=name, home=home,
            permissions=permissions)

    # Set playable character list
    account.db._playable_characters.append(character)

    # Allow only the character itself and the account to puppet it.
    character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) " \
            "or pperm(Immortals)" % (character.id, account.id))

    # If no description is set, set a default description
    if not character.db.desc:
        character.db.desc = ""

    # We need to set this to have @ic auto-connect to this character.
    account.db._last_puppet = character


    # Join the new character to the public channel
    pchannel = ChannelDB.objects.get_channel(settings.DEFAULT_CHANNELS[0]["key"])
    if not pchannel or not pchannel.connect(character):
        string = "New character '%s' could not connect to public channel!" % character.key
        logger.log_err(string)

    return character

def _text_choose_characters(account):
    """Display the menu to choose a character."""
    text = "Entrez un numéro pour vous connecter sur ce personnage.\n"
    characters = account.db._playable_characters
    if len(characters):
        for i, character in enumerate(characters):
            text += "\n  |y{}|n - Jouer avec {}.".format(str(i + 1),
                    character.name)
    else:
        text += "\n  Aucun personnage n'a été créé dans ce compte pour l'heure."

    text += "\n"
    if len(characters) < 5:
        text += "\n  |yC|n pour créer un nouveau personnage."

    if len(characters) > 0:
        text += "\n  |yS|n pour supprimer un de vos personnages actuels."

    return text

def _options_choose_characters(account):
    """Return the options for choosing a character.

    The first options must be the characters name (5 are allowed
    by account).  The other nodes must be reached through letters:
    C to create, D to delete.

    """
    options = list()
    characters = account.db._playable_characters
    if len(characters) < 5:
        options.append(        {
                "key": "c",
                "desc": "Créer un nouveau personnage.",
                "goto": "create_character",
        })

    if len(characters) > 0:
        options.append(        {
                "key": "s",
                "desc": "Supprime un de vos personnages.",
                "goto": "delete_character",
        })

    options.append(        {
            "key": "_default",
            "desc": "Jouer avec un de vos personnages.",
            "goto": "choose_characters",
    })
    return tuple(options)

def _login(session, account, menu=True):
    """Log the account into the session.

    Args:
        session: the session to log to
        account: the playter to be looged to.

    In addition, this function creates the login screen for that
    account.

    """
    session.sessionhandler.login(session, account)

    # Keep track of the session, as it might become necessary
    account.db._session = session

    if not menu:
        return

    # Create the EvMenu
    if account.db._playable_characters:
        startnode = "display_characters"
    else:
        startnode = "create_character"

    menu = CharacterMenu(account, startnode=startnode)


class CharacterMenu(evmenu.EvMenu):

    """Menu for login into an account or creating an account."""

    def __init__(self, caller, startnode="start"):
        super(CharacterMenu, self).__init__(caller, "menu.character", startnode=startnode, auto_quit=False,
                cmd_on_exit=None)

    def node_formatter(self, nodetext, optionstext):
        """
        Formats the entirety of the node.

        Args:
            nodetext (str): The node text as returned by `self.nodetext_formatter`.
            optionstext (str): The options display as returned by `self.options_formatter`.
            caller (Object, Account or None, optional): The caller of the node.

        Returns:
            node (str): The formatted node to display.

        """
        return nodetext
