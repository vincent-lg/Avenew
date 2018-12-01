# -*- coding: utf-8 -*-

"""
Commands to manipualte objects.
"""

from collections import defaultdict
import re
from textwrap import wrap

from evennia.utils.utils import crop, inherits_from

from commands.command import Command
from logic.object.sets import ObjectSet

## Constants
CATEGORY = "Manipulation des objets"
RE_D = re.compile(r"^\d+$")


class CmdGet(Command):
    """
    Ramasse quelque chose.

    Syntaxe :
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

    Voir aussi : drop, wear, remove, hold, empty.

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
        from_obj_contents = [content for obj in from_objs for content in obj.contents]
        objs = self.caller.search(obj_text, quiet=True, candidates=from_obj_contents)
        if objs:
            # Alter the list depending on quantity
            if quantity == 0:
                quantity = 1
            objs = objs[:quantity]
        else:
            self.msg("|rVous ne voyez pas cela : {}.|n".format(obj_text))
            return

        # Try to find the into objects
        into_objs = None
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True)
            if not into_objs:
                self.msg("|rVous ne voyez pas cela : {}.|n".format(into_text))
                return

        # Try to put the objects in the caller
        can_get = self.caller.equipment.can_get(objs, filter=into_objs)
        if can_get:
            # Messages to display
            ot_kwargs = {"char": self.caller}
            objs = can_get.objects()
            my_msg = "Vous ramassez "
            my_msg += objs.wrapped_names(self.caller)
            ot_msg = "{char} ramasse {objs}"
            ot_kwargs["objs"] = objs
            if from_text:
                from_objs = ObjectSet(from_objs)
                my_msg += " depuis " + from_objs.wrapped_names(self.caller)
                ot_msg += " depuis {from_objs}"
                ot_kwargs["from_objs"] = from_objs
            if into_text:
                my_msg += ", dans "
                my_msg += ObjectSet(into_objs).wrapped_names(self.caller)
            my_msg += "."
            ot_msg += "."
            self.msg(my_msg)
            self.caller.location.msg_contents(ot_msg, exclude=[self.caller], mapping=ot_kwargs)
            self.caller.equipment.get(can_get)
        else:
            self.msg("|rOn dirait que vous ne pouvez pas ramasser cela.|n")


class CmdDrop(Command):
    """
    Pose quelque chose.

    Syntaxe :
      drop [quantité] <nom de l'objet> [from <conteneur>] [into <conteneur>]

    Pose des objets sur le sol ou ailleurs. La syntaxe la plus simple de cette
    commande est de préciser le nom de l'objet à poser :
      |ydrop pomme|n

    Vous pouvez aussi poser plusieurs objets d'un coup :
      |ydrop 3 pommes|n

    Ou poser tous les objets de ce nom :
      |ydrop * pommes|n

    Par défaut, les objets que vous voulez poser seront cherchés dans votre
    inventaire, c'est-à-dire, tous les conteneurs que vous portez actuellement sur
    vous. Il n'est pas nécessaire de préciser l'origine des objets à poser : en
    suivant le même exemple, si les pommes que vous souhaitez poser peuvent se
    trouver dans votre inventaire, il n'est pas nécessaire d'indiquer leur
    conteneur spécifiquement. Parfois cependant, il est utile de préciser dans quel
    conteneur regarder en particulier pour trouver les objets indiqués. Pour ce
    faire, préciser le nom du conteneur après le mot-clé |yfrom|n :
      |ydrop 5 pommes from boîte en plastique|n

    Vous pouvez également placer ces objets, non pas sur le sol de la salle où
    vous vous trouvez, mais dans un conteneur spécifique, soit dans la salle (comme
    un coffre), soit sur vous. Cette syntaxe particulière est surtout utile pour
    placer des vêtements dans un tiroir par exemple, ou bien un pot dans un
    placard. Pour placer les objets dans un conteneur spécifique, utilisez
    le mot-clé |yinto|n suivi du nom du conteneur :
      |ydrop billet into coffre|n

    Vous pouvez mélanger toutes ces syntaxes dans une commande si besoin :
      |ydrop 5 pommes from panier into filet|n

    Voir aussi : get, wear, remove, hold, empty.

    """

    key = "drop"
    aliases = ["put", "poser", "mettre", "placer"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gQue voulez-vous poser ?|n")
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
            self.msg("|gPrécisez au moins le nom de l'objet à poser.|n")
            return

        # Try to find the from object (higher priority since we need it in the next search)
        if from_text:
            candidates = caller.equipment.all(only_visible=True)
            from_objs = self.caller.search(from_text, quiet=True, candidates=candidates)
            from_obj_contents = [content for obj in from_objs for content in obj.contents]
            if not from_obj_contents:
                self.msg("|rVous ne voyez pas cela : {}.|n".format(from_text))
                return
        else:
            from_obj_contents = caller.equipment.all(only_visible=True)

        # Try to find the object
        objs = self.caller.search(obj_text, quiet=True, candidates=from_obj_contents)
        if objs:
            # Alter the list depending on quantity
            if quantity == 0:
                quantity = 1
            objs = objs[:quantity]
        else:
            self.msg("|rVous ne voyez pas cela : {}.|n".format(obj_text))
            return

        # Try to find the into objects
        into_objs = []
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True)
            if not into_objs:
                self.msg("|rVous ne voyez pas cela : {}.|n".format(into_text))
                return

        # Try to put the objects in the containers
        can_drop = self.caller.equipment.can_drop(objs, filter=into_objs)
        if can_drop:
            # Messages to display
            ot_kwargs = {"char": self.caller}
            objs = can_drop.objects()
            my_msg = "Vous posez " + objs.wrapped_names(self.caller)
            ot_msg = "{char} pose {objs}"
            ot_kwargs["objs"] = objs
            if from_text:
                from_objs = ObjectSet(from_objs)
                my_msg += " depuis " + from_objs.wrapped_names(self.caller)
                ot_msg += " depuis {from_objs}"
                ot_kwargs["from_objs"] = from_objs
            if into_text:
                into_objs = ObjectSet(into_objs)
                my_msg += ", dans "
                my_msg += into_objs.wrapped_names(self.caller)
                ot_msg = "{char} place {objs} dans {into_objs}"
                ot_kwargs["into_objs"] = into_objs
            my_msg += "."
            ot_msg += "."
            self.msg(my_msg)
            self.caller.location.msg_contents(ot_msg, exclude=[self.caller], mapping=ot_kwargs)
            self.caller.equipment.drop(can_drop)
        else:
            self.msg("|rIl semble que vous ne puissiez pas poser cela|n")


class CmdUse(Command):

    """
    Use an object given in argument.

    Syntaxe :
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

    Cette commande affiche votre équipement, c'est-à-dire, ce que vous portez sur
    vous comme vêtement ou conteneur, y compris ce que vous tenez dans vos mains.
    Notez que vous verrez tout ce que vous portez grâce à cette commande : si vous
    portez des chaussettes dissimulées par vos chaussures, vous verrez autant vos
    chaussures que chaussettes, contrairement aux autres personnages qui vous
    regardent et ne verront que vos chaussures, ce qui est somme toute préférable.

    Voir aussi : inventory, get, drop, wear, remove, hold, empty.

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
    Affiche votre inventaire.

    Syntaxe :
      inventory [nom de l'objet]

    Cette commande affiche votre inventaire, c'est-à-dire, la liste des conteneurs
    que vous portez et ce qu'ils contiennent, si ils contiennent quelque chose. Si
    vous ne portez rien, en utilisant la commande |yget|n pour ramasser quelque
    chose, vous ramasserez cet objet avec l'une de vos mains. La plupart du temps,
    vous aurez des habits, certains avec des poches, peut-être des sacs ou autres,
    tous pouvant contenir quelques objets variant en poids et taille. Un conteneur
    peut contenir d'autres conteneurs également, vous pouvez donc porter un sac à
    dos qui contient un sac en plastique dans lequel se trouve des pommes. La
    commande |yinventory|n vous permet de voir, d'un coup d'un seul, ce que vous
    portez et leur contenu, si biien que vous verrez le sac à dos, contenant le sac
    en plastique, contenant les pommes dans cet exemple. Cette commande permet donc
    de garder une vue d'ensemble de ce que vous portez sans examiner tous vos
    conteneurs un par un.

    Si vous cherchez un objet, ou plusieurs objets du même nom, et souhaitez savoir
    où ils se trouvent, vous pouvez aussi préciser un argument en paramètre de
    cette commande. Ne seront alors listés que les objets dont le nom correspond à
    ce paramètre, ainsi que leur conteneur. En suivant le même exemple, si vous
    avez oublié où se trouvent vos pommes, vous pouvez entrer |yinventory pommes|n
    qui affichera alors les pommes que vous portez et le chemin y menant (vous
    pouvez très bien avoir plusieurs pommes éparpillées sur plusieurs conteneurs,
    ils seront tous affichés). Dans un sens, cette syntaxe permet de "fouiller" ses
    poches et différents conteneurs d'une façon simple et réaliste.

    N'oubliez pas cependant que la plupart du temps, pour manipuler vos objets,
    vous n'avez pas besoin de préciser le conteneur d'où ils viennent, tant que ce
    conteneur est sur vous. Suivant le même exemple des pommes contenus dans un sac
    plastique contenu dans un sac à dos que vous portez, si vous voulez manger une
    pomme, il vous suffit d'entrer |yeat pomme|n sans préciser son conteneur.

    Voir aussi : equipment, get, drop, wear, remove, hold, empty.

    """

    key = "inventory"
    aliases = ["i", "inventaire"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        only_show = None
        if self.args.strip():
            candidates = self.caller.equipment.all(only_visible=True, looker=self.caller)
            only_show = self.caller.search(self.args, candidates=candidates, quiet=True)
            if not only_show:
                self.msg("Vous ne portez pas cela.")
                return

        inventory = self.caller.equipment.format_inventory(only_show=only_show)
        self.msg(inventory)


class CmdWear(Command):
    """
    Équipe un objet que vous possédez dans votre inventaire.

    Syntaxe :
      wear <nom de l'objet>[, <partie du corps à équiper>]

    Cette comme vous permet de porter (équiper) un objet que vous possédez dans
    votre inventaire. Pour prendre un exemple simple, admettons que vous venez de
    ramasser une chemise : en utilisant la commande |yget|n, cette chemise ira soit
    dans l'une de vos mains, soit dans un conteneur que vous portez (comme un sac à
    dos). Pour porter cette chemise, utilisez la commande |ywear|n :
      |ywear chemise|n

    Parfois, un objet peut être équipé sur différentes parties du corps. Une
    chaussette, par exemple, peut aller sur un pied ou l'autre. Vous pouvez
    préciser le nom de la partie du corps à équiper dans ce cas, après une virgule :
      |ywear chaussette rose, pied droit|n

    Cette syntaxe n'est pas obligatoire si l'objet peut être porté à plusieurs
    emplacements, mais que vous ne précisez pas la partie du corps. La partie du
    corps la plus logique sera, dans ce cas, choisie automatiquement.
      |ywear chaussette rose|n

    Voir aussi : equipment, inventory, get, drop, remove, hold, empty.

    """

    key = "wear"
    aliases = ["porter", "équiper", "equiper"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        if "," in self.args:
            obj_name, body_part = self.args.rsplit(",", 1)
            obj_name = obj_name.strip()
            body_part = body_part.strip()
        else:
            obj_name = self.args.strip()
            body_part = ""

        # First, try to find the object to wear
        objs = self.caller.search(obj_name, quiet=True, candidates=self.caller.equipment.all(only_visible=True))
        # Filter, removing already-worn objects
        objs = [obj for obj in objs if self.caller.equipment.can_wear(obj)]

        if not objs:
            self.msg("|gVous ne voyez pas cela : {}.|n".format(obj_name))
            return

        obj = objs[0]

        # Check the body parts
        first_level = self.caller.equipment.first_level
        prefered_limbs = []
        if body_part:
            for limb in first_level.keys():
                if limb.name.startswith(body_part):
                    prefered_limbs.append(limb)

            if not prefered_limbs:
                self.msg("|gImpossible de trouver cette partie du corps : {}.|n".format(body_part))
                return

        if prefered_limbs:
            for limb in prefered_limbs:
                if self.caller.equipment.can_wear(obj, limb):
                    limb.msg_wear(doer=self.caller, obj=obj)
                    self.caller.equipment.wear(obj, limb)
                    return
            self.msg("|rVous ne pouvez porter {} nulle part.|n".format(obj.get_display_name(self.caller)))
            return

        # Choose the first match
        limb = self.caller.equipment.can_wear(obj)
        if limb:
            limb.msg_wear(doer=self.caller, obj=obj)
            self.caller.equipment.wear(obj, limb)
        else:
            self.msg("|rVous ne pouvez porter {} nulle part.|n".format(obj.get_display_name(self.caller)))


class CmdRemove(Command):
    """
    Déséquipe un objet.

    Syntaxe :
      remove <nom de l'objet [into <conteneur>]

    Déséquipe (cesse de porter) un objet que vous portez actuellement, c'est-à-dire,
    quelque chose de visible dans votre équipement (voir la commande |yequipment|n).
    Si vous équipez une chemise, par exemple, et voulez la retirer :
      |yremove chemise|n

    Vous pouvez également préciser un conteneur dans lequel placer cet objet une
    fois retiré. Par défaut, cette commande cherchera le conteneur cible sur vous
    (dans votre inventaire), mais vous pouvez l'aider à trouver un meilleur endroit
    où poser l'objet précédemment équipé. Utilisez le mot-clé |yinto|n suivi du nom
    du conteneur dans lequel placer l'objet retiré :
      |yremove chemise into sac à dos|n

    Voir aussi : get, drop, wear, hold, empty.

    """

    key = "remove"
    aliases = ["retirer"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gQue voulez-vous déséquiper ?|n")
            return

        # Extract into
        words = self.args.strip().split(" ")
        obj_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gPrécisez au moins le nom de l'objet à retirer.|n")
            return

        # Try to find the object
        objs = caller.search(obj_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
        if not objs:
            self.msg("|rVous ne voyez pas cela : {}.|n".format(obj_text))
            return
        obj = objs[0]

        # Try to find the into objects
        into_obj = None
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True)
            if not into_objs:
                self.msg("|rVous ne voyez pas cela : {}.|n".format(into_text))
                return
            into_obj = into_objs[0]

        can_remove = caller.equipment.can_remove(obj, container=into_obj)
        if can_remove:
            caller.equipment.remove(obj, can_remove)
            caller.msg("Vous retirez {obj}.".format(obj=obj.get_display_name(caller)))
            caller.location.msg_contents("{caller} retire {obj}.", mapping=dict(caller=caller, obj=obj), exclude=[caller])
        else:
            self.msg("|rVous ne pouvez déséquiper {}.|n".format(obj.get_display_name(self.caller)))


class CmdHold(Command):
    """
    Place un objet dans votre main.

    Syntaxe :
      hold <nom de l'objet>

    Cette commande permet de placer un objet dans l'une de vos mains, si l'un est
    libre. Si l'objet que vous préciser se trouve dans votre inventaire mais pas
    dans votre main, vous le prendrez directement à la main, admettant que vous
    ayiez une main de libre. Cette commande est utile pour saisir rapidement des
    armes et les utiliser, sans avoir à fouiller frénétiquement votre inventaire
    pour les trouver :
      |yhold matraque|n

    Voir aussi : get, drop, wear, remove, empty.

    """

    key = "hold"
    aliases = ["tenir"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gQue voulez-vous tenir ?|n")
            return

        # Try to find the object
        obj_text = self.args.strip()
        objs = caller.search(obj_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
        objs = [obj for obj in objs if not obj.tags.get(category="eq")]
        if not objs:
            self.msg("|rVous ne voyez pas cela : {}.|n".format(obj_text))
            return

        obj = objs[0]

        can_hold = caller.equipment.can_hold(obj)
        if can_hold:
            can_hold[0].msg_hold(doer=self.caller, obj=obj)
            caller.equipment.hold(obj, can_hold[0])
        else:
            self.msg("|rVous ne pouvez pas tenir {}.|n".format(obj.get_display_name(self.caller)))


class CmdEmpty(Command):

    """
    Vide un conteneur.

    Syntaxe :
      empty <conteneur> [into <autre conteneur>]

    Cette commande vous permet de vider un conteneur, comme un sac que vous portez.
    La syntaxe la plus simple de cette commande est de prçiser le nom du conteneur
    à vider sur le sol :
      |yempty sac à dos|n

    Le contenu du conteneur sera posé au sol, à vos pieds. Vous pouvez également
    préciser un second conteneur, dans lequel vider le premier. Pour ce faire,
    utilisez le mot-clé |yinto|n suivi du nom du second conteneur :
      |yempty sac à main into sac à dos|n

    Remarquez que le premier conteneur sera toujours à la même place dans votre
    inventaire : il sera simplement vidé de son contenu, il sera donc complètement
    vide si cette commande ne rencontre aucun obstacle infranchissable.

    Voir aussi : get, drop, hold, wear, remove.

    """

    key = "empty"
    aliases = ["dump", "vider"]
    locks = "cmd:all()"
    help_category = CATEGORY

    def func(self):
        """Implements the command."""
        caller = self.caller
        if not self.args.strip():
            self.msg("|gQue voulez-vous vider ?|n")
            return

        # Extract into
        words = self.args.strip().split(" ")
        obj_text = into_text = ""
        for i, word in reversed(list(enumerate(words))):
            if word.lower() == "into":
                into_text = " ".join(words[i + 1:])
                del words[i:]
        obj_text = " ".join(words)

        if not obj_text:
            self.msg("|gPrécisez au minimum un nom de conteneur à vider.|n")
            return

        # Try to find the object
        objs = caller.search(obj_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
        objs = [content for obj in objs for content in obj.contents]
        if not objs:
            self.msg("|rVous ne voyez pas cela : {}.|n".format(obj_text))
            return

        # Try to find the into objects
        into_objs = []
        if into_text:
            into_objs = self.caller.search(into_text, quiet=True, candidates=caller.equipment.all(only_visible=True))
            if not into_objs:
                self.msg("|rVous ne voyez pas cela : {}.|n".format(into_text))
                return

        # Try to put the objects in the containers
        can_drop = caller.equipment.can_drop(objs, filter=into_objs)
        if can_drop:
            # Messages to display
            ot_kwargs = {"char": self.caller}
            objs = can_drop.objects()
            my_msg = "You posez " + objs.wrapped_names(self.caller)
            ot_msg = "{char} pose {objs}"
            ot_kwargs["objs"] = objs
            if into_text:
                into_objs = ObjectSet(into_objs)
                my_msg += ", dans "
                my_msg += into_objs.wrapped_names(self.caller)
                ot_msg = "{char} place {objs} dans {into_objs}"
                ot_kwargs["into_objs"] = into_objs
            my_msg += "."
            ot_msg += "."
            self.msg(my_msg)
            self.caller.location.msg_contents(ot_msg, exclude=[self.caller], mapping=ot_kwargs)
            self.caller.equipment.drop(can_drop)
        else:
            self.msg("|rIl semble que vous ne puissiez vider ce conteneur.|n")
