"""
This file contains the editing commands and options for builders.
"""

from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import class_from_module

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
        field_name = field_name.lower()
        if field_name.endswith("/del"):
            field_name = field_name[:-4]
            self.switches = ["del"]

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

        # Get the representation value for this object type
        repr = getattr(type(obj), "repr", None)
        if repr is None:
            self.msg("This object has no representation to describe it.")
            return

        repr = class_from_module(repr)
        repr = repr(obj)
        if self.rhs:
            value = self.rhs
            if hasattr(repr, "set_" + field_name):
                getattr(repr, "set_" + field_name)(self.caller, value)
            else:
                self.msg("You cannot modify this field name {} in {}.".format(
                        field_name, obj.get_display_name(self.caller)))
        elif "del" in self.switches:
            if hasattr(repr, "clear_" + field_name):
                getattr(repr, "clear_" + field_name)(self.caller)
            else:
                self.msg("You cannot clear this field name {} in {}.".format(
                        field_name, obj.get_display_name(self.caller)))
        else:
            if hasattr(repr, "get_" + field_name):
                getattr(repr, "get_" + field_name)(self.caller)
            elif field_name in repr.fields:
                value = getattr(obj, field_name)
                self.caller.msg("Current value {} = {} for {}.".format(
                        field_name, value, obj.get_display_name(self.caller)))
            else:
                self.msg("You cannot see this field name {} in {}.".format(
                        field_name, obj.get_display_name(self.caller)))
