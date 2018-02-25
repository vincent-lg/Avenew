# -*- coding: utf-8 -*-

"""Module containing the event help strings for characters."""

CAN_DELETE = """
Le personnage peut-il être supprimé ?
Cet évènement est appelé avant la suppression d'un personnage. Vous pouvez utiliser `deny()`
dans cet évènement pour empêcher le personnage d'être supprimé. Si cet évènement n'est
pas interrompu avec `deny()`, l'évènement `delete` est appelé et le personnage est supprimé.

Variables disponibles dans cet évènement :
    personnage: le personnage connecté à cet évènement.
"""

CAN_MOVE = """
Le personnage peut-il se déplacer ?
Cet évènment est appelé avant que le personnage ne se déplace dans une nouvelle salle.
Vous pouvez utiliser la fonction `deny()` pour interdir le déplacement.

Variables disponibles dans cet évènement :
    destination : la salle de destination du personnage.
    origine : la salle courante du personnage.
    personnage : le personnage connecté à cet évènement.
"""

CAN_PART = """
Est-ce qu'un autre personnage peut quitter cette salle ?
Cet évè3nement est appelé avant qu'un autre personnage ne quitte la salle où le
personnage connecté à l'évènement se trouve. Utilisez cet évènement pour empêcher un
autre personnage de quitter la salle, si il n'a pas payé par exemple, ou si il veut
accéder à une salle protégée par un garde. Utilisez la fonction `deny()` pour empêcher
le déplacement.

Variables disponibles dans cet évènement :
    acteur : le personnage voulant quitter cette salle.
    personnage : le personnage connecté à cet évènement.
"""

CAN_SAY = """
Avant qu'un autre personnage ne puisse dire quelque chose dans la salle.
Cet évènement est appelé avant qu'un autre personnage ne puisse dire quelque chose
dans cette salle. Le quelque chose en question peut être modifié ou l'action peut être
annulée en utilisant la fonction `deny()`. Pour modifier le contenu du message,
modifier la variable `message` en lui donnant une chaîne de caractères.

Variables you can use in this event:
    acteur : le personnage voulant parler.
    message : le message que l'acteur veut dire dans cette salle.
    personnage : le personnage connecté à cet évènement.
"""

DELETE = """
Avant la suppression du personnage.
Cet évènement est appelé juste avant la suppression du personnage. Annuler la
suppression n'est pas possible à ce stade : si vous voulez annuler la suppression,
utilisez l'évènement `can_delete`.

Variables disponibles dans cet évènement :
    personnage : le personnage connecté à cet évènement.
"""

GREET = """
Un nouveau personnage arrive dans la salle.
Cet évènement est appelé quand un nouveau personnage vient d'arriver dans la salle.
Comme son nom l'indique, il est très utile pour permettre aux PNJ d'accueillir
d'autres PNJ ou bien des joueurs qui viennent leur rendre visite.

Variables disponibles dans cet évènement :
    acteur : le personnage arrivant dans la salle.
    personnage : le personnage connecté à cet évènement.
"""

MOVE = """
Le personnage vient de se déplacer dans une nouvelle salle.
Cet évènement est appelé quand le personnage vient de se déplacer dans une nouvelle
salle. Il est trop tard pour empêcher le déplacement à ce stade.

Variables disponibles dans cet évènement :
    destination : la salle dans laquelle le personnage se trouve à présent.
    origine : la salle de laquelle vient le personnage.
    personnage : le personnage connecté à cet évènement.
"""

PRE_TURN = """
Avant que le véhicule conduit n'arrive à un carrefour.
Cet évènement est appelé sur le personnage conduisant un véhicule, peu avant que le
véhicule ne doive tourner sur un carrefour. Cet évènement peut être utiliser pour
coder des PNJ devant conduire. Notez cependant que le comportement `driver` existe
explicitement pour permettre aux PNJ de savoir conduire. Cet évènement ne devrait
pas être utilisé pour donner l'abilité à un personnage de conduire.

Variables disponibles dans cet évènement :
    carrefour: le carrefour (Crossroad) sur lequel le véhicule arrive.
    personnage : le personnage connecté à cet évènement.
    vehicule : le véhicule conduit par le personnage.
"""

POST_TURN = """
Après que le véhicule conduit ait tourné à un carrefour.
Cet évènement est appelé sur le conducteur d'un véhicule, quand le véhicule vient de
tourner dans une nouvelle rue. Vous pouvez utiliser cet évènement pour créer des PNJ
avec des missions spécifiques en voiture.

Variables disponibles dans cet évènement :
    carrefour: le carrefour (Crossroad) derrière le véhicule.
    personnage : le personnage connecté à cet évènement.
    vehicule : le véhicule conduit par le personnage.
"""

PUPPETED = """
Quand ce personnage vient d'être contrôlé par un compte.
Cet évènement est appelé quand un compte vient de contrôler ce personnage. Cela peut
se produire quand un joueur se connecte et contrôle l'un des personnages de son
compte, ou bien quand un bâtisseur prend le contrôle d'un PNJ.

Variables disponibles dans cet évènement :
    personnage : le personnage connecté à cet évènement.
"""

SAY = """
Un autre personnage vient de dire quelque chose dans la salle.
Cet évènement est appelé quand un autre personnage vient de dire quelque chose dans
la salle. L'action ne peut être interrompuee à ce jmoment. En revanche, cet évènement
est idéal pour créer des mot-clés auxquels un personnage (comme un PNJ) pourra
réagir, pour créer un dialogue ou des déclencheurs d'action.
Pour utiliser cet évènement, vous devez préciser une liste de mot-clés en paramètres.
Le callback sera appelé seulement si l'un des mots prononcés par l'autre personnage
est contenu dans la liste des mot-clés spécifiés.
Par exemple, si vous voulez que ce personnage réagisse si un autre personnage dit
"menu" ou "manger", vous pourriez écrire :
    @call/add <personnage> say menu, manger

Variables disponibles dans cet évènement :
    acteur : le personnage qui vient de parler.
    message : le message parlé.
    personnage : le personnage connecté à cet évènement.
"""

TIME = """
Un évènement régulier à appeler à heure fixe.
Cet évènement est appelé à heures fixes de façon répétée. L'heure ou la date sont à
préciser en paramètre. Par exemple :
    @call/add ici 8:30
La ligne ci-dessous va créer un callback qui s'exécutera tous les jours in-game à 8
heures 30 précise. Vous pouvez préciser plusieurs unités de temps séparés par des deux
points, tirets ou espaces. Essayez de garder le format aussi réaliste que possible. Par
exemple :
    @call/add ici time 06-15 15:00
Le callback ci-dessus sera appelé tous les ans in-game, le 15 juin à 15 heures.
En variant les unités, vous pouvez créer des callbacks s'exécutant toutes les heures,
jours, mois ou années.

Variables disponibles dans cet évènement :
    personnage : le personnage connecté à cet évènement.
"""

UNPUPPETED = """
Quand le personnage est sur le point d'être dé-contrôlé par un compte.
Cet évènement est appelé quand un compte dé-contrôle ce personnage. Cela se produit
quand un joueur se déconnecte d'un personnage qu'il contrôlait, ou bien quand un
bâtisseur cesse de contrôler un PNJ.

Variables disponibles dans cet évènement :
    personnage : le personnage connecté à cet évènement.
"""

