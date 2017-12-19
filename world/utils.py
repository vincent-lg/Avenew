# -*- coding: utf-8 -*-

"""
Utility functions, specific to Avenew but generic enough to be ported to other projects.

Functions:
    latinify(unicode[, default][, mapping]): return a unicode string containing only ASCII.

"""

_UNICODE_MAPPING = {
    u"\u00bc": "OE",
    u"\u00bd": "oe",
    u"\u00c0": u"A",
    u"\u00c2": u"A",
    u"\u00c7": u"C",
    u"\u00c8": u"E",
    u"\u00c9": u"E",
    u"\u00ca": u"E",
    u"\u00cb": u"E",
    u"\u00ce": u"I",
    u"\u00cf": u"I",
    u"\u00d4": u"O",
    u"\u00d9": u"U",
    u"\u00db": u"U",
    u"\u00dc": u"U",
    u"\u00e0": u"a",
    u"\u00e2": u"a",
    u"\u00e7": u"c",
    u"\u00e8": u"e",
    u"\u00e9": u"e",
    u"\u00ea": u"e",
    u"\u00eb": u"e",
    u"\u00ee": u"i",
    u"\u00ef": u"i",
    u"\u00f4": u"o",
    u"\u00f9": u"u",
    u"\u00fb": u"u",
    u"\u00fc": u"u",
    u"\u0152": u"OE",
    u"\u0153": u"oe",
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
