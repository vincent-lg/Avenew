"""Module to handle automatic documentation."""

from textwrap import dedent

from evennia import ScriptDB, ObjectDB
from evennia.utils.utils import class_from_module

from world.op_wiki import get_URI, create, update

def generate_documentation():
    """Generate the automatic documentation.

    This function will attempt to write to the wiki, to create or
    update) automatically-generated articles.  The articles that will
    be generated are:

    - 'ingame-python': the in-game Python help.

    """
    generate_ingame_python_documentation()

def generate_ingame_python_documentation():
    """Generate the documentation for the in-game Python system."""
    title = "In-game Python system"
    typeclasses = [
        "typeclasses.characters.Character",
        "typeclasses.exits.Exit",
        "typeclasses.objects.Object",
        "typeclasses.rooms.Room",
    ]

    # Generate the help text
    try:
        script = ScriptDB.objects.get(db_key="event_handler")
    except ScriptDB.DoesNotExist:
        return

    text = "**This document has been automatically-generated by the " \
            "game engine.  If you edit it, your changes will be lost " \
            "the next time the server reloads.**"
    text += "\n\n[TOC]"

    # Browse typeclasses
    for path in typeclasses:
        typeclass = class_from_module(path)
        name = path.split(".")[-1]
        text += "\n\n## {} ({})".format(name, path)

        # Browse the list of events for this typeclass
        # Waiting for [PR#1377](https://github.com/evennia/evennia/pull/1377),
        # we must query one object with this typeclass.  This is not
        # ideal and should be removed whenever we will be able to directly
        # query typeclass events.
        obj = ObjectDB.objects.filter(db_typeclass_path=path).first()
        events = []
        if obj:
            events = script.get_events(obj)
            events = list(events.items())
            events.sort()

        if events:
            for name, (variables, help, cal1, cal2) in events:
                help = help.strip("\n")
                text += "\n\n### {}".format(name)

                # Display variable's help
                lines = [l.strip() for l in help.splitlines()]
                text += "\n\n{}".format(lines[0])
                if variables:
                    text += "\n\n" + dedent("""
                        | Variable | Help |
                        | -------- | ---- |
                    """.strip("\n")).strip()
                    for variable in variables:
                        var_help = [line for line in lines if line.startswith(variable + ": ")]
                        if var_help:
                            var_help = var_help[0]
                            var_help = var_help[len(variable) + 2:]
                            var_help = var_help[0].upper() + var_help[1:]
                        else:
                            var_help = "No help seems to exist for this variable."
                        text += "\n| {} | {} |".format(variable, var_help)

                else:
                    text += "\n\n- This event has no variable."

                # Write the help (without the variable list at the bottom)
                del lines[0]
                end = None
                for i, line in enumerate(lines):
                    if line.startswith("Variables ") and line.endswith(":"):
                        end = i
                        break

                if end:
                    while end < len(lines):
                        del lines[end]

                help = "\n".join(lines).strip("\n")
                text += "\n\n{}".format(help)
        else:
            text += "\n\n**There is no event in this typeclass.**"

    # Create/update a wiki entry
    page = get_URI("ingame_python")
    if page is None:
        create("ingame_python", title, text)
    else:
        # Only update if the content is different
        if page.current_revision.content != text:
            update(page, text, title=title, message="Automatic update")
