# Batch-code for wiki pages
# Run this batch-code by entering the following command in-game: @batchcode public.wiki

# Note that this is a public file.  It will attempt to create or update
# wiki pages to update the documentation.  Keep in mind that, although
# efforts have been made to have this documentation as complete and
# accurate as possible, since this file is intended to be modified
# (or even replaced by a private file), this documentation must be
# adapted to fit your game environment.

#HEADER

from textwrap import dedent

from evennia_wiki.models import Page
from evennia import AccountDB

superuser = AccountDB.objects.get(id=1)

def write_wiki(address, title, text):
    """Create or update a wiki page."""
    page = Page.objects.create_or_update_content(address, superuser, dedent(text), force_update=False)
    page.title = title
    page.save()

#CODE

write_wiki("doc/yaml", "Bâtissage de masse avec YML", """
        Le bâtissage de masse désigne un outil permettant aux bâtisseurs de créer un grand nombre de salles, objets ou autre information, en
        utilisant un seul fichier. Evennia propose deux [processeurs de bâtissage de masse](https://github.com/evennia/evennia/wiki/Batch-Processors),
        [le processeur de bâtissage de masse par commande](https://github.com/evennia/evennia/wiki/Batch-Command-Processor) et
        [le processeur de bâtissage de masse par code](https://github.com/evennia/evennia/wiki/Batch-Code-Processor). Bien que ces deux processeurs
        soient vraiment puissants, les bâtisseurs peuvent les trouver un peu intimidants au premier abord. Le premier est utilisé pour exécuter une liste de commandes contenues dans un fichier et est,
        par définition, plus délicat à mettre à jour, et poser problème lors de la rédaction de descriptions (qui se produit quotidiennement pour les bâtisseurs). Le second processeur est
        utilisé pour exécuter du code Python et est moins intuitif pour les bâtisseurs, bien qu'évidemment, il soit plus flexible au final.

        Le bâtissage de masse par YML offre une troisième alternative, visant à être plus intuitive pour les bâtisseurs, facile à mettre à jour et assez étendue. Ce document
        décrit plus en détail le processeur YML et comment l'utiliser.

        ## Principe de base du processeur YML

        Le processeur YML attend un fichier contenant du texte, formaté à l'aide du langage YAML.

        1. Un fichier peut contenir plusieurs parties, traditionnellement, une par salle / objet / personnage.
        2. Le bâtisseur souhaitant appliquer ce fichier peut se connecter à [/builder/batch](/builder/batch). Sur cette page se trouve un formulaire très simple permettant de télécharger le fichier YML depuis le PC de l'utilisateur.
        3. Une fois envoyé, le fichier est lu par le système, les salles, objets, personnages sont créés ou mis à jour et le statut de chaque tâche est envoyé au bâtisseur.

        Ainsi, la création de masse à l'aide de fichiers YML est assez simple. Ces fichiers peuvent être mis à jour et téléchargés à nouveau (pour corriger une description, une sortie,
        les coordonnées d'une salle, un callback...).

        ## Syntaxe YML de base

        Bien que le langage YML soit assez simple, il doit suivre certaines règles précises. En règle générale, il est recommandé d'utiliser les exemples ci-dessous (copiez / collez-les dans un fichier, puis modifiez la valeur de chaque champ). Voici les règles générales à appliquer au processeur YML :

        - Les fichiers doivent être encodés en utf-8. Si vous essayez d'entrer des caractères non-ASCII dans un encodage différent, le fichier ne sera probablement pas lu correctement.
        - Un document YML est utilisé pour représenter chaque objet, salle ou personnage. Les documents YML sont séparés par `---` (trois tirets sur une ligne à part).
        - Chaque document est un dictionnaire YML suivant la syntaxe du dictionnaire (une clé / valeur sur chaque ligne en règle générale). Voir les exemples ci-dessous.
        - Le premier champ de chaque document doit être "type" et contenir le type de l'objet à créer (un objet, une salle, un prototype...). Encore une fois, reportez-vous aux exemples ci-dessous.
        - Respecter l'indentation. YML est un langage strict qui utilise l'indentation pour délimiter les données, comme le fait Python lui-même.
        - Respectez les symboles des exemples. Certains peuvent ne pas être évidents mais tous sont néanmoins obligatoires. Des erreurs de syntaxe surviendront si ces symboles ne sont pas présents.

        Tous les documents doivent commencer par une ligne avec `---` (trois tirets).

        ## Exemples détaillés

        Cette section liste des exemples de documents. Un document YML est destiné à décrire la création d'une donnée (une salle, un objet, un prototype, etc.).

        ### Salle (type salle)

        #### Exemple

        ```
        ---
        type: salle
        ident: identifiant_salle
        prototype: clé_du_prototype_de_salle_si_désiré
        coords: [0, 5, -8]
        titre: Le titre de la salle
        description: |
            Ceci est la description de la salle. Notez qu'il est préférable de
            spécifier sur plusieurs lignes en retrait sous le champ "description",
            après la barre verticale. Cette barre verticale informe l'analyseur
            YML que le contenu du champ est sur les lignes suivantes, identé vers
            la droite. Les sauts de ligne doivent être conservés. Cependant, dans
            ce cas, les sauts de ligne simples sont ignorés (remplacés par des espaces).

            Cependant, si vous laissez une ligne vide, avant de poursuivre
            la description (toujours identée), un nouveau paragraphe sera
            créé dans cette description.
        sorties:
            - direction: est
              destination: identifiant_salle
              nom: toboggan
              alias: [t]
            - direction: ouest
              destination: identifiant_salle
              nom: porte
              alias: [p, po]
        ```

        #### Champs

        | Champ | Présence | Valeur |
        | ----- | -------- | ----- |
        | type | Obligatoire | Doit être salle |
        | ident | Obligatoire | L'identifiant de la salle, une clé qui ne peut contenir que des lettres minuscules, des chiffres et le symbole deux-points (`:`). |
        | prototype | Facultatif La clé du prototype de salle (proom) à utiliser. Ceci n'est pas obligatoire, car les salles peuvent exister sans prototype. |
        | coords | Facultatif Les coordonnées de la salle dans une liste, X, Y et Z étant des nombres entiers. Si ce champ n'est pas présent, la salle n'aura pas de coordonnées valides. |
        | titre | Facultatif Le titre de la salle. |
        | description | Facultatif La description de la salle. Notez que si la salle possède un prototype, et aucune description, elle utilisera la description du prototype. |
        | sorties | Facultatif | Les sorties de la salle, dans une liste. Suivez la syntaxe des exemples proposés. Voir la section ci-dessous pour plus d'information sur les sorties. |

        #### Remarques

        L'identifiant de la salle (champ `ident`) est important lors de la mise à jour. La salle qui possède le même identifiant sera recherchée dans le jeu actuel
        lorsqu'un document de type salle est téléchargé. Si une salle avec cet identifiant existe, le document lui est appliqué pour la mettre à jour. Sinon, la salle sera créée.
        Par conséquent, ne modifiez pas les identifiants après le premier téléchargement, et assurez-vous que les identifiants que vous utilisez ne sont pas utilisés dans
        le reste du jeu.

        En supposant que les identifiants restent les mêmes, tous les champs (y compris les coordonnées) peuvent être modifiés. Si vous changez les coordonnées (champ `coords`) de
        tout document, puis le téléchargez à nouveau, les coordonnées de la salle seront modifiées. Cela ne fonctionnera pas cependant s'il y a une autre salle avec les mêmes coordonnées,
        mais pas le même identifiant (`ident`).

        ### Sortie

        #### Exemple

        ```
        type: salle
        # ...
        sorties:
            - direction: direction de la sortie
              destination: identifiant_salle
              nom: nom de la sortie
              alias: [alias1, alias2, alias3]
        ```

        #### Champs

        | Champ | Présence | Valeur |
        | ----- | -------- | ----- |
        | direction | Obligatoire | La direction absolue de la sortie (est, sud, nord, sud-est, haut, bas...). |
        | destination | Obligatoire | L'identifiant de la salle de destination de cette sortie. La sortie sera créée entre la salle où elle est définie et celle ayant l'identifiant précisé dans le champ `destination`. Gardez à l'esprit que la sortie réciproque (dans l'autre sens) n'est pas créée automatiquement, il faut l'ajouter manuellement dans la salle de destination. |
        | nom | Facultatif | Le nom de la sortie. Si aucun nom n'est précisé, le nom de la sortie sera identique à la direction (sud, par exemple). |
        | alias | Facultatif | Une liste optionnelle d'alias, c'est-à-dire de commandes permettant d'emprunter cette sortie en plus du nom. Si ce champ n'est pas précisé et qu'aucun nom de sortie n'est défini, les alias par défaut de la direction sont choisis (par exemple, "s" si la sortie pointe vers le sud). Vous pouvez cependant indiquer des alias de remplacement dans une liste, comme `alias = [alias1, alias2, ...]`. |

        #### Remarques

        Les sorties sont définies dans les documents des salles, dans un champ appelé `sorties`. Typiquement, le document de salle avec sortie ressemble à cela :

        ```
        ---
        type: salle
        # ...
        sorties:
            - direction: direction de la sortie
              destination: identifiant_salle
            - direction: direction de la sortie
              destination: identifiant_salle
            - direction: direction de la sortie
              destination: identifiant_salle
        ```

        Notez l'indentation sous le champ `sorties`. Chaque sortie doit commencer par un tiret suivi d'un espace. Les champs de la sortie suivent ensuite
        ce même niveau d'indentation, avec un champ et sa valeur sur une ligne comme les autres documents. Vous pouvez définir une ou plusieurs sorties
        dans un document de salle. Si vous souhaitez créer une salle sans sorties, ne précisez pas le champ `sorties` dans le document.
        Il est sans doute préférable de copier/coller l'un des exemples donnés afin d'être certain(e) de respecter la syntaxe.

        L'ordre de définition des salles et sorties n'est pas important. Par exemple, une salle peut définir une sortie dont le champ de destination fait référence
        à une salle encore inexistante : la salle sera créée avant la sortie et sera ensuite mises à jour dans un autre document, plus bas dans le fichier.

        ### Prototype de salle (type psalle)

        #### Exemple

        ```
        ---
        type: psalle
        ident: identifiant_du_prototype_de_salle
        description: |
            La description du prototype. Encore une fois, pour créer deux
            paragraphes, insérez simplement une ligne vide entre eux. Par exemple :
            C'est le paragraphe 1.

            C'est le paragraphe 2.
        ```

        #### Champs

        | Champ | Présence | Valeur |
        | ----- | -------- | ----- |
        | type | Obligatoire | Doit être psalle |
        | ident | Obligatoire | L'identifiant du prototype de salle, une clé qui ne peut contenir que des lettres minuscules, des chiffres et le symbole deux-points (`:`). |
        | description | Facultatif La description du prototype de salle. |

        #### Remarques

        L'identifiant spécifié dans un document psalle est la clé à utiliser dans le champ `prototype` d'un document de salle
        qui définit un prototype. Encore une fois, si le prototype n’existe pas, il est créé, sinon il est mis à jour. Par conséquent, vous pouvez
        avoir des documents de salle avec un prototype inexistant, et un document de prototype de salle plus bas dans le même fichier. La première salle qui a besoin du prototype spécifié
        le créera, il sera mis à jour lors de la lecture du document psalle. Toutefois, il est recommandé de placer les prototypes de salle au-dessus des documents de salle l'utilisant.

        Si une salle possède un prototype mais aucune description, sa description sera empruntée au prototype et mise à jour si le prototype change. Une description de salle peut également demander la description du prototype. Considérez cet exemple simple :

        ```
        ---
        type: psalle
        ident: trottoir
        description: |
            C'est un trottoir.

        ---
        type: salle
        ident: trottoir1
        prototype: trottoir
        description: |
            $parent C'est un peu étroit.
        ```

        Si vous téléchargez un fichier YML avec ce code, la salle (trottoir1) sera créée, sa description sera : Ceci est un trottoir. C'est un peu étroit.
""")

