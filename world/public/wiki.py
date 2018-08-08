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

write_wiki("doc/yaml", "Batch building in YML", """
        Batch building refers to a way for builders to create a great many rooms, objects, characters and more through execution of a single
        file.  Evennia offers two [batch processors](https://github.com/evennia/evennia/wiki/Batch-Processors),
        [the batch-command processor](https://github.com/evennia/evennia/wiki/Batch-Command-Processor) and
        [the batch-code processor](https://github.com/evennia/evennia/wiki/Batch-Code-Processor).  While both processors
        are really powerful, builders can find them somewhat intimidating at first glance.  The former is used to run a list of commands in a file and is,
        by definition, less easy to update, and can be challenging when writing descriptions (which occurs on a daily basis for builders).  The latter is
        intended to run Python code and is less explicit to builders, although, obviously, it allows for more flexibility.

        The batch-YML processor offers a third alternative, intended to be more intuitive to builders, easy to replicate and quite extensive.  This document
        further describes the batch-YML processor and how to use it.

        ## Basic principle of the batch-YML processor

        The batch-YML processor expects a file containing text, formatted using the YAML language.

        1. A file can contain several portions, traditionally, one per room/object/character.
        2. The builder wishing to apply this batch file can connect to [/builder/batch](/builder/batch).  On this page is a very simple form allowing to upload the YML file.
        3. Once sent, the file is read by the system, the rooms, objects, characters are created or updated, and the status of each task is sent back to the builder.

        Thus, building using batch YML files is quite simple.  These files can be updated and uploaded again (to fix a description, an exit,
        room coordinates, a callback...).

        ## Basic YML syntax

        Although the YML language is quite simple, it needs to follow some precise rules.  As a general rule, it is recommended to use the examples below (copy/pasting them in a file and then changing the value of each field).  Here are the guiding rules applied to the batch-YML processor:

        - Files should be encoded in utf-8.  If you try to enter non-ASCII characters in a different encoding, the file will most likely not be read correctly.
        - A YML document is used to represent each single object, room, or character.  YML documents are separated by `---` (three dashes on a single line).
        - Each document is a YML dictionary following the dictionary syntax (one key/value on each line as a rule).  See the examples below.
        - The first field of each document should be `type` and contain the type of the object to be created (an object, a room, a prototype...).  Again, refer to the examples below.
        - Respect the examples' indentation.  YML is a strict language that uses indentation to delimit data, much as Python itself does.
        - Respect the examples' symbols.  Some may not be obvious but all are mandatory nevertheless.  Syntax errors will arise if these symbols are not present.

        All documents should begin by a line with `---` only (three drashes).

        ## Detailed examples

        This section list examples of documents.  A YML document is meant to describe the creation of one piece of data (such as a room, an object, a prototype...).

        ### Room (type room)

        #### Example

        ```
        ---
        type: room
        ident: room_identifier
        prototype: the_key_of_the_room_prototype_to_be_used_if_any
        coords: [0, 5, -8]
        title: The room title
        description: |
            This is the room description.  Notice that it is preferable to specify
            it on several indented lines below the 'description' field, after
            the vertical bar.  This vertical bar informs the YML parser that
            the content of the field is on the lines below, indented to the
            right.  Line breaks are to be kept.  However, in this case, simple
            line breaks are ignored (replaced by spaces).

            However, if you leave a blank, empty line, and begin the
            description again (still indented), this will begin a new
            paragraph.  Use this system if you need to create several
            paragraphs in one description.
        exits:
            - direction: east
              destination: room_identifier
              name: slide
              aliases: [s]
            - direction: west
              destination: room_identifier
              name: door
              aliases: [d, dr]
        ```

        #### Fields

        | Field | Presence | Value |
        | ----- | -------- | ----- |
        | type | Mandatory | Must be room |
        | ident | Mandatory | The room identifier, a key that can only contain lowercase letters, digits, and the colon (`:` ) symbol. |
        | prototype | Optional | The key of the room prototype (proom) to use.  This is not mandatory, as rooms can exist without prototype. |
        | coords | Optional | The room coordinates in a list, with X, Y and Z as integers.  If this field is not present, the room will have no valid coordinates. |
        | title | Optional | The room title. |
        | description | Optional | The room description.  Notice that if the room has a prototype, and no description, it will use the prototype's description instead. |
        | exits | Optional | The room exits in a list.  Follow the example syntax.  See the section about exits for more details. |

        #### Notes

        The room identifier (`ident` field) is important when updating.  The room that has the same identifier will be searched in the current game
        when a document of type room is being read.  If a room with this identifier exists, the document is applied to it, to update it.  Otherwise, the room will be created.
        Therefore, do not change identifiers after the first upload and be sure the identifiers you use are not being used in
        the game.

        Assuming the identifiers remain the same, all fields (including coordinates) can be changed.  If you change the coordinates (`coords` field) of
        any document and then upload it again, the room coordinates will be changed.  This will break if there is another room with the same coordinates,
        but not the same identifier (`ident`).

        ### Exit

        #### Example

        ```
        type: room
        # ...
        exits:
            - direction: exit direction
              destination: room_identifier
              name: name of exit
              aliases: [alias1, alias2, alias3]
        ```

        #### Fields

        | Field | Presence | Value |
        | ----- | -------- | ----- |
        | direction | Mandatory | The exit's absolute direction (east, south, north, southeast, up, down...). |
        | destination | Mandatory | The identifier of the room to which this exit should point to.  An exit will be created or updated leading from the room described by the document, to the room with the `destination` identifier.  Notice that the back exit is not created, you will have to include it in the destination's document. |
        | name | Optional | The exit name, optional.  If it is not specified, it will be identical to the exit direction. |
        | aliases | Optional | A list of aliases pointing to this exit, available in the room.  If no name or alias is specified, default aliases linked with this direction (like e for east) will be used.  Alternatively, you can specify aliases within a list, like `aliases = [command1, command2, ...]`. |

        #### Notes

        Exits are defined in rooms, under the `exits` field.  Typically, the room should look like this:

        ```
        ---
        type: room
        # ...
        exits:
            - direction: room_direction
              destination: room_identifier
            - direction: room_direction
              destination: room_identifier
            - direction: room_direction
              destination: room_identifier
        ```

        Notice the indentation below the `exits` field.  Each exit should begin by a dash, a space and a set of fields with a key, a colon and a value (a YML
        dictionary).  You can define one or more exits in the same room.  If you don't want your room to have any exit, do not include this field in the room
        document.  Again, it may be better to simply copy/paste these examples.

        When referring to a room as destination of an exit, whether the room exists or not isn't important.  If the room doesn't yet
        exist, it will be created (empty, at this point).  Another document might update it later.

        ### Room prototype (type proom)

        #### Example

        ```
        ---
        type: proom
        ident: proom_identifier
        description: |
            The description of the prototype.  Again, in order to create two paragraphs, just insert an empty line between them.  For instance:
            This is paragraph 1.

            This is paragraph 2.
        ```

        #### Fields

        | Field | Presence | Value |
        | ----- | -------- | ----- |
        | type | Mandatory | Must be proom |
        | ident | Mandatory | The room prototype identifier, a key that can only contain lowercase letters, digits, and the colon (`:` ) symbol. |
        | description | Optional | The room prototype description. |

        #### Notes

        The identifier specified in a proom document is the key to be used in the `prototype` field of a room document
        that has a prototype.  Again, if the prototype doesn't exist, it is created, otherwise it is updated.  Therefore, you can
        have room documents with a prototype that is not created, and a room prototype document below.  The first room that needs the specified prototype
        will create it, it will then be updated.  However, it is good practice to place the room prototypes above the room documents.

        If a room has a prototype but no description, its description will be borrowed from the prototype, and updated if the prototype changes.  A room description can also require the prototype's description.  Consider this basic example:

        ```
        ---
        type: proom
        ident: sidewalk
        description: |
            This is a sidewalk.

        ---
        type: room
        ident: sidewalk1
        prototype: sidewalk
        description: |
            $parent  It is somewhat narrow.
        ```

        If you upload a YML file with this code, the room (sidewalk1) will be created, its description will be: This is a sidewalk.  It is somewhat narrow.
""")

