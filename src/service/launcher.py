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

"""Launcher service."""

import asyncio
from importlib import import_module
import sys

from async_timeout import timeout as async_timeout
from enum import Enum, Flag, auto

from beautifultable import BeautifulTable

from service.base import BaseService

class MUDOp(Flag):

    """Cumulative MUD operations."""

    OFFLINE = 0
    PORTAL_ONLINE = auto()
    GAME_ONLINE = auto()
    STOPPING = auto()
    STARTING = auto()
    RELOADING = auto()
    NEED_ADMIN = auto()


class MUDStatus(Enum):

    """Mud status."""

    OFFLINE = 0
    PORTAL_ONLINE = 1
    ALL_ONLINE = 2


class Service(BaseService):

    """Launcher main service."""

    name = "launcher"
    sub_services = ("host", )

    async def init(self):
        """
        Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        self.has_admin = True
        self.operations = MUDOp.OFFLINE
        self.status = MUDStatus.OFFLINE

    async def setup(self):
        """Set the game up."""
        self.services["host"].connect_on_startup = False

    async def cleanup(self):
        """Clean the service up before shutting down."""
        pass

    async def error_read(self):
        """Cannot read from CRUX anymore, prepare to shut down."""
        pass

    async def check_status(self):
        """Check the MUD status."""
        if MUDOp.NEED_ADMIN in self.operations:
            need_admin = True
        else:
            need_admin = False

        host = self.services["host"]
        max_attempts = host.max_attempts
        timeout = host.timeout
        host.max_attempts = 2
        host.timeout = 0.2
        await host.build_SSL()
        await host.connect_to_CRUX()

        if not host.connected:
            self.operations = MUDOp.OFFLINE
            self.status = MUDStatus.OFFLINE
            host.max_attempts = max_attempts
            host.timeout = timeout
            return

        # Otherwise, check that the game is also running
        self.operations = MUDOp.PORTAL_ONLINE
        self.status = MUDStatus.PORTAL_ONLINE
        await host.send_cmd(host.writer, "what_game_id")

        # Wait for the reply
        success, args = await host.wait_for_cmd(host.reader, "game_id",
                timeout=5)
        if not success:
            host.max_attempts = max_attempts
            host.timeout = timeout
            return False

        host.max_attempts = max_attempts
        host.timeout = timeout
        if args.get("game_id"):
            self.operations = MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE
            if need_admin:
                self.operations |= MUDOp.NEED_ADMIN

            self.status = MUDStatus.ALL_ONLINE

    # Command handlers
    async def handle_registered_game(self, reader, game_id, sessions, **kwargs):
        """The game service has been registered by CRUX."""
        pass

    async def handle_game_id(self, reader, game_id):
        """A game ID has been sent by the portal, do nothing."""
        pass

    async def handle_game_stopped(self, reader):
        """The game service has been registered by CRUX."""
        pass

    async def handle_created_admin(self, reader, success: bool):
        """
        When the portal receives 'created_admin', do nothing.

        This response is expected from the 'create_admin' handler.
        Intercepting this response while 'create_admin' hasn't been
        sent isn't of much use.

        """
        pass

    async def handle_result(self, reader, **kwargs):
        """When the launcher receives 'result', do nothing."""
        pass

    async def handle_cannot_start_game(self, reader, error):
        """Cannot start the game."""
        self.logger.error(error)
        sys.exit(1)

    # User actions
    async def action_start(self) -> bool:
        """
        Start the game.

        Return whether the game was correctly started.

        Order of operations:
            1.  Connect to CRUX.  It should not work, since the portal
                shouldn't be running.  If it works, however, skip to step 4.
            2.  Launch the `poral` process.  This should also create a
                CRUX server.
            3.  Attempt to connect to CRUX again.  This time it should work,
                possibly after some retries.  If it doesn't, the start
                process is broken, report and stop.
            4.  Start the `game` process.  The game will attempt to
                connect to the portal and send a command to it to register.
            5.  On receiving the 'register_game' command, the portal will
                check that no other game has been registered, assign an
                ID for clarity to it, send the 'registered_game' command
                with the new game ID to all hosts.  This includes the
                launcher at this point.
            6.  Wait for the `registered_game` command to be issued.  If it
                is, report success to the user.

        """
        # 1. Connect to CRUX.  Failure is expected.
        host = self.services["host"]
        host.max_attempts = 2
        host.timeout = 0.2
        await host.build_SSL()
        await host.connect_to_CRUX()

        if not host.connected:
            # 2. 'host' is not connected.  Start the portal.
            self.operations = MUDOp.OFFLINE
            self.status = MUDStatus.OFFLINE
            self.logger.info("Starting the portal ...")
            self.process.start_process("portal")
            self.operations = MUDOp.STARTING

            # 3. Try to connect to CRUX again.  This time if it fails, it's an error.
            host.max_attempts = 20
            host.timeout = 1
            await host.build_SSL()
            await host.connect_to_CRUX()

            if not host.connected:
                self.operations = MUDOp.OFFLINE
                self.status = MUDStatus.OFFLINE
                self.logger.error(
                        "The portal should have been started. For some "
                        "reason, it hasn't. Check the logs in "
                        "logs/portal.log for errors."
                )
                return False

            # The portal has started
            self.operations = MUDOp.STARTING | MUDOp.PORTAL_ONLINE
            self.status = MUDStatus.PORTAL_ONLINE
            self.logger.info("... portal started.")
        else:
            self.operations = MUDOp.STARTING | MUDOp.PORTAL_ONLINE
            self.status = MUDStatus.PORTAL_ONLINE
            self.logger.info("The portal is already running.")

        # 4. Start the game process
        self.logger.info("Starting the game ...")
        await host.send_cmd(host.writer, "start_game")

        # 5. The game process will send a 'register_game' command to CRUX.
        # 6. ... so wait for the 'registered_game' command to be received.
        success, args = await host.wait_for_cmd(host.reader, "registered_game",
                timeout=10)
        if success:
            self.operations = MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE
            self.status = MUDStatus.ALL_ONLINE
            game_id = args.get("game_id", "UNKNOWN")
            pid = args.get("pid", "UNKNOWN")
            self.has_admin = has_admin = args.get("has_admin", False)
            if not has_admin:
                self.operations |= MUDOp.NEED_ADMIN
            self.logger.info(f"... game started (id={game_id}, pid={pid}, has_admin={has_admin}).")
            return True
        else:
            self.operations = MUDOp.PORTAL_ONLINE
            self.status = MUDStatus.PORTAL_ONLINE
            self.logger.error(
                    "The game hasn't started. See logs/game.log "
                    "for more information."
            )
            return False

    async def action_stop(self):
        """
        Stop the game and portal process.

        Order of operations:
            1.  Connect to CRUX.  It should succeed.
            2.  Send the 'stop_portal' command to CRUX.
            3.  CRUX will send a 'stop_game' command to the game host.
            4.  Wait for CRUX to shut down.

        """
        # 1. Connect to CRUX.  Success is expected.
        host = self.services["host"]
        if not host.connected:
            host.max_attempts = 10
            host.timeout = 2
            await host.build_SSL()
            await host.connect_to_CRUX()

            if not host.connected:
                self.operations = MUDOp.OFFLINE
                self.status = MUDStatus.OFFLINE
                self.logger.warning("The portal seems to be off, the game isn't running.")
                return

        # 3. Send the 'stop_portal' command
        self.operations = (
            MUDOp.STOPPING | MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE
        )
        self.status = MUDStatus.ALL_ONLINE
        self.logger.info("Portal and game stopping ...")
        await host.send_cmd(host.writer, "stop_portal")

        # 4. Wait for any command to be received.  None should.
        while (args := await host.wait_for_cmd(host.reader, "*", timeout=0.1)):
            success, args = args
            if not success:
                break

        if host.connected:
            self.operations = MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE
            self.status = MUDStatus.ALL_ONLINE
            self.logger.error("The portal is still running, although asked to shudown.")
        else:
            self.operations = MUDOp.OFFLINE
            self.status = MUDStatus.OFFLINE
            self.logger.info("... portal and game stopped.")

    async def action_restart(self):
        """
        Restart the game, maintains the portal.

        Order of operations:
            1.  Connect to CRUX.  It should succeed.
            2.  Send the 'stop_game' command to CRUX.
            3.  CRUX will send a 'restart_game' command to the game host.
            3.  Listen for the `stopped_game` command, that will
                be sent when the game has disconnected.
            4.  The portal will start the `game` process.  The game will
                attempt to connect to the portal and send a command to it
                to register.
            5.  On receiving the 'register_game' command, the portal will
                check that no other game has been registered, assign an
                ID for clarity to it, send the 'registered_game' command
                with the new game ID to all hosts.  This includes the
                launcher at this point.
            6.  Wait for the `registered_game` command to be issued.  If it
                is, report success to the user.

        """
        # 1. Connect to CRUX.  Success is expected.
        host = self.services["host"]
        host.max_attempts = 10
        host.timeout = 2
        await host.build_SSL()
        await host.connect_to_CRUX()

        if not host.connected:
            self.operations = MUDOp.OFFLINE
            self.status = MUDStatus.OFFLINE
            self.logger.warning("The portal seems to be off, the game isn't running.")
            return

        # 2. Send the 'restart_game' command
        self.logger.info("Game stopping ...")
        self.operations = (MUDOp.RELOADING |
                MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE)
        self.status = MUDStatus.ALL_ONLINE
        await host.send_cmd(host.writer, "restart_game", dict(announce=True))

        # 3. The portal should stop the game process...
        # ... and restart it.
        # 4. Listen for the 'stopped_game' command.
        success, args = await host.wait_for_cmd(host.reader, "game_stopped",
                timeout=10)
        if not success:
            self.operations = MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE
            self.status = MUDStatus.ALL_ONLINE
            self.logger.warning("The game is still running.")
            return

        self.operations = MUDOp.RELOADING | MUDOp.PORTAL_ONLINE
        self.status = MUDStatus.PORTAL_ONLINE
        self.logger.info("... game stopped.")
        self.logger.info("Start game ...")
        # 5. The game process will send a 'register_game' command to CRUX.
        # 6. ... so wait for the 'registered_game' command to be received.
        success, args = await host.wait_for_cmd(host.reader, "registered_game",
                timeout=10)
        if success:
            self.operations = MUDOp.PORTAL_ONLINE | MUDOp.GAME_ONLINE
            self.status = MUDStatus.ALL_ONLINE
            game_id = args.get("game_id", "UNKNOWN")
            self.logger.info(f"... game started (id={game_id}).")
        else:
            self.operations = MUDOp.PORTAL_ONLINE
            self.status = MUDStatus.PORTAL_ONLINE
            self.logger.error(
                    "The game hasn't started. See logs/game.log "
                    "for more information."
            )

    async def action_create_admin(self, username: str,
            password: str, email: str = ""):
        """
        Send a 'create_admin' command to the game, to create a new admin.

        Args:
            reader (StreamReader): the reader for this command.
            username (str): the username to create.
            password (str): the plain text password to use.
            email (str, optional): the new account's email address.

        Response:
            The 'created_admin' command with the result.

        """
        host = self.services["host"]
        if host.writer:
            await host.send_cmd(host.writer, "create_admin",
                    dict(username=username, password=password, email=email))

        success, args = await host.wait_for_cmd(host.reader,
                "created_admin", timeout=60)
        return success

    async def action_shell(self):
        """
        Open a Python-like shell and send command to the portal.

        These commands are then sent to the game where they
        are interpreted.

        """
        host = self.services["host"]
        await self.check_status()
        init_started = self.status == MUDStatus.ALL_ONLINE
        if not init_started:
            await self.action_start()

        # In a loop, ask user input and send the Python command
        # to the portal, which will forward it to the game, which
        # will evaluate and answer in the same way.
        prompt = ">>> "
        while True:
            try:
                code = input(prompt)
            except KeyboardInterrupt:
                print()
                break

            await host.send_cmd(host.writer, "shell", dict(code=code))
            success, args = await host.wait_for_cmd(host.reader, "result")
            if success:
                prompt = args.get("prompt", "??? ")
                display = args.get("display", "")
                if display:
                    print(display.rstrip("\n"))

        # If the game wasn't started before executing code, stop it.
        if not init_started:
            await self.action_stop()

    async def action_script(self):
        """
        Open a scripting shell and send command to the portal.

        These commands are then sent to the game where they
        are interpreted.

        """
        host = self.services["host"]
        await self.check_status()
        init_started = self.status == MUDStatus.ALL_ONLINE
        if not init_started:
            await self.action_start()

        # In a loop, ask user input and send the scripting command
        # to the portal, which will forward it to the game, which
        # will evaluate and answer in the same way.
        prompt = ">>> "
        while True:
            try:
                code = input(prompt)
            except KeyboardInterrupt:
                print()
                break

            await host.send_cmd(host.writer, "scripting", dict(code=code))
            success, args = await host.wait_for_cmd(host.reader, "result")
            if success:
                prompt = args.get("prompt", "??? ")
                display = args.get("display", "")
                if display:
                    print(display.rstrip('\n'))

        # If the game wasn't started before executing code, stop it.
        if not init_started:
            await self.action_stop()

    async def action_command(self, args):
        """
        Examine TalisMUD commands.

        Note:
            This is done by importing the game commands.  The output
            might not align with the current game instance,
            if not reloaded.

        """
        filters = args.filters
        from command.layer import COMMANDS_BY_LAYERS, load_commands
        load_commands()

        if not filters:
            table = BeautifulTable()
            table.columns.header = ("Layer", "Number of commands", "Category")
            table.columns.header.alignment = BeautifulTable.ALIGN_LEFT
            table.columns.alignment["Layer"] = BeautifulTable.ALIGN_LEFT
            table.columns.alignment["Number of commands"] = BeautifulTable.ALIGN_RIGHT
            table.columns.alignment["Category"] = BeautifulTable.ALIGN_LEFT
            table.columns.padding_left['Layer'] = 0
            table.columns.padding_right['Category'] = 0
            table.set_style(BeautifulTable.STYLE_NONE)
            table.rows.separator = ""
            for layer, commands in COMMANDS_BY_LAYERS.items():
                categories = set(command.category
                        for command in commands.values())
                if len(categories) == 1:
                    category = categories.pop()
                else:
                    category = "{Multiple}"

                table.rows.append((layer, len(commands), category))
            print(table)
        elif len(filters) == 1 and '.' in filters[0]:
            # Try to debug a single command
            from command import Command
            pypath = filters[0]
            mod_path, cmd_name = pypath.rsplit(".", 1)
            print(f"Try to import this module: {mod_path!r}")
            module = import_module(mod_path)
            command = getattr(module, cmd_name, None)
            if command is None:
                print(f"{cmd_name} cannot be found in the {mod_path} module.")
                return

            # Check its type
            if isinstance(command, type) and command is not Command and issubclass(command, Command):
                print(f"{cmd_name} is a subclass of the Command class, as it should be.")
            else:
                print(f"{cmd_name} isn't a class inheriting from the Command class.")
                return

            # Prints some details
            name = command.name or "{UNSET}"
            category = command.category or "{UNSET}"
            layer = command.layer or "{UNSET}"
            aliases = command.alias or ("{No alias}", )
            aliases = aliases if isinstance(aliases, (tuple, list)) else (aliases, )
            aliases = ",".join(aliases)
            permissions = command.permissions or "{Everyone}"
            print(f"Name   : {name:<15} Category   : {category:<25} Layer: {layer}")
            print(f"Aliases: {aliases:<15} Permissions: {permissions:<25}")

            # Try to see if it has been replaced by another
            layer = COMMANDS_BY_LAYERS[command.layer]
            same_name = layer[command.name]
            if command is same_name:
                print("This command has properly been loaded into its layer.")
            else:
                print(f"Inside the {command.layer} command layer, another command has the name {command.name}.")
                print(f"Therefore, {same_name.__module__}.{same_name.__name__} replaces {pypath}.")
        else:
            commands = [command for commands in COMMANDS_BY_LAYERS.values()
                    for command in commands.values()
                    if command.layer in filters or command.name in filters or f"{command.__module__}.{command.__name__}" in filters]
            commands.sort(key=lambda cmd: (cmd.layer, cmd.name))
            table = BeautifulTable()
            table.columns.header = ("Layer", "Command", "Category", "Permissions", "Python path")
            table.columns.header.alignment = BeautifulTable.ALIGN_LEFT
            table.columns.alignment = BeautifulTable.ALIGN_LEFT
            table.columns.padding_left['Layer'] = 0
            table.columns.padding_right['Python path'] = 0
            table.set_style(BeautifulTable.STYLE_NONE)
            table.rows.separator = ""
            for cmd in commands:
                permissions = cmd.permissions
                permissions = permissions or "{Everyone}"
                table.rows.append((cmd.layer, cmd.name, cmd.category, permissions, f"{cmd.__module__}.{cmd.__name__}"))
            print(table)

    async def action_web(self):
        """Display web routes."""
        from web.base_template import load_base_templates
        from web.uri import URI
        load_base_templates()
        uris = URI.gather()
        uris = sorted(list(uris.values()), key=lambda uri: uri.uri)
        table = BeautifulTable()
        table.columns.header = ("Route", "Template", "Program", "Get", "Post",
                "Put", "Delete")
        table.columns.header.alignment = BeautifulTable.ALIGN_LEFT
        table.columns.alignment[0] = BeautifulTable.ALIGN_LEFT
        table.columns.alignment[-1] = BeautifulTable.ALIGN_RIGHT
        table.columns.alignment = BeautifulTable.ALIGN_LEFT
        table.columns.padding_left[0] = 0
        table.columns.padding_right[-1] = 0
        table.set_style(BeautifulTable.STYLE_NONE)
        for uri in uris:
            template = uri.page_path or "No"
            program = uri.program_path or "No"
            get = "Yes" if "get" in uri.methods else "No"
            post = "Yes" if "post" in uri.methods else "No"
            put = "Yes" if "put" in uri.methods else "No"
            delete = "Yes" if "delete" in uri.methods else "No"
            table.rows.append((uri.uri, template, program, get, post,
                    put, delete))

        print(table)
