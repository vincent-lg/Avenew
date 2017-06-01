"""
This file contains the editing commands and options for builders.
"""

from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.evtable import EvTable

class CmdEdit(MuxCommand):

    """
    Global editing command.

    To use this command, you have to specify the field you wish to
    edit, the object's name (or #ID) and the value after an equal
    sign.  For instance:

        @speed a porsche = 180

    Depending on the object, you will have different fields you can
    modify through this command.  If you have the object and want to
    know what you can edit, simply use this command without the first
    parameter:

        @ a porsche

    Use both the field name and object name without the equal sign
    and value to see the current value of this field:

        @speed #331

    """

    key = "@"
    locks = "cmd:id(1) or perm(Builders)"
    help_category = "Building"

    def func(self):
        """Main function for this command."""
        field_name, sep, obj_name = self.lhs.partition(" ")
        if not obj_name:
            obj_name = field_name
            field_name = ""

        if not obj_name:
            self.msg("Specify at least an object's name or #ID.")
            return

        # Search for the actual object
        obj = self.caller.search(obj_name)
        if not obj:
            return

        # Get the fields that can be modified
        fields = getattr(type(obj), "to_edit", {})

        # If no field name is specified, display the table
        if not field_name:
            table = EvTable("Field", "Value", width=78)
            for field, attr in sorted(fields.items()):
                table.add_row(field, self.get_value(obj, attr))

            self.msg(table)
            return

        # At this point, field_name is not empty and should match a field
        if field_name not in type(obj).to_edit:
            self.msg("You can't edit {} in {} (#{}) of type {}.".format(
                    field_name, obj, obj.id, type(obj).__name__))
            return

        # If the value isn't specified, only display this field
        attr = type(obj).to_edit[field_name]
        if not self.rhs:
            self.msg("Current value for the field {}: {}".format(
                    field_name, self.get_value(obj, attr)))
            return

        # If a value has been specified, try to update it
        old = self.get_value(obj, attr)
        self.set_value(obj, attr, self.rhs)
        new = self.get_value(obj, attr)
        if old != new:
            self.msg("Set to: {}.".format(new))

    def get_value(self, obj, attr):
        """Return a string value of the attribute."""
        if isinstance(attr, str):
            attrs = attr.split(".")
            for a in attrs[:-1]:
                obj = getattr(obj, a)
            return str(getattr(obj, attrs[-1], "|rUnknown|n"))
        elif isinstance(attr, (tuple, list)):
            return " / ".join([self.get_value(obj, a) for a in attr])
        elif isinstance(attr, dict):
            attr = attr["attr"]
            return self.get_value(obj, attr)
        else:
            raise ValueError("unknwon type for attribute")

    def set_value(self, obj, attr, value):
        """Set the new value to the attribute."""
        if isinstance(attr, str):
            attrs = attr.split(".")
            for a in attrs[:-1]:
                obj = getattr(obj, a)

            value = value.strip()
            if not value:
                self.msg("The field's value cannot be empty.")
            else:
                setattr(obj, attrs[-1], value)
        elif isinstance(attr, (tuple, list)):
            values = value.split("/")
            for i, a in enumerate(attr):
                try:
                    value = values[i]
                except IndexError:
                    self.msg("You didn't specify enough parameters for this field.")
                else:
                    self.set_value(obj, a, value)
        elif isinstance(attr, dict):
            attrs = attr["attr"].split(".")
            for a in attrs[:-1]:
                obj = getattr(obj, a)

            name = attrs[-1]
            f_type = attr.get("type")
            if f_type == "str":
                pass
            elif f_type in ("int", "float"):
                cnv = int if f_type == "int" else float
                try:
                    value = cnv(value)
                except ValueError:
                    self.msg("This value is invalid.")
                else:
                    valid = attr.get("valid")
                    if valid:
                        if not valid(value):
                            self.msg("This value is invalid.")
                            return

                    f_set = attr.get("set")
                    if f_set:
                        value = f_set(value)

                    setattr(obj, name, value)
        else:
            raise ValueError("unknwon type for attribute")
