# -*- coding: utf-8 -*-

"""Building menu for rooms."""

from menu.building.building_menu import BuildingMenu

class RoomBuildingMenu(BuildingMenu):

    def init(self, room):
        self.add_choice("title", "t", attr="key", glance="{obj.key}", text="""
                -------------------------------------------------------------------------------
                Room title for {obj}({obj.id})

                You can change the room title simply by entering it.
                Use |y@|n to go back to the main menu.

                Current title: |c{obj.key}|n
        """)
        self.add_choice_edit()
        self.add_choice("exits", key="x", glance=glance_exits, text=text_exits, on_nomatch=nomatch_exits)
        self.add_choice_quit()

        # Exit level
        self.add_choice("exit", key="x.*", on_nomatch=nomatch_exit, text=text_exit)

def glance_exits(room):
    """Show the exits in the room.

    Args:
        room (Room): the room with exits.

    """
    exits = room.exits
    if exits:
        ret = ""
        for exit in exits:
            ret += "\n   " + exit.key.ljust(20)
            ret += " (to {}(#{})".format(exit.destination.key, exit.destination.id)
        return ret
    else:
        return "\n    None yet"

def text_exits(room):
    """Return the text when entering the exits menu."""
    exits = room.exits
    text = """
        Exits of: {obj.key}(#{obj.id})

        Enter an exit name to create or edit it.  Aliases can also be used.  To edit
        the |ynorth|n exit, for instance, you can simply type |yn|n.  If the exit
        you want to edit doesn't exist, it will be created.
        Type |y@|n to go back to the main menu.

        Current exits:
    """
    if exits:
        for exit in exits:
            text += "\n" + " " * 12 + "|y" + exit.key.ljust(20) + "|n"
            text += " to {:<30}(#{:<4})".format(exit.destination.key, exit.destination.id)
            if exit.aliases:
                text += " with aliases |y" + "|n, |y".join([alias for alias in exit.aliases.all()]) + "|n"
    else:
        text += "\n" + " " * 12 + "|gNone yet|n"

    return text

def nomatch_exits(room, caller, string, menu):
    """Edit an exit, specified as a name."""
    if string.startswith("@e "):
        string = string[3:].lower()
        exits = room.exits
        for exit in exits:
            if string == exit.key.lower() or any(string == alias for alias in exit.aliases.all()):
                caller.msg("Editing: {}".format(exit))
                menu.move(exit)
                return False

    return False

def text_exit(room, menu):
    """Return the text in a specific exit menu."""
    exit = menu.keys[-1]
    return """
        Editing exit {key} from room {room}(#{room_id})

        Exit title  : {key:<20} (use |y@t <new title>|n to change it).
        Exit aliases: {aliases:<20} (use |y@a <alias 1> [, alias 2...]|n to set).
        Destination : {dest:<20} (use |y@d #<new room ID>|n to change destination).

        Delete this exit with |y@del|n.
    """.format(key=exit.key, room=exit.location, room_id=exit.location.id,
            aliases=", ".join([alias for alias in exit.aliases.all()]) if exit.aliases.all() else "none yet", dest=exit.destination)

def nomatch_exit(caller, menu, string, room):
    """Handle no match in a specific exit."""
    # Find the exit
    exit = menu.keys[-1]
    if exit is None:
        caller.msg("|rCannot find the exit {}.|n".format(menu.keys[-1]))
        return False

    # Analyze the command
    cmd, args = string.split(" ", 1)
    cmd = cmd.lower()
    if cmd == "@t":
        exit.key = args
        return True

    caller.msg("Unknown command {}.".format(cmd))
