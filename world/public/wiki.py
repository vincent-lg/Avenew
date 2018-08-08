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

write_wiki("doc/yaml", "B�tissage de masse avec YML", """
        Le b�tissage de masse d�signe un outil permettant aux b�tisseurs de cr�er un grand nombre de salles, objets ou autre information, en
        utilisant un seul fichier. Evennia propose deux [processeurs de b�tissage de masse](https://github.com/evennia/evennia/wiki/Batch-Processors),
        [le processeur de b�tissage de masse par commande](https://github.com/evennia/evennia/wiki/Batch-Command-Processor) et
        [le processeur de b�tissage de masse par code](https://github.com/evennia/evennia/wiki/Batch-Code-Processor). Bien que ces deux processeurs
        soient vraiment puissants, les b�tisseurs peuvent les trouver un peu intimidants au premier abord. Le premier est utilis� pour ex�cuter une liste de commandes contenues dans un fichier et est,
        par d�finition, plus d�licat � mettre � jour, et poser probl�me lors de la r�daction de descriptions (qui se produit quotidiennement pour les b�tisseurs). Le second processeur est
        utilis� pour ex�cuter du code Python et est moins intuitif pour les b�tisseurs, bien qu'�videmment, il soit plus flexible au final.

        Le b�tissage de masse par YML offre une troisi�me alternative, visant � �tre plus intuitive pour les b�tisseurs, facile � mettre � jour et assez �tendue. Ce document
        d�crit plus en d�tail le processeur YML et comment l'utiliser.

        ## Principe de base du processeur YML

        Le processeur YML attend un fichier contenant du texte, format� � l'aide du langage YAML.

        1. Un fichier peut contenir plusieurs parties, traditionnellement, une par salle / objet / personnage.
        2. Le b�tisseur souhaitant appliquer ce fichier peut se connecter � [/builder/batch](/builder/batch). Sur cette page se trouve un formulaire tr�s simple permettant de t�l�charger le fichier YML depuis le PC de l'utilisateur.
        3. Une fois envoy�, le fichier est lu par le syst�me, les salles, objets, personnages sont cr��s ou mis � jour et le statut de chaque t�che est envoy� au b�tisseur.

        Ainsi, la cr�ation de masse � l'aide de fichiers YML est assez simple. Ces fichiers peuvent �tre mis � jour et t�l�charg�s � nouveau (pour corriger une description, une sortie,
        les coordonn�es d'une salle, un callback...).

        ## Syntaxe YML de base

        Bien que le langage YML soit assez simple, il doit suivre certaines r�gles pr�cises. En r�gle g�n�rale, il est recommand� d'utiliser les exemples ci-dessous (copiez / collez-les dans un fichier, puis modifiez la valeur de chaque champ). Voici les r�gles g�n�rales � appliquer au processeur YML :

        - Les fichiers doivent �tre encod�s en utf-8. Si vous essayez d'entrer des caract�res non-ASCII dans un encodage diff�rent, le fichier ne sera probablement pas lu correctement.
        - Un document YML est utilis� pour repr�senter chaque objet, salle ou personnage. Les documents YML sont s�par�s par `---` (trois tirets sur une ligne � part).
        - Chaque document est un dictionnaire YML suivant la syntaxe du dictionnaire (une cl� / valeur sur chaque ligne en r�gle g�n�rale). Voir les exemples ci-dessous.
        - Le premier champ de chaque document doit �tre "type" et contenir le type de l'objet � cr�er (un objet, une salle, un prototype...). Encore une fois, reportez-vous aux exemples ci-dessous.
        - Respecter l'indentation. YML est un langage strict qui utilise l'indentation pour d�limiter les donn�es, comme le fait Python lui-m�me.
        - Respectez les symboles des exemples. Certains peuvent ne pas �tre �vidents mais tous sont n�anmoins obligatoires. Des erreurs de syntaxe surviendront si ces symboles ne sont pas pr�sents.

        Tous les documents doivent commencer par une ligne avec `---` (trois tirets).

        ## Exemples d�taill�s

        Cette section liste des exemples de documents. Un document YML est destin� � d�crire la cr�ation d'une donn�e (une salle, un objet, un prototype, etc.).

        ### Salle (type salle)

        #### Exemple

        ```
        ---
        type: salle
        ident: identifiant_salle
        prototype: cl�_du_prototype_de_salle_si_d�sir�
        coords: [0, 5, -8]
        titre: Le titre de la salle
        description: |
            Ceci est la description de la salle. Notez qu'il est pr�f�rable de
            sp�cifier sur plusieurs lignes en retrait sous le champ "description",
            apr�s la barre verticale. Cette barre verticale informe l'analyseur
            YML que le contenu du champ est sur les lignes suivantes, ident� vers
            la droite. Les sauts de ligne doivent �tre conserv�s. Cependant, dans
            ce cas, les sauts de ligne simples sont ignor�s (remplac�s par des espaces).

            Cependant, si vous laissez une ligne vide, avant de poursuivre
            la description (toujours ident�e), un nouveau paragraphe sera
            cr�� dans cette description.
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

        | Champ | Pr�sence | Valeur |
        | ----- | -------- | ----- |
        | type | Obligatoire | Doit �tre salle |
        | ident | Obligatoire | L'identifiant de la salle, une cl� qui ne peut contenir que des lettres minuscules, des chiffres et le symbole deux-points (`:`). |
        | prototype | Facultatif La cl� du prototype de salle (proom) � utiliser. Ceci n'est pas obligatoire, car les salles peuvent exister sans prototype. |
        | coords | Facultatif Les coordonn�es de la salle dans une liste, X, Y et Z �tant des nombres entiers. Si ce champ n'est pas pr�sent, la salle n'aura pas de coordonn�es valides. |
        | titre | Facultatif Le titre de la salle. |
        | description | Facultatif La description de la salle. Notez que si la salle poss�de un prototype, et aucune description, elle utilisera la description du prototype. |
        | sorties | Facultatif | Les sorties de la salle, dans une liste. Suivez la syntaxe des exemples propos�s. Voir la section ci-dessous pour plus d'information sur les sorties. |

        #### Remarques

        L'identifiant de la salle (champ `ident`) est important lors de la mise � jour. La salle qui poss�de le m�me identifiant sera recherch�e dans le jeu actuel
        lorsqu'un document de type salle est t�l�charg�. Si une salle avec cet identifiant existe, le document lui est appliqu� pour la mettre � jour. Sinon, la salle sera cr��e.
        Par cons�quent, ne modifiez pas les identifiants apr�s le premier t�l�chargement, et assurez-vous que les identifiants que vous utilisez ne sont pas utilis�s dans
        le reste du jeu.

        En supposant que les identifiants restent les m�mes, tous les champs (y compris les coordonn�es) peuvent �tre modifi�s. Si vous changez les coordonn�es (champ `coords`) de
        tout document, puis le t�l�chargez � nouveau, les coordonn�es de la salle seront modifi�es. Cela ne fonctionnera pas cependant s'il y a une autre salle avec les m�mes coordonn�es,
        mais pas le m�me identifiant (`ident`).

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

        | Champ | Pr�sence | Valeur |
        | ----- | -------- | ----- |
        | direction | Obligatoire | La direction absolue de la sortie (est, sud, nord, sud-est, haut, bas...). |
        | destination | Obligatoire | L'identifiant de la salle de destination de cette sortie. La sortie sera cr��e entre la salle o� elle est d�finie et celle ayant l'identifiant pr�cis� dans le champ `destination`. Gardez � l'esprit que la sortie r�ciproque (dans l'autre sens) n'est pas cr��e automatiquement, il faut l'ajouter manuellement dans la salle de destination. |
        | nom | Facultatif | Le nom de la sortie. Si aucun nom n'est pr�cis�, le nom de la sortie sera identique � la direction (sud, par exemple). |
        | alias | Facultatif | Une liste optionnelle d'alias, c'est-�-dire de commandes permettant d'emprunter cette sortie en plus du nom. Si ce champ n'est pas pr�cis� et qu'aucun nom de sortie n'est d�fini, les alias par d�faut de la direction sont choisis (par exemple, "s" si la sortie pointe vers le sud). Vous pouvez cependant indiquer des alias de remplacement dans une liste, comme `alias = [alias1, alias2, ...]`. |

        #### Remarques

        Les sorties sont d�finies dans les documents des salles, dans un champ appel� `sorties`. Typiquement, le document de salle avec sortie ressemble � cela :

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
        ce m�me niveau d'indentation, avec un champ et sa valeur sur une ligne comme les autres documents. Vous pouvez d�finir une ou plusieurs sorties
        dans un document de salle. Si vous souhaitez cr�er une salle sans sorties, ne pr�cisez pas le champ `sorties` dans le document.
        Il est sans doute pr�f�rable de copier/coller l'un des exemples donn�s afin d'�tre certain(e) de respecter la syntaxe.

        L'ordre de d�finition des salles et sorties n'est pas important. Par exemple, une salle peut d�finir une sortie dont le champ de destination fait r�f�rence
        � une salle encore inexistante : la salle sera cr��e avant la sortie et sera ensuite mises � jour dans un autre document, plus bas dans le fichier.

        ### Prototype de salle (type psalle)

        #### Exemple

        ```
        ---
        type: psalle
        ident: identifiant_du_prototype_de_salle
        description: |
            La description du prototype. Encore une fois, pour cr�er deux
            paragraphes, ins�rez simplement une ligne vide entre eux. Par exemple :
            C'est le paragraphe 1.

            C'est le paragraphe 2.
        ```

        #### Champs

        | Champ | Pr�sence | Valeur |
        | ----- | -------- | ----- |
        | type | Obligatoire | Doit �tre psalle |
        | ident | Obligatoire | L'identifiant du prototype de salle, une cl� qui ne peut contenir que des lettres minuscules, des chiffres et le symbole deux-points (`:`). |
        | description | Facultatif La description du prototype de salle. |

        #### Remarques

        L'identifiant sp�cifi� dans un document psalle est la cl� � utiliser dans le champ `prototype` d'un document de salle
        qui d�finit un prototype. Encore une fois, si le prototype n�existe pas, il est cr��, sinon il est mis � jour. Par cons�quent, vous pouvez
        avoir des documents de salle avec un prototype inexistant, et un document de prototype de salle plus bas dans le m�me fichier. La premi�re salle qui a besoin du prototype sp�cifi�
        le cr�era, il sera mis � jour lors de la lecture du document psalle. Toutefois, il est recommand� de placer les prototypes de salle au-dessus des documents de salle l'utilisant.

        Si une salle poss�de un prototype mais aucune description, sa description sera emprunt�e au prototype et mise � jour si le prototype change. Une description de salle peut �galement demander la description du prototype. Consid�rez cet exemple simple :

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
            $parent C'est un peu �troit.
        ```

        Si vous t�l�chargez un fichier YML avec ce code, la salle (trottoir1) sera cr��e, sa description sera : Ceci est un trottoir. C'est un peu �troit.
""")

