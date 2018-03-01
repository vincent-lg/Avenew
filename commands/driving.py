# -*- coding: utf-8 -*-

"""
Driving command set and commands.
"""

from evennia import default_cmds
from evennia.utils.utils import inherits_from

from commands.command import Command
from logic.geo import distance_between, get_direction, NAME_DIRECTIONS
from typeclasses.vehicles import Crossroad, log

# Constants
CATEGORY = "Conduite"

# Commands
class CmdDrive(Command):

    """
    Commence ou arrête de conduire un véhicule.

    Usage :
        drive

    Cette commande est utilisé pour commencer à conduire un véhicule, si vous
    vous trouvez dans la cabine et que personne d'autre ne tient le volant.
    Vous pouvez également l'utiliser pour cesser de conduire si le véhicule
    est arrêté. Si le véhicule est toujours sur la chaussée, cette commande
    vous permet de relâcher le volant et le véhicule s'arrêtera au milieu
    de la route, ce qui n'est pas nécessairement le plus sûr. Il est préférable
    d'utiliser la commande |ypark|n pour essayer de se garer sur le trottoir
    avant de relâcher le volant (|ydrive|n) et quitter le véhicule (|yleave|n).

    Pendant que vous conduisez, vous pouvez utiliser les commandes |yspeed|n
    pour modifier la vitesse, |yturn|n pour tourner (des alias existent
    pour le faire automatiquement) et |ymode|n pour changer de mode de
    conduite. Lisez l'aide de ces commandes pour plus d'informations ou
    bien, quand il sera écrit, le fichier d'aide |yconduire|n.

    """

    key = "drive"
    aliases = ["conduire"]
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("|rIl semble que vous ne soyez pas dans un véhicule.|n")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg("|rÊtes-vous bien dans un véhicule ? Difficile à dire...|n")
            return

        # We can only control the steering wheel from the front seat
        if room is not vehicle.contents[0]:
            self.msg("|rVous n'êtes pas dans la cabine pour conduire {}|n.".format(
                    vehicle.key))
            return

        # Are we already driving this vehicle
        if vehicle.db.driver is self.caller:
            vehicle.db.driver = None
            self.msg("Vous relâchez le volant.")
            room.msg_contents("{driver} relâche le volant.",
                    exclude=[self.caller], mapping=dict(driver=self.caller))
            self.caller.cmdset.remove("commands.driving.DrivingCmdSet")
            return

        # Or someone else could be riving
        if vehicle.db.driver:
            self.msg("Quelqu'un d'autre est au volant.")
            return

        # All is good, allow 'self.caller' to drive
        vehicle.db.driver = self.caller
        self.msg("Vous saisissez le volant et placez vos pieds sur les pédales.")
        room.msg_contents("{driver} saisie le volant et place ses pieds sur les pédales.", exclude=[self.caller],
                mapping=dict(driver=self.caller))

        # If the vehicle is in a room, leave it.
        if vehicle.location is not None:
            vehicle.location = None
            vehicle.msg_contents("Le moteur de {vehicle} commence à tourner.",
                    mapping=dict(vehicle=vehicle))

        self.caller.cmdset.add("commands.driving.DrivingCmdSet",
                permanent=True)


class CmdPark(Command):

    """
    Gare le véhicule que vous conduisez.

    Usage :
        park [direction]

    Cette commande permet de garer le véhicule que vous conduisez actuellement.
    Pour vous garer, le véhicule devra avoir une vitesse assez basse.
    Vous ne pourrez garer votre véhicule à n'importe quel endroit. Commencez
    par utiliser la commande |yspeed|n pour ralentir. Utilisez la commande
    |ypark|n pour vous garer puis la commande |ydrive|n pour relâcher le
    volant. Enfin, utilisez la commande |yleave|n pour quitter le véhicule.

    Si vous ne précisez aucun argument à la commande |ypark|n, vous
    essayerez de vous garer sur le côté droit de la route. La direction
    dépendra donc de là où vous vous trouvez et le déplacement du véhiculle.
    Vous pouvez aussi préciser la direction dans laquelle vous souhaitez
    vous garer, comme |ypark nord|n ou |ypark se|n.

    """

    key = "park"
    aliases = ["garer"]
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("|rIl semble que vous ne soyez pas dans un véhicule.|n")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg("|rÊtes-vous réellement dans un véhicule ? Difficile à dire...|n")
            return

        # Make sure we are currently driving
        if vehicle.db.driver is not self.caller:
            self.msg("|gVous ne conduisez pas {}.|n".format(vehicle.key))
            return

        # Check the speed
        if vehicle.db.speed > 10:
            self.msg("|gVous allez toujours trop vite pour pouvoir vous garer.|n")
            return

        # Get both sides of the current coordinate
        x, y, z = vehicle.db.coords

        # The Z coordinate could be invalid at this point, if there's a slope.
        previous = vehicle.db.previous_crossroad
        direction = vehicle.db.direction
        distance = distance_between(int(round(x)), int(round(y)), 0,
                previous.x, previous.y, 0)

        if (x, y) != (previous.x, previous.y):
            street = previous.db.exits[direction]

            try:
                assert distance > 0
                x, y, z = street["coordinates"][distance - 1]
            except AssertionError:
                x, y, z = previous.x, previous.y, previous.z
            except IndexError:
                log.warning("Cannot find the Z coordinate for vehicle " \
                        "#{}, trying to park at {} {}.".format(
                        vehicle.id, x, y))

                self.msg("|gIl semble que vous ne puissiez pas vous garer ici.|n")
                return
        else:
            self.msg("|gVous pourriez difficilement vous garer au milieu d'un carrefour.|n")
            return

        # Get the matching street
        log.debug("Parking #{} on {} {} {}".format(vehicle.id, x, y, z))
        closest, name, streets = Crossroad.get_street(x, y, z)
        if not streets:
            self.msg("|gVous ne trouez aucune place de libre pour vous garer.|n")
            return

        # Park left of right, according to the specified direction
        args = self.args if self.args.strip() else get_direction((direction + 2) % 8)["name"]
        infos = get_direction(args)
        if infos is None or infos["direction"] in (8, 9):
            self.msg("|rVous ne pouvez vous garer dans cette direction : {}.|n".format(self.args))
            return

        side_direction = infos["direction"]
        if (side_direction + 2) % 8 != direction and (side_direction - 2) % 8 != direction:
            self.msg("|r{} n'est pas une direction valide dans laquelle se garer.|n\n|gCheck the street direction.|n".format(infos["name"]))
            return

        spot = streets.get(side_direction)
        log.debug("  Parking #{} in {}, found {}".format(vehicle.id, infos["name"], spot))

        # If there's no room there
        if spot and spot["room"] is None:
            self.msg("|gVous ne trouez aucune place de libre pour vous garer.|n")
            return

        room = spot["room"]
        vehicle.location = room
        vehicle.stop()
        numbers = "-".join(str(n) for n in spot["numbers"])
        self.caller.msg("Vous garez {} sur le côté {sidewalk} de la route.".format(
                vehicle.key, sidewalk=infos["name"]))
        self.caller.location.msg_contents("{driver} gare {vehicle} sur le côté {sidewalk} de la route.",
                exclude=[self.caller], mapping=dict(driver=self.caller,
                vehicle=vehicle, sidewalk=infos["name"]))
        vehicle.msg_contents("{vehicle} s'arrête devant {numbers} {street}",
                mapping=dict(vehicle=vehicle, numbers=numbers, street=name))


class CmdSpeed(Command):

    """
    Change la vitesse désirée de votre véhicule, quand vous le conduisez.

    Usage :
        speed <kilomètres par heure>

    Cette commande peut être utilisée pour changer la vitesse du véhicule
    que voous conduisez. Vous n'avez pas besoin de l'entrer systématiquement
    pour accélérer ou freiner à chaque croisement, feu de circulation ou
    autre. Cette commande permet de modifier la vitesse désirée et vous
    ralentirez tout seul à l'approche de carrefours ou autre, pour accélérer
    de nouveau après. Il s'agit plus de modifier votre vitesse de croisière
    maximale. Si votre véhicule s'arrête pour une raison ou une autre, et
    accélère de nouveau après, vous accélérerez jusqu'à atteindre de nouveau
    votre vitesse de croisière, si d'autres obstacles ne se présentent pas.
    Cette vitesse est également influencée par votre mode de conduite : par
    défaut, vous conduisez en mode normal, ralentissant progressivement avant
    chaque carrefour ou virage. Vous pouvez changer ce mode pour avoir une
    conduite plus rapide et agressive. Si changer de mode de conduite peut
    vous permettre de gagner en vitesse, cela ne va pas sans risques : ignorer
    les feux de circulation, par exemple, pourrait très bien mener à un
    accident au prochain carrefour. Tout dépend de votre rapidité et talent de
    conducteur. Pour plus d'informations, lisez l'aide de la commande |ymode|n.

    Pour modifier votre vitesse désirée sans modifier votre mode de conduite,
    utilisez donc la commande |yspeed|n suivie de la vitesse, en kilomètres
    par heure.

    Par exemple :
        |yspeed 25|n

    Si vous souhaitez ralentir pour vous garer, vous pouvez utiliser
    |yspeed 0|n pour décélérer progressivement. Une fois le véhicule
    arrêté ou suffisamment ralenti, utilisez la commande |ypark|n pour
    vous garer.

    """

    key = "speed"
    aliases = ["vitesse", "vit"]
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("|rIl semble que vous ne soyez pas dans un véhicule.|n")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg("|rÊtes-vous réellement dans un véhicule ? Difficile à dire...|n")
            return

        # Make sure we are currently driving
        if vehicle.db.driver is not self.caller:
            self.msg("|gVous ne conduisez actuellement pas {}|n.".format(vehicle.key))
            return

        # If the vehicle is parked, un-park it
        if vehicle.location is not None:
            vehicle.location = None

        # Change the speed
        current = vehicle.db.speed
        desired = self.args.strip()

        try:
            desired = int(desired)
            assert desired >= 0
        except (ValueError, AssertionError):
            self.msg("|rDésolé, cela n'est pas une vitesse correcte.|n")
        else:
            vehicle.db.desired_speed = desired
            self.msg("Vous allez essayer de conduire à {} Km/h.".format(desired))

            # Display a message to the vehicle if the speed changes
            if current < desired:
                vehicle.msg_contents("{} commence à accélérer.".format(
                        vehicle.key))
            elif current > desired:
                vehicle.msg_contents("{} commence à ralentir.".format(
                        vehicle.key))


class CmdTurn(Command):

    """
    Prépare à tourner dans une direction.

    Si vous êtes en train de conduire un véhicule, vous pouvez utiliser
    cette commande pour vous préparer à tourner. Peu avant d'arriver à un
    carrefour, vous recevrez la liste des rues possibles, de façon assez
    semblable aux sorties disponibles dans une salle. Le véhicule ne sera pas au milieu du carrefour, vous
    aurez quelques secondes pour vous préparer à tourner. Si vous ne choisissez
    aucune direction, cependant, le véhicule s'arrêtera au milieu du
    carrefour et vous devrez tourner, puis accélérer manuellement de nouveau
    à l'aide de la commande |yspeed|n.

    Pour utiliser cette commande, vous pouvez soit préciser le nom complet
    de la direction, ou bien des alias. Utiliser des alias est bien plus
    rapide. Les alias étant les mêmes que pour vous déplacer à pied, les lier
    à des macros est aussi extrêmement simple. Voici les directions et syntaxes possibles :

    +------------|---------------------------------------------+-----------+
    | Directions | Commandes                                   |           |
    +------------|---------------------------------------------+-----------+
    | est        | |yturn est|n           | |yest|n            | |ye|n     |
    | sud-est    | |yturn sud-est|n       | |ysud-est|n        | |yse|n    |
    | sud        | |yturn sud|n           | |ysud|n            | |ys|n     |
    | sud-ouest  | |yturn sud-ouest|n     | |ysud-ouest|n      | |yso|n    |
    | ouest      | |yturn ouest|n         | |youest|n          | |yo|n     |
    | nord-ouest | |yturn nord-ouest|n    | |ynord-ouest|n     | |yno|n    |
    | nord       | |yturn nord|n          | |ynord|n           | |yn|n     |
    | nord-est   | |yturn nord-est|n      | |ynord-est|n       | |yne|n    |
    +------------||---------------------------------------------+

    En d'autres termes, un peu avant d'arriver à un carrefour ayant une
    rue disponible au nord, vous pouvez vous préparer à tourner en entrant
    |yturn nord|n ou |ynord|n ou simplement |yn|n.

    """

    key = "turn"
    aliases = ["tourner"] + list(NAME_DIRECTIONS.keys())
    help_category = CATEGORY

    def func(self):
        """Execute the command."""
        room = self.caller.location
        if not inherits_from(room, "typeclasses.rooms.VehicleRoom"):
            self.msg("|rIl semble que vous ne soyez pas dans un véhicule.|n")
            return

        vehicle = room.location

        # A VehicleRoom should be contained in a vehicle... but let's check
        if not inherits_from(vehicle, "typeclasses.vehicles.Vehicle"):
            self.msg("|rÊtes-fvous bien dans un véhicule ? Diffile à dire...")
            return

        # Make sure we are currently driving
        if vehicle.db.driver is not self.caller:
            self.msg("|gVous ne conduisez pas {} actuellement.|n".format(vehicle.key))
            return

        # Proceed to turn
        name = self.raw_string.strip().lower()
        if name.startswith("turn "):
            name = name[5:]
        elif name.startswith("tourner "):
            name = name[8:]

        direction = vehicle.db.direction
        infos = get_direction(name)
        if infos is None or infos["direction"] in (8, 9):
            self.msg("|gLa direction que vous avez précisée est inconnue.|n")
            return

        vehicle.db.expected_direction = infos["direction"]
        self.msg("Vous vous préparer à tourner vers {} au prochain carrefour.".format(infos["name"]))


class DrivingCmdSet(default_cmds.CharacterCmdSet):

    """
    Driving command set.

    This command set contains additional commands that are active
    when one drives a vehicle.  These commands aren't automatically
    active when one climbs into a vehicle, the user should use the
    'drive' command.  Doing so will give him/her additional commands,
    like control of the speed, the direction and basic information
    on the vehicle he/she is driving, like a constant glimpse of the
    control panel.  The user should use 'drive' again to release the
    steering wheel, something that shouldn't be done when the car
    is still rolling.

    """

    key = "driving"
    priority = 102

    def at_cmdset_creation(self):
        """Populates the cmdset with commands."""
        self.add(CmdPark())
        self.add(CmdSpeed())
        self.add(CmdTurn())
