# -*- coding: utf-8 -*-

"""
Module containing the mixins to be used by apps.

These mixin classes should be used in combination with `BaseApp` to add
features to the app.  These "features" are methods and properties on the
app itself, and are only shortcuts.

"""

from evennia.utils.search import search_tag

## Mix-in

class ContactMixin:

    """Mixin to be used in other apps requiring access to contacts.

    This mixin gives methods and properties that can be useful for and
    for any app that has need of the contact app.  They are shortcuts
    and they should be used in the inheritance hierarchy along with BaseApp:

        class AnyApp(BaseApp, ContactMixin):
            # ...

    Properties:
        phone_number: the object's phone number.
        pretty_phone_number: the pretty phone number (XXX-YYYY).

    Instance methods:
        get_phone_number: return the phone number of an object, if available.
        find_phone: return the phone linked to a given phone number.
        format: format a phone number, giving its contact name if possible.
        search: search a name and return matching phone numbers if found.

    """

    @property
    def phone_number(self):
        """Shortcut, return the phone number of the app object."""
        return self.get_phone_number(pretty=False)

    @property
    def pretty_phone_number(self):
        """Shortcut, return the pretty phone number of the app object."""
        return self.get_phone_number(pretty=True)

    def get_phone_number(self, pretty=False, obj=None):
        """Return the phone number of this object, if found.

        Args:
            pretty (bool, optional): add a dash after the third number.
            obj (Object): the object (phone) to query, `self` if not set.

        Returns:
            number (str): the phone number.

        Raises:
            ValueError: the specified object has no phone number.

        """
        obj = obj or self.obj
        number = obj.tags.get(category="phone number")
        if not number or not isinstance(number, basestring):
            raise ValueError("unknown or invalid phone number")

        if pretty:
            number = number[:3] + "-" + number[3:]

        return number

    def find_phone(self, phone_number):
        """Return the object with this associated phone number, or None.

        Args:
            phone_number (str): the phone number.

        """
        phones = search_tag(phone_number, category="phone number")
        return phones[0] if phones else None

    def format(self, phone_number, use_contact=True, obj=None):
        """Return the formatted phone number or contact name if found.

        Args:
            phone_number (str): the phone number.
            use_contact (bool, optional): use the contact to retrieve the name.
            obj (Object, optional): the object to use for the contact
                    app (will be `self` if not specified).

        Returns:
            name (str): the display name or formatted phone number.

        """
        obj = obj or self.obj
        return self.format_obj(obj, phone_number, use_contact)

    def search(self, name_or_number, obj=None):
        """Search for a phone number, giving a name or number.

        If the contact app can be found on this object, use it.  Otherwise,
        return the number as is.

        Args:
            name_or_number (str): the name or phone number.
            obj (Object, optional): the object to use for the search.
                    Will be `self` if not set.

        Returns:
            matches (list of str): the list of the found phone numbers.

        """
        obj = obj or self.obj
        matches = []

        # Find the contact app and query the specified number or name
        contacts = obj.attributes.get(
                "_type_storage", {}).get(
                "computer", {}).get(
                "app_storage", {}).get(
                "app", {}).get(
                "contact", {}).get(
                "contacts", [])
        for contact in contacts:
            # Skip contacts without phone numbers
            if not contact.get("phone_number"):
                continue

            first = contact.get("first_name", "")
            last = contact.get("last_name", "")
            name = first
            if name:
                name += " "
            name += last
            if name.lower() == name_or_number.lower():
                return [contact["phone_number"]]
            elif last.lower().startswith(name_or_number.lower()):
                matches.append(contact["phone_number"])
            elif first.lower().startswith(name_or_number.lower()):
                matches.append(contact["phone_number"])

        if matches:
            return matches
        else:
            name_or_number = name_or_number.replace("-", "")
            if name_or_number.isdigit() and len(name_or_number) == 7:
                return [name_or_number]
            else:
                return []

    @staticmethod
    def format_obj(obj, phone_number, use_contact=True):
        """Format the specified phone number.

        Args:
            obj (Objerct): the object in which the contact app must be sought.
            phone_number (str): the phone number to format.
            use_contact (bool, optional): use the contact app if available.

        Returns:
            name (str): the formatted phone number or contact name if found.

        """
        # Remove dashes from the phone number
        if isinstance(phone_number, basestring):
            phone_number = phone_number.replace("-", "")

        if not isinstance(phone_number, basestring) or not phone_number.isdigit() or len(phone_number) != 7:
            raise ValueError("the specified phone number is invalid: {}".format(phone_number))

        # Find a contact with this phone number
        if use_contact:
            contacts = obj.attributes.get(
                    "_type_storage", {}).get(
                    "computer", {}).get(
                    "app_storage", {}).get(
                    "app", {}).get(
                    "contact", {}).get(
                    "contacts", [])
            for contact in contacts:
                if contact.get("phone_number") == phone_number:
                    first = contact.get("first_name", "")
                    last = contact.get("last_name", "")
                    name = first
                    if name:
                        name += " "
                    name += last
                    return name

        return phone_number[:3] + "-" + phone_number[3:]
