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


from auto.apps._mixins import ContactMixin
from auto.apps.base import BaseApp, BaseScreen, AppCommand
from web.text.models import Text, Thread, Number

## App class

class TextApp(BaseApp, ContactMixin):

    """Text applicaiton.

    This class defines the application for texting.  It doesn't contain
    many things, as most features are defined in the screen themselves.

    """

    app_name = "text"
    display_name = "Text"
    start_screen = "MainScreen"

    @lazy_property
    def contact(self):
        """Return the contact app, if available."""
        return self.type.apps.get("contact")

    def get_display_name(self):
        """Return the display name for this app."""
        try:
            number = self.phone_number
        except ValueError:
            return "Text"

        unread = Text.objects.get_num_unread(number)
        if unread:
            return "Text({})".format(unread)

        return "Text"


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
    short_help = "Screen to display your text messages."
    long_help = """
        From here, you can use the |ynew|n command to create a new text message.
        You should also see the list of texts you already have, assuming you
        have any.  In front of every text message, you should see a number.
        Enter this number to open this text, to read or reply to it.
        You can also use the |ysettings|n command to open the settings screen,
        to change configuration for your text app.
        As in any screen, use the |yback|n command to go back to the previous
        screen, or the |yexit|n command to exit the interface.  You can obtain
        additional help with the |yhelp|n command.
    """

    def get_text(self):
        """Display the app."""
        try:
            number = self.app.phone_number
            pretty_number = self.app.pretty_phone_number
        except ValueError:
            self.msg("Your phone number couldn't be found.")
            self.back()
            return

        # Load the threads (conversations) to which "number" participated
        threads = Text.objects.get_threads_for(number)
        string = "Texts for {}".format(pretty_number)
        string += "\n"
        self.db["threads"] = {}
        stored_threads = self.db["threads"]
        if threads:
            len_i = 3 if len(threads) < 100 else 4
            string += "  Create a {new} message.\n".format(new=self.format_cmd("new"))
            i = 1
            table = EvTable(pad_left=0, border="none")
            table.add_column("S", width=2)
            table.add_column("I", width=len_i, align="r", valign="t")
            table.add_column("Sender", width=21)
            table.add_column("Content", width=36)
            table.add_column("Ago", width=15)
            for thread_id, text in threads.items():
                thread = text.db_thread
                stored_threads[i] = thread
                sender = text.recipients
                sender = [self.app.format(num) for num in sender]
                sender = ", ".join(sender)
                if thread.name:
                    sender = thread.name
                sender = crop(sender, 20, "")

                content = text.content.replace("\n", "  ")
                if text.sender.db_phone_number == number:
                    content = "[You] " + content
                content = crop(content, 35)
                status = " " if thread.has_read(number) else "|rU|n"
                table.add_row(status, self.format_cmd(str(i)), sender, content, text.sent_ago.capitalize())
                i += 1
            lines = unicode(table).splitlines()
            del lines[0]
            lines = [line.rstrip() for line in lines]
            string += "\n" + "\n".join(lines)
            string += "\n\n(Type a number to open this text.)"
        else:
            string += "\n  You have no texts yet.  Want to create a {new} one?".format(new=self.format_cmd("new"))

        string += "\n\n(Enter {settings} to edit the app settings).".format(settings=self.format_cmd("settings"))
        count = Text.objects.get_texts_for(number).count()
        s = "" if count == 1 else "s"
        string += "\n\nText app: {} saved message{s}.".format(count, s=s)
        return string

    def no_match(self, string):
        """Method called when no command matches the user input.

        This allows us to redirect to the ThreadScreen if a number
        has been entered.

        """
        number = self.app.phone_number
        if string.isdigit():
            thread = int(string)
            if thread not in self.db["threads"]:
                self.user.msg("This is not a number in your current threads.")
                self.display()
            else:
                thread = self.db["threads"][thread]
                self.next("ThreadScreen", db=dict(thread=thread))

            return True

        return False

    def wrong_input(self, string):
        """A wrong input has been entered."""
        self.user.msg("Enter a thread number to oepn it.")


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
    short_help = "Screen to write a text message."
    long_help = """
        The first thing to do is to set the recipient, if not set already.
        To do so, use the |yto|n command.  You can specify it a phone number,
        like |yto 555-1234|n, or a contact name, like |yto annabeth|n.
        Type text to simply add it to the text content to be sent.  For instance:
            |yhello, how is it going?|n
        If you want to delete the content you have typed, you can use the
        |yclear|n command.  When you want to send your message, simply use the
        |ysend|n command.  Notice that if you have the |yautosend|n setting
        turned on, the text that you type will be automatically sent whenever
        you press RETURN.  Therefore, the |ysend|n and |yclear|n commands are
        not necessary here.
        As in any screen, use the |yback|n command to go back to the previous
        screen, or the |yexit|n command to exit the interface.  You can obtain
        additional help with the |yhelp|n command.
    """

    def get_text(self):
        """Display the new message screen."""
        number = self.app.phone_number
        pretty_number = self.app.pretty_phone_number
        screen = """
            New message

            From: {}
              To: {}

            Text message (use {clear} to clear your current text):
                {}

                {send}                                             {cancel}
        """
        recipients = list(self.db.get("recipients", []))
        for i, recipient in enumerate(recipients):
            recipients[i] = self.app.format(recipient)

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
        sender = TextApp.format_obj(obj, text.sender.db_phone_number)
        message = "{obj} emits a short beep."
        title = "New message from {}".format(sender)
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
    short_help = "Screen to see a thread, and reply to it."
    long_help = """
        This screen displays a thread, a list of messages between several
        recipients (probably you and someone else).  You should see the list
        of more recent messages here.  You can also reply to this thread
        right away and send your reply.
        Type text to simply add it to the text content to be sent.  For instance:
            |yhello, how is it going?|n
        If you want to delete the content you have typed, you can use the
        |yclear|n command.  When you want to send your message, simply use the
        |ysend|n command.  Notice that if you have the |yautosend|n setting
        turned on, the text that you type will be automatically sent whenever
        you press RETURN.  Therefore, the |ysend|n and |yclear|n commands are
        not necessary here.
        As in any screen, use the |yback|n command to go back to the previous
        screen, or the |yexit|n command to exit the interface.  You can obtain
        additional help with the |yhelp|n command.
    """

    def get_text(self):
        """Display the new message screen."""
        self.db["go_back"] = False
        thread = self.db.get("thread")
        if not thread:
            self.user.msg("Can't display the thread, an error occurred.")
            return

        number = self.app.phone_number

        # Mark the thread as read (should be done elsewhere)
        thread.mark_read(number)
        NewTextScreen.forget_notification(self.obj, thread)

        screen = dedent("""
            Messages with {}
            |lccontact|ltCONTACT|le to edit the contact for this conversation.

            {}

            Text message (use {clear} to clear your current text):
                {}

                {send}
        """.strip("\n"))
        texts = list(reversed(thread.text_set.order_by("db_date_sent").reverse()[:10]))

        # Browse the list of texts in this thread
        messages = []
        for text in texts:
            sender = text.sender
            if sender.db_phone_number == number:
                sender = "You"
            else:
                sender = self.app.format(sender.db_phone_number)
            sender = "|c" + sender + "|n"

            content = text.content + " (" + text.sent_ago + ")"
            content = wrap(content, 75 - len(sender) - 3)
            content = ("\n" + (len(sender) + 2) * " ").join(content)
            messages.append(sender + ": " + content)

        content = self.db.get("content", "(type your text here)")
        content = "\n    ".join(wrap(content, 75))
        recipients = [o.db_phone_number for o in thread.db_recipients.exclude(db_phone_number=number)]
        self.db["recipients"] = recipients
        recipients = [self.app.format(number) for number in recipients]
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
    short_help = "Screen to edit settings of the text app."
    long_help = """
        You can set settings of your text app here.  Simply enter the
        setting name if you want to turn it on or off.  Some settings might
        require additional arguments that you have to specify after the
        setting name, like |ylog 3|n.
        Available settings:
            |yautosend|n   Allow to auto-send a message when pressing RETURN.
        As in any screen, use the |yback|n command to go back to the previous
        screen, or the |yexit|n command to exit the interface.  You can obtain
        additional help with the |yhelp|n command.
    """

    def get_text(self):
        """Display the app."""
        string = """
            Text settings

            {autosend}          :                                          {autosend_value}
                                  If turned on, when you type in a new message and press the |wRETURN|n
                                  key, the text will be sent automatically, instead
                                  of you having to type |ySEND|n.

            You can customize some settings of the text app here.  Just enter the name
            (or the beginning of the name) of the setting to toggle it.  Sometimes, you will
            have to specify an argument after a space to change the settings.
        """.format(
                autosend=self.format_cmd("autosend"),
                autosend_value="yes" if self.app.db.get("autosend", False) else "no",
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
        self.user.msg("Enter a setting name to change it.")


## Commands

class CmdSettings(AppCommand):

    """
    Open the text app settings.

    Usage:
        settings
    """

    key = "settings"
    aliases = ["set", "setting"]

    def func(self):
        self.screen.next(SettingsScreen)


class CmdNew(AppCommand):

    """
    Compose a new text message.

    Usage:
        new
    """

    key = "new"

    def func(self):
        self.screen.next(NewTextScreen)


class CmdSend(AppCommand):

    """
    Send the current text message.

    Usage:
        send

    This will send the text message on your screen to the selected
    recipients, who might already be members of the conversation.
    """

    key = "send"

    def func(self):
        """Execute the command."""
        screen = self.screen
        sender = screen.app.phone_number
        recipients = list(screen.db.get("recipients", []))
        if not recipients:
            self.msg("You haven't specified at least one recipient.")
            screen.display()
            return

        content = screen.db.get("content")
        if not content:
            self.msg("This text is empty, write something before sending it.")
            screen.display()
            return

        # Send the new text
        text = Text.objects.send(sender, recipients, content)
        thread = text.thread
        self.msg("Thanks, your message has been sent successfully.")
        if screen.db.get("go_back", True):
            screen.back()
        else:
            del screen.db["content"]

        # Notify the recipients
        for number in text.recipients:
            devices = search_tag(number, category="phone number")
            for device in devices:
                NewTextScreen.notify(device, text)


class CmdCancel(AppCommand):

    """
    Cancel and go back to the list of texts.

    Usage:
        cancel
    """

    key = "cancel"

    def func(self):
        """Execute the command."""
        screen = self.screen
        self.msg("Your text was cancelled.  Going back to the previous screen.")
        screen.back()


class CmdTo(AppCommand):

    """
    Add or remove a recipient.

    Usage:
        to <phone number or contact>

    If the phone number, or contact, is already present, remove it.

    Usage:
        to 555-1234

    If your device has access to a contact app, you can add and remove
    recipients by their names:

    Usage:
        to Martin

    You don't have to specify the full name of the contact.  If more than one
    contact matches the letters you have specified, you will be given the list
    of possibilities and will have to specify more letters next time.
    """

    key = "to"

    def func(self):
        """Execute the command."""
        screen = self.screen
        number = self.args.strip()
        if not number:
            self.msg("Specify a phone number or contact name of a recipient, to add or remove him.")
            return

        # First of all, maybe it's a contact name
        matches = screen.app.search(number)
        if len(matches) == 0:
            self.msg("No match could be found bearing this name.")
            return
        elif len(matches) == 1:
            number = matches[0]
        elif len(matches) >= 2:
            self.msg("This contact name isn't specific enough.  It could be:\n  {}\nPlease specify.".format("\n  ".join([screen.app.format(contact) for contact in matches])))
            return

        number = number.replace("-", "")
        if not number.isdigit() or len(number) != 7:
            self.msg("This is not a valid phone number.")
            return

        # Add or remove
        if "recipients" not in screen.db:
            screen.db["recipients"] = []
        recipients = screen.db["recipients"]
        if number in recipients:
            recipients.remove(number)
            self.msg("This contact was removed from the list of recipients.")
        else:
            recipients.append(number)
            self.msg("This contact was added to the list of recipients.")
        screen.display()


class CmdClear(AppCommand):

    """
    Erases your current text message and start over.

    Usage:
        clear

    Use this command to clear the text you had begun to type, and start over
    again.
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
    Open the contact dialog for a recipient in this conversation.

    Usage:
        contact [number]

    This command will open the contact dialog for the recipient in the current
    conversation.  This will allow to create a new contact if the recipient has
    none yet.  If more than one recipient are present in this conversation, the |hCONTACT|n
    command will show you a list of possible contacts in a numbered list, and ask you to enter
    |hCONTACT|n followed by the number of the contact you want to open.  For instance:

        contact 2
    """

    key = "contact"

    def func(self):
        """Execute the command."""
        screen = self.screen
        recipients = list(screen.db.get("recipients", []))
        if not recipients:
            self.msg("There are no recipient in this conversation yet.  Use the |hTO|n command to add recipients.")
            return

        contact_app = screen.app.contact
        if not contact_app:
            self.msg("You do not have the contact application.")
            return

        if len(recipients) == 1:
            recipient = recipients[0]
            screen, db = contact_app.edit(recipient)
            self.screen.next(screen, contact_app, db=db)
            return

        # Otherwise, choose a contact
        args = self.args.strip()
        if not args:
            string = "Specify a contact number after |hCONTACT|n:\n"
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
            self.msg("Invalid contact number.")
        else:
            screen, db = contact_app.edit(recipient)
            self.screen.next(screen, contact_app, db=db)
