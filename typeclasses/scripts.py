"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from textwrap import dedent

from evennia import DefaultScript
from evennia.contrib.ingame_python.scripts import EventHandler
from evennia.utils.utils import class_from_module, inherits_from

class Script(DefaultScript):
    """
    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.

    """
    pass


class AvEventHandler(EventHandler):

    """Avenew version of the event handler."""

    def at_start(self):
        """Start the script and generate documentation."""
        super(AvEventHandler, self).at_start()
        #self.generate_documentation()

    def generate_documentation(self):
        """Generate automatic documentation for the in-game Python system."""
        title = "In-game Python system"
        typeclasses = [
            "typeclasses.characters.Character",
            "typeclasses.exits.Exit",
            "typeclasses.objects.Object",
            "typeclasses.rooms.Room",
        ]

        # Generate the help text
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
            events = self.get_events(typeclass)
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

    def get_events(self, obj):
        """
        Return a dictionary of the object's events.
        """
        events = EventHandler.get_events(self, obj)
        others = {}

        # If a character, look for a PChar
        if not isinstance(obj, type) and inherits_from(obj, "typeclasses.characters.Character"):
            if obj.db.prototype:
                others = EventHandler.get_events(self, obj.db.prototype)

        # Merge both dictionaries
        for name, event in others.items():
            if name not in events:
                events[name] = event

        return events

    def get_callbacks(self, obj):
        """
        Return a dictionary of the object's callbacks.

        Args:
            obj (Object): the connected objects.

        Returns:
            A dictionary of the object's callbacks.

        Note:
            This method can be useful to override in some contexts,
            when several objects would share callbacks.

        """
        callbacks = EventHandler.get_callbacks(self, obj)
        others = {}

        # If a character, look for a PChar
        if inherits_from(obj, "typeclasses.characters.Character"):
            if obj.db.prototype:
                others = EventHandler.get_callbacks(self, obj.db.prototype)

        # Merge both dictionaries
        for name, callback_list in others.items():
            if name not in callbacks:
                callbacks[name] = []
            callbacks[name].extend(callback_list)

        return callbacks
