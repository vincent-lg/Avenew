# -*- coding: utf-8 -*-

"""Package persistent, containing features to make things persistent.

The most notable usage is the persistent `delay`, a delay that will
still exist after a reload and execute as planned.  This is supposed
to be used instead of `utils.delay` in Avenew for persistent delays.

"""

from datetime import datetime, timedelta
from evennia import DefaultScript, ScriptDB, logger
from evennia.utils import utils
from evennia.utils.create import create_script
from evennia.utils.dbserialize import dbserialize

## Constants
SCRIPT = None

## Functions
def delay(seconds, callback, *args, **kwargs):
    """
    Schedule a persistent task to run in a given number of seconds.

    Args:
        seconds (int, float): the delay in seconds from now.
        callback (funciton): the callback to call.

    Note:
        Additional arguments (positional or keyword) can be passed
        to this function.  The signature of this function must be
        identical to `utils.delay`, and it's use should be similar,
        except that it will "remember" the task that haven't run in
        case of a reboot/reload.  Note, however, that due to this,
        not all arguments can be accepted.  The callback itself will
        need to be picklable (like a top-level function in a module).

    """
    # Make sure the script exist.  If not, start it
    global SCRIPT
    if SCRIPT is None:
        try:
            SCRIPT = ScriptDB.objects.get(db_key="persistent")
        except ScriptDB.DoesNotExist:
            SCRIPT = create_script("standalone.persistent.PersistentScript")

    # Create the delayed task
    now = datetime.now()
    delta = timedelta(seconds=seconds)

    # Choose a free task_id
    used_ids = SCRIPT.db.tasks.keys()
    task_id = 1
    while task_id in used_ids:
        task_id += 1

    # Check that callback, args and kwargs can be saved
    safe_callback = None
    safe_args = []
    safe_kwargs = {}

    try:
        dbserialize(callback)
    except (TypeError, AttributeError):
        raise ValueError("the specified callback {} cannot be pickled. " \
                "It must be a top-level function in a module.".format(callback))
    else:
        safe_callback = callback

    for arg in args:
        try:
            dbserialize(arg)
        except (TypeError, AttributeError):
            logger.log_err("The positional argument {} cannot be " \
                    "pickled and will not be present in the arguments " \
                    "fed to the callback {}".format(arg, callback))
        else:
            safe_args.append(arg)

    for key, value in kwargs.items():
        try:
            dbserialize(value)
        except (TypeError, AttributeError):
            logger.log_err("The {} keyword argument {} cannot be " \
                    "pickled and will not be present in the arguments " \
                    "fed to the callback {}".format(key, value, callback))
        else:
            safe_kwargs[key] = value

    SCRIPT.db.tasks[task_id] = (now + delta, safe_callback, safe_args,
            safe_kwargs)
    utils.delay(seconds, _complete_task, task_id)

## Script class
class PersistentScript(DefaultScript):

    """
    The persistent script keeping track of persistent tasks.

    This script is automatically created the first time
    `persistent.delay` is called.

    """

    def at_script_creation(self):
        """Hook called when the script is created."""
        self.key = "persistent"
        self.desc = "Persistent script"
        self.persistent = True

        # Persistent data to be stored
        self.db.tasks = {}

    def at_start(self):
        """Set up the persistent script and start tasks in `utils.delay`."""
        global SCRIPT
        now = datetime.now()
        for task_id, definition in tuple(self.db.tasks.items()):
            future, callback, args, kwargs = definition
            seconds = (future - now).total_seconds()
            if seconds < 0:
                seconds = 0

            utils.delay(seconds, _complete_task, task_id)

        SCRIPT = self

## Private functions
def _complete_task(task_id):
    """
    Mark the task in the persistent script as complete.

    Args:
        task_id (int): the task ID.

    Note:
        This function should be called automatically for individual tasks.

    """
    if task_id not in SCRIPT.db.tasks:
        logger.log_err("The task #{} was scheduled, but it cannot be " \
                "found".format(task_id))
        return

    delta, callback, args, kwargs = SCRIPT.db.tasks.pop(task_id)

    # Call the callback
    callback(*args, **kwargs)
