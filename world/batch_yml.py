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
from world.utils import load_YAML

## Constants
NO_DOCUMENTS = """
    The file you sent doesn't contain a valid list of documents.  See
    <a href=\"/wiki/doc/YAML\"">the YAML syntax</a> for proper usage.
"""

def batch_YAML(content, author):
    """Apply a batch YAML file or stream.

    Args:
        content (stream): the YAML content to be processed.
        author (Object): the author of the change.

    """
    documents = load_YAML(content)
    messages = []

    if not isinstance(documents, list):
        messages.append(3, 0, NO_DOCUMENTS)
        return 0

    for document in documents:
        to_do = []
        line = document.get("--begin", -1)
        messages.append((1, line, ""))
        type = document.get("type", [None, None])[0]

        if type == "proom":
            to_do = parse_proom(document, author, messages)
        elif type == "room":
            to_do = parse_room(document, author, messages)
        else:
            messages.append((1, line, "Unknown type: {}".format(type)))

        # Apply to_do, if appropriate
        if to_do:
            first = to_do[0]
            del to_do[0]
            function, args, kwargs = first
            obj = function(*args, **kwargs)

            for function, args, kwargs in to_do:
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

    return messages

def parse_proom(document, author, messages):
    """Parse a YAML document describing a room prototype."""
    to_do = []
    line = document.get("--begin", -1)
    ident = get_field(document, "ident", basestring, True, "", messages).strip()
    if not ident:
        messages.append((2, line,
                "A proom needs to have a valid field name 'ident'."))
        return

    if isinstance(ident, unicode):
        ident = ident.encode("utf-8")
    to_do.append((get_proom, [ident], {}))

    # Handle the description
    desc = describe(get_field(document, "description", basestring, False, "", messages))
    if desc:
        to_do.append((setattr, ["db.desc", desc], {}))

    # All is right, confirmation
    messages.append((0, line, "The proom '{}' was succesfully created or updated.".format(ident)))

    return to_do

def parse_room(document, author, messages):
    """Parse a YAML document describing a room."""
    to_do = []
    line = document.get("--begin", -1)
    ident = get_field(document, "ident", basestring, True, "", messages).strip()
    if not ident:
        messages.append((2, line,
                "A room needs to have a valid field name 'ident'."))
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
            messages.append((1, line, "The room coordinates ('coords' field) expects three arguments: X, Y and Z in a list.  Example: coords: [1, 2, -5]"))
        elif not all([coord is None or isinstance(coord, int) for coord in coords]):
            messages.append((1, line, "Field 'coords': the only acceptable value of each coordinate is either none or an integer"))
        else:
            x, y, z = coords

            # Check that these coords are free or that the same ident is shared by both
            other = Room.get_room_at(x, y, z)
            if other and other.ident != ident:
                messages.append((1, line, "Another room (#{}, ident='{}') already exists at these coordinates (X={}, Y={}, Z={}).  This is considered to be an error since two rooms cannot share the same coordinates.  If they had the same ident, the former will be updated.  Fix the issue before proceeding.".format(other.id, other.ident, x, y, z)))
            else:
                to_do.append((setattr, ["x", x], {}))
                to_do.append((setattr, ["y", y], {}))
                to_do.append((setattr, ["z", z], {}))

    # Handle the title
    title = get_field(document, "title", basestring, False, "", messages).strip()
    if title:
        to_do.append((setattr, ["key", title], {}))

    # Handle the description
    desc = describe(get_field(document, "description", basestring, False, "", messages))
    if desc:
        to_do.append((setattr, ["db.desc", desc], {}))

    # Handle the exits
    exits = get_field(document, "exits", list, False, [], messages)
    for exit in exits:
        if not isinstance(exit, dict):
            messages.append((1, line, "This room specifies exits, but not as a list of dictionaries.  Check your syntax."))
            break

        to_do.extend(parse_exit(exit, author, messages))

    # All is right, confirmation
    messages.append((0, line, "The room '{}' was succesfully created or updated.".format(ident)))

    return to_do

def parse_exit(document, author, messages):
    """Parse a single exit."""
    line = document.get("--begin", -1)
    args = []
    kwargs = {}
    direction = get_field(document, "direction", basestring, True, "", messages).lower().strip()
    if not direction:
        messages.append((2, line,
                "An exit needs to have a valid field name 'direction'."))
        return []

    if isinstance(direction, unicode):
        direction = direction.encode("utf-8")

    if direction not in NAME_DIRECTIONS.keys():
        messages.append((2, line,
                "An exit was defined with an incorrect direction: '{}'.".format(direction)))
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
    name = get_field(document, "name", basestring, False, "", messages).strip()
    if name:
        kwargs["name"] = name

    # Handle the aliases
    aliases = get_field(document, "aliases", list, False, [], messages)
    if aliases:
        for i, alias in enumerate(aliases):
            if not isinstance(alias, basestring):
                aliases[i] = str(alias)

        kwargs["aliases"] = aliases

    # All is right, confirmation
    messages.append((0, line, "The '{}' exit to '{}' was succesfully created or updated.".format(direction, destination)))

    return [(get_exit, args, kwargs)]


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
    line = document.get("--begin", -1)

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
                    "The field '{}' at line {} isn't of the proper type: {} expected but {} received".format(
                    field_name, line, expected, type(value))))
            return default

        return value
    elif required:
        messages.append((1, line,
                "In the document beginning at line {}, the '{}' field is required, yet has not been specified.".format(line, field_name)))

    return default
