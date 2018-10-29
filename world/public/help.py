# Batch-code file containing the standard help files
# Generate with: @batchcode public.help

#HEADER
from world.batch import get_help_entry

#CODE
get_help_entry("v�hicle", """
    Dans Avenew One, vous pouvez conduire un v�hicule en utilisant un ensemble de commandes
    d�crites dans cette page d'aide. Bien que les v�hicules puissent acc�der � des zones
    inaccessibles, ils sont principalement utilis�s pour gagner du temps. Les voitures,
    par exemple, offrent un raccourci pratique pour se d�placer dans la ville, bien que
    vous puissiez marcher. Les v�hicules typiques seraient les voitures, camions, motos.
    Des v�hicules plus atypiques sont encore � pr�voir toutefois.

    Pour conduire un v�hicule que vous poss�dez ou un v�hicule public auquel vous avez
    acc�s, vous devez d�abord vous trouvez aupr�s du dit v�hicule. Vous le verrez dans
    la description de la salle. Les v�hicules sont regroup�s par type et par marque afin de
    ne pas vous surcharger d'information, mais vous pouvez rechercher facilement un v�hicule
    sp�cifique. Vous devez y monter en utilisant la commande |yenter|n. Vous devez
    pr�ciser en param�tre le nom (ou une partie du nom) du v�hicule dans lequel vous
    voulez monter. Vous pouvez �galement fournir la plaque d'immatriculation, pour
    �viter la confusion. Notez que le v�hicule peut �tre verrouill�, auquel cas,
    vous devrez utiliser la commande |yunlock|n. Vous ne pourrez pas d�verrouillez tous
    les v�hicules dans un parking, vous aurez besoin des cl�s ou d�un autre moyen de
    d�verrouiller ce v�hicule. Les v�hicules publics sont g�n�ralement
    d�verrouill�s, ce qui signifie que vous pouvez entrer dedans sans contrainte. D'autre
    part, cela signifie �galement que tout le monde peut faire la m�me chose,
    peut-�tre ne devriez-vous pas trop vous fier � ce moyen de transport.

    Une fois sur le si�ge avant du v�hicule, vous devez utiliser la commande |ydrive|n
    pour saisir le volant. Il n'est pas possible de conduire si quelqu'un d'autre est
    d�j� derri�re le volant. Vous utiliserez la m�me commande pour rel�cher le volant
    quand vous voulez arr�ter de conduire. Si vous �tes gar� et que vous utilisez la
    commande |ydrive|n, vous d�marrerez le moteur et avancerez les quelques m�tres n�cessaires pour
    �tre dans la rue.

    Vous devez maintenant acc�l�rer. Vous pouvez contr�ler la vitesse en utilisant
    la commande |yspeed|n. Sp�cifiez votre vitesse d�sir�e en kilom�tres par heure.
    Notez que cela ressemble plus � votre vitesse de croisi�re maximale. Il ne sera
    pas n�cessaire de freiner manuellement � chaque obstacle. Vous allez juste
    essayer de conduire au plus pr�s possible de cette vitesse de croisi�re.
    Si vous voulez arr�ter compl�tement le v�hicule, utilisez simplement |yspeed 0|n
    qui r�duira lentement votre vitesse.

    Un peu avant d'arriver � un carrefour au bout de la rue, vous serez inform� des
    sorties disponibles dans ce carrefour. C'est un peu comme obtenir les sorties
    visibles quand vous regardez une salle. Cependant, vous devez choisir un tournant
    relativement rapidement. Si vous ne choisissez pas la direction � suivre, et que
    le v�hicule entre dans le carrefour, vous prendrez automatiquement la sortie
    directement en face de vous si possible. Si cette sortie n'existe pas, le
    v�hicule s'arr�tera au milieu du carrefour. Dans ce dernier cas, vous devrez
    tourner et changez � nouveau votre vitesse avec la commande |yspeed|n.
    Une fois averti des sorties disponibles dans un carrefour, vous pouvez utiliser
    la commande |yturn|n. Ce n�est cependant pas la solution la plus simple : vous
    pouvez utiliser les noms de direction pour tourner, comme |ynord-est|n ou m�me
    l'alias |yne|n. Cela est bien plus rapide � �crire, et puisque les sorties
    standard utilisent les m�mes noms, vous pouvez aller encore plus vite avec les
    macros de votre client, si il les supporte.

    Une fois arriv� � la destination souhait�e, commencez par ralentir � l�aide de la
    commande |yspeed|n. Pour vous garer, vous pouvez utiliser la commande |ypark|n.
    Votre v�hicule doit �tre relativement lent ou vous ne pourrez pas utiliser cette
    commande. La commande |ypark|n tentera de garer votre v�hicule du c�t� droit de
    la rue. Si vous pr�f�rez vous garer sur la gauche, utilisez la direction absolue
    (son nom ou alias), comme |ypark sud|n ou |ypark e|n.

    Enfin, vous pouvez simplement sortir de votre v�hicule � l�aide de la commande
    |yleave|n. Une fois de plus, vous devrez peut-�tre d�verrouiller le v�hicule car
    certains ne le feront pas automatiquement pour des raisons de s�curit�. Une
    fois � l'ext�rieur, vous pourriez vouloir utiliser la commande |ylock|n afin de
    verrouiler votre v�hicule et emp�cher les autres de vous les voler.

    """, aliases=["conducteur", "voiture", "camion", "moto"])
