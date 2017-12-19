# -*- coding: utf-8 -*-

"""
Utility functions, specific to Avenew but generic enough to be ported to other projects.

Functions:
    latinify(unicode[, default][, mapping]): return a unicode string containing only ASCII.

"""

_UNICODE_MAPPING = {
    # Insert characters to escape here
}

def latinify(unicode_string, replace=u"?", mapping=_UNICODE_MAPPING):
    """
    Return a unicode string containing only ASCII, following a mapping.

    Args:
        unicode_string (unicode): the unicode string to have non-ASCII removed.
        replace (optional, unicode): the replacement string when the character cannot be
                found in the mapping and is not ASCII.
        mapping (optional, dict): the mapping with unicode characters as keys
                and unicode replacements as values.

    """
    # Replace characters found in the mapping
    print repr(unicode_string)
    for char, repl in mapping.items():
        unicode_string = unicode_string.replace(char, repl)

    # Check that unicode_string is all ASCII now
    for i, char in enumerate(unicode_string):
        if ord(char) >= 128: # Non-ascii
            unicode_string = unicode_string[:i] + replace + unicode_string[i + 1:]

    return unicode_string
