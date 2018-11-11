# -*- coding: utf-8 -*-

"""Batch YAML reader, used to batch-build using YAML format.

In some respect, the batch-YAML utility is similar to the batch command or
batch code processor.  However, it is designed to offer a friendlier
interface to builders.  From the website (the builder web portal), builders
can upload the YAML file containing the area they have built.  YAML being a
very simple format, it is both easy to use and to read.  This sytstem allows
for relative independence in work (builders can work on one or several
files without knowing or caring about the other builders') while quicly
updating and replicating changes.  The workflow suggested by Avenew is as
follows:

1. Builders create their YAML files and describe their areas in it.
2. They install Avenew on their system and upload their YAML file locally, to see if it is correctly processed.
3. They check the proper working of their areas, locally.
4. They then upload their files to the server.

When some modification has to be made to an area, the proper workflow for
builders is to:

1. Fix the changes in their file (this is much easier to do to fix spelling errors for instance).,
2. Upload their file again.

The server will not duplicate all data and check, each time, that the
information is to be created or updated.

"""

from logic.geo import NAME_DIRECTIONS
from typeclasses.prototypes import PRoom
from typeclasses.rooms import Room
from world.batch import *
from world.log import batch as log
from world.utils import load_YAML

## Constants
NO_DOCUMENTS = """
    Le fichier que vous avez mis en ligne ne contient pas une liste valide
    de documents YAML. Consulter
    <a href=\"/wiki/doc/YAML\"">la syntaxe du fichier YML</a> pour une explication détaillée.
"""

def batch_YAML(content, author):
    """Apply a batch YAML file or stream.

    Args:
        content (stream): the YAML content to be processed.
        author (Object): the author of the change.

    """
    log.info("Batch YML start processing...")
    documents = load_YAML(content)
    messages = []

    if not isinstance(documents, list):
        messages.append(3, 0, NO_DOCUMENTS)
        return 0

    delayed = []
    for document in documents:
        to_do = []
        line = document.get("--begin", 0)
        messages.append((1, line, ""))
        type = document.get("type", [None, None])[0]

        if type == "info":
            continue
        elif type == "psalle":
            to_do = parse_proom(document, author, messages)
        elif type == "salle":
            to_do = parse_room(document, author, messages)
        elif type == "carrefour":
            to_do = parse_crossroad(document, author, messages)
        else:
            messages.append((1, line, "Type inconnu : {}".format(type)))

        # Apply to_do, if appropriate
        if to_do:
            first = to_do[0]
            del to_do[0]
            function, args, kwargs = first
            obj = function(*args, **kwargs)

            i = 0
            for function, args, kwargs in list(to_do):
                if kwargs.get("delay"):
                    del kwargs["delay"]
                    delayed.append((function, args, kwargs))
                    i += 1
                    continue

                if function is setattr:
                    key, value = args
                    subobj = obj
                    if "." in key:
                        for subkey in key.split(".")[:-1]:
                            subobj = getattr(subobj, subkey)
                    setattr(subobj, key.split(".")[-1], value)
                    continue
                elif isinstance(function, basestring):
                    function = getattr(obj, function)
                else:
                    args.insert(0, obj)

                function(*args, **kwargs)
                del to_do[i]

    # Apply delayed to_do
    for function, args, kwargs in delayed:
        for arg in args:
            log.info("{}".format(arg.__class__))
        function(*args, **kwargs)

    log.info("Batch YML processed.")
    return messages

def parse_proom(document, author, messages):
    """Parse a YAML document describing a room prototype."""
    to_do = []
    line = document.get("--begin", 0)
    ident = get_field(document, "ident", basestring, True, "", messages).strip()
    if not ident:
        messages.append((2, line,
                "Un prototype de salle (psalle) a besoin d'avoir un champ valide nommé 'ident'."))
        return

    if isinstance(ident, unicode):
        ident = ident.encode("utf-8")
    to_do.append((get_proom, [ident], {}))

    # Handle the description
    desc = describe(get_field(document, "description", basestring, False, "", messages))
    if desc:
        to_do.append((setattr, ["db.desc", desc], {}))

    # All is right, confirmation
    messages.append((0, line, "Le prototype de salle '{}' a bien été créé ou mis à jour.".format(ident)))

    return to_do

def parse_room(document, author, messages):
    """Parse a YAML document describing a room."""
    to_do = []
    line = document.get("--begin", 0)
    ident = get_field(document, "ident", basestring, True, "", messages).strip()
    if not ident:
        messages.append((2, line,
                "Une salle a besoin d'avoir un champ valide nommé 'ident'."))
        return

    if isinstance(ident, unicode):
        ident = ident.encode("utf-8")
    to_do.append((get_room, [ident], {}))

    # Handle the prototype
    prototype = get_field(document, "prototype", basestring, False, "", messages).strip()
    if prototype:
        if isinstance(prototype, unicode):
            prototype = prototype.encode("utf-8")
        proom = get_proom(prototype)
        to_do.append((setattr, ["prototype", proom], {}))

    # Handle the coordinates
    coords = get_field(document, "coords", list, False, [None, None, None], messages)
    if coords:
        # Check that X, Y and Z are integers
        if len(coords) != 3:
            messages.append((1, line, "Les coordonnées (champ 'coords') de cette salle doivent contenir une liste avec trois arguments : les coordonnées X, Y et Z. Exemple : coords: [1, 2, -5]"))
        elif not all([coord is None or isinstance(coord, int) for coord in coords]):
            messages.append((1, line, "Champ 'coords' : la seule valeur possible pour chacunes des coordonnées est une valeur nulle (none) ou un nombre entier."))
        else:
            x, y, z = coords

            # Check that these coords are free or that the same ident is shared by both
            other = Room.get_room_at(x, y, z)
            if other and other.ident != ident:
                messages.append((1, line, "Une autre salle (/{}, ident='{}') existe déjà à ces coordonnées (X={}, Y={}, Z={}). Ceci est considéré comme une erreu puisque deux salles ne peuvent avoir les mêmes coordonnées. Si elles possèdent également le même identifiant, la salle existante sera mise à jour avec les nouvelles coordonnées. Corrigez l'erreur avant de mettre en ligne ce fichier de nouveau.".format(other.id, other.ident, x, y, z)))
            else:
                to_do.append((setattr, ["x", x], {}))
                to_do.append((setattr, ["y", y], {}))
                to_do.append((setattr, ["z", z], {}))

    # Handle the title
    title = get_field(document, "titre", basestring, False, "", messages).strip()
    if title:
        to_do.append((setattr, ["key", title], {}))

    # Handle the description
    desc = describe(get_field(document, "description", basestring, False, "", messages))
    if desc:
        to_do.append((setattr, ["db.desc", desc], {}))
    if isinstance(desc, unicode):
        desc = desc.encode("utf-8")

    # Handle the exits
    exits = get_field(document, "sorties", list, False, [], messages)
    for exit in exits:
        if not isinstance(exit, dict):
            messages.append((1, line, "Cette salle définit des soties dans un format invalide. Le format attendu est une liste de dictionnaires. Vérifiez la syntaxe des exemples proposés."))
            break

        to_do.extend(parse_exit(exit, author, messages))

    # Handle the callbacks
    callbacks = get_field(document, "callbacks", list, False, [], messages)
    for callback in callbacks:
        if not isinstance(callback, dict):
            messages.append((1, line, "This room specifies callbacks, but not as a list of dictionaries.  Check your syntax."))
            break

        to_do.extend(parse_callback(callback, author, messages))

    # All is right, confirmation
    messages.append((0, line, "La salle '{}' a été créée ou mise à jour avec succès.".format(ident)))

    return to_do

def parse_exit(document, author, messages):
    """Parse a single exit."""
    line = document.get("--begin", 0)
    args = []
    kwargs = {}
    direction = get_field(document, "direction", basestring, True, "", messages).lower().strip()
    if not direction:
        messages.append((2, line,
                "Une sortie doit posséder un champ valide nommé 'direction'."))
        return []

    if isinstance(direction, unicode):
        direction = direction.encode("utf-8")

    if direction not in NAME_DIRECTIONS.keys():
        messages.append((2, line,
                "Une sortie a été définie avec une direction incorrecte : '{}'.".format(direction)))
        return []
    args.append(direction)

    # Handle the destination
    destination = get_field(document, "destination", basestring, True, "", messages).strip()
    if not destination:
        return []
    else:
        if isinstance(destination, unicode):
            destination = destination.encode("utf-8")
        room = get_room(destination)
        args.append(room)

    # Handle the name
    name = get_field(document, "nom", basestring, False, "", messages).strip()
    if name:
        kwargs["name"] = name

    # Handle the aliases
    aliases = get_field(document, "alias", list, False, [], messages)
    if aliases:
        for i, alias in enumerate(aliases):
            if not isinstance(alias, basestring):
                aliases[i] = str(alias)

        kwargs["aliases"] = aliases

    # All is right, confirmation
    messages.append((0, line, "La sortie '{}' menant vers '{}' a bien été créée ou mise à jour.".format(direction, destination)))

    return [(get_exit, args, kwargs)]

def parse_callback(document, author, messages):
    """Parse a single callback."""
    line = document.get("--begin", 0)
    args = []
    kwargs = {"author": author}
    event = get_field(document, "event", basestring, True, "", messages).lower().strip()
    if not event:
        messages.append((2, line,
                "A callback needs to have a valid field name 'event'."))
        return []

    if isinstance(event, unicode):
        event = event.encode("utf-8")

    args.append(event)

    # Handle the destination
    number = get_field(document, "number", int, False, 0, messages)
    args.append(number)

    # Handle the code
    code = get_field(document, "code", basestring, True, "", messages).strip()
    if not code:
        messages.append((2, line,
                "A callback needs to have a valid field name 'code'."))
        return []
    if isinstance(code, unicode):
        code = code.encode("utf-8")
    kwargs["code"] = code

    # Handle the parameters
    parameters = get_field(document, "params", basestring, False, "", messages)
    if parameters:
        kwargs["parameters"] = parameters

    # All is right, confirmation
    messages.append((0, line, "The '{}'.{} callback was succesfully created or updated.".format(event, number)))

    return [(add_callback, args, kwargs)]

def parse_crossroad(document, author, messages):
    """Parse a YAML document describing a crossroad."""
    to_do = []
    line = document.get("--begin", 0)
    ident = get_field(document, "ident", basestring, True, "", messages).strip()
    if not ident:
        messages.append((2, line,
                "Un carrefour doit avoir un champ 'ident'."))
        return

    if isinstance(ident, unicode):
        ident = ident.encode("utf-8")

    # Handle the coordinates
    coords = get_field(document, "coords", list, False, [None, None, None], messages)
    if coords:
        # Check that X, Y and Z are integers
        if len(coords) != 3:
            messages.append((1, line, "Le champ de coordonnées ('coords') de ce carrefour attend 3 arguments dans une liste (X, Y et Z). Vérifiez la syntaxe."))
        elif not all([isinstance(coord, int) for coord in coords]):
            messages.append((1, line, "Champ 'coords': la valeur de chaque coordonnée doit être un entier"))
        else:
            x, y, z = coords

            # Check that these coords are free or that the same ident is shared by both
            other = Crossroad.get_crossroad_at(x, y, z)
            if other and other.ident != ident:
                messages.append((1, line, "Un autre carrefour (#{}, ident='{}') exite déjà à ces coordonnées (X={}, Y={}, Z={}). Ceci est considéré une erreur car deux carrefours ne peuvent partager les mêmes corodonnées et différents identifiants. Si ils possèdent le même identifiant cependant, l'ancien sera mis à jour. Corrigez l'erreur avant de réessayer.".format(other.id, other.ident, x, y, z)))
            else:
                to_do.append((get_crossroad, [x, y, z, ident], {}))

                # Be sure to create the crossroad right away
                origin = get_crossroad(x, y, z, ident)

    # Handle the streets
    streets = get_field(document, "rues", list, False, [], messages)
    for street in streets:
        if not isinstance(street, dict):
            messages.append((1, line, "Ce carrefour possède des rues mais qui ne sont pas décrites dans une liste de dictionnaires. Vérifiez la syntaxe."))
            break

        if "destination" not in street:
            messages.append((1, line, "La rue dans ce carrefour n'a pas de champ 'destination'."))
            continue

        destination, line = street["destination"]
        if isinstance(destination, unicode):
            destination = destination.encode("utf-8")
        destination = get_crossroad(ident=destination)
        name, line = street.get("nom", ("unknown street", line))
        back, line = street.get("back", (True, line))
        to_do.append((add_road, [origin, destination, name, back], {"delay": True}))

    # All is right, confirmation
    messages.append((0, line, "Le carrefour '{}' a bien été créé ou mis à jour.".format(ident)))

    return to_do

def get_field(document, field_name, types, required=True, default=None, messages=None):
    """Get the specified field, adding errors if appropriate.

    Args:
        document (dict): the document.
        field_name (str): the name of the field to get from the document.
        types (tuple): the authorized types of the field value.
        required (bool, optional): is this field mandatory?
        default (any, optional): the default value, returned if not present.
        messages (lsit): the list of messages, written in case of an error.

    """
    line = document.get("--begin", 0)

    if field_name in document:
        value = document[field_name]
        if isinstance(value, list):
            unpacked = []
            for v in value:
                if isinstance(v, (tuple, list)) and len(v) == 2:
                    unpacked.append(v[0])
                else:
                    unpacked.append(v)

            value = unpacked
        else:
            value, line = value

        if not isinstance(value, types):
            if isinstance(types, (list, tuple)):
                types = [types]

            expected = ", ".join([str(t) for t in types])
            messages.append((1, line,
                    "Le champ '{}' à la ligne {} n'est pas du bon type : {} attendu mais {} reçu".format(
                    field_name, line, expected, type(value))))
            return default

        return value
    elif required:
        messages.append((1, line,
                "Dans le document débutant à la ligne {}, le champ '{}' est attendu, et n'est pas présent dans le fichier mis en ligne.".format(line, field_name)))

    return default
