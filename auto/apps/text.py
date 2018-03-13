# -*- coding: utf-8 -*-

"""
Text application.

This app allows to send text, and see what texts have been received.
Texts are grouped by threads.  A thread is a list of messages sharing
the same users participating in the conversation.  For instance, if
A sends a message to B, and B a message to A, both messages will belong
to the same thread.

When a user enters into the text appl, she will see the list of threads
(of conversations that she participated to).  She can open one of these
threads by entering a number.  This will display the most recent messages
in the thread (both that she sent and received).  It will also allow
her to directly respond to the thread (all other users in the conversation
will see this new message).

Screens in this app:
    MainScreen: the main screen, displaying the list of threads as
            numbers.  The user can enter a number to open this thread
            and reply to it.
    ThreadScreen: the screen allowing to visualize a thread with its most
            recent messages, and to reply to it.
    NewTextScreen: the screen allowing to send a new text independent of any thread.
    SettingsScreen: the screen to change the settings of the text app for this device.

Commands in this app:
    MainScreen:
        new: create a new message outside of a thread (CmdNew).
    ThreadScreen:
        send: send the content of the reply to the thread (CmdSend).
    NewTextScreen:
        to: add or remove a contact or phone number as recipient (CmdTo).
        send: send the message (CmdSend).
        cancel: cancel (CmdCancel).

Note:
    Texts aren't stored in the application itself.  To allow greater
    speed in retrieving (and more advanced searching), texts are
    saved in a specific model, along with threads.  To see the mechanism,
    visit `web.text`.

"""

from textwrap import dedent, wrap

from evennia import search_tag
from evennia.utils.evtable import EvTable
from evennia.utils.utils import crop, lazy_property

from auto.apps.base import BaseApp, BaseScreen, AppCommand
from web.text.models import Text, Thread

## App class

class TextApp(BaseApp):

    """Text applicaiton.

    This class defines the application for texting.  It doesn't contain
    many things, as most features are defined in the screen themselves.

    """

    app_name = "text"
    display_name = "Texte"
    start_screen = "MainScreen"

    @lazy_property
    def contact(self):
        """Return the contact app, if available."""
        return self.type.apps.get("contact")

    def get_display_name(self):
        """Return the display name for this app."""
        number = self.get_phone_number(self.obj)
        unread = Text.objects.get_nb_unread(number)
        if unread:
            return "Texte({})".format(unread)

        return "Texte"

    @classmethod
    def get_phone_number(cls, obj, pretty=False):
        """Return the phone number of this object, if found.

        Args:
            obj (Object): the object (phone) to query.
            pretty (bool, optional): add a dash after the third number.

        Returns:
            number (str): the phone number.

        Raises:
            ValueError: the specified object has no phone number.

        """
        number = obj.tags.get(category="phone number")
        if not number or not isinstance(number, basestring):
            raise ValueError("unknown or invalid phone number")

        if pretty:
            number = number[:3] + "-" + number[3:]

        return number

    @classmethod
    def format(cls, obj, number):
        """Return the formatted contact or phone number for obj.

        Args:
            obj (Object): the object for whom to display the phone number or contact.
            number (str): the number in question.

        """
        number = number.replace("-", "")
        storage = obj.attributes.get("_type_storage", {})
        type = storage.get("computer", {})
        app_storage = type.get("app_storage", {})
        contact = app_storage.get("app", {})
        contact = contact.get("contact", {})
        contacts = contact.get("contacts", [])
        for contact in contacts:
            if contact.get("phone_number") == number:
                first = contact.get("first_name", "")
                last = contact.get("last_name", "")
                full = first
                if first and last:
                    full += " "
                full += last
                return full

        # The contact couldn't be found, return the formatted number
        return number[:3] + "-" + number[3:]


## Main screen and commands

class MainScreen(BaseScreen):

    """Main screen of the text app.

    This screen displays the text messages, both sent and received
    by this phone, as a list of conversations (or threads).  It provides
    commands to create new messages, and open them in a separate screen.

    Data attributes you can use (in screen.db):
        None

    """

    commands = ["CmdNew", "CmdSettings"]
    back_screen = "auto.apps.base.MainScreen"
    short_help = "Écran d'accueil pour afficher vos messages."
    long_help = """
        D'ici, vous pouvez utiliser la commande |ynew|n pour créer un nouveau
        message. Vous devriez également voir la liste des messages que vous avez reçus
        ou envoyés, si vous en avez reçu ou envoyé au moins un. Devant chaque message
        se trouve un numéro. Entrez ce numéro pour ouvrir la conversation, afin de
        la lire ou y répondre. Vous pouvez également utiliser la commande |ysettings|n
        pour ouvrir et modifier les options de l'app.
        Comme dans la plupart des écrans, vous pouvez utiliser la commande |yback|n
        pour revenir à l'écran précédent, ou la commande |yexit|n pour quitter l'interface
        et revenir au jeu. Vous pouvez également accéder à l'aide de l'écran en entrant
        la commande |yhelp|n.
    """

    def get_text(self):
        """Display the app."""
        try:
            number = self.app.get_phone_number(self.obj)
            pretty_number = self.app.get_phone_number(self.obj, pretty=True)
        except ValueError:
            self.msg("|gImpossible de trouver votre numéro de téléphone.|n")
            self.back()
            return

        # Load the threads (conversations) to which "number" participated
        threads = Text.objects.get_threads_for(number)
        string = "Textes pour {}".format(pretty_number)
        string += "\n"
        self.db["threads"] = {}
        stored_threads = self.db["threads"]
        if threads:
            len_i = 3 if len(threads) < 100 else 4
            string += "  ( Entrez {new} pour créer un nouveau message. )\n".format(new=self.format_cmd("new"))
            i = 1
            table = EvTable(pad_left=0, border="none")
            table.add_column("S", width=2)
            table.add_column("I", width=len_i, align="r", valign="t")
            table.add_column("Sender", width=21)
            table.add_column("Content", width=36)
            table.add_column("Ago", width=15)
            for thread_id, text in threads.items():
                thread = text.thread
                stored_threads[i] = thread
                senders = text.exclude(number)
                if self.app.contact:
                    senders = [self.app.contact.format(sender) for sender in senders]

                sender = ", ".join(senders)
                if thread.name:
                    sender = thread.name
                senders = crop(senders, 20, "")

                content = text.content.replace("\n", "  ")
                if text.sender == number:
                    content = "[Moi] " + content
                content = crop(content, 35)
                status = " " if thread.has_read(number) else "|rN|n"
                table.add_row(status, self.format_cmd(str(i)), sender, content, text.sent_ago.capitalize())
                i += 1
            lines = unicode(table).splitlines()
            del lines[0]
            lines = [line.rstrip() for line in lines]
            string += "\n" + "\n".join(lines)
            string += "\n\n( Entrez un numéro pour lire cette conversation. )"
        else:
            string += "\n  Vous n'avez aucun message pour l'heure. Entrez {new} pour en créer un.".format(new=self.format_cmd("new"))

        string += "\n\n( Entrez {settings} pour accéder aux options de l'app ).".format(settings=self.format_cmd("settings"))
        count = Text.objects.get_texts_for(number).count()
        s = "" if count == 1 else "s"
        string += "\n\nApp texte: {} message{s} enregistré{s}.".format(count, s=s)
        return string

    def no_match(self, string):
        """Method called when no command matches the user input.

        This allows us to redirect to the ThreadScreen if a number
        has been entered.

        """
        number = self.app.get_phone_number(self.obj)
        if string.isdigit():
            thread = int(string)
            if thread not in self.db["threads"]:
                self.user.msg("|yCe n'es tpas un nombre dans vos conversations actuelles.|n")
                self.display()
            else:
                thread = self.db["threads"][thread]
                thread.mark_as_read(number)
                NewTextScreen.forget_notification(self.obj, thread)
                self.next("ThreadScreen", db=dict(thread=thread))

            return True

        return False

    def wrong_input(self, string):
        """A wrong input has been entered."""
        self.user.msg("Entrez un nombre pour ouvrir une conversation..")


class NewTextScreen(BaseScreen):

    """This screen appears to write a new message, with possibly some
    fields that are pre-loaded.  This screen will appear to create
    a new message independent of any thread.  Note, however, that if
    the list of recipients matches a previous conversation, the new
    message will simply be appended to this previous thread.

    Data attributes you can use (in screen.db):
        recipients: a list of phone numbers representing the list of recipients.
        content: the new text content as a string.

    """

    commands = ["CmdSend", "CmdCancel", "CmdTo", "CmdClear"]
    back_screen = MainScreen
    short_help = "Écran pour rédiger un message."
    long_help = """
        La première chose à faire est d'ajouter un destinataire si ce n'est pas
        déjà le cas. Pour ce faire, utilisez la commande |yto|n en précisant en
        paramètre le numéro ou le nom du contact à ajouter. Par exemple :
            |yto Annabeth|n ou |yto 555-1234|n
        Vous pouvez ensuite entrer du texte simplement pour l'ajouter à votre message.
        Par exemple :
            |ySalut, comment ça va ?|n
        Si vous voulez supprimer le texte que vous avez entré, vous pouvez utiliser
        la commande |yclear|n. Quand vous voudrez envoyer votre message, utilisez
        simplement la commande |ysend|n. Si vous avez l'option |yautosend|n d'activée,
        le texte que vous entrerez sera automatiquement envoyé quand vous appuyerez sur
        ENTRÉE, et vous n'utiliserez donc pas les commandes |yclear|n et |ysend|n.
        Comme dans la plupart des écrans, vous pouvez utiliser la commande |yback|n
        pour revenir à l'écran précédent, ou la commande |yexit|n pour quitter l'interface
        et revenir au jeu. Vous pouvez également accéder à l'aide de l'écran en entrant
        la commande |yhelp|n.
    """

    def get_text(self):
        """Display the new message screen."""
        number = self.app.get_phone_number(self.obj)
        pretty_number = self.app.get_phone_number(self.obj, pretty=True)
        screen = """
            Nouveau message

            De  : {}
              À : {}

            Texte du message (utilisez {clear} pour effacer le texte actuel) :
                {}

                {send} pour envoyer                            {cancel} pour annuler
        """
        recipients = list(self.db.get("recipients", []))
        for i, recipient in enumerate(recipients):
            if self.app.contact:
                recipients[i] = self.app.contact.format(recipient)

        content = self.db.get("content", "(type your text here)")
        content = "\n    ".join(wrap(content, 75))
        recipients = ", ".join(recipients)
        return screen.format(number, recipients, content, clear=self.format_cmd("clear"), send=self.format_cmd("send"), cancel=self.format_cmd("cancel"))

    def no_match(self, string):
        """Command no match, to write the text content."""
        old_content = self.db.get("content", "")
        if old_content:
            old_content += "\n"
        content = old_content + string
        self.db["content"] = content

        # If autosend, send the text right away
        if self.app.db.get("autosend", False):
            self.user.execute_cmd("send")
        else:
            self.display()

        return True

    @staticmethod
    def notify(obj, text):
        """Notify obj of a new text message.

        This is a shortcut to specifically send a "new message" notification
        to the object.  It uses the app's `notify` which calls the
        notification handler in time, doing just a bit of wrapping.

        Args:
            obj (Object): the object being notified.
            text (Text): the text message.

        """
        # Try to get the sender's phone number
        group = "text.thread.{}".format(text.thread.id)
        sender = TextApp.format(obj, text.sender)
        message = "{obj} émet un beep très court."
        title = "Nouveau message de {}".format(sender)
        content = text.content
        screen = "auto.apps.text.ThreadScreen"
        db = {"thread": text.thread}
        TextApp.notify(obj, title, message, content, screen, db, group)

    @staticmethod
    def forget_notification(obj, thread):
        """Forget the unread notifications for this thread.

        Args:
            obj (Object): the object having been notified.
            thread (Thread): the thread toi mask as read.

        """
        group = "text.thread.{}".format(thread.id)
        TextApp.forget_notification(obj, group)


## Thread screen

class ThreadScreen(BaseScreen):

    """This screen appears to see a specific thread and allow to
    write and reply right away.

    Data attributes you can use (in screen.db):
        thread: the thread object (`web.text.models.Thread`).

    """

    commands = ["CmdSend", "CmdClear", "CmdContact"]
    back_screen = MainScreen
    short_help = "Écran permettant de voir une conversation ainsi que d'y répondre."
    long_help = """
        Cet écran affiche une liste de messages dans la même conversation entre
        plusieurs personnes (probablement vous et quelqu'un d'autre). Vous devriez
        voir la liste des messages les plus récents ici. Vous disposez également d'un
        champ de texte pour rédiger une réponse et l'envoyer tout de suite.
        Entrez du texte pour ajouter du contenu à votre message de réponse. Vous pouvez
        utiliser la commande |yclear|n pour supprimer ce texte. Pour envoyer votre message
        de réponse, entrez simplement la commande |ysend|n. Si vous avez l'option
        |yautosend|n d'activée, votre réponse sera envoyée dès que vous entrez du texte
        et appuyez sur ENTRÉE. Vous n'aurez donc pas besoin des commandes |yclear|n
        et |ysend|n.
        Comme dans la plupart des écrans, vous pouvez utiliser la commande |yback|n
        pour revenir à l'écran précédent, ou la commande |yexit|n pour quitter l'interface
        et revenir au jeu. Vous pouvez également accéder à l'aide de l'écran en entrant
        la commande |yhelp|n.
    """

    def get_text(self):
        """Display the new message screen."""
        self.db["go_back"] = False
        thread = self.db.get("thread")
        if not thread:
            self.user.msg("Impossible d'afficher la conversation, une erreur est survenue.")
            return

        number = self.app.get_phone_number(self.obj)
        screen = dedent("""
            Messages avec {}
            ( Utilisez |lccontact|ltCONTACT|le pour éditer la fiche de contact de cette personne. )

            {}

            Texte du message (utilisez {clear} pour supprimer votre texte actuel) :
                {}

                {send} pour envoyer
        """.strip("\n"))
        texts = list(reversed(thread.text_set.order_by("db_date_sent").reverse()[:10]))
        if texts:
            recipients = texts[0].exclude(number)
            self.db["recipients"] = recipients
            if self.app.contact:
                recipients = [self.app.contact.format(recipient) for recipient in recipients]

        # Browse the list of texts in this thread
        messages = []
        for text in texts:
            sender = text.sender
            if sender == number:
                sender = "Moi"
            elif self.app.contact:
                sender = self.app.contact.format(sender)
            sender = "|c" + sender + "|n"

            content = text.content + " (" + text.sent_ago + ")"
            content = wrap(content, 75 - len(sender) - 3)
            content = ("\n" + (len(sender) + 2) * " ").join(content)
            messages.append(sender + ": " + content)

        content = self.db.get("content", "(type your text here)")
        content = "\n    ".join(wrap(content, 75))
        recipients = ", ".join(recipients)
        messages = "\n".join(messages)
        return screen.format(recipients, messages, content, clear=self.format_cmd("clear"), send=self.format_cmd("send"))

    def no_match(self, string):
        """Command no match, to write the text content."""
        old_content = self.db.get("content", "")
        if old_content:
            old_content += "\n"
        content = old_content + string
        self.db["content"] = content
        if self.app.db.get("autosend", False):
            self.user.execute_cmd("send")
        else:
            self.display()
        return True


class SettingsScreen(BaseScreen):

    """Setting screen, to edit text settings.

    Data attributes you can use (in screen.db):
        None

    """

    commands = []
    back_screen = "auto.apps.text.MainScreen"
    short_help = "Écran des options de l'app texte."
    long_help = """
        Vous pouvez modifier les options de l'app texte ici. Entrez simplement le nom
        de l'option si vous voulez l'activer ou la désactiver. Certaines options
        pourraient nécessiter un paramètre en plus que vous devrez préciser après
        le nom de l'option et un espace, comme |yresultats 20|n
        Options disponibles :
            |yautosend|n   Permet d'envoyer automatiquement un message quand on appuie sur ENTRÉE.
        Comme dans la plupart des écrans, vous pouvez utiliser la commande |yback|n
        pour revenir à l'écran précédent, ou la commande |yexit|n pour quitter l'interface
        et revenir au jeu. Vous pouvez également accéder à l'aide de l'écran en entrant
        la commande |yhelp|n.
    """

    def get_text(self):
        """Display the app."""
        string = """
            Options de l'app texte

            {autosend}          :                                          {autosend_value}
                                  Si cette option est activée, quand vous entrez un
                                  nouveau message et appuyez sur ENTRÉE, le message sera envoyé
                                  automatiquement, au lieu d'avoir à utiliser la commande |ysend|n.

            Vous pouvez changer des options de l'app texte ici. Entrez simplement
            le nom (ou les premières lettres du nom) de l'option à modifier. Parfois, vous
            aurez besoin de préciser une valeur en paramètre pour modifier cette option.
        """.format(
                autosend=self.format_cmd("autosend"),
                autosend_value="oui" if self.app.db.get("autosend", False) else "non",
        )
        return string

    def no_match(self, string):
        """Method called when no command matches the user input."""
        string = string.strip().lower()
        settings = ["autosend"]
        for setting in settings:
            if setting.startswith(string):
                self.app.db[setting] = not self.app.db.get(setting, False)
                self.display()
                return True

        return False

    def wrong_input(self, string):
        """A wrong input has been entered."""
        self.user.msg("Entrez le nom d'une option pour la modifier.")


## Commands

class CmdSettings(AppCommand):

    """
    Ouvre les options de l'app texte.

    Usage :
        settings
    """

    key = "settings"
    aliases = ["set", "setting"]

    def func(self):
        self.screen.next(SettingsScreen)


class CmdNew(AppCommand):

    """
    Compose un nouveau message.

    Usage :
        new
    """

    key = "new"
    aliases = ["nouveau"]

    def func(self):
        self.screen.next(NewTextScreen)


class CmdSend(AppCommand):

    """
    Envoie le message en cours de composition.

    Usage :
        send

    Cette commande enverra le texte affiché à l'écran (le message en cours de
    composition) aux destinataires spécifiés.

    """

    key = "send"
    aliases = ["envoyer"]

    def func(self):
        """Execute the command."""
        screen = self.screen
        sender = screen.app.get_phone_number(screen.obj)
        recipients = list(screen.db.get("recipients", []))
        if not recipients:
            self.msg("Vous devez configurer au moins un destinataire.")
            screen.display()
            return

        content = screen.db.get("content")
        if not content:
            self.msg("Ce message est vide, écrivez quelque chose avant de l'envoyer.")
            screen.display()
            return

        # Send the new text
        text = Text.objects.send(sender, recipients, content)
        thread = text.thread
        thread.read = ""
        thread.mark_as_read(sender)
        self.msg("Merci, votre message a bien été envoyé.")
        if screen.db.get("go_back", True):
            screen.back()
        else:
            del screen.db["content"]

        # Notify the recipients
        for number in text.list_recipients:
            devices = search_tag(number, category="phone number")
            for device in devices:
                NewTextScreen.notify(device, text)


class CmdCancel(AppCommand):

    """
    Annule et revient à la liste des messages.

    Usage :
        cancel
    """

    key = "cancel"
    aliases = ["annuler"]

    def func(self):
        """Execute the command."""
        screen = self.screen
        self.msg("Votre message a été annulé. Retour à l'écran précédent.")
        screen.back()


class CmdTo(AppCommand):

    """
    Ajoute ou retire un destinataire.

    Usage :
        to <numéro de téléphone ou nom de contact>

    Si le numéro de téléphone ou contact précisé est déjà présent, il est
    retiré de la liste des destinataires.

    Par exemple :
        to 555-1234

    Si votre appareil a accès à une app contact, vous pouvez ajouter et
    retirer des contacts en entrant simplement leur nom, ou un fragment de leur nom.
        to Martin

    Vous n'avez pas besoin de préciser le nom complet du contact. Si plus
    d'un contact correspond aux lettres que vous avez entré, la liste des
    possibilités sera affichée et vous devrez entrer davantage de lettres
    pour l'ajouter.
    """

    key = "to"
    aliases = ["a", "à"]

    def func(self):
        """Execute the command."""
        screen = self.screen
        number = self.args.strip()
        if not number:
            self.msg("Précisez un numéro de téléphone ou nom de contact pour l'ajouter ou le supprimer en tant que destinataire.")
            return

        # First of all, maybe it's a contact name
        if screen.app.contact:
            matches = screen.app.contact.search(number)
            if len(matches) == 1:
                number = matches[0].phone_number
            elif len(matches) >= 2:
                self.msg("Ce nom de contact n'est pas assez spécifique. Choix possibles :\n  {}\nEssayez à nouveau.".format("\n  ".join([contact.name for contact in matches])))
                return

        number = number.replace("-", "")
        if not number.isdigit() or len(number) != 7:
            self.msg("Ce n'est pas un nombre valide.")
            return

        # Add or remove
        if "recipients" not in screen.db:
            screen.db["recipients"] = []
        recipients = screen.db["recipients"]
        if number in recipients:
            recipients.remove(number)
            self.msg("Cette personne a été retirée de la liste des destinataires.")
        else:
            recipients.append(number)
            self.msg("Cette personne a été ajoutée à la liste des destinataires.")
        screen.display()


class CmdClear(AppCommand):

    """
    Efface votre message en cours.

    Usage :
        clear

    Utilisez cette commande pour supprimer le texte que vous aviez entré, et
    vous permet de recommencer.
    """

    key = "clear"

    def func(self):
        """Execute the command."""
        screen = self.screen
        if "content" in screen.db:
            del screen.db["content"]

        screen.display()


class CmdContact(AppCommand):

    """
    Ouvre l'applicaiton contact pour un destinataire dans cette conversation.

    Usage :
        contact [numéro]

    Cette commande ouvre la fiche du contact précisé, si votre appareil a une
    application contact installée. Si un seul destinataire est présent, vous n'avez
    pas besoin de préciser de paramètre, entrez |ycontact|n tout simplement.
    Cette commande vous permettra de créer une fiche de contact pour ce destinataire,
    ou bien de la modifier si elle existe déjà. Si plus d'un destinataire est présent
    dans cette conversation, la commande |ycontact|n vous affichera une liste de
    choix avec un numéro devant chacun. Vous devrez choisir le contact que vous souhaitez
    éditer en entran ce numéro, comme |ycontact 2|n.
    """

    key = "contact"

    def func(self):
        """Execute the command."""
        screen = self.screen
        recipients = list(screen.db.get("recipients", []))
        if not recipients:
            self.msg("Il n'y a aucun destinataire configuré dans ce message. Utilisez la commande |yto|n pour ajouter des destinataires.")
            return

        contact_app = screen.app.contact
        if not contact_app:
            self.msg("L'application contact n'est pas accessible depuis cet appareil.")
            return

        if len(recipients) == 1:
            recipient = recipients[0]
            screen, db = contact_app.edit(recipient)
            self.screen.next(screen, contact_app, db=db)
            return

        # Otherwise, choose a contact
        args = self.args.strip()
        if not args:
            string = "Précisez un numéro après |yCONTACT|n :\n"
            for i, recipient in enumerate(recipients):
                string += "\n{:>2}: {}".format(i + 1, contact_app.format(recipient))
            self.msg(string)
            return

        # Try to get the recipient
        try:
            args = int(args)
            assert args > 0
            recipient = recipients[args - 1]
        except (ValueError, AssertionError, IndexError):
            self.msg("Numéro de contact invalide.")
        else:
            screen, db = contact_app.edit(recipient)
            self.screen.next(screen, contact_app, db=db)
