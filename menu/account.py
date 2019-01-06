# -*- coding: utf-8 -*-

"""This module contains the account connexion/creation menu nodes.

start: First login, prompted for username
    'new': create_account
    (any): username
username: check that the username exists
    'b': pre_start
    (any): password (if exists) or username (if not)

"""

from hashlib import sha256
from random import choice
import re
from smtplib import SMTPException
import socket
from textwrap import dedent

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from evennia import logger
from evennia.server.models import ServerConfig
from evennia.utils import create, evmenu
from evennia.utils.utils import delay, random_string_from_module

from menu.character import _login, _options_choose_characters, _text_choose_characters
from typeclasses.accounts import Account
from web.mailgun.utils import send_email

## Constants
CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE
LEN_PASSWD = 6
RE_VALID_USERNAME = re.compile(r"^[a-z0-9_.]{3,}$", re.I)

## Connection nodes
def start(caller):
    """The user should enter his/her username or NEW to create one.

    This node is called at the very beginning of the menu, when
    a session has been created OR if an error occurs further
    down the menu tree.  From there, users can either enter a
    username (if this username exists) or type NEW (capitalized
    or not) to create a new account.

    """
    text = random_string_from_module(CONNECTION_SCREEN_MODULE)
    text += "\n\nEntrez votre nom d'utilisateur ou |yNOUVEAU|n pour créer un nouveau compte."
    options = (
        {
            "key": "nouveau",
            "desc": "Créer un nouveau compte.",
            "goto": "create_account",
        },
        {
            "key": "_default",
            "desc": "Se connecter à un compte existant.",
            "goto": "username",
        },
    )
    return text, options

def username(caller, input):
    """Check that the username is an existing account.

    Check that the specified username exists.  If the username doesn't
    exist, display an error message and ask the user to either
    enter 'b' to go back, or to try again.
    If it does exist, move to the next node (enter password).

    """
    input = input.strip()
    accounts = Account.objects.filter(username__iexact=input)
    account = accounts[0] if accounts else None
    if account is None:
        text = dedent("""
            |rLe nom d'utilisateur {} n'existe pas encore. L'avez-vous déjà créé ?|n
                Entrez |yp|n pour revenir au menu de connexion.
                Ou essayez d'entrer un nom d'utilisateur pour s'y connecter.
        """.strip("\n")).format(input)
        options = (
            {
                "key": "p",
                "desc": "Revenir à l'écran de connexion.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Essayez à nouveau.",
                "goto": "username",
            },
        )
    else:
        caller.db._account = account
        locked = account.db._locked

        # The account is temporarily locked when a wrong password
        # has been supplied.  This lock shouldn't last more than
        # 3 seconds.
        if locked:
            text = "Veuillez patienter..."
        else:
            text = "Entrez le mot de passe pour accéder au compte {}.".format(
                    account.name)

        # Disables echo for the password
        caller.msg(echo=False)
        options = (
            {
                "key": "_default",
                "desc": "Entrez le mot de passe du compte.",
                "goto": "password",
            },
        )

    return text, options

def password(caller, input):
    """Ask the user to enter the password to this account.

    This is assuming the user exists (see 'create_username' and
    'create_password').  This node "loops" if needed:  if the
    user specifies a wrong password, offers the user to try
    again or to go back by entering 'b'.
    If the password is correct, then login.

    """
    input = input.strip()
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Entrez votre mot de passe.",
            "goto": "password",
        },
    )

    # Check the password
    account = caller.db._account

    # If the account is locked, the user has to wait (maximum
    # 3 seconds) before retrying
    if account.db._locked:
        text = "|gVeuillez patienter, vous ne pouvez pas encore entrer votre mot de passe.|n"
        return text, options

    bans = ServerConfig.objects.conf("server_bans")
    banned = bans and (any(tup[0] == account.name.lower() for tup in bans) \
            or any(tup[2].match(caller.address) for tup in bans if tup[2]))

    if not account.check_password(input):
        text = dedent("""
            |rMot de passe incorrect.|n
                Entrez |yp|n pour revenir à l'écran de connexion.
                Ou attendez 3 secondes avant d'essayer d'entrer le mot de passe de ce compte.
        """.strip("\n"))

        # Loops on the same node, lock for 3 seconds
        account.db._locked = True
        delay(3, _wrong_password, account)
        options = (
            {
                "key": "p",
                "desc": "Revenir à l'écran de connexion.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Entrez votre mot de passe de nouveau.",
                "goto": "password",
            },
        )
    elif banned:
        # This is a banned IP or name
        string = dedent("""
            |rVous avez été banni du jeu et ne pouvez vous connecter|n
            Si vous estimez que ce bannissesement est une erreur, contactez les administrateurs du jeu.
        """.strip("\n"))
        caller.msg(string)
        caller.sessionhandler.disconnect(
                caller, "Au revoir. Déconnexion...")
    else:
        # The password is correct, we can log into the account.
        caller.msg(echo=True)
        if not account.email:
            # Redirects to the node to set an email address
            text = _text_email_address(account)
            options = (
                {
                    "key": "_default",
                    "desc": "Entrez votre adresse e-mail.",
                    "goto": "email_address",
                },
            )
        elif not account.db.valid:
            # Redirects to the node for the validation code
            text = "Entrez votre code de validation à 4 chiffres."
            options = (
                {
                    "key": "_default",
                    "desc": "Entrez votre code de validation.",
                    "goto": "validate_account",
                },
            )
        else:
            _login(caller, account)
            text = ""
            options = _options_choose_characters(account)
            if not account.db._playable_characters:
                options = (
                    {
                        "key": "_default",
                        "desc": "Enter le prénom de votre personnage à créer.",
                        "goto": "create_first_name",
                    },
                )

    return text, options

# New account/account nodes
def create_account(caller):
    """Create a new account.

    This node simply prompts the user to enter a username.
    The input is redirected to 'create_username'.

    """
    text = dedent("""
        Bienvenue sur Avenew One ! Merci de vouloir créer un compte sur notre jeu!
        La première étape est de nous donner un nom d'utilisateur pour ce
        compte. Vous devrez l'entrer à chaque fois que vous souhaiterez vous
        connecter sur le jeu. Les noms d'utilisateurs n'ont pas à être identiques
        au nom de votre futur personnage sur le jeu. Il est conseillé de
        garder le nom d'utilisateur distinct de vos noms de personnage pour
        des raisons de sécurité. Une fois que votre compte sera créé, vous
        pourrez créer un personnage dans ce compte. Votre compte peut
        contenir jusqu'à 5 personnages.

        Entrez votre nom d'utilisateur à créer :
    """.strip("\n"))
    options = (
        {
            "key": "_default",
            "desc": "Entrez votre nom d'utilisateur.",
            "goto": "create_username",
        },
    )
    return text, options

def create_username(caller, input):
    """Prompt to enter a valid username (one that doesnt exist).

    'input' contains the new username.  If it exists, prompt
    the username to retry or go back to the login screen.

    """
    input = input.strip()
    accounts = Account.objects.filter(username__iexact=input)
    account = accounts[0] if accounts else None
    options = (
        {
            "key": "_default",
            "desc": "Entrez votre nouveau mot de passe.",
            "goto": "create_password",
        },
    )

    # If an account with that name exists, a new one will not be created
    if account:
        text = dedent("""
            |rLe nom de compte {} existe déjà.|n
                Entrez |yp|n pour revenir à l'écran de connexion.
                Ou entrez un nouveau nom d'utilisateur.
        """.strip("\n")).format(input)

        # Loops on the same node
        options = (
            {
                "key": "p",
                "desc": "Revenir à l'écran de connexion.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Entrez un nouveau nom d'utilisateur.",
                "goto": "create_username",
            },
        )
    elif not RE_VALID_USERNAME.search(input):
        text = dedent("""
            |rCe nom d'utilisateur n'est pas valide.|n
            Le nom d'utilisateur peut contenir des lettres, chiffres, le signe souligné (_)
            et le point (.). Le nom d'utilisateur doit contenir au minimum 3 caractères.
                Entrez |yp|n pour revenir à l'écran de connexion.
                Ou entrez un nouveau nom d'utilisateur.
        """.strip("\n"))
        options = (
            {
                "key": "p",
                "desc": "Revenir à l'écran de connexion.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Entrez un nouveau nom d'utilisateur.",
                "goto": "create_username",
            },
        )
    else:
        # We don't create the account right away, so we store its name
        caller.db._accountname = input

        # Disables echo to enter the password
        caller.msg(echo=False)

        # Redirects to the creation of a password
        text = "Entrez le nouveau mot de passe de ce compte."
        options = (
            {
                "key": "_default",
                "desc": "Entrer le mot de passe du compte.",
                "goto": "create_password",
            },
        )

    return text, options

def create_password(caller, input):
    """Ask the user to create a password.

    This node creates and validates a new password for this
    account.  It then follows up with the confirmation
    (confirm_password).

    """
    text = ""
    options = (
        {
            "key": "p",
            "desc": "Revenir à l'écran de connexion.",
            "goto": "pre_start",
        },
        {
            "key": "_default",
            "desc": "Entrez votre mot de passe.",
            "goto": "create_password",
        },
    )

    password = input.strip()
    accountname = caller.db._accountname
    if len(password) < LEN_PASSWD:
        # The password is too short
        text = dedent("""
            |rVotre mot de passe doit contenir au minimum {} caractères.|n
                Entrez |wp|n pour revenir à l'écran de connexion.
                Ou entrez un nouveau mot de passe.
        """.strip("\n")).format(LEN_PASSWD)
    else:
        # Redirects to the "confirm_passwrod" node
        caller.db._password = sha256(password.encode()).hexdigest()
        text = "Entrez votre mot de passe de nouveau."
        options = (
            {
                "key": "_default",
                "desc": "Entrez le même mot de passe de nouveau.",
                "goto": "confirm_password",
            },
        )

    return text, options

def confirm_password(caller, input):
    """Ask the user to confirm the account's password.

    The account's password has been saved in the session for the
    time being, as a hashed version.  If the hashed version of
    the retyped password matches, then the account is created.
    If not, ask for another password.

    """
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Entrez votre mot de passe.",
            "goto": "create_password",
        },
    )

    password = input.strip()

    accountname = caller.db._accountname
    first_password = caller.db._password
    second_password = sha256(password.encode()).hexdigest()
    if first_password != second_password:
        text = dedent("""
            |rLe mot de passe que vous avez entré ne correspond pas au mot de passe entré
            précédemment.|n

            Entrez un nouveau mot de passe pour ce compte.
        """.strip("\n"))
    else:
        # Creates the new account.
        caller.msg(echo=True)
        try:
            permissions = settings.PERMISSION_ACCOUNT_DEFAULT
            account = _create_account(caller, accountname,
                    password, permissions)
        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't, we
            # won't see any errors at all.
            caller.msg(dedent("""
                |rUne erreur s'est produite|n. Contactez un administrateur si l'erreur persiste.

                Entrez un nouveau mot de passe.
            """.strip("\n")))
            logger.log_trace()
        else:
            caller.db._account = account
            del caller.db._password
            text = "Votre nouveau compte a été créé avec succès !"
            text += "\n\n" + _text_email_address(account)
            options = (
                {
                    "key": "_default",
                    "desc": "Entrez une adresse e-mail valide.",
                    "goto": "email_address",
                },
            )

    return text, options

def email_address(caller, input):
    """Prompt the user to enter a valid email address."""
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Entrez une adresse e-mail valide.",
            "goto": "email_address",
        },
    )

    email_address = input.strip()
    account = caller.db._account

    # Search for accounts with an identical email address
    identical = list(Account.objects.filter(email__iexact=email_address))

    if account in identical:
        identical.remove(account)

    # Try to validate the email address
    try:
        validate_email(email_address)
    except ValidationError:
        valid = False
    else:
        valid = True

    if not valid:
        # The email address doesn't seem to be valid
        text = dedent("""
            |rDésolé, l'adresse e-mail spécifiée {} ne peut être acceptée comme valide.|n

            Entrez une nouvelle adresse e-mail.
        """.strip("\n")).format(email_address)
    elif identical:
        # The email address is already used
        text = dedent("""
            |rL'adresse e-mail spéicifée est déjà utilisée par un autre compte.|n

            Entrez une nouvelle adresse e-mail.
        """.strip("\n"))
    else:
        account.email = email_address
        account.save()

        # Generates the 4-digit validation code
        numbers = "012345678"
        code = ""
        for i in range(4):
            code += choice(numbers)

        # Sends an email with the code
        subject = "[Avenew] Validation de compte"
        body = dedent("""
            Le compte {} a bien été créé sur Avenew One.

            Afin de le valider et commencer à jouer, vous devrez entrer le code de validation
            à 4 chiffres suivant dans votre client MUD. Si vous avez été déconnecté du serveur,
            connectez-vous de nouveau, précisant votre nom d'utilisateur et mot de passe : le code
            de validation vous sera à nouveau demandé.

            Code de validation : {}
        """.strip("\n")).format(account.name, code)
        recipient = email_address
        account.db.valid = False
        account.db.validation_code = code
        try:
            assert not settings.TEST_SESSION
            send_email("NOREPLY", recipient, subject, body, store=False)
        except AssertionError:
            account.db.valid = True
            account.attributes.remove("validation_code")
            caller.msg(dedent("""
                Avenew est en mode de session de test, votre compte a été validé automatiquement.
            """.strip("\n")).format(email_address))
            caller.msg("----- Vous créez maintenant le premier personnage dans votre compte. -----")
            _login(caller, account)
            text = ""
            options = (
                {
                    "key": "_default",
                    "desc": "Entrez le prénom de votre personnage.",
                    "goto": "create_first_name",
                },
            )
        except (SMTPException, socket.error):
            # The email could not be sent
            account.db.valid = True
            account.attributes.remove("validation_code")
            caller.msg(dedent("""
                Avenew n'a pas pu envoyer l'e-mail de validation à {}.
                Ce problème est probablement dû au fait qu'Avenew n'arrive pas à se connecter
                au serveur SMTP. Votre compte a été validé automatiquement.
            """.strip("\n")).format(email_address))
            caller.msg("----- Vous créez maintenant le premier personnage dans votre compte. -----")
            _login(caller, account)
            text = ""
            options = (
                {
                    "key": "_default",
                    "desc": "Entrez le prénom de votre nouveau personnage.",
                    "goto": "create_first_name",
                },
            )
        else:
            text = dedent("""
                Un e-mail a été envoyé à l'adresse {}. Il contient le code de validation dont
                vous aurez besoin pour commencer à jouer. Si vous n'avez pas reçu l'e-mail de validation
                après quelques minutes, vérifiez votre dossier de messages indésirables. Si le message
                ne s'y trouve toujours pas, vous pourriez vouloir essayer une autre adresse e-mail
                ou contacter un administrateur du jeu.

                Vous pouvez :
                    Entrez |yp|n pour choisir une nouvelle adresse e-mail.
                    Entrer votre code de validation à 4 chiffres.
                """.strip("\n")).format(email_address)
            options = (
                {
                    "key": "p",
                    "desc": "Revenir au choix de l'adresse e-mail.",
                    "goto": "pre_email_address",
                },
                {
                    "key": "_default",
                    "desc": "Entrer votre code de validation.",
                    "goto": "validate_account",
                },
            )

    return text, options

def validate_account(caller, input):
    """Prompt the user to enter the received validation code."""
    text = ""
    options = (
        {
            "key": "p",
            "desc": "Revenir au choix de l'adresse e-mail.",
            "goto": "pre_email_address",
        },
        {
            "key": "_default",
            "desc": "Entrer le code de validation.",
            "goto": "validate_account",
        },
    )

    account = caller.db._account
    if account.db.validation_code != input.strip():
        text = dedent("""
            |rDésolé, le code de validation spécifié {} ne correspond pas à celui enregistré.|n
            S'agit-il bien du code qui vous a été envoyé par e-mail ? Vous pouvez essayer de
            l'entrer à nouveau ou entrer |yp|n pour choisir une adresse e-mail différente.
        """.strip("\n")).format(input.strip())
    else:
        account.db.valid = True
        account.attributes.remove("validation_code")
        account.record_email_address()
        caller.msg("----- Vous créez maintenant le premier personnage dans votre compte. -----")
        _login(caller, account)
        text = ""
        options = (
            {
                "key": "_default",
                "desc": "Entrez le prénom de votre premier personnage.",
                "goto": "create_first_name",
            },
        )

    return text, options

## Transition nodes
def pre_start(self):
    """Node to redirect to 'start'."""
    text = "Entrez votre nom d'utilisateur ou |yNOUVEAU|n pour créer un compte."
    options = (
        {
            "key": "nouveau",
            "desc": "Créer un nouveau compte.",
            "goto": "create_account",
        },
        {
            "key": "_default",
            "desc": "Se connecter à un compte existant.",
            "goto": "username",
        },
    )
    return text, options

def pre_email_address(self):
    """Node to redirect to 'email_address'."""
    text = "Entrez une autre adresse e-mail valide."
    options = (
        {
            "key": "_default",
            "desc": "Entrez une adresse e-mail valide.",
            "goto": "email_address",
        },
    )
    return text, options

## Private functions
def _create_account(session, accountname, password, permissions, typeclass=None, email=None):
    """
    Helper function, creates an account of the specified typeclass.


    Contrary to the default `evennia.commands.default.unlogged._create_account`,
    the account isn't connected to the public chaannel.

    """
    try:
        new_account = create.create_account(accountname, email, password, permissions=permissions, typeclass=typeclass)

    except Exception as e:
        session.msg("Une erreur s'est produite lors de la création du compte:\n%s\nSi l'erreur persiste, contacter un administrateur." % e)
        logger.log_trace()
        return False

    # This needs to be set so the engine knows this account is
    # logging in for the first time. (so it knows to call the right
    # hooks during login later)
    new_account.db.FIRST_LOGIN = True
    return new_account

def _text_email_address(account):
    """Return the text for the email address menu node."""
    text = dedent("""
        Entrez une adresse e-mail valide pour le compte {}.

        Un e-mail de confirmation sera envoyé à cette adresse, contenant un code de validation à
        4 chiffres dont vous aurez besoin pour valider ce compte. Cette adresse e-mail ne sera
        utilisée que par les administrateurs du jeu, en cas de besoin. Vous pourrez changer
        cette adresse e-mail par la suite.

        Entrez votre adresse e-mail.
    """.strip("\n")).format(account.name)

    return text

def _wrong_password(account):
    """Function called after the 3 seconds are up, when a wrong password has been supplied."""
    account.db._locked = False
    account.msg("Entrez votre mot de passe de nouveau.")


class AccountMenu(evmenu.EvMenu):

    """Menu for login into an account or creating an account."""

    def __init__(self, caller):
        super(AccountMenu, self).__init__(caller, "menu.account", startnode="start", auto_quit=False,
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
