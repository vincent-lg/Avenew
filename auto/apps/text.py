"""
Text application.
"""

from textwrap import dedent, wrap

from evennia.utils.utils import crop, lazy_property

from auto.apps.base import BaseApp, BaseScreen, AppCommand
from web.text.models import Text, Thread

## Helper functions
def get_phone_number(obj):
    """Return the phone number of this object, if found."""
    number = obj.tags.get(category="phone number")
    if not number or not isinstance(number, basestring):
        raise ValueError("unknown or invalid phone number")

    number = number[:3] + "-" + number[3:]
    return number

## New text screen and commands

class CmdSend(AppCommand):

    """
    Send  the current text message.
    """

    key = "send"

    def func(self):
        """Execute the command."""
        screen = self.screen
        db = screen.db
        sender = screen.obj.tags.get(category="phone number")
        recipients = list(db.get("recipients", []))
        if not recipients:
            self.msg("You haven't specified at least one recipient.")
            screen.display()
            return

        content = db["content"]
        if not content:
            self.msg("This text is empty, write something before sending it.")
            screen.display()
            return

        # Send the new text
        Text.objects.send(sender, recipients, content)
        self.msg("Thanks, your message has been sent successfully.")
        screen.back()


class CmdCancelSend(AppCommand):

    """
    Cancel and go back to the list of texts.
    """

    key = "cancel"

    def func(self):
        """Execute the command."""
        screen = self.screen
        self.msg("Your text was cancelled.  Going back to the list of texts.")
        screen.back()


class CmdTo(AppCommand):

    """
    Add or remove a recipient.

    Usage:
        to <phone number or contact>

    If the phone number, or contact, is already present, remove it.

    """

    key = "to"

    def func(self):
        """Execute the command."""
        screen = self.screen
        db = screen.db
        number = self.args.strip()
        if not number:
            self.msg("Specify a phone number or contact name of a recipient, to add or remove him.")
            return

        # First of all, maybe it's a contact name
        if screen.app.contact:
            matches = screen.app.contact.search(number)
            if len(matches) == 1:
                number = matches[0].phone_number
            elif len(matches) >= 2:
                self.msg("This contact name isn't specific enough.  It could be:\n  {}\nPlease specify.".format("  ".join([contact.name for contact in matches])))
                return

        number = number.replace("-", "")
        if not number.isdigit() or len(number) != 7:
            self.msg("This is not a valid phone number.")
            return

        # Add or remove
        if "recipients" not in db:
            db["recipients"] = []
        recipients = db["recipients"]
        if number in recipients:
            recipients.remove(recipient)
            self.msg("This phone number was removed from the list of recipients.")
        else:
            recipients.append(number)
            self.msg("This phone number was added to the list of recipients.")
        screen.display()


class NewTextScreen(BaseScreen):

    """This screen appears to write a new message, with possibly some
    fields that are pre-loaded.

    """

    commands = [CmdSend, CmdCancelSend, CmdTo]

    def display(self):
        """Display the new message screen."""
        number = get_phone_number(self.obj)
        screen = dedent("""
            New message (|hBACK|n to go back)

            From: {}
              To: {}

            Text message:
                {}

                |hSEND|n                                             |hCANCEL|n
        """.lstrip("\n"))
        db = self.db
        recipients = list(db.get("recipients", []))
        for i, recipient in enumerate(recipients):
            if self.app.contact:
                recipients[i] = self.app.contact.format(recipient)

        content = db.get("content", "(type your text here)")
        content = "\n    ".join(wrap(content, 75))
        recipients = ", ".join(recipients)
        self.user.msg(screen.format(number, recipients, content))

    def no_match(self, string):
        """Command no match, to write the text content."""
        db = self.db
        old_content = db.get("content", "")
        if old_content:
            old_content += "\n"
        content = old_content + string
        db["content"] = content
        self.display()
        return True


## Thread screen anc commands

class ThreadScreen(BaseScreen):

    """This screen appears to see a specific thread and allow to
    write and reply right away.

    """

    commands = [CmdSend]

    def display(self):
        """Display the new message screen."""
        db = self.db
        thread = db["thread"]
        if not thread:
            self.user.msg("Can't display the thread, an error occurred.")
            return

        number = self.obj.tags.get(category="phone number")
        screen = dedent("""
            Messages with {} (|hBACK|n to go back)

            {}

            Text message:
                {}

                |hSEND|n
        """.lstrip("\n"))
        texts = list(reversed(thread.text_set.order_by("db_date_sent").reverse()[:10]))
        if texts:
            recipients = texts[0].exclude(number)
            db["recipients"] = recipients
            if self.app.contact:
                recipients = [self.app.contact.format(recipient) for recipient in recipients]

        # Browse the list of texts in this thread
        messages = []
        for text in texts:
            sender = text.sender
            if sender == number:
                sender = "You"
            elif self.app.contact:
                sender = self.app.contact.format(sender)

            content = text.content + " (" + text.sent_ago + ")"
            content = wrap(content, 75 - len(sender) - 3)
            content = ("\n" + (len(sender) + 2) * " ").join(content)
            messages.append(sender + ": " + content)

        content = db.get("content", "(type your text here)")
        content = "\n    ".join(wrap(content, 75))
        recipients = ", ".join(recipients)
        messages = "\n".join(messages)
        self.user.msg(screen.format(recipients, messages, content))

    def no_match(self, string):
        """Command no match, to write the text content."""
        db = self.db
        old_content = db.get("content", "")
        if old_content:
            old_content += "\n"
        content = old_content + string
        db["content"] = content
        self.display()
        return True


## Main screen and commands

class CmdNew(AppCommand):

    """
    Compose a new text message.
    """

    key = "new"

    def func(self):
        self.screen.next(NewTextScreen)


class MainScreen(BaseScreen):

    """Main screen of the text app.

    This screen displays the text messages, both sent and received
    by this phone.  It provides commands to create new messages, reply
    to messages, and ...

    """

    commands = [CmdNew]

    def display(self):
        """Display the app."""
        number = self.obj.tags.get(category="phone number")
        if not number or not isinstance(number, basestring):
            self.msg("Your phone number couldn't be found.")
            self.back()
            return

        threads = Text.objects.get_threads_for(number)
        string = "Texts for {} (|hBACK|n to go back)".format(number)
        string += "\n"
        self.db["threads"] = {}
        stored_threads = self.db["threads"]
        if threads:
            string += "  Create a |hNEW|n message.\n"
            i = 1
            for thread_id, text in threads.items():
                thread = text.thread
                stored_threads[i] = thread
                senders = text.exclude(number)
                if self.app.contact:
                    senders = [self.app.contact.format(sender) for sender in senders]

                sender = ", ".join(senders)
                if thread.name:
                    sender = thread.name
                sender = crop(sender, 20)

                content = text.content
                if text.sender == number:
                    content = "]You] " + content
                content = crop(content, 35)
                string += "\n  {{|h{:>2}|n}} {:<20}: {:<35} ({}(".format(i, sender, content, text.sent_ago)
                i += 1
            string += "\n\n(Type a number to open this text.)"
        else:
            string += "\n  You have no texts yet.  Want to create a |hNEW|n one?"

        count = Text.objects.get_texts_for(number).count()
        s = "" if count == 1 else "s"
        string += "\n\nText app: {} saved message{s}.".format(count, s=s)
        self.user.msg(string)

    def no_match(self, string):
        """Method called when no command matches the user input.

        This allows us to redirect to the ThreadScreen if a number
        has been entered.

        """
        if string.isdigit():
            thread = int(string)
            if thread not in self.db["threads"]:
                self.user.msg("This is not a number in your current threads.")
                self.display()
            else:
                thread = self.db["threads"][thread]
                self.next(ThreadScreen, db=dict(thread=thread))

            return True

        return False

    def wrong_input(self, string):
        """A wrong input has been entered."""
        self.user.msg("Enter a thread number to oepn it.")


class TextApp(BaseApp):

    """Text applicaiton.

    """

    app_name = "text"
    start_screen = MainScreen

    @lazy_property
    def contact(self):
        """Return the contact app, if available."""
        return self.type.apps.get("contact")
