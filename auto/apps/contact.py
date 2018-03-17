# -*- coding: utf-8 -*-

"""
Contact application.

This application allows to add and manage contacts.  Contacts are a
useful link between identity (a name, usually) and a phone number.  They
are available in other applications, like the text app.  Contacts
are stored directly in the application, which has a few shortcuts to
add, remove and edit contacts.  It can also easily format a phone number
(retrieving the matching name if possible), and search a name for its
matching phone number.  See the `ContactApp` for details.  From anywhere
in another app, you could do something like this:

    contact = self.type.apps.get("contact")
    if contact: # Remember the contact app may not be installed
        name = contact.format("555-1234")
        # Will return 555-1234, or the contact name if found

Screens in this app:
    MainScreen: display the list of contacts in this device and allow
            to edit one, or create a new one.
    ContactScreen: edit an existing contact or do further operations on it.

Commands in this app:
    MainScreen:
        new: create a new contact (CmdNew).
    ContactScreen:
        first: edit the contact's first name (CmdFirst).
        last: edit the contact's last name (CmdLast).
        number: edit the contact's phone number (CmdNumber).
        done: save the modifications for this contact (CmdDone).

"""

from textwrap import dedent, wrap

from evennia.utils.utils import crop, lazy_property

from auto.apps.base import BaseApp, BaseScreen, AppCommand

## Application class

class ContactApp(BaseApp):

    """Contact applicaiton.

    This application supports several shortcut methods to manipulate
    contacts.  Use these methods instead of directly creating and
    manipulating the contact object in order to save into the database.

    Methods in this class:
        format: format a phone number, giving its contact name if possible.
        add: add a new contact and store it in the database.
        sort: sort the list of contacts alphabetically.
        remove: remove a contact from the list and the database.
        search: search a name and return its phone number if found.
        update: update an existing contact and store it in the database.

    This class also has a `contacts` property which will contain a
    list of current Contact objects.

    """

    app_name = "contact"
    display_name = "Contact"
    start_screen = "MainScreen"

    @lazy_property
    def contacts(self):
        """Return the list of contacts (Contact objects)."""
        contacts = []
        for info in self.db.get("contacts", []):
            contact = Contact(**info)
            contacts.append(contact)

        return contacts

    def format(self, phone_number, use_contact=True):
        """Return the formatted phone number or contact name if found.

        Args:
            phone_number (str): the phone number.
            use_contact (bool, optional): use the contact to retrieve the name.

        Returns:
            name (str): the display name or formatted phone number.

        """
        # Remove dashes from the phone number
        if isinstance(phone_number, basestring):
            phone_number = phone_number.replace("-", "")

        if not isinstance(phone_number, basestring) or not phone_number.isdigit() or len(phone_number) != 7:
            raise ValueError("the specified phone number is invalid: {}".format(phone_number))

        # Find a contact with this phone number
        if use_contact:
            for contact in self.contacts:
                if contact.phone_number == phone_number:
                    return contact.name

        return phone_number[:3] + "-" + phone_number[3:]

    def edit(self, number):
        """Edit the contact information for the specified number.

        Args:
            number (str): the phone number of the existing or new contact.

        Returns:
            screen, db: the information needed to move to this screen.

        """
        data = {}
        for i, contact in enumerate(self.contacts):
            if contact.phone_number == number:
                data["first_name"] = contact.first_name
                data["last_name"] = contact.last_name
                data["phone_number"] = contact.phone_number
                data["contact_id"] = i
                return "auto.apps.contact.ContactScreen", data

        data["phone_number"] = number
        return "auto.apps.contact.ContactScreen", data

    def add(self, first_name="", last_name="", phone_number=""):
        """Add a new contact at the end of the list.

        This method adds a contact at the end of the list, without sorting
        of any kind.  It also stores the added contact in the database.

        Args:
            first_name 9str, optional): the first name of the new contact.
            last_name (str, optional): the last name of the new contact.
            phone_number (str, optional): the phone number of the new contact.

        Returns:
            contact (Contact): the newly-created contact.

        """
        contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number)
        self.contacts.append(contact)
        if "contacts" not in self.db:
            self.db["contacts"] = []
        self.db["contacts"].append(contact.info)
        return contact

    def sort(self):
        """Sort the contact list."""
        self.contacts.sort(key=lambda contact: contact.name)
        lst = list(self.db.get("contacts", []))
        if lst:
            lst.sort(key=lambda info: info["last_name"] + " " + info["first_name"])
            self.db["contacts"] = lst

    def remove(self, contact):
        """Remove a contact.

        Args:
            contact (Contact): the contact to be removed.

        """
        if contact in self.contacts:
            self.contacts.remove(contact)
        if contact.info in self.db["contacts"]:
            self.db["contacts"].remove(contact.info)

    def search(self, name):
        """Search the list of contacts to retrieve a phone number.

        This method always returns a list of matches.

        Args:
            name (str): the contact name.

        Returns:
            matches (list of Contact): a list of matching contacts.

        """
        matches = []
        name = name.lower()
        for contact in self.contacts:
            if contact.name.lower() == name:
                return [contact]
            elif contact.last_name.lower().startswith(name):
                matches.append(contact)
            elif contact.first_name.lower().startswith(name):
                matches.append(contact)

        return matches

    def update(self, contact, first_name=None, last_name=None, phone_number=None):
        """Update a specified contact.

        Args:
            contact (Contact): the contact to be modified.
            first_name (str, optional): the new first name of the contact.
            last_name (str, optional): the new last name of the contact.
            phone_number (str, optional): the new phone number of the contact.

        """
        info = contact.info
        if phone_number and isinstance(phone_number, basestring):
            phone_number = phone_number.replace("-", "")

        if phone_number is not None and (not isinstance(phone_number, basestring) or not phone_number.isdigit() or len(phone_number) != 7):
            raise ValueError("the specified phone number is invalid: {}".format(phone_number))

        if contact in self.contacts:
            if first_name is not None:
                contact.first_name = first_name
            if last_name is not None:
                contact.last_name = last_name
            if phone_number is not None:
                contact.phone_number = phone_number

        if info in self.db.get("contacts", []):
            index = self.db["contacts"].index(info)
            self.db["contacts"][index].update(contact.info)


## Contact class (used throughout all the screens)

class Contact(object):

    """A class to represent a contact with name and number.

    Objects of this class aren't stored in the database.  However,
    through its methods, the contact app (see `ContactApp` in this
    file) offers shortcuts to add, sort and delete contacts.  These
    shortcut methods will create an entry in the database and a
    `Contact` object to manipulate more easily.

    """

    def __init__(self, first_name="", last_name="", phone_number=""):
        """Create a new contact.

        Use the `ContactApp.add` method instead, which has the same
        signature but will make sure the contact is also saved in
        the database.

        Args:
            first_name 9str, optional): the first name of the new contact.
            last_name (str, optional): the last name of the new contact.
            phone_number (str, optional): the phone number of the new contact.

        """
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number

    @property
    def info(self):
        """Return the contact information as a dictionary."""
        return {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "phone_number": self.phone_number,
        }
        return info

    @property
    def name(self):
        """Return the first name and last name when known."""
        first = self.first_name
        last = self.last_name
        name = first
        if name:
            name += " "
        name += last
        return name

    def __repr__(self):
        return "<Contact {} (phone={})>".format(self.name, self.phone_number)


## Screens

class MainScreen(BaseScreen):

    """Main screen of the contact app.

    This screen displays the contact list, allowing to edit one.
    It also has a new command to create a new contact.

    """

    commands = ["CmdNew"]
    short_help = "Écran affichant la liste des contacts."
    long_help = """
        Depuis cet écran, vous pouvez utiliser la commande |ynew|n pour créer un
        nouveau contact. Vous devriez également voir la liste de vos contacts, si
        vous avez enregistré au moins un contact auparavant. Chaque contact, trié
        alphabétiquement, se trouve placé après un numéro. Utilisez ce numéro pour
        ouvrir la fiche du contact, pour l'éditer ou lui envoyer un message. Par
        exemple : |y3|n.
        Comme dans la plupart des écrans, vous pouvez utiliser la commande |yback|n
        pour revenir à l'écran précédent, ou la commande |yexit|n pour quitter l'interface
        et revenir au jeu. Vous pouvez également accéder à l'aide de l'écran en entrant
        la commande |yhelp|n.
    """

    def get_text(self):
        """Display the app."""
        number = self.obj.tags.get(category="phone number")
        if not number or not isinstance(number, basestring):
            self.msg("Votre numéro de téléphone n'a pas pu être trouvé.")
            self.back()
            return

        contacts = self.app.contacts
        string = "Liste de vos contacts"
        string += "\n"
        if contacts:
            string += "  ( Utilisez la commande {new} pour créer un nouveau contact. )\n".format(new=self.format_cmd("new"))
            i = 1
            for contact in contacts:
                name = contact.name
                number = contact.phone_number
                if number:
                    number = self.app.format(number, False)
                else:
                    number = "|ginconnu|n"

                string += "\n  {{{i}}} {:<30} ({})".format(name, number, i=self.format_cmd(str(i), str(i).rjust(2)))
                i += 1
            string += "\n\n( Entrez un numéro pour ouvrir une fiche de contact. )"
        else:
            string += "\n  Vous n'avez aucun contact enregistré. Utilisez la commande {new} pour en créer un.".format(new=self.format_cmd("new"))

        count = len(contacts)
        s = "" if count == 1 else "s"
        string += "\n\nApp contact : {} contact{s} enregistré{s}.".format(count, s=s)
        return string

    def no_match(self, string):
        """Method called when no command matches the user input.

        This allows us to redirect to the ContactScreen if a number
        has been entered.

        """
        contacts = self.app.contacts
        if string.isdigit():
            contact = int(string)
            try:
                assert contact > 0
                contact = contacts[contact - 1]
            except (AssertionError, IndexError):
                self.user.msg("|rCe numéro de contact n'est pas valide.|n")
                self.display()
            else:
                self.next(ContactScreen, db=dict(
                        contact_id=contacts.index(contact),
                        first_name=contact.first_name,
                        last_name=contact.last_name,
                        phone_number=contact.phone_number))

            return True

        return False

    def wrong_input(self, string):
        """A wrong input has been entered."""
        self.user.msg("|rEntrez le numéro d'une fiche de contact pour l'éditer.|n")


class ContactScreen(BaseScreen):

    """Contact screen to edit or add a contact.

    This screen will be displayed if a user types NEW or a number
    to edit an existing contact.

    """

    commands = ["CmdFirst", "CmdLast", "CmdNumber", "CmdDone"]
    short_help = "Écran pour éditer une fiche de contact."
    long_help = """
        Vous pouvez modifier les différents champs d'une fiche de contact.
        La commande |yfirst|n permet de modifier le prénom du contact. La commande
        |ylast|n permet de modifier le nom de famille du contact. La commande
        |ynumber|n permet de changer le numéro de téléphone du contact. Pour ces
        commandes, précisez le nouveau prénom, nom ou numéro de téléphone en
        paramètre. Par exemple, voici les commandes à entrer pour modifier
        complètement un contact :
            |yfirst Annabeth|n
            |ylast Chase|n
            |ynumber 551-0821|n
        Pour enregistrer vos modifications, utilisez la commande |ydone|n.
        Comme dans la plupart des écrans, vous pouvez utiliser la commande |yback|n
        pour revenir à l'écran précédent, ou la commande |yexit|n pour quitter l'interface
        et revenir au jeu. Vous pouvez également accéder à l'aide de l'écran en entrant
        la commande |yhelp|n.
    """

    @property
    def contact(self):
        """Return the contact or None."""
        if "contact_id" in self.db:
            return self.app.contacts[self.db["contact_id"]]

        return None

    def get_text(self):
        """Display the app."""
        contact = self.contact
        first = self.db.get("first_name", contact.first_name if contact else "")
        last = self.db.get("last_name", contact.last_name if contact else "")
        number = self.db.get("phone_number", contact.phone_number if contact else "")
        string = "Contact {}".format(contact.name) if contact else "Nouveau contact"
        string += "\n"
        string += "\n  Prénom         : {} (utilisez |yfirst|n pour changer ce champ)".format(first)
        string += "\n  Nom de famille : {} (utilisez |ylast|n pour changer ce champ)".format(last)
        string += "\n  Téléphone      : {} (utilisez |ynumber|n pour modifier ce champ)".format(number)
        string += "\n\n( Utilisez la commande {done} pour sauvegarder vos modifications. )".format(done=self.format_cmd("done"))
        return string

    def wrong_input(self, string):
        """A wrong input has been entered."""
        self.user.msg("Utilisez les commandes |yfirst|n, |ylast|wn, |ynumber|n ou |ydone|n.")


## Commands

class CmdNew(AppCommand):

    """
    Crée un nouveau contact.

    Usage :
        new

    Cette commande vous permet de créer une nouvelle fiche de contact. Vous
    devrez ensuite préciser le prénom, nom de famille et numéro de téléphone
    de ce contact. Vous n'aurez toutefois pas besoin de préciser toutes ces
    informations pour enregistrer la fiche de contact.
    """

    key = "new"
    aliases = ["nouveau"]

    def func(self):
        self.screen.next(ContactScreen)


class CmdFirst(AppCommand):

    """
    Modifie le prénom de ce contact.

    Usage :
        first <nouveau prénom>

    Exemple :
        first James

    N'oubliez pas : vous devrez utiliser la commande |ydone|n après avoir changé
    un ou plusieurs champs du contact, sans quoi vos modifications ne seront
    pas enregistrées.
    """

    key = "first"
    aliases = ["prénom", "prenom"]

    def func(self):
        screen = self.screen
        name = self.args.strip()
        if not name:
            self.msg("Précisez le prénom du contact pour le modifier..")
            return

        screen.db["first_name"] = name
        screen.display()


class CmdLast(AppCommand):

    """
    Modifie le nom de famille de ce contact.

    Usage :
        last <nouveau nom de famille>

    Exemple :
        last Bond

    N'oubliez pas : vous devrez utiliser la commande |ydone|n après avoir changé
    un ou plusieurs champs du contact, sans quoi vos modifications ne seront
    pas enregistrées.
    """

    key = "last"
    aliases = ["nom de famille", "nom"]

    def func(self):
        screen = self.screen
        name = self.args.strip()
        if not name:
            self.msg("Précisez le nom de famille de ce contact pour le modifier.")
            return

        screen.db["last_name"] = name
        screen.display()


class CmdNumber(AppCommand):

    """
    Modifie le numéro de téléphone de ce contact.

    Usage :
        number <nouveau numéro de téléphone>

    Exemple :
        number 555-1234

    N'oubliez pas : vous devrez utiliser la commande |ydone|n après avoir changé
    un ou plusieurs champs du contact, sans quoi vos modifications ne seront
    pas enregistrées.
    """

    key = "number"
    aliases = ["numéro", "numero"]

    def func(self):
        screen = self.screen
        number = self.args.strip()
        if not number:
            self.msg("Précisez le numéro de téléphone de ce contact pour le modifier.")
            return

        number = number.replace("-", "")
        if len(number) != 7 or not number.isdigit():
            self.msg("|rCela n'est pas un numéro de téléphone valide.|n")
            return

        screen.db["phone_number"] = number
        screen.display()


class CmdDone(AppCommand):

    """
    Enregistre vos modifications et revient à l'écran précédent.

    Usage :
        done

    Si vous faites des modifications à un contact sans les enregistrer, en
    utilisant la commande |yback|n ou |yexit|n directement, vos modifications
    sur le contact seront perdues. N'oubliez donc pas d'utiliser |ydone|n
    pour enregistrer vos modifications.
    """

    key = "done"
    aliases = ["save", "enregistrer", "sauvegarder"]

    def func(self):
        screen = self.screen
        contact = screen.contact
        first = screen.db.get("first_name", "")
        last = screen.db.get("last_name", "")
        if not first and not last:
            self.msg("|rVous devez préciser au moins un prénom ou un nom de famille avant d'enregistrer.|n")
            return

        number = screen.db.get("phone_number", "")
        if contact:
            screen.app.update(contact, first, last, number)
            self.msg("Vos modifications ont bien été enregistrées.")
        else:
            screen.app.add(first, last, number)
            self.msg("Votre nouveau contact vient d'être ajouté.")
        screen.app.sort()
        screen.back()
