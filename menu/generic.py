"""Module containing generic functions for EvMenu."""

def _formatter(nodetext, optionstext, caller=None):
    """Do not display the options, only the text.

    This function is used by EvMenu to format the text of nodes.
    Options are not displayed for this menu, where it doesn't often
    make much sense to do so.  Thus, only the node text is displayed.

    """
    return nodetext

def _input_no_digit(menuobject, raw_string, caller):
    """
    Process input.

    Processes input much the same way the original function in
    EvMenu operates, but if input is a number, consider it a
    default choice.

    Args:
        menuobject (EvMenu): The EvMenu instance
        raw_string (str): The incoming raw_string from the menu
            command.
        caller (Object, Player or Session): The entity using
            the menu.
    """
    cmd = raw_string.strip().lower()

    if cmd.isdigit() and menuobject.default:
        goto, callback = menuobject.default
        menuobject.callback_goto(callback, goto, raw_string)
    elif cmd in menuobject.options:
        # this will take precedence over the default commands
        # below
        goto, callback = menuobject.options[cmd]
        menuobject.callback_goto(callback, goto, raw_string)
    elif menuobject.auto_look and cmd in ("look", "l"):
        menuobject.display_nodetext()
    elif menuobject.auto_help and cmd in ("help", "h"):
        menuobject.display_helptext()
    elif menuobject.auto_quit and cmd in ("quit", "q", "exit"):
        menuobject.close_menu()
    elif menuobject.default:
        goto, callback = menuobject.default
        menuobject.callback_goto(callback, goto, raw_string)
    else:
        caller.msg(_HELP_NO_OPTION_MATCH)

    if not (menuobject.options or menuobject.default):
        # no options - we are at the end of the menu.
        menuobject.close_menu()

