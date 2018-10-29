# Batch-code file containing the standard help files
# Generate with: @batchcode public.help

#HEADER
from world.batch import get_help_entry

#CODE
get_help_entry("véhicle", """
    Dans Avenew One, vous pouvez conduire un véhicule en utilisant un ensemble de commandes
    décrites dans cette page d'aide. Bien que les véhicules puissent accéder à des zones
    inaccessibles, ils sont principalement utilisés pour gagner du temps. Les voitures,
    par exemple, offrent un raccourci pratique pour se déplacer dans la ville, bien que
    vous puissiez marcher. Les véhicules typiques seraient les voitures, camions, motos.
    Des véhicules plus atypiques sont encore à prévoir toutefois.

    Pour conduire un véhicule que vous possédez ou un véhicule public auquel vous avez
    accès, vous devez d’abord vous trouvez auprès du dit véhicule. Vous le verrez dans
    la description de la salle. Les véhicules sont regroupés par type et par marque afin de
    ne pas vous surcharger d'information, mais vous pouvez rechercher facilement un véhicule
    spécifique. Vous devez y monter en utilisant la commande |yenter|n. Vous devez
    préciser en paramètre le nom (ou une partie du nom) du véhicule dans lequel vous
    voulez monter. Vous pouvez également fournir la plaque d'immatriculation, pour
    éviter la confusion. Notez que le véhicule peut être verrouillé, auquel cas,
    vous devrez utiliser la commande |yunlock|n. Vous ne pourrez pas déverrouillez tous
    les véhicules dans un parking, vous aurez besoin des clés ou d’un autre moyen de
    déverrouiller ce véhicule. Les véhicules publics sont généralement
    déverrouillés, ce qui signifie que vous pouvez entrer dedans sans contrainte. D'autre
    part, cela signifie également que tout le monde peut faire la même chose,
    peut-être ne devriez-vous pas trop vous fier à ce moyen de transport.

    Une fois sur le siège avant du véhicule, vous devez utiliser la commande |ydrive|n
    pour saisir le volant. Il n'est pas possible de conduire si quelqu'un d'autre est
    déjà derrière le volant. Vous utiliserez la même commande pour relâcher le volant
    quand vous voulez arrêter de conduire. Si vous êtes garé et que vous utilisez la
    commande |ydrive|n, vous démarrerez le moteur et avancerez les quelques mètres nécessaires pour
    être dans la rue.

    Vous devez maintenant accélérer. Vous pouvez contrôler la vitesse en utilisant
    la commande |yspeed|n. Spécifiez votre vitesse désirée en kilomètres par heure.
    Notez que cela ressemble plus à votre vitesse de croisière maximale. Il ne sera
    pas nécessaire de freiner manuellement à chaque obstacle. Vous allez juste
    essayer de conduire au plus près possible de cette vitesse de croisière.
    Si vous voulez arrêter complètement le véhicule, utilisez simplement |yspeed 0|n
    qui réduira lentement votre vitesse.

    Un peu avant d'arriver à un carrefour au bout de la rue, vous serez informé des
    sorties disponibles dans ce carrefour. C'est un peu comme obtenir les sorties
    visibles quand vous regardez une salle. Cependant, vous devez choisir un tournant
    relativement rapidement. Si vous ne choisissez pas la direction à suivre, et que
    le véhicule entre dans le carrefour, vous prendrez automatiquement la sortie
    directement en face de vous si possible. Si cette sortie n'existe pas, le
    véhicule s'arrêtera au milieu du carrefour. Dans ce dernier cas, vous devrez
    tourner et changez à nouveau votre vitesse avec la commande |yspeed|n.
    Une fois averti des sorties disponibles dans un carrefour, vous pouvez utiliser
    la commande |yturn|n. Ce n’est cependant pas la solution la plus simple : vous
    pouvez utiliser les noms de direction pour tourner, comme |ynord-est|n ou même
    l'alias |yne|n. Cela est bien plus rapide à écrire, et puisque les sorties
    standard utilisent les mêmes noms, vous pouvez aller encore plus vite avec les
    macros de votre client, si il les supporte.

    Une fois arrivé à la destination souhaitée, commencez par ralentir à l’aide de la
    commande |yspeed|n. Pour vous garer, vous pouvez utiliser la commande |ypark|n.
    Votre véhicule doit être relativement lent ou vous ne pourrez pas utiliser cette
    commande. La commande |ypark|n tentera de garer votre véhicule du côté droit de
    la rue. Si vous préférez vous garer sur la gauche, utilisez la direction absolue
    (son nom ou alias), comme |ypark sud|n ou |ypark e|n.

    Enfin, vous pouvez simplement sortir de votre véhicule à l’aide de la commande
    |yleave|n. Une fois de plus, vous devrez peut-être déverrouiller le véhicule car
    certains ne le feront pas automatiquement pour des raisons de sécurité. Une
    fois à l'extérieur, vous pourriez vouloir utiliser la commande |ylock|n afin de
    verrouiler votre véhicule et empêcher les autres de vous les voler.

    """, aliases=["conducteur", "voiture", "camion", "moto"])
