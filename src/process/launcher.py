# Copyright (c) 2020-20201, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

"""The launcher process, should control portal and game."""

import argparse
import asyncio
from getpass import getpass

from process.base import Process

parser = argparse.ArgumentParser()
parser.set_defaults(action="help")
subparsers = parser.add_subparsers()
sub_start = subparsers.add_parser("start", help="start the game and portal processes")
sub_start.set_defaults(action="start")
sub_stop = subparsers.add_parser("stop", help="stop the game and portal processes")
sub_stop.set_defaults(action="stop")
sub_restart = subparsers.add_parser("restart", help="restart the game process")
sub_restart.set_defaults(action="restart")
sub_shell = subparsers.add_parser("shell", help="open a Python console")
sub_shell.set_defaults(action="shell")
sub_script = subparsers.add_parser("script", help="open a scripting console")
sub_script.set_defaults(action="script")
sub_test = subparsers.add_parser("test", help="run TalisMUD tests")
sub_test.set_defaults(action="test")
sub_cmd = subparsers.add_parser("command", help="examine TalisMUD commands")
sub_cmd.set_defaults(action="command")
sub_cmd.add_argument("filters", nargs="*",
        help="Optional filters (layers or commands))")
sub_web = subparsers.add_parser("web", help="show TalisMUD web routes")
sub_web.set_defaults(action="web")

class Launcher(Process):

    """
    Launcher process, running the launcher service.

    The launcher process should only have a connection to the CRUX server.
    This host service can be expected to be unavailable altogether.

    """

    name = "launcher"
    services = ("launcher", )

    def __init__(self):
        super().__init__()
        self.stream_handler.format_string = "{record.message}"
        self.window_task = None

    async def setup(self):
        """Called when services have all been started."""
        args = parser.parse_args()

        launcher = self.services["launcher"]
        if args.action == "start":
            started = await launcher.action_start()
            if started and not launcher.has_admin:
                print(
                        "There's no admin character on this game "
                        "yet.  It would be better to create one now."
                )
                username = input("Username to create: ")
                password = getpass("New account's password: ")
                email = input("New account's email (can be blank): ")
                success = await launcher.action_create_admin(username,
                        password, email)
                if success:
                    print("The new admin account and password were created.")
                else:
                    print(
                            "An error occurred while creating the "
                            "admin account/password.  Please check the logs."
                    )
        elif args.action == "stop":
            await launcher.action_stop()
        elif args.action == "restart":
            await launcher.action_restart()
        elif args.action == "shell":
            await launcher.action_shell()
        elif args.action == "script":
            await launcher.action_script()
        elif args.action == "test":
            self.run_command("behave features plugins/builder/features")
        elif args.action == "command":
            await launcher.action_command(args)
        elif args.action == "web":
            await launcher.action_web()
        else:
            parser.print_help()

        self.should_stop.set()

    async def cleanup(self):
        """Called when the process is about to be stopped."""
        if self.window_task:
            self.window_task.cancel()
