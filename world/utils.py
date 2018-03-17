# -*- coding: utf-8 -*-

"""
Utility functions, specific to Avenew but generic enough to be ported to other projects.

Functions:
    latinify(unicode[, default][, mapping]): return a unicode string containing only ASCII.
    show_list(strings, width=4, **kwargs): return a formatted list.

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

def show_list(strings, width=4, vertical=False, length=None, begin="",
        between_lines="\n"):
    """Show a formatted list in a ls-like display.

    Args:
        strings (list of str): the list of strings to display.
        width (int): the number of columns per line.
        vertical (bool): should the strings be added vertically?
        length (int): the length of each column.
        begin (str): the beginning of each line in the table.
        between_lines (str): what to put between lines?

    This function takes a list of strings as argument, and format it
    in a table with a fixed number per line.  Other options are used to
    give more freedom regarding formatting.

    """
    lines = [[]]
    i = 0
    max_length = 0

    # Add the strings horizontally or vertically
    for entry in strings:
        line = lines[-1]
        if len(line) >= width:
            line = []
            lines.append(line)
        line.append(entry)
        if len(entry) > max_length:
            max_length = len(entry)

    # Create the string
    ret = ""
    if length is None:
        length = max_length

    for i, line in enumerate(lines):
        if i != 0:
            ret += between_lines
        ret += begin
        for entry in line:
            if len(entry) > length - 1:
                entry = entry[:length - 4] + "..."
            ret += entry.ljust(length)

    return ret
