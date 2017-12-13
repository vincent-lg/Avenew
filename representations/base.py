# -*- coding: utf-8 -*-

"""Module containing the abstract representation."""

from evennia.utils.evform import EvForm
from evennia.utils.evtable import EvTable

class BaseRepr(object):

    """Abstract representation."""

    fields = {}
    to_display = []
    form = None

    def __init__(self, obj):
        self.obj = obj

    def process(self, caller, field, value=None, operation="get"):
        """Process the data.  This is called by the 2 command.

        Args:
            caller (Object): the object calling for this modification.
            field (str): the field name.
            value (str, optional): the provided value, if any.
            operation (str, optional): the operation to perform. Can be
                    'get', 'set', 'clear', 'add', 'del'.

        Notes:
            The speicifed field can be in the field list (`fields`
            class variable).  If so, the value of the field in this
            class variable should be a type (like `int` or `str`).
            The methods `get_<field>`, `set_<field>`, `clear_<field>`,
            `add_<field>`, and `del_<field>` can also be provided for
            additional customization.

        """
        if not field:
            return self.display(caller)

        if value and field in type(self).fields and operation in ("set", "add", "del"):
            to_type = type(self).fields[field]
            try:
                value = to_type(value)
            except ValueError:
                caller.msg("Invalid value for {}: {}.".format(field, value))
                return

        # Different operations
        if operation == "set":
            if hasattr(self, "set_{}".format(field)):
                getattr(self, "set_{}".format(field))(caller, value)
            else:
                setattr(self.obj, field, value)
                caller.msg("New value {} = {} for {}.".format(field, value, self.obj))
        elif operation == "add":
            if hasattr(self, "add_{}".format(field)):
                getattr(self, "add_{}".format(field))(caller, value)
            else:
                old = getattr(self.obj, field)
                if isinstance(old, list):
                    old.append(value)
                elif isinstance(old, tuple):
                    setattr(self.obj, field, old + (value, ))
                else:
                    raise ValueError("I don't know what to make of this type.")
                caller.msg("New value {} added to {} for {}.".format(value, field, self.obj))

            operation = "get"
        elif operation == "del":
            if hasattr(self, "del_{}".format(field)):
                getattr(self, "del_{}".format(field))(caller, value)
            else:
                old = getattr(self.obj, field)
                if isinstance(old, list):
                    setattr(self.obj, field, [e for e in old if e != value])
                elif isinstance(old, tuple):
                    setattr(self.obj, field, tuple(e for e in old if e != value))
                else:
                    raise ValueError("I don't know what to make of this type.")

                caller.msg("Value {} removed from {} for {}.".format(value, field, self.obj))
        elif operation == "get":
            if hasattr(self, "get_{}".format(field)):
                value = getattr(self, "get_{}".format(field))(caller)
            else:
                value = getattr(self.obj, field)
            caller.msg("Current value {} = {} for {}.".format(
                    field, value, self.obj.get_display_name(caller)))

    def display(self, caller):
        """Display the object."""
        self.caller.msg(self.get_form(caller))

    def get_form(self, caller):
        """Return the formatted form."""
        if type(self).form:
            to_display = {}
            for i, field in enumerate(type(self).to_display):
                if hasattr(self, "get_{}".format(field)):
                    value = getattr(self, "get_{}".format(field))(caller)
                else:
                    value = getattr(self.obj, field)
                to_display[i + 1] = value
            return unicode(EvForm(form={"CELLCHAR": "x", "TABLECHAR": "c",
                    "FORM": type(self).form}, cells=to_display))
        else:
            return "No display method has been provided for this object."
