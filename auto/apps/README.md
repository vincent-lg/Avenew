# Les apps sur Avenew one

[Avenew One](https://www.avenew.one) possède un système complet et extensible d'applications (apps) pour téléphones et ordinateurs, avec une interface utilisable depuis le jeu. Cette interface, appelée AvenOS, est une interface simple et épurée en mode texte représentant une interface mobile, se voulant flexible et simple d'utilisation. Les téléphones ou ordinateurs (smartphones) peuvent utiliser ces applications. La création d'applications est relativement simple, mais elle nécessite l'édition de code source. Bien que le développement reste facile et intuitif au possible, ajouter une app dans Avenew nécessite de coder en Python. Les étapes nécessaires seront décrites en détail dans la suite de ce document, ainsi que dans d'autres documents annexes. Si vous possédez une connaissance de base de la syntaxe de Python, si vous savez ce qu'est une variable, une fonction, une condition, une boucle, une exception, une classe et la syntaxe pour les manipuler, si vous comprenez le principe de base de l'héritage, alors coder une app en suivant ce document ne devrait pas être difficile.

## Pour commencer

La première étape est d'installer une copie d'Avenew sur votre PC. Pour ce faire, vous aurez besoin d'[Evennia](www.evennia.com) déjà installé.

Vous pouvez suivre le document [installation rapide d'Avenew](https://github.com/vlegoff/avenew/blob/fr/README.md).

Une fois le système configuré, vous devriez pouvoir exécuter `evennia start` dans le dossier "avenew".  Evennia vous demandera de créer un super-utilisateur (superuser) avec un nom, e-mail (optionnel) et mot de passe. Une fois cela fait, vous devriez pouvoir vous connecter à l'adresse "localhost" (port 4000) en utilisant votre client MU* favoris, ou bien vous rendre à l'adresse http://localhost:4001 et cliquer sur le lien "jouer en ligne" pour utiliser le webclient.

Une fois connecté en utilisant les identifiants du super-utilisateur que vous venez de créer, vous vous retrouverez dans une salle vide. Vous pouvez créer une démonstration du jeu (contenant plusieurs salles et objets, incluant un smartphone) en entrant la commande suivante :

    @batchcode demo

La commande peut prendre quelques secondes avant de répondre. Si tout va bien, vous devriez voir un smartphone à vos pieds. Vous le verrez en entrant `look`.  Vous pouvez le ramasser en entrant `get aven`. Vous pouvez ouvrir l'interface AvenOS en entrant `use aven`.

Vous vous trouvez maintenant dans l'interface du téléphone. Vous pouvez ouvrir une application en entrant son nom, comme `texte`. Si vous avez été, ou êtes joueur sur Avenew One, cette interface ne devrait pas vous surprendre. La différence étant que vous pouvez créer votre propre app et demander qu'elle soit intégrée au jeu.

## Créer une nouvelle application

Une application est très facile à ajouter dans le code. Dans le dossier "avenew", ouvrez le dossier "auto", puis le dossier "apps". Dans ce dernier, les apps se trouvent listées, une application par fichier. Pour créer une application, créez une nouveau fichier avec l'extension `.py` et placez-y quelques lignes de code (voir ci-dessous). C'est aussi simple que cela.

### Code minimal d'une app

Admettons que vous souhaitiez créer une application simple, appelée "memo", permettant d'ajouter, éditer et supprimer des mémos (des notes). La première étape est de créer un fichier appelé  "memo.py" et de le placer dans "auto/apps". Notez que le nom de fichier doit être un module Python valide : évitez les accents et n'utilisez pas de caractères autres que des lettres. Certains caractères comme le souligné (`_`) sont autorisés, ainsi que des chiffres dans une certaine mesure. Gardez un nom court et explicite.

Dans ce fichier, vous pouvez coller le code suivant (en changeant le nom de l'application, si vous voulez) :

```
# -*- coding: utf-8 -*-

"""
App mémo : conserve des notes courtes entrées par l'utilisateur de l'application.

Entrez plus de détails sur l'application ici. Vous pouvez écrire plusieurs
lignes. De préférence, gardez vos lignes plus courtes que 75 caractères.
Regardez les exemples d'autres fichiers pour voir les informations qui sont
généralement écrites ici.

"""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

class Memo(BaseApp):

    """
    App mémo.

    Vous pouvez ajouter davantage de détails ici à l'adresse des développeurs.
    Par exemple, une liste des méthodes les plus importantes peut être utile.

    """

    app_name = "memo"
    display_name = "Mémo"
```

Détaillons un peu ce que fait ce code. Si il vous paraît trop obscur de prime abord, vous trouverez de très nombreux tutoriels de qualité sur le langage Python pour vous permettre de comprendre plus intuitivement la syntaxe. Je recommande fortement d'en lire un avant de continuer ce document.

1. Tout en haut se trouve la ligne décrivant l'encodage du fichier. N'y touchez pas, recopiez-la simplement. Veillez à ce que votre éditeur soit bien configuré pour écrire en utf-8.
2. Au début du fichier se trouvent plusieurs lignes entourées par des signes `"""`. C'est ce qu'on appelle une **docstring**, et à cet endroit elle permet simplement de donner des informations sur le module.  Puisque notre module contiendra une app, c'est un bon moment pour décrire cette app : dire ce qu'elle permet de faire, qui l'a faite, comment l'utiliser. N'écrivez pas un roman à cet endroit non plus, la documentation n'ayant d'intérêt que si elle n'est pas trop longue.
3. On importe ensuite trois classes depuis le module `auto.apps.base`. Ce module contient le mécanisme de base d'une app. Pour l'instant, nous n'utilisons que `BaseApp`. Nous explorerons les autres classes bien plus à fond dans la suite de ce document.
4. Nous définissions ensuite la structure de l'app. Afin d'avoir une app utilisable, il nous faut créer une classe héritant de `BaseApp`, contenant au moins une variable de classe appelée `app_name`. C'est le strict minimum. Ainsi, on définit la classe `Memo`, qui hérite de `BaseApp`. Vous pourriez ajouter un peu de documentation dans la classe même, cela ne peut pas faire de mal.
5. On définit plusieurs variables de classe qui sont utilisées par l'interface AvenOS : `app_name` contient le nom unique de l'application. Ce devrait être une `str` en minuscule contenant uniquement des lettres sans accent. Utiliser le nom du fichier (sans l'extension) peut être une bonne idée. Deux applications ne peuvent pas avoir le même `app_name`, sans quoi l'une écrasera l'autre. `display_name` contient une version plus lisible et agréable du nom de l'application. C'est une autre `str`, et vous pouvez y mettre des lettres accentuées, des minuscules ou majuscules, sans aucun problème. C'est le nom qui sera affiché à l'utilisateur. Par convention, la première lettre de l'application est en majuscule, même si ce n'est pas une obligation. À la différence de `app_name`, `display_name` n'est pas un identifiant unique : deux applications peuvent avoir le même `display_name`, bien que ce puisse être problématique pour les utilisateurs.

### Et c'est tout, ajoutons notre application

Vous pouvez fermer ce fichier pour l'instant. Rechargez Evennia (en utilisant la commande @reload`). Avant d'utiliser votre téléphone (avec `use`), vous devez ajouter l'application au téléphone "un téléphone (ou ordinateur) n'a pas toutes les applications par défaut). Ajouter l'application à un objet est cependant très simple en utilisant `@py` :

    @py self.search("aven").types.get("computer").apps.add("memo")

> Wow, une longue commande assez peu intuitive !

Inutile de trop s'attarder sur le détail de cette commande ici, car vous n'en aurez besoin qu'une fois lors de l'ajout de l'application. Vous la comprendrez mieux avec du temps et de la pratique. Pour simplifier, on cherche l'objet (le téléphone ici). On cherche son type "computer" (les applications étant stockées dans ce type). On accède aux applications conservées sur le téléphone et on en ajoute une, utilisant le nom de l'application (son `app_name`).

Vous pouvez à présent entrer la commande `use aven`. L'interface AvenOS devrait s'ouvrir, mais cette fois, vous devriez voir votre application dans la liste, son `display_name`.

> Je ne peux pas ouvrir l'application. Si j'entre "memo", le jeu me retourne une erreur étrange à propos d'un "écran inexistant".

En effet. Le code que je vous ai montré jusqu'ici était le minimum nécessaire et nous n'avons pas du tout fini. C'était le code simple et minimal pour avoir une application, et j'espère que vous serez d'accord, c'est un code très court et intuitif. Nous allons maintenant ajouter un peu de contenu dans notre application.

## La structure de toute application

Une app est structurée autour de trois concepts essentiels :

- La classe de l'application : c'est la classe que nous avons créé juste au-dessous. Elle contient des informations sur l'application-même. Elle peut très bien ne rien contenir d'autre. C'est souvent la classe la plus courte dans le fichier. Cependant, sans elle, rien ne marcherait.
- Une ou plusieurs classes d'écran (screen) : un écran décrit ce qui est affiché sur l'interface à un certain moment. Par exemple, si vous entrez `use aven`, puis `texte`, l'application "texte" (text) s'ouvrira. L'écran vous montrera la liste des messages que vous avez reçu ou envoyé, et vous proposera de créer un nouveau message. Ceci est un écran. Si vous entrez `new` pour créer un nouveau message, un nouvel écran apparaîtra contenant les champs nécessaires. Après avoir préparé et envoyé le message, cet écran se refermera et vous serez de retour dans l'écran principal de l'application, vous montrant la liste des messages. Ce concept d'écran est essentiel. Une application peut n'avoir qu'un seul écran, mais elle en possède souvent plus d'un.
- Une ou plusieurs commandes : en ouvrant un écran dans l'application, l'utilisateur aura accès à plusieurs commandes propres à cet écran. Suivant le même exemple, si vous avez entré `use aven` et `texte` pour ouvrir l'application "texte", l'écran principal s'affiche. Cet écran contient la commande "new", qu'un utilisateur peut utiliser pour créer un nouveau message. Si vous entrez "new", vous vous déplacerez dans un nouvel écran et aurez accès à de nouvelles commandes : "send", "cancel", "to" et ainsi de suite. Une commande est tout simplement une [commande d'Evennia](https://github.com/evennia/evennia/wiki/Commands) avec quelques valeurs par défaut.

En résumé : une application possède une classe-mère (héritant de `BaseApp`) et un ou plusieurs écrans (screen). Un écran peut posséder plusieurs commandes.

Si ces explications vous semblent claires, vous pouvez passer à la suite. Sinon, n'hésitez pas à relire cette section ou à avancer malgré tout, certaines choses pourront vous sembler plus claires en lisant des exemples concrets. N'hésitez pas à lire d'autres fichiers d'exemple également.

### Notre premier écran

Une application ne peut fonctionner sans écran, il lui en faut au moins un. Pour l'instant, nous allons garder l'exemple aussi simple que possible. Un écran affiche plusieurs informations propres au contexte (une boîte de dialogue en texte brut, par exemple) et propose plusieurs commandes pour interagir dans ce contexte. Ajoutons notre premier écran (vous pouvez copier ce code dans votre fichier "memo.py").

```python
# -*- coding: utf-8 -*-

"""
App mémo : conserve des notes courtes entrées par l'utilisateur de l'application.

Entrez plus de détails sur l'application ici. Vous pouvez écrire plusieurs
lignes. De préférence, gardez vos lignes plus courtes que 75 caractères.
Regardez les exemples d'autres fichiers pour voir les informations qui sont
généralement écrites ici.

"""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

## Classe de l'application

class Memo(BaseApp):

    """
    App mémo.

    Vous pouvez ajouter davantage de détails ici à l'adresse des développeurs.
    Par exemple, une liste des méthodes les plus importantes peut être utile.

    """

    app_name = "memo"
    display_name = "Mémo"
    start_screen = "EcranPrincipal"


## Écrans de l'application

class EcranPrincipal(BaseScreen):

    """Écran principal, affichant 'bonjour'."""

    def get_text(self):
        """Retourne le texte à afficher quand on ouvre l'écran."""
        return """
                App mémo !

                C'est ma première application, n'est-elle pas belle ?

                Bien entendu, elle ne fait pas grand chose pour l'heure.

                App mémo, de moi, licence BSD.
            """
```

> Dois-je entrer de nouveau la commande compliquée `@py` ?

Non, c'était simplement nécessaire pour ajouter l'application. Il suffit maintenant de recharger le jeu (entrez la commande `@reload`), ouvrez de nouveau l'interface AvenOS (`use aven`) puis ouvrez votre app (`memo`). Cette fois, votre app s'ouvre et que voyez-vous ?

```
App mémo! (BACK pour revenir à l'écran précédent, EXIT pour quitter, HELP pour obtenir de l'aide)

C'est ma première application, n'est-elle pas belle ?

Bien entendu, elle ne fait pas grand chose pour l'heure.

App mémo, de moi, licence BSD.
```

Vous voyez le texte que vous avez entré dans `get_text`, avec quelques modifications :

1. À la première ligne, après le nom de votre écran, se trouve maintenant une en-tête (header). Cette en-tête contient trois commandes (ou boutons) : back qui permet de retourner à l'écran précédent, exit qui permet de quitter l'interface sans attendre, et help qui permet d'obtenir de l'aide spécifique sur cet écran. Vous n'avez pas besoin de créer ces trois commandes, elles sont disponibiles automatiquement peu importe l'écran. Elles peuvent être désactivées (et l'en-tête peut être retiré) en modifiant certaines variables de notre classe. En principe, il est préférable de laisser l'en-tête. Souvenez-vous de garder la première ligne de `get_text` courte au possible.
2. Bien que le texte ait été entré avec plusieurs niveaux d'indentation, les espaces en début de ligne ont disparues. Ce n'est pas tout à fait vrai, en réalité : vous pouvez essayer d'entrer d'avantage d'indentation sur une ligne pour voir l'effet. Mais la méthode appelant `get_text` retire automatiquement une partie de l'indentation pour rendre l'édition du code plus simple et plus jolie (jetez un coup d’œil à [textwrap.dedent](https://docs.python.org/2/library/textwrap.html) si vous voulez savoir comment cela marche.)

Nous avons fait quelque chose d'autre également, quelque chose d'important. Notre application doit savoir quel écran ouvrir (elle ne peut le deviner, il y a souvent plusieurs écrans par application). Une autre variable de notre classe `Memo` est utilisée : quand un utilisateur entre `memo` pour ouvrir l'app, l'application ouvre son écran principal.

```python
class Memo(BaseApp):

    """..."""

    app_name = "memo"
    display_name = "Mémo"
    start_screen = "EcranPrincipal"
```

La variable de classe `start_screen` de notre app doit contenir le nom de l'écran à ouvrir (le nom de la classe héritant de `BaseScreen`). C'est souvent le nom de la classe elle-même, mais ce peut être un chemin absolu si vous souhaitez rediriger vers une autre application (comme `"auto.apps.base.MainScreen"`). Souvent cependant, on précise juste le nom de la classe : la classe en question sera cherchée dans le même module (votre module `memo.py` sera exploré pour trouver une classe `EcranPrincipal` qui hérite de `BaseScreen`).

Pour l'instant, notre écran ne fait pas grand chose, à part afficher du texte. De toute évidence, un écran doit faire quelque chose, supporter une ou plusieurs commandes (boutons).

## Un exemple fonctionnel

### Décrire la structure de l'app

C'est un bon moment pour réfléchir à l'aspect futur de notre app. Ici, nous voudrions créer une app simple, `mémo`, qui permet d'ajouter, éditer et supprimer de courtes notes (mémos). Un mémo sera donc tout simplement cela : une note avec un champ de texte. Notre écran principal pourrait donc ressembler à ceci :

```
Mémos (BACK pour revenir à l'écran précédent, EXIT pour quitter, HELP pour obtenir de l'aide)

( Entrez NEW pour créer un nouveau mémo. )

(Insérer la liste de mémos ici.)

Mémos : 15
```

Ce n'est qu'un premier brouillon, bien entendu, mais il nous permettra de voir la connexion entre écran et commande.

Dans cet exemple, nous voudrions une commande, "new", qui permet de créer un nouveau mémo. Nous voudrions aussi pouvoir ouvrir nos mémos individuellement pour pouvoir les éditer. Et peut-être qu'après, nous pourrions avoir une commande pour supprimer un mémo.

La première question que l'on doit se poser ici : combien d'écrans voulons-nous avoir ? Seulement un ? Peut-être... mais quand on créera un nouveau mémo, ou l'éditera, on voudrait avoir un affichage différent de l'écran d'accueil. Bien entendu, nous pourrions le faire depuis l'écran principal, mais ce serait moins confortable et intuitif pour l'utilisateur. Dans notre cas, nous allons donc diviser en deux écrans : l'écran principal qui affiche tous les mémos et l'écran d'un mémo qui permet d'ajouter/éditer un mémo.

Question suivante : de quelles commandes aurons-nous besoin ? La commande "new", de toute évidence, permettant d'aller de l'écran d'accueil vers l'écran d'un nouveau mémo. Pourquoi pas une commande pour ouvrir un mémo existant... peut-être "edit" ? On pourrait, en effet. Mais ici, je vous propose une structure plus simple :

```
Mémos (BACK pour revenir à l'écran précédent, EXIT pour quitter, HELP pour obtenir de l'aide)

( Entrez NEW pour créer un nouveau mémo.
  Ou un numéro de mémo pour l'éditer. )

 1 - Ne pas oublier de nourir les animaux et les plantes avant de partir demain.
 2 - Le téléphone de Stella est 000-0000, apeler avant samedi.
 3 - La facture d'électricité est à payer avant le 12 mars, plus de délai !

Mémos: 3
```

Si vous entrez "NEW", vous pouvez créer un nouveau mémo. Si vous entrez un numéro, vous ouvrirez un mémo existant et pourrez l'éditer. Nous pourrions créer une commande pour chaque numéro, mais ce ne serait pas le plus intuitif. Nous allons implémenter cette option plus simplement, en redirigeant l'entrée de l'utilisateur et vérifier qu'il s'agisse d'un nombre.

### Stockage de données

Peut-être vous êtes-vous demandé : où allons-nous stocker nos mémos ? C'est une question légitime. Le système des apps sur AvenOS permet de facilement conserver des données à plusieurs endroits. Nous pouvons conserver des informations dans l'app elle-même ou dans un écran de l'app.

> Quelle est la différence ?

En règle générale, on garde les données sur l'app quand :

1. On veut conserver des informations dont plusieurs écrans auront besoin.
2. On veut conserver des informations sur l'app elle-même, qui peuvent être accessibles depuis d'autres apps si besoin.
3. On a besoin d'informations permanentes et valides jusqu'à ce qu'on les supprime explicitement.

D'un autre côté, on conserve les données sur l'écran quand :

1. On veut garder des informations qui ne seront valables que pour cet écran spécifiquement.
2. Les informations conservées ne sont pas "vitales", on peut éventuellement faire sans si besoin.

Ainsi, dans notre cas, ce serait plus logique de conserver les mémos sur l'app elle-même : les mémos sont accessibles depuis différents écrans de l'app, et on ne veut certainement pas qu'il soit supprimé ou remplacé par erreur.

> Que pourrions-nous conserver sur un écran, finalement ?

L'édition de champ de texte est un excellent exemple d'information qu'il serait préférable de conserver sur un écran. Dans notre classe `EcranMemo`, qui permet d'ajouter un nouveau mémo ou éditer un mémo existant, nous allons conserver le texte en cours d'édition. Nous avons aussi besoin de conserver le mémo en cours d'édition pour l'éditer rapidement. Vous verrez de nombreux exemples de cas où conserver sur un écran est davantage pratique et logique.

Dans les deux cas, l'information peut être conservée en utilisant la propriété `db`, soit sur l'app, soit sur l'écran. La propriété `db` contient un dictionnaire (ou un `_SaverDict` pour être précis)i dans lequel vous pouvez écrire des informations qui seront sauvegardées automatiquement. Vous verrez plusieurs exemples dans la suite de ce tutoriel. Voici notre écran principal avec une gestion simple des données :

```python
class EcranPrincipal(BaseScreen):

    """Écran principal, affichant 'bonjour'."""

    def get_text(self):
        """Retourne le texte à afficher."""
        memos = self.app.db.get("memos", [])
        texte = "Mémos"
        texte += "\n\n( Entrez NEW pour créer un nouveau mémo."
        texte += "\n  Ou un numéro pour éditer un mémo existant. )\n"

        # Ajouter les mémos existants
        i = 1
        for ligne in memos:
            contenu = ligne.get("contenu")
            texte += "\n {i} - {contenu}".format(i=i, contenu=contenu)
            i += 1

        # Affiche la dernière ligne
        texte += "\n\nMémos: {}".format(len(memos))
        return texte
```

Nous avons changé la façon dont notre texte est affiché. Le texte est un peu moins lisible sous cette forme, mais il permet davantage de dynamisme. Notez que vous pouvez combiner le confort et le dynamisme assez simplement, en utilisant par exemple la méthode `.format()`.

Notre première ligne dans `get_text` mérite une seconde d'attention : `memos = self.app.db.get("memos", [])` .  `self.app` contient l'app (un objet créé depuis notre classe `Memo`).  Ainsi, `self.app.db` contient un dictionnaire des données persistantes conservées sur l'app elle-même.  On l'utilise donc comme un dictionnaire tout ce qu'il y a de plus normal : nous essayons de récupérer une valeur (appelée `memos`) et précisons une valeur par défaut (la case du dictionnaire pourrait ne pas exister, elle n'existera pas si vous ouvrez l'app et n'avez pas encore enregistré de mémo).

ainsi, `memos` contient une liste. Elle peut être vide si la case n'existe pas dans le dictionnaire. Si elle ne l'est pas, que contient-elle ? Et bien... chaque case de la liste est un autre dictionnaire ! Dans Evennia, on évite de conserver des objets directement dans la base de donnée. Cela aurait été plus lisible, mais il est préférable de conserver chaque mémo comme un dictionnaire. Noter qu'on aurait pu conserver le texte du mémo tout simplement : chaque case de la liste aurait pu être une chaîne (`str`). Cela aurait été plus clair. Mais conserver des dictionnaires nous permettra d'ajouter d'autres champs pour chaque mémo. Quelques lignes plus tard, on parcourt notre liste. `ligne` contient donc un dictionnaire (un mémo). On cherche la case `contenu` dans ce dictionnaire et l'utilisons comme le texte contenu dans le mémo.

Si cela vous aide, voici un exemple possible de contenu dans `self.apps.db` :

```
"memos": [
    { "contenu": "Ne pas oublier de nourrir les animaux et les plantes avant de partir demain." },
    { "contenu": "Le téléphone de Stella est 000-0000, appeler avant samedi."},
    { "contenu": "La facture d'électricité est à payer avant le 12 mars, plus de délai !" }
]
```

> Puis-je essayer ce code de l'écran ?

Vous pouvez, oui. Mettez à jour le code de l'écran avec l'exemple de la classe `EcranPrincipal` donné au-dessus. Cela dit, je vous conseille d'ajouter un mémo à la main pour rendre le test plus intéressant :

Après avoir mis à jour `EcranPrincipal`, rechargez Evennia (avec `@reload` par exemple). Si ce n'est pas déjà fait, ouvrez l'interface AvenOS (`use aven`).

Avant d'ouvrir l'app `mémo`, nous allons ajouter un mémo à la main. La commande suivante devrait s'en charger (vous pouvez la copier-coller dans votre client).

    @py self.search("aven").types.get("computer").apps.get("memo").db["memos"] = [{"contenu": "Ne pas oublier de nourrir les animaux et les plantes avant de partir demain."}]

Vous pouvez maintenant ouvrir votre app en entrant `memo`.

```
Mémos (BACK pour revenir à l'écran précédent, EXIT pour quitter, HELP pour obtenir de l'aide)

( Entrez NEW pour créer un nouveau mémo.
  Ou un numéro pour éditer un mémo existant. )

 1 - Ne pas oublier de nourrir les animaux et les plantes avant de partir demain.

Mémos: 1
```

> Incroyable, cela marche ! Puis-je ajouter d'autres mémos pour tester ?

Vous pouvez, je vous conseilleais simplement d'utiliser une autre commande, car maintenant, la liste existe bel et bien :

    @py self.search("aven").types.get("computer").apps.get("memo").db["memos"].append({"contenu": "<insérer votre texte ici>"}]

> J'en ai ajouté de nouveaux, mais je dois quitter l'écran avec BACK et y retourner pour voir les changements.

En effet, vous pouvez mettre à jour l'écran en fermant l'écran (BACK) et ouvrir l'écran à nouveau (memo). Plus simplement, vous pouvez appuyer sur ENTRÉE sans aucune commande, cela mettra à jour l'écran.

### Ajoutons un second écran

> Tout ça c'est bien beau mais on ne peut toujours pas ajouter de nouveaux mémos, sauf en utilisant la commande contre-intuitive avec `@py`.

C'est ce que nous allons faire ici. Et pour y arriver, nous allons ajouter un nouvel écran !

> Pourquoi un nouvel écran ? Ne pourrions-nous éditer les mémos directement dans l'écran principal ?

Vous pourriez. Mais les utilisateurs de l'app pourraient apprécier un nouvel écran. Notre app mémo n'est peut-être pas très grande pour l'instant, mais elle peut très bien grandir au-delà de ce que vous aviez imaginé. Rappelez-vous : AvenOS doit rester flexible et intuitif pour les utilisateurs. Et c'est plus intuitif d'entrer une commande courte (ou de cliquer dessus) que d'entrer une commande avec plusieurs paramètres pour se simplifier la tâche. Dans tous les cas, ajouter un nouvel écran n'est vraiment pas bien dur. Et j'ajouterai que nous utiliserons le même écran pour créer un nouveau mémo ou en éditer un existant.

Donc... que doit-on faire dans ce nouvel écran ?

Je vous propose un écran très simple : un écran juste pour éditer le texte du mémo. Quand vous ouvrez l'écran, le texte du mémo apparaît. Si vous entrez du texte, le texte du mémo est mis à jour et l'écran est refermé.

Essayons donc de coder notre écran. Dans votre fichier "memo.py", sous la classe `EcranPrincipal`, ajoutons notre écran :

```python
class EcranMemo(BaseScreen):

    """Ajoute ou édite un mémo.

    Cet écran permet d'ajouter un nouveau mémo ou éditer un mémo existant.
    Si l'utilisateur entre du texte dans cet écran, le texte du mémo
    sera mis à jour et l'écran se refermera.

    """

    back_screen = EcranPrincipal

    def get_text(self):
        """Retourne le texte à afficher."""
        memo = self.db.get("memo", {})
        if memo:
            titre = "Édition d'un mémo"
        else:
            titre = "Nouveau mémo"
        contenu = memo.get("contenu", "(Entrez le texte de votre mémo ici.)")
        if "contenu" in self.db:
            contenu = self.db["contenu"]

        return """
            {titre}

            Texte:
                {contenu}

                    SAVE pour sauvegarder
        """.format(titre=titre, contenu=contenu)
```

Cet exemple n'est pas trop différent de ce que nous avons vu jusqu'à présent. Sauf quelques petites choses qu'il est bon de noter :

1. Cette fois-ci, nous créons une variable de classe appelée `back_screen`. Elle contient l'écran auquel nous devrions aller si nous entrons la commande "back". C'est une bonne habitude à prendre : toujours avoir un `back_screen` configuré, sauf pour l'écran d'accueil (celui spécifié par la classe variable `start_screen` dans l'app) pour qui cela n'est pas nécessaire. La variable `back_screen` n'est normalement pas utilisée. Quand l'utilisateur navigue d'écran en écran, la liste des écrans est conservée et "back" permet juste de revenir à l'écran précédent dans la liste. Dans certains cas, cependant, il n'y a pas d'écran précédent explicite, et la variable `back_screen` sera utilisée comme choix par défaut.
2. On part du principe que notre mémo est conservé sur notre écran, dans la case `memo`. Ce mémo devrait être un dictionnaire. Si la case n'existe pas, l'écran part du principe qu'il s'agit d'un mémo vide. Si cette case existe, il affichera "édition" dans le titre, sinon "nouveau" pour indiquer que le mémo n'a pas encore été enregistré.
3. Le texte du mémo peut aussi être conservé sur l'écran, dans la case "contenu". Nous verrons plus en détail pourquoi stocker le texte à part, pour l'instant, souvenez-vous simplement que `self.db` peut contenir la case `contenu`.

> Bien... notre écran marche mais comment y accéder pour le vérifier ? Notre seul écran pour l'instant est `EcranPrincipal`.

### Changer d'écran

Il y a trois moyens pour changer l'écran actuel, et toutes trois sont des méthodes sur la classe `BaseScreen` :

- `back()`: cette méthode referme l'écran actuel et cherche l'écran précédent, comme la commande "back". C'est une fonctionnalité fréquemment utilisée.
- `move_to()`: Cette méthode permet de se déplacer vers un nouvel écran. Elle a besoin de savoir vers quel écran l'on veut se déplacer. Elle possède certaines options que nous détaillerons plus tard. Contrairement à l'apparence, ce n'est pas la méthode que nous utilisons le plus fréquemment.
- `next`: cette méthode a exactement le même comportement que `move_to`, sauf qu'elle écrit le nouvel écran dans la liste des écrans visitées (le screen tree).

Pour rappel, le screen tree est ici pour se souvenir de tous les écrans ouverts par l'utilisateur. Quand vous ouvrez l'interface AvenOS, un élément est ajouté dans le screen tree. Si vous ouvrez une application, un nouvel élément est ajouté dans le screen tree. Et ainsi de suite. Si vous entrez la commande "back", le screen tree sera lu pour savoir quel est l'écran précédent. Le dernier élément du screen tree sera retiré.

> Pourquoi voudrais-je rediriger vers un autre écran sauf que celui-ci apparaisse dans le screen tree ?

C'est assez rare, en effet. La plupart du temps, vous utiliserez la méthode `next` qui écrit dans le screen tree. Quand vous utilisez des écrans très génériques, comme des boîtes de dialogue ou confirmation, vous pourriez vouloir ouvrir un écran sans que celui-ci ne soit accessible si l'utilisateur entre "back".

Regardons la méthode `next` de plus près. Souvenez-vous : `move_to` a exactement les mêmes paramètres :

- `screen`: le nouvel écran à ouvrir. Ce peut être une classe dérivée de `BaseScreen` ou bien un chemin menant à cette classe (comme `EcranPrincipal` ou `auto.apps.base.MinScreen`).
- `app`: l'application du nouvel écran. Si vous ne précisez pas cette option, ce sera la même application que l'écran actuel, ce qui est souvent le comportement souhaité.
- `db`: un dictionnaire optionnel contenant les données à écrire dans le nouvel écran. Ces données seront écrites dans la propriété `db` du nouvel écran.

Dans notre exemple, le paramètre `screen` sera `EcranMemo`, puisque nous voulons rediriger vers cet écran. Cependant, `EcranMemo` a besoin de quelques données, souvenez-vous.

- `memo` est un dictionnaire contenant le mémo en cours d'édition.
- `contenu` est un champ de texte optionnel contenant le texte actuel du mémo.

Nous utiliserons donc `.next()` de cette façon :

```python
screen.next("EcranMemo", db=dict(memo=memo, contenu=contenu))
```

Voyons maintenant où mettre cette ligne de code.

### Rediriger l'entrée utilisateur

Peut-être vous souvenez-vous : j'ai conseillé de pouvoir éditer un mémo actuel en entrant simplement un numéro. "Entrer un nombre" signifie que nous aurons besoin de récupérer les commandes qu'envoie l'utilisateur. Il y a une méthode très simple dans `BaseScreen` que vous pouvez remplacer pour ce faire. Son nom est `no_match`, et elle ne prend qu'un argument : le texte entré par l'utilisateur dans une `str`.

Nous allons donc ajouter cette méthode à notre `EcranPrincipal` pour rediriger sur `EcranMemo` si l'utilisateur a entré un nombre valide.

```python
# ...
## Screens
class EcranPrincipal(BaseScreen):

    """Écran principal, affichant 'bonjour'."""

    def get_text(self):
        """Retourne le texte à afficher."""
        memos = self.app.db.get("memos", [])
        texte = "Mémos"
        texte += "\n\n( Entrez NEW pour créer un nouveau mémo."
        texte += "\n  Ou un numéro pour éditer un mémo existant. )\n"

        # Ajouter les mémos existants
        i = 1
        for ligne in memos:
            contenu = ligne.get("contenu")
            texte += "\n {i} - {contenu}".format(i=i, contenu=contenu)
            i += 1

        # Affiche la dernière ligne
        texte += "\n\nMémos: {}".format(len(memos))
        return texte

    def no_match(self, texte):
        """Appelée quand aucune commande ne correspond à l'entrée utilisateur.

        Nous avons besoin de tester `texte` pour voir si cette chaîne
        contient un nombre valide. Si oui, redirige vers l'écran `EcranMemo`.

        """
        # Souvenez-vous, la liste des mémos doit se trouver dans `self.db`
        memos = self.app.db.get("memos", [])

        # Essaye de convertir l'entrée utilisateur
        try:
            nombre = int(texte)
            assert nombre > 0
            memo = memos[nombre - 1]
        except (ValueError, AssertionError, IndexError):
            self.user.msg("Ce nombre n'est pas valide.")
        else:
            contenu = memo.get("contenu")
            # Ouvre EcranMemo
            self.next("EcranMemo", db=dict(memo=memo, contenu=contenu))

        return True

# ...
```

Je vous donne ici le code complet de la classe `EcranPrincipal`. Souvenez-vous : vous avez aussi besoin de la classe `Memo` (au-dessus) et l'autre écran (`EcranMemo`) au-dessous. Si vous commencez à être perdu, vous trouverez le code complet du fichier dans une autre section.

Rechargez Evennia. Ouvrez AvenOS, puis votre app "mémo". Puis entrez `1`. Si vous avez au moins un mémo d'enregistré, celui-ci devrait s'ouvrir dans `EcranMemo`.

```
Édition d'un mémo (BACK pour revenir à l'écran précédent, EXIT pour quitter, HELP pour obtenir de l'aide)

Texte:
    Ne pas oublier de nourrir les animaux et les plantes avant de partir demain.

        SAVE pour sauvegarder
```

Cela marche ! Le nouvel écran s'ouvre et on voit bien le texte de notre mémo... on ne peut l'éditer encore, mais une chose à la fois. Revenons un peu sur la méthode `no_match` d'abord, certaines choses pourraient ne pas être explicites.

- Une fois encore, n'oubliez pas que `no_match` prend un argument à part `self`: le texte entré par l'utilisateur. Cette méthode est appelée si aucune commande ne correspond à l'entrée de l'utilisateur.
- On obtient les mémos de la même façon qu'avant. Ce sera une liste de dictionnaires. Elle pourrait ne pas exister, on s'assure donc d'avoir une liste quoiqu'il arrive.
- On convertit ensuite l'entrée de l'utilisateur et faisons quelques vérifications en plus. L'entrée de l'utilisateur doit être un nombre entre 1 et N, mais nous devons vérifier qu'il s'agisse bien d'un numéro valide. Le faire ainsi dans un bloc `try/except` est une façon très "pythonique" de vérifier la validité de l'entrée.
- Si une erreur se produit, on envoie un message d'explication à l'utilisateur, contenu dans `self.user`. Cet attribut contient le personnage (Character) utilisant l'interface à ce moment. Comme nous l'avons vu, vous avez aussi `self.app` qui pointe vers un objet de l'app (`Memo` ici).
- Si il n'ý a pas eu d'erreur, on a une variable `memo` qui contient un élément de la liste des mémos, c'est-à-dire un dictionnaire (un mémo). On crée aussi la variable `contenu` qui contient le contenu du mémo.
- Pour finir, on appelle `self.next` pour rediriger vers `EcranMemo`. Les paramètres ne devraient normalement pas vous surprendre à ce stade.
- La méthode `no_match` doit retourner `True` or `False`. `True` indique que l'entrée utilisateur a été lue et traitée, `False` indique qu'il faut envoyer un message d'erreur à l'utilisateur. Puisqu'ici nous traitons le cas où l'entrée n'est pas valide, on retourne `True` quoiqu'il arrive.

Et voilà. On peut maintenant éditer un mémo (en tous cas, l'ouvrir et voir son texte dans notre nouvel écran).

Vous pourriez essayer de créer la méthode `no_match` sur `EcranMemo`, pour mettre à jour le texte du mémo. Ce n'est pas bien difficile et offre un bon exercice. Vous avez déjà tout ce qu'il faut pour coder cette méthode. Je vous conseille d'essayer de coder cette méthode avant de regarder la solution un peu plus bas. Cela dit, n'hésitez pas à regarder la solution si vous êtes bloqués.

Là encore, demandons-nous, que doit-on faire dans notre `EcranMemo`? Simplement, si l'utilisateur entre du texte, on pourrait mettre à jour le texte du mémo. Faisons cela pour commencer, on mettra à jour cette méthode ensuite.

```python
class EcranMemo(BaseScreen):

    """Ajoute ou édite un mémo.

    Cet écran permet d'ajouter un nouveau mémo ou éditer un mémo existant.
    Si l'utilisateur entre du texte dans cet écran, le texte du mémo
    sera mis à jour et l'écran se refermera.

    """

    back_screen = EcranPrincipal

    def get_text(self):
        """Retourne le texte à afficher."""
        memo = self.db.get("memo", {})
        if memo:
            titre = "Édition d'un mémo"
        else:
            titre = "Nouveau mémo"
        contenu = memo.get("contenu", "(Entrez le texte de votre mémo ici.)")
        if "contenu" in self.db:
            contenu = self.db["contenu"]

        return """
            {titre}

            Texte:
                {contenu}

                    SAVE pour sauvegarder
        """.format(titre=titre, contenu=contenu)

    def no_match(self, texte):
        """Cette méthode est appelée quand aucune commande ne correspond."""
        memo = self.db.get("memo", {})
        memo["contenu"] = texte

        # Ferme cet écran et revient à l'écran précédent
        self.back()
        return True
```

> Et bien, cette méthode `no_match` est très courte.

- On récupère le mémo. Là encore, souvenez-vous qu'il s'agit d'un dictionnaire sauvegardé dans la propriété `db`, case `"memo"`.
- On place simplement l'entrée de l'utilisateur dans la case `contenu` du mémo.
- Puis on appelle `self.back()` pour fermer l'écran actuel et revenir à l'écran précédent.
- N'oubliez pas de retourner `True`.

> Et c'est tout ?

C'est tout. Rechargez le jeu, ouvrez votre app, éditez un mémo, entrez un texte différent, appuyez sur ENTRÉE et le mémo devrait être mis à jour. Vous serez de retour dans l'écran d'accueil.

> On a juste changé un dictionnaire... comment cela peut-il être sauvegardé automatiquement ?

Tout ce qui se trouve dans `db` (que ce soit dans l'app ou dans l'écran) est persistant. Modifier une simple clé dans le dictionnaire provoquera l'enregistrement automatique du dictionnaire dans la base de données. Vous n'avez pas besoin de trop vous tracasser à propos du mécanisme, c'est une fonctionnalité très pratique d'Evennia.

### Et une commande d'écran

Pour que notre app soit réellement utilisable, nous devrions aussi créer une commande : la commande "new", accessible dans "EcranPrincipal", permettant de créer un nouveau mémo. Créer une commande d'écran n'est pas différent de créer une commande dans Evennia, sauf qu'on utilise `AppCommand` comme parent. À la fin du fichier "memo.py", créez une nouvelle section et ajoutez les lignes suivantes :

```python
# ...

## Commandes

class CmdNew(AppCommand):

    """
    Crée un nouveau mémo.

    Usage :
      new

    """

    key = "new"
    aliases = ["nouveau"]

    def func(self):
        """Corps de la commande."""
        ecran = self.screen
        ecran.next("EcranMemo")
```

Si vous êtes familier des commandes dans Evennia, rien ne devrait trop vous surprendre... sauf une petite chose. C'est quoi cette variable `self.screen` qu'on utilise dans le corps ? C'est un petit plus des `AppCommand`, elles savent quelle écran les a appelé. Et avoir cette information nous rendra la vie plus bien simple. Puisque nous avons accès à l'écran, nous pouvons maintenant rediriger vers `EcranMemo`.

> Pourquoi on ne spécifie pas d'argument dans `db` cette fois ?

Bonne quesiton. Puisque l'on souhaite créer un nouveau mémo, le mémo (dans son dictionnaire) n'existe pas encore à ce stade. On aura besoin de le créer quand on appuie sur ENTRÉE.

Il reste une dernière chose : nous devons dire à l'écran utilisant cette commande qu'il a accès à notre `AppCommand`. On utilise une autre variable de classe pour ce faire : `commands`, qui contient une liste de noms d'`AppCommand` à utiliser dans cet écran. Dans quel écran doit-on avoir accès à notre commande "new"? `EcranPrincipal` :

```python
class EcranPrincipal(BaseScreen):

    """Écran principal, affichant 'bonjour'."""

    commands = ["CmdNew"]

    # ...
```

Là encore, si vous commencez à vous perdre et ne trouvez pas les emplacements à mettre à jour, vous trouverez le code complet de l'app dans une section un peu plus bas.

Tout ce que nous avons fait, c'est créer une variable de classe `commands` dans notre écran, contenant la liste des commandes utilisables dans cet écran. Nous n'avons qu'une commande utilisable dans `EcranPrincipal` pour l'heure.

Rechargeons Evennia et ouvrons l'app de novueau !

Utilisez votre téléphone, ouvrez l'application, puis entrez `new` pour créer un nouveau mémo. Vous devriez voir le texte suivant :

```
Nouveau mémo (BACK pour revenir à l'écran précédent, EXIT pour quitter, HELP pour obtenir de l'aide)

Texte:
    (Entrez le texte de votre mémo ici.)

        SAVE pour sauvegarder
```

> Si j'entre du texte et appuie sur ENTRÉE, rien ne se passe, l'écran se ferme.

C'est parce que `EcranMemo` veut un mémo, et jusqu'ici notre mémo n'existe pas. Donc rien ne se passe dans ce cas. Ajoutons cette gestion dans la méthode `no_match` de `EcranMemo` :

```python
class EcranMemo(BaseScreen):

    """Ajoute ou édite un mémo.

    Cet écran permet d'ajouter un nouveau mémo ou éditer un mémo existant.
    Si l'utilisateur entre du texte dans cet écran, le texte du mémo
    sera mis à jour et l'écran se refermera.

    """

    back_screen = EcranPrincipal

    # ...

    def no_match(self, texte):
        """Cette méthode est appelée quand aucune commande ne correspond."""
        memo = self.db.get("memo", {})

        if memo:
            memo["contenu"] = texte
        else:
            # Si le mémo est vide (n'existe pas), crée un nouveau
            if "memos" not in self.app.db:
                self.app.db["memos"] = []
            self.app.db["memos"].insert(0, {"contenu": texte})

        # Ferme l'écran et revient au menu précédent
        self.back()
        return True
```

> Quelle est la nouveauté dans cette nouvelle méthode `no_match` ?

Au lieu de changer une case du mémo quoiqu'il arrive, on vérifie si le mémo existe. Si ce n'est pas le cas (le mémo est un dictionnaire vide), on en ajoute un, dans `self.app.db["memos"]`. Si vous rechargez Evennia et esszyez de créer un nouveau mémo ou d'en éditer un existant, les deux devraient à présent marcher !

### Pour conclure cet exemple

C'était juste un premier exemple, mais il a permit de montrer la classe de l'application, les classes d'écran et les classes de commande, comment elles interagissent l'une avec l'autre, et comment sauvegarder des données. N'hésitez pas à regarder le code d'autres apps. Ces autres apps peuvent être plus longues et un peu plus complexes que cet exemple. Voici le code complet de l'exemple :

```python
# -*- coding: utf-8 -*-

"""
App mémo : conserve des notes courtes entrées par l'utilisateur de l'application.

Écrans:
    EcranPrincipal : écran affichant la liste des mémos enregistrés.
    EcranMemo: écran affiché pour créer ou éditer un mémo.
Commandes :
    CmdNew: Commande pour créer un nouveau mémo.

"""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

## Classe de l'application

class Memo(BaseApp):

    """
    App mémo.

    Vous pouvez ajouter davantage de détails ici à l'adresse des développeurs.
    Par exemple, une liste des méthodes les plus importantes peut être utile.

    """

    app_name = "memo"
    display_name = "Mémo"
    start_screen = "EcranPrincipal"


## Écrans de l'application

class EcranPrincipal(BaseScreen):

    """Écran principal, affichant 'bonjour'."""

    commands = ["CmdNew"]

    def get_text(self):
        """Retourne le texte à afficher."""
        memos = self.app.db.get("memos", [])
        texte = "Mémos"
        texte += "\n\n( Entrez NEW pour créer un nouveau mémo."
        texte += "\n  Ou un numéro pour éditer un mémo existant. )\n"

        # Ajouter les mémos existants
        i = 1
        for ligne in memos:
            contenu = ligne.get("contenu")
            texte += "\n {i} - {contenu}".format(i=i, contenu=contenu)
            i += 1

        # Affiche la dernière ligne
        texte += "\n\nMémos: {}".format(len(memos))
        return texte

    def no_match(self, texte):
        """Appelée quand aucune commande ne correspond à l'entrée utilisateur.

        Nous avons besoin de tester `texte` pour voir si cette chaîne
        contient un nombre valide. Si oui, redirige vers l'écran `EcranMemo`.

        """
        # Souvenez-vous, la liste des mémos doit se trouver dans `self.db`
        memos = self.app.db.get("memos", [])

        # Essaye de convertir l'entrée utilisateur
        try:
            nombre = int(texte)
            assert nombre > 0
            memo = memos[nombre - 1]
        except (ValueError, AssertionError, IndexError):
            self.user.msg("Ce nombre n'est pas valide.")
        else:
            contenu = memo.get("contenu")
            # Ouvre EcranMemo
            self.next("EcranMemo", db=dict(memo=memo, contenu=contenu))

        return True


class EcranMemo(BaseScreen):

    """Ajoute ou édite un mémo.

    Cet écran permet d'ajouter un nouveau mémo ou éditer un mémo existant.
    Si l'utilisateur entre du texte dans cet écran, le texte du mémo
    sera mis à jour et l'écran se refermera.

    """

    back_screen = EcranPrincipal

    def get_text(self):
        """Retourne le texte à afficher."""
        memo = self.db.get("memo", {})
        if memo:
            titre = "Édition d'un mémo"
        else:
            titre = "Nouveau mémo"
        contenu = memo.get("contenu", "(Entrez le texte de votre mémo ici.)")
        if "contenu" in self.db:
            contenu = self.db["contenu"]

        return """
            {titre}

            Texte:
                {contenu}

                    SAVE pour sauvegarder
        """.format(titre=titre, contenu=contenu)

    def no_match(self, texte):
        """Cette méthode est appelée quand aucune commande ne correspond."""
        memo = self.db.get("memo", {})

        if memo:
            memo["contenu"] = texte
        else:
            # Si le mémo est vide (n'existe pas), crée un nouveau
            if "memos" not in self.app.db:
                self.app.db["memos"] = []
            self.app.db["memos"].insert(0, {"contenu": texte})

        # Ferme l'écran et revient au menu précédent
        self.back()
        return True


## Commandes

class CmdNew(AppCommand):

    """
    Crée un nouveau mémo.

    Usage :
      new

    """

    key = "new"
    aliases = ["nouveau"]

    def func(self):
        """Corps de la commande."""
        ecran = self.screen
        ecran.next("EcranMemo")
```

Remarquez, nous n'avons pas fait tout ce que nous voulions faire. On ne peut supprimer un mémo. Quand on édite un mémo, on ne peut entrer plusieurs lignes de texte, le bouton SAVE ne sert à rien. Mais vous pouvez maintenant améliorer cette application, ce sera un bon entraînement !

## Fonctionnalités avancées

Cette section contient plusieurs explications avancées dédiées à certains sujets. Vous n'aurez probablement pas besoin de toutes les utiliser dans votre app, mais si vous avez besoin de l'une d'entre elles, cette section vous aidera. Comme toujours, le meilleur moyen d'obtenir de la documentation de référence est de lire le code, qui est abondamment documenté.

### Les écrans génériques
#### Demander confirmation à l'utilisateur
#### Afficher une boîte de dialogue avec un simple bouton OK
#### Un écran générique pour les options d'une app
### Notifications et statut d'app

An app can send notifications to alert the device of incoming information.  The text app, for instance, sends a notification to the recipients of a text when it is sent.  Additionally, an app can have a status (mark the number of items that should be read).  It is usually done through the app's display name (like "Text(3)" to say that 3 texts ought to be read).

Both systems (notifications and status) are independent.  An app can have none, either, or both of them.

#### Le statut de l'app dans son nom affiché

Changing the app status is quite simple: we used `display_name` as a class variable so far, defined on the app itself.  However, it can also have a `get_display_name` method that will return the name to be displayed.  This allows to display a name that will vary depending on the context.  Here, for instance, is the `Text` application `get_display_name` to give you an example:

```python
class TextApp(BaseApp):

    """Text applicaiton."""

    app_name = "text"
    display_name = "Text"
    start_screen = "MainScreen"

    def get_display_name(self):
        """Return the display name for this app."""
        number = self.get_phone_number(self.obj)
        unread = Text.objects.get_nb_unread(number)
        if unread:
            return "Text({})".format(unread)

        return "Text"
```

Don't worry about the two first lines of this method: it will simply get the phone number of the object and then, query the number of unread messages.  You will definitely adapt this example.  The next lines show you how to return a different name depending on status (the number of unread texts, in our case).

#### Envoyer des notifications

Notifications can be accessed through the `NotificationHandler`.  However, in most cases, we'll use two simple methods of every app:

- `notify`: send a notification to a user.
- `forget_notification`: forget one or more notifications.

Since `notify` takes a lot of arguments, we usually wrap its call in a screen.  It's not unheard of to have an app sending several types of notification.  A screen, however, usually sends only one type.  It is up to you, and you can definitely use these methods directly.

`notify` and `forget_notification` are class methods, so you can use them from outside of the class, which may be very handy at times.

##### notify

This method has the following arguments:

- `obj`: the object to notify, usually a phone or a computer depending on what is available.
- `title`: the title of the notification to be displayed.
- `message`: the message to be sent to the user of `obj`, if any.  If the user is not presently connected, this will be ignored.
- `content`: the content of the notification, a longer text.  This could be the received text for instance.
- `screen`: the screen having created this notification.  Notifications can be "answered", so a user could want to answer a notification.  For instance, if the recipient of a message is not logged in, she will be notified when login that notifications wait for her.  She can see them and answer them.  If she answers a message, for instance, the screen will be opened with the message content.  If you prefer, it's a bit like tapping on a notification on your smartphone to open it.  To do this, it needs the screen name and some other information.
- `db`: the database attributes to generate when opening the screen.  Again, this is screen-specific.
- `group`: notifications can be grouped.  This is useful to remove several notifications.  This argument is not necessary but it might be very handy.  See the following section for details on notification grouping.

As you can see, these are a lot of arguments that could be deduced by the screen itself.  That's why, when we need to notify the user, we often wrap the call to `notify` in a screen method.  Rather than a long explanation though, let's see the `notify` method of `NewTextScreen` in the `text` app.

```python
class NewTextScreen(BaseScreen):

    """This screen appears to write a new message, with possibly some
    fields that are pre-loaded.  This screen will appear to create
    a new message independent of any thread.  Note, however, that if
    the list of recipients matches a previous conversation, the new
    message will simply be appended to this previous thread.

    Data attributes you can use (in screen.db):
        recipients: a list of phone numbers representing the list of recipients.
        content: the new text content as a string.

    """

    # ... class variables and other methods

    @staticmethod
    def notify(obj, text):
        """Notify obj of a new text message.

        This is a shortcut to specifically send a "new message" notification
        to the object.  It uses the app's `notify` which calls the
        notification handler in time, doing just a bit of wrapping.

        Args:
            obj (Object): the object being notified.
            text (Text): the text message.

        """
        # Try to get the sender's phone number
        group = "text.thread.{}".format(text.thread.id)
        sender = TextApp.format(obj, text.sender)
        message = "{obj} emits a short beep."
        title = "New message from {}".format(sender)
        content = text.content
        screen = "auto.apps.text.ThreadScreen"
        db = {"thread": text.thread}
        TextApp.notify(obj, title, message, content, screen, db, group)
```

If someone is using the interface, he will receive the message "{obj} emits a short beep.".  Otherwise, the message will be sent to the object location (the room in which it sits, for instance) and a notification will be created.

##### forget_notification

In some cases, we want to erase the notifications we have sent.  This can happen, for instance, when opening the phone, the text app, and then reading a thread (conversation) for which we have been notified.  All notifications are deleted when answering one.  But if you open the phone using the `use` command, then notifications are not removed automatically.  And they shouldn't be.  So we need to remove them manually.

In the previous example, you might have noticed we specify a notification group.  In this example, it would be `text.thread.<thread_id>` with `thread_id` being a number.  Without detailing too much the working of the text app, threads are conversations and can contain several text messages.  So basically, all texts in a conversation have the same thread ID.

Assuming no none has ever used messages before, if you send a text to someone else, the text will have the thread ID 1.  If this someone answers, it will have the same thread ID, because it still is the same conversation.  So if you send a message, the "text.thread.1" notification will be created.  If you send another message to the same recipient, it will add a new notification with the same group: "text.thread.1".  When the recipient reads your messages, it should mark the notifications of group "text.thread.1" as read.

That's why `forget_notification` has a `group` argument.  This allows to remove several notifications with the same group.  If you don't specify a group, all notifications for this object will be removed.

You can set unique group notifications too.  Nothing forces you to keep a group with more than one notification.  It will, again, depend on your app.  For more information, read the `BaseApp.notify` and `BaseApp.forget_notification` methods.  You could also check to see how these methods are used in other apps.

### Jeux et invitations
### Payer depuis une app
## Développement
### Troubleshooting

> Mon app ne se charge pas et n'apparaît pas sur mon téléphone.

Il peut y avoir plusieurs choses empêchant une app de se charger convenablement. La première chose à faire est de vérifier si l'app a été chargée. Vous pouvez le faire grâcce à une commande `@py` :

    @py __import__("auto").types.high_tech.APPS

Cette commande devrait afficher un dictionnaire Python contenant en clé les dossiers, et en valeur un autre dictionnaire contenant en clé le nom des apps et en valeur la classe de l'application. Si vous ne voyez pas votre app dans ce dictionnaire, vérifiez les logs.

Le logger des apps se trouve dans `server/logs/app.log`. Ce fichier contient plusieurs informations de debug. Il contient aussi les erreurs qui se produisent au chargement des applications.

    11:59 [WARNING] Error while loading auto.apps.text: invalid syntax (text.py, line 677)

Si vous corrigez l'erreur et rechargez Evennia, admettant que vous n'ayez pas d'autre erreur, l'app devrait se charger convenablement. Les erreurs qui se produisent quand on utilise l'app sont gérées comme des traceback normaux.

> Mon app ne se charge pas et il n'y a aucune erreur dedans, aucune information dans les logs.

Certains fichiers ne sont même pas lus par le système responsable de charger les apps. Il est possible que vous ayez créé un tel fichier sans le savoir. Voici les règles. Les apps devraient se trouver dans des fichiers :

- Avec l'extension `.py`. D'autres extensions dans le répertoire sont ignorées.
- Dans le dossier `auto.apps` ou dans un sous-répertoire. Si vous avez placé votre fichier dans un sous-dossier, n'oubliez pas de mettre un fichier `__init__.py` dedans (il peut être vide).
- Doit contenir seulement un nom valide en Python. Une app nommée `quelquechose-de-bien.py` ne sera pas chargée, à cause des tirets dans son nom.
- Ne commence pas par un souligné (_). Les fichiers dont le nom commence par `_` sont ignorés.
- Ne doit pas être "base.py". Ce fichier est spécial pour le système et n'est pas directement chargé.

### Tester les apps pour leur stabilité
### Envoyer une app à Avenew

