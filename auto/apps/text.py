"""
Text application.
"""

from textwrap import dedent, wrap

from evennia.utils.utils import crop

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
        recipients.sort()
        if not recipients:
            self.msg("You haven't specified at least one recipient.")
            screen.display()
            return

        content = db["content"]
        if not content:
            self.msg("This text is empty, write something before sending it.")
            screen.display()
            return

        # Create a new thread if necessary
        texts = Text.objects.get_texts_with([sender] + recipients)
        if texts:
            thread = texts[0].thread
        else:
            thread = Thread()
            thread.save()
        thread.text_set.create(sender=sender, recipients=",{},".format(recipients), content=content)
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
        to <phone number>

    If the phone number is already present, remove it.

    """

    key = "to"

    def func(self):
        """Execute the command."""
        screen = self.screen
        db = screen.db
        number = self.args.strip()
        if not number:
            self.msg("Specify a phone number of a recipient, to add or remove him.")
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
        content = db.get("content", "(type your text here)")
        content = "\n    ".join(wrap(content, 75))
        recipients = ",  ".join(recipients)
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
        if threads:
            string += "  Create a |hNEW|n message.\n"
            i = 1
            for thread_id, text in threads.items():
                thread = text.thread
                sender = text.sender
                if thread.name:
                    sender = group.name
                elif sender == number:
                    sender = "you"

                content = crop(text.content, 40)
                string += "\n  {{|h{:>2}|n}} From {:<20}: {}".format(i, sender, content)
                i += 1
            string += "\n\n(Type a number to open this text.)"
        else:
            string += "\n  You have no texts yet.  Want to create a |hNEW|n one?"

        count = Text.objects.get_texts_for(number).count()
        s = "" if count == 1 else "s"
        string += "\n\nText app: {} saved message{s}.".format(count, s=s)
        self.user.msg(string)


class TextApp(BaseApp):

    """Text applicaiton.

    """

    app_name = "text"
    start_screen = MainScreen

