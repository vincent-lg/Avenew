"""Module dcontaining the menu nodes of logged in player.

This menu allows to login to character, create a new one, delete
one and so on.

"""

import re
from textwrap import dedent

from django.conf import settings

from evennia import ObjectDB
from evennia.utils import create
from evennia.utils.evmenu import EvMenu

from menu.generic import _formatter, _input_no_digit
from typeclasses.characters import Character

## Constants
RE_VALID_FIRST_NAME = re.compile(r"^[a-z -]{2,}$", re.I)
RE_VALID_LAST_NAME = re.compile(r"^[a-z -]{2,}$", re.I)

## Menu nodes

def display_characters(player):
    """This node simply displays the character list.

    The input will be redirected to the 'choose_characters' menu
    node.  'display_characters' is useful to maintain a layer
    between a node and the character menu.

    """
    text = _text_choose_characters(player)
    options = _options_choose_characters(player)
    return text, options

def choose_characters(player, command):
    """Log into one of this player's characters."""
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Press RETURN to continue.",
            "goto": "start",
        },
    )

    command = command.strip()

    # Search for a valid character
    session = player.db._session
    for i, character in enumerate(player.db._playable_characters):
        if command == str(i + 1):
            del player.db._session
            player.puppet_object(session, character)
            return "", None

    text = "|rThis character cannot be found.  Try again.|n"
    text += "\n" + _text_choose_characters(player)
    options = _options_choose_characters(player)

    return text, options

def create_character(player):
    """Display the introduction to the character creation."""
    text = dedent("""
        You find yourself driving at high speed on a highway.  Said high
        speed slowly begins to diminish, as traffic becomes heavier.  You
        finally navigate through a wide exit ramp, to be finally stopped by
        a checkpoint before entering into the city.
        A police officer walks toward your door and motions you to slide
        down the car window:
            'Sorry, just a few questions, it won't take more than a minute
            or so.  We need to keep track of visitors, we've had some trouble
            before.  Could you tell me your first name?'
        Enter your character's first name.
    """.strip("\n"))
    options = (
        {
            "key": "_default",
            "desc": "Enter your character's first name.",
            "goto": "create_first_name",
        },
    )

    return text, options

def pause_first_name(player):
    """A menu node to pause before the choice of the first name."""
    text = dedent("""
        A police officer crosses out something on his pad.
            'Okay, let's start over then.  Could you give me your first
            name, please?'
        Enter your character's first name.
    """.strip("\n"))
    options = (
        {
            "key": "_default",
            "desc": "Enter your character's first name.",
            "goto": "create_first_name",
        },
    )

    return text, options

def create_first_name(player, command):
    """Prompt the new character for his/her first name."""
    command = command.strip()
    if not RE_VALID_FIRST_NAME.search(command):
        text = dedent("""
            |rSorry, this first name is not valid.|n
            A correct first name may contain letters (and possibly
            spaces), without special characters.  You can:
                Type |yb|n to go back to the character selection.
                Or enter this character's first name again.
        """.strip("\n"))
        options = (
            {
                "key": "b",
                "desc": "Go back to the character selection.",
                "goto": "display_characters",
            },
            {
                "key": "_default",
                "desc": "Enter another first name.",
                "goto": "create_first_name",
            },
        )
    else:
        first_name = " ".join(word.capitalize() for word in command.split(" "))
        player.db._first_name = first_name

        # Redirects to the creation of the last name
        text = dedent("""
            The police officer startes at you with some wariness:
                'All right, we're getting somewhere.  Would you mind
                giving me a last name now?'
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Enter this character's last name.",
                "goto": "create_last_name",
            },
        )

    return text, options

def create_last_name(player, command):
    """Prompt the new character for his/her last name."""
    command = command.strip()

    last_name = " ".join(word.capitalize() for word in command.split(" "))
    first_name = player.db._first_name
    full_name = first_name + " " + last_name

    # Gets the characters with the same name
    characters = Character.objects.filter(db_key=full_name)
    if not RE_VALID_LAST_NAME.search(command):
        text = dedent("""
            |rSorry, this last name is not valid.|n
            A correct last name may contain letters (and possibly
            spaces), without special characters.  You can:
                Type |yb|n to go back to the first name selection.
                Or enter this character's last name again.
        """.strip("\n"))
        options = (
            {
                "key": "b",
                "desc": "Go back to the first name selection.",
                "goto": "pause_first_name",
            },
            {
                "key": "_default",
                "desc": "Enter another last name.",
                "goto": "create_last_name",
            },
        )
    elif len(characters) > 0:
        text = dedent("""
            |rA character named {} already exists.  You can:
                Type |yb|n to go back to the first name selection.
                Or enter this character's last name again.
        """.strip("\n"))
        options = (
            {
                "key": "b",
                "desc": "Go back to the first name selection.",
                "goto": "pause_first_name",
            },
            {
                "key": "_default",
                "desc": "Enter another last name.",
                "goto": "create_last_name",
            },
        )
    else:
        player.db._full_name = full_name
        del player.db._first_name

        # Redirects to the gender selection.
        text = dedent("""
            The police officer nods and scribbles on his pad.
                'Nice name, I s'pose.  What gender should I indicate here?'
                Select your gender (|yF|n/|yM|n).
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Enter your gender (F or M).",
                "goto": "select_gender",
            },
        )

    return text, options

def select_gender(player, command):
    """Prompt the new character for his/her gender."""
    gender = command.strip().lower()
    if gender not in "mf":
        text = dedent("""
            The police officer scratches his head thoughtfully.
                'Sorry, I didn't catch that.'
                Enter |yF|n for female or |yM|n for male.
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Select this character's gender.",
                "goto": "select_gender",
            },
        )
    else:
        female = True if gender == "f" else False
        title = "ma'am" if female else "sir"
        player.db._female = female

        text = dedent("""
            The police officer nods and scribbles on his pad.
                'Thank you {title}.  We're almost done.  I just need to know
                your age.'
                Enter your character's age.
        """.strip("\n")).format(title=title)
        options = (
            {
                "key": "_default",
                "desc": "Enter your character's age.",
                "goto": "select_age",
            },
        )

    return text, options

def select_age(player, command):
    """Prompt the new character for his/her age."""
    age = command.strip()

    try:
        age = int(age)
    except ValueError:
        age = None

    if age is None:
        text = dedent("""
            The police officer scratches his head thoughtfully.
                'Sorry, I didn't quite catch that.'
                Please enter your character's age again.
        """.strip("\n"))
        options = (
            {
                "key": "_default",
                "desc": "Select this character's age.",
                "goto": "select_age",
            },
        )
    else:
        full_name = player.db._full_name
        female = player.db._female
        title = "ma'am" if female else "sir"
        options = (
            {
                "key": "_default",
                "desc": "Enter your character's age.",
                "goto": "select_age",
            },
        )

        # There are invalid choices
        if age < 0:
            text = dedent("""
                The police officer steps back in surprise.
                    'Now, how's that possible?  Probably a mistake he?'
                    Please enter your character's age again.
            """.strip("\n"))
        elif age < 10:
            text = dedent("""
                The police officer gazes at you in surprise.
                    'Shouldn't you be in the backseat?  Okay, I'm sorry,
                    but it's a bit too young to drive, don't you think?'
                    Please enter your character's age again.
            """.strip("\n"))
        elif age < 18:
            text = dedent("""
                The police officer looks you up and down.
                    'Well kid, I don't mean to sound offensive or anything,
                    but you can't drive a car at that age.  As far as I'm
                    concerned, you can lie, but be convincing.'
                    Please enter your character's age again.
            """.strip("\n"))
        else:
            text = dedent("""
                The police officer takes a final note on his pad.
                    'That will do!  Have a good stay with us, {title}.
                The police officer steps back and waves your car through the
                checkpoint.  After a few minute drive, you park in front of
                a large building.  You get off your car, lock the door
                behind you, and walk toward the building, stopping a few feet
                away from the main entrance inside.
            """.strip("\n")).format(title=title)

            # Create the character
            character = _create_character(full_name, player)
            character.db.female = female
            character.db.age = age
            del player.db._full_name
            del player.db._female

            # Connects on this character
            player.msg(text)
            session = player.db._session
            del player.db._session
            player.puppet_object(session, character)
            return "", None

    return text, options

## Generic functions

def _create_character(name, player):
    """Create a new character.

    Args:
        name: the name of the character to be created
        player: the player owning the character.

    Return:
        The newly-created character.

    """
    # Look for default values
    permissions = settings.PERMISSION_PLAYER_DEFAULT
    typeclass = settings.BASE_CHARACTER_TYPECLASS
    home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)

    # Create the character
    character = create.create_object(typeclass, key=name, home=home,
            permissions=permissions)

    # Set playable character list
    player.db._playable_characters.append(character)

    # Allow only the character itself and the player to puppet it.
    character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) " \
            "or pperm(Immortals)" % (character.id, player.id))

    # If no description is set, set a default description
    if not character.db.desc:
        character.db.desc = ""

    # We need to set this to have @ic auto-connect to this character.
    player.db._last_puppet = character

    return character

def _text_choose_characters(player):
    """Display the menu to choose a character."""
    text = "Enter a valid number to log into that character.\n"
    characters = player.db._playable_characters
    if len(characters):
        for i, character in enumerate(characters):
            text += "\n  |y{}|n - Log into {}.".format(str(i + 1),
                    character.name)
    else:
        text += "\n  No character has been created in this account yet."

    text += "\n"
    if len(characters) < 5:
        text += "\n  |yC|n to create a new character."

    if len(characters) > 0:
        text += "\n  |yD|n to delete one of your characters."

    return text

def _options_choose_characters(player):
    """Return the options for choosing a character.

    The first options must be the characters name (5 are allowed
    by player).  The other nodes must be reached through letters:
    C to create, D to delete.

    """
    options = list()
    characters = player.db._playable_characters
    if len(characters) < 5:
        options.append(        {
                "key": "c",
                "desc": "Create a new character.",
                "goto": "create_character",
        })

    if len(characters) > 0:
        options.append(        {
                "key": "d",
                "desc": "Delete an existing character.",
                "goto": "delete_character",
        })

    options.append(        {
            "key": "_default",
            "desc": "Login to an existing character.",
            "goto": "choose_characters",
    })
    return tuple(options)

def _login(session, player):
    """Log the player into the session.

    Args:
        session: the session to log to
        player: the playter to be looged to.

    In addition, this function creates the login screen for that
    player.

    """
    session.sessionhandler.login(session, player)

    # Keep track of the session, as it might become necessary
    player.db._session = session

    # Create the EvMenu
    menu = EvMenu(player, "menu.character", startnode="display_characters",
            auto_quit=False, cmd_on_exit=None, node_formatter=_formatter,
            input_parser=_input_no_digit, persistent=True)
