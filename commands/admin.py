# -*- coding: utf-8 -*-

"""This file contains the commands for administrators."""

from commands.command import Command

class CmdApp(Command):

    """
    Inspect the app structure.

    Syntax:
        @app [object name]

    This command will inspect the app structure (the open screens) on self
    or a specified object.

    """

    key = "@app"
    locks = "cmd:id(1) or perm(Admins)"
    help_category = "Admin"

    def func(self):
        """Command body."""
        # Search for the actual object
        args = self.args.strip()
        if args:
            obj = self.caller.search(args, global_search=True)
            if obj is None:
                return
        else:
            obj = self.caller

        string = "Examining {}:".format(obj.get_display_name(self.caller))

        # The object could be a computer
        if hasattr(obj, "types") and obj.types.get("computer"):
            otype = obj.types.get("computer")
            string += "\n  This object is of type computer and has apps."
            string += "\n  Available apps ({}): ".format(
                    sum(len(apps) for apps in otype.db.get("apps", {}).values()))
            for folder, apps in otype.db.get("apps", {}).items():
                if len(apps):
                    string += "\n    Folder {folder!r}: {apps}".format(folder=folder, apps=", ".join(apps))

            if "used" in otype.db:
                obj = otype.db["used"]
                string += "\n  This object is currently used by {}.".format(obj.get_display_name(self.caller))
            else:
                string += "\n  This object is not currently used by anyone."
                self.msg(string)
                return

        # Explore the object for the proper CmdSet
        num = 0
        for cmdset in obj.cmdset.all():
            if cmdset.key == "computer":
                computer = cmdset
                num += 1

        if num == 0:
            string += "\n|rNo computer CmdSet were found on this object.|n"
            self.msg(string)
            return
        elif num == 1:
            string += "\nThe computer CmdSet has been found on this object."
        else:
            string += "\n|rWARNING|n: {} computer CmdSets were found on this object.".format(num)

        # Current screen
        screen = computer.screen
        if screen is None:
            string += "\n  |rThe current screen couldn't be found.|n"
        else:
            string += "\n  |rCurrent screen {}".format(screen.path)
            if screen.app is None:
                string += " (no app)."
            else:
                string += " ({} app, {} folder).".format(screen.app.app_name, screen.app.folder)

            # Display the current commands
            cmd_names = [cmd.key for cmd in computer.commands if not cmd.key.startswith("_")]
            cmd_names.sort()
            string += "\n  Available commands: {}".format(", ".join([name for name in cmd_names]))
        self.msg(string)
