# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

from collections import defaultdict
import re
from textwrap import wrap

from evennia.utils.utils import crop, inherits_from, list_to_string

from commands.command import Command

## Constants
CATEGORY = "Manipulation des objets"
RE_D = re.compile(r"^\d+$")


class CmdGet(Command):
    """
    Ramasse quelque chose.

    Usage:
      get [quantité] <nom de l'objet> [from <conteneur>] [into <conteneur>]

    Ramasse un ou plusieurs objets. La syntaxe la plus simple de cette commande
    est de préciser tout simplement le nom d'un objet se trouvant sur le sol
    pour le ramasser :
      |yget pomme|n

    Vous pouvez aussi ramasser plusieurs objets d'un coup :
      |yget 3 pommes|n

    Ou ramasser tous les objets de ce nom :
      |yget * pommes|n

    Par défaut, les objets que vous ramassez seront placés dans votre inventaire,
    défini par la liste de ce que vous portez sur vous, pouvant contenir l'objet en
    question. Si vous portez une paire de jeans par exemple, vous possédez
    probablement des poches, même si elles ne sont pas trop grandes. Si vous n'avez
    plus de place dans vos vêtements ou conteneurs, vous essayerez de prendre
    autant que possible avec vos mains, si ce que vous essayez de prendre n'est pas
    trop lourd. Vous pouvez aussi préciser dans quel conteneur placer les objets
    que vous venez de ramasser :
      |yget 5 pommes into sac en papier|n

    Vous pouvez également récupérer les objets depuis un conteneur, dans la
    salle (comme un coffre ou un meuble), ou bien sur vous. Pour ce faire,
    précisez le nom du conteneur après le mot-clé |yfrom|n :
      |yget billet from coffre|n

    Vous pouvez combiner ces différentes syntaxes si besoin :
      |yget 5 pommes from panier into filet|n

    Voir aussi : drop, hold, put, wear, remove.

    """

    key = "get"
    aliases = ["prendre"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gQue voulez-vous ramasser ?|n")
            return

        # Extract the quantity, if specified
        quantity = 1
        words = self.args.strip().split(" ")
        if RE_D.search(words[0]):
            quantity = int(words.pop(0))
        elif words[0] == "*":
            quantity = None
            del words[0]

        # Extract from and into
        obj_text = from_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "from":
                from_text = " ".join(words[i + 1:])
                del words[i:]
            elif word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gVous devez préciser au moins un nom d'objet à ramasser.|n")
            return

        # Try to find the from object (higher priority since we need it in the next search)
        from_objs = [self.caller.location]
        if from_text:
            candidates = self.caller.location.contents + self.caller.equipment.all()
            from_objs = self.caller.search(from_text, quiet=True, candidates=candidates)
            if not from_objs:
                self.msg("|rVous ne voyez pas cela : {}.|n".format(from_text))
                return

        # Try to find the object
        from_objs = [content for obj in from_objs for content in obj.contents]
        objs = self.caller.search(obj_text, quiet=True, candidates=from_objs)
        if objs:
            # Alter the list depending on quantity
            if quantity == 0:
                quantity = 1
            objs = objs[:quantity]
        else:
            self.msg("|rVous ne voyez pas cela : {}.|n".format(obj_text))
            return

        # Try to put the objects in the caller
        can_get = self.caller.equipment.can_get(objs)
        if can_get:
            self.caller.equipment.get(can_get)
            self.msg("Vous ramassez {}.".format(list_to_string(can_get.objects().names(self.caller), endsep="et")))
        else:
            self.msg("|rOn dirait que vous ne pouvez pas ramasser cela.|n")


class CmdUse(Command):

    """
    Use an object given in argument.

    Usage:
        use <object name>

    This command allows you to use an object with an obvious usage, like a phone
    or computer.  More specific commands are available for more specific actions.
    To use a phone that you have near at hand, for instance, just enter
    |huse|n followed by the name of the phone to use.

    Example:
        use computer

    """

    key = "use"
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        # Search for this object
        obj = self.caller.search(self.args)
        if not obj:
            return

        # First, check that what is being used isn't a character
        if inherits_from(obj, "typeclasses.characters.Character"):
            self.msg("Hmm, il faudrait peut-être demander la permission avant d'essayer de faire cela !")
            return

        # It needs to have a type handler anyway
        types = []
        if hasattr(obj, "types"):
            types = obj.types.can("use")

        if not types:
            self.msg("Que voulez-vous faire avec {} ?".format(obj.get_display_name(self.caller)))
            return

        types[0].use(self.caller)


class CmdAnswer(Command):

    """
    Answer to the most recent notification you have received.

    If you have a phone or computer and it receives notifications (like a
    new message), you can use the |yanswer|n command to directly open
    this notification and answer to it.  Obviously, the most common use case is when
    somebody calls you.  You will then hear the phone ring and can answer to it by
    entering |yanswer|n.

    If you have more than one devices, you can specify part of the name of the device
    as an argument, to choose only the most recent notification from this device.
    For example:
      |yanswer orange phone|n

    """

    key = "answer"
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        candidates = self.caller.contents + self.caller.location.contents
        notifications = []
        if self.args.strip():
            # Filter based on the object's name
            objs = self.caller.search(self.args.strip(), candidates=candidates, quiet=True)
            if objs:
                obj = objs[0]
                if not hasattr(obj, "types"):
                    self.msg("|r{} isn't a phone or computer with notifications.|n".format(obj.get_display_name(self.caller)))
                    return

                for type in obj.types:
                    if hasattr(type, "notifications"):
                        notifications.extend(type.notifications.all())
            else:
                self.msg("|rCan't find that:|n {}".format(self.args.strip()))
                return

        else:
            for obj in candidates:
                if not hasattr(obj, "types"):
                    continue

                for type in obj.types:
                    if hasattr(type, "notifications"):
                        notifications.extend(type.notifications.all())

        if not notifications:
            self.msg("It seems like you have no unread notification on any of your devices.")
            return
        notification = notifications[-1]

        # Try to see if the device can be used
        obj = notification.obj
        if not obj.types.can("use"):
            self.msg("Vous ne pouvez adresser cette notification sur {}.".format(obj.get_display_name(self.caller)))
            return

        notification.address(self.caller)


class CmdEquipment(Command):
    """
    Affiche votre équipement.

    Syntaxe :
      equipment

    Alias :
      eq, équipement

    Cette commande affiche votre équipement, c'est-à-dire, ce que vous portez sur
    vous comme vêtement ou conteneur, y compris ce que vous tenez dans vos mains.
    Notez que vous verrez tout ce que vous portez grâce à cette commande : si vous
    portez des chaussettes dissimulées par vos chaussures, vous verrez autant vos
    chaussures que chaussettes, contrairement aux autres personnages qui vous
    regardent et ne verront que vos chaussures, ce qui est somme toute préférable.

    Voir aussi : inventory, get, drop, wear, remove, empty, hold.

    """

    key = "equipment"
    aliases = ["eq", "équipement"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        self.msg(self.caller.equipment.format_equipment(looker=self.caller, show_covered=True))


class CmdInventory(Command):
    """
    Display your inventory.

    Usage:
      inventory [object name]

    Aliases:
      i

    This command displays your inventory, that is, the list of what you are wearing
    and what they contain, if they contain anything.  Usually, when you pick up
    something, it will end up in one of your hands.  However, if you have some
    pocket or a backpack or similar, what you pick up will probably end up in there,
    assuming there is room.  A container can contain other containers, too, so that
    you can have a backpack containing a plastic bag containing apples.  In this
    case, when you type |yinventory|n, you will see your backpack, inside of it the
    plastic bag, and inside of it your apples.  This command is useful to list
    everything you are carrying, even if it's hidden in various containers.

    You can also specify an object name to filter based on this name.  This allows
    to use |yinventory|n as a request: find where are my apples.  Following the same
    example, you could use |yinventory apples|n and it will only display your apples
    and where they are, not displaying you the rest of your inventory.  Notice that
    containers that contain your apples are still displayed for clarity.  This will
    help you retrieve something you have lost, something you know you are carrying but
    can't remember where.  In a way, it's a bit like patting your pockets and
    looking into all your bags to find something, but it will be much quicker.

    Remember that you do not need to specify the containers to use your objcts:
    following the same example, of your backpack containing a plastic bag containg
    your apples, if you want to eat one, you just need to enter |yeat apple|n.
    The system will find them automatically, no need to get them manually from the
    plastic bag.

    See also: equipment, get, drop, wear, remove, empty, hold.

    """

    key = "inventory"
    aliases = ["i"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        only_show = None
        if self.args.strip():
            candidates = self.caller.equipment.all(only_visible=True, looker=self.caller)
            only_show = self.caller.search(self.args, candidates=candidates, quiet=True)
            if not only_show:
                self.msg("You don't carry that.")
                return

        inventory = self.caller.equipment.format_inventory(only_show=only_show)
        self.msg(inventory)
