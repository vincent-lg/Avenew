# -*- coding: utf-8 -*-

from evennia.utils.test_resources import EvenniaTest

from world.utils import *

doc = u"""
---
type: room
title: A room
x: 5
y: 12
z: 1
length: 12.5
text: >
    One
    Two
keep: |
    One
    Two
list1: [1, 2, 3.5, ok]
list2:
  - 1
  - 2
  - {field: 123}
"""

class TestUtils(EvenniaTest):

    """Test for Avenew utilities."""

    def test_load_YAML(self):
        """Try to load a YAML document and see if line numbers match."""
        documents = load_YAML(doc)
        self.assertEqual(len(documents), 1)

        # Explore the first document
        document = documents[0]
        self.assertIsInstance(document, dict)

        # Check the keys and proper line numbers
        self.assertEqual(document.keys()[0], "type")
        self.assertEqual(document.values()[0][1], 3)
        self.assertEqual(document.keys()[1], "title")
        self.assertEqual(document.values()[1][1], 4)
        self.assertEqual(document.keys()[5], "length")
        self.assertEqual(document.values()[5][1], 8)
        self.assertEqual(document.keys()[6], "text")
        self.assertEqual(document.values()[6][1], 9)
        self.assertEqual(document.keys()[7], "keep")
        self.assertEqual(document.values()[7][1], 12)
        self.assertEqual(document.keys()[8], "list1")
        self.assertEqual(document.values()[8][1][1], 15)
        self.assertEqual(document.keys()[9], "list2")
        self.assertEqual(document.values()[9][0][1], 17)
        self.assertEqual(document.values()[9][1][1], 18)

        # Check the matching values
        self.assertEqual(document.values()[0][0], "room")
        self.assertEqual(document.values()[0][1], 3)
        self.assertEqual(document.values()[1][0], "A room")
        self.assertEqual(document.values()[1][1], 4)
        self.assertEqual(document.values()[5][0], 12.5)
        self.assertEqual(document.values()[5][1], 8)
        self.assertEqual(document.values()[6][0].strip(), "One Two")
        self.assertEqual(document.values()[6][1], 9)
        self.assertEqual(document.values()[7][0].strip(), "One\nTwo")
        self.assertEqual(document.values()[7][1], 12)
        self.assertEqual(document.values()[8][0][0], 1)
        self.assertEqual(document.values()[8][0][1], 15)
        self.assertEqual(document.values()[8][1][0], 2)
        self.assertEqual(document.values()[8][1][1], 15)
        self.assertEqual(document.values()[8][2][0], 3.5)
        self.assertEqual(document.values()[8][2][1], 15)
        self.assertEqual(document.values()[8][3][0], "ok")
        self.assertEqual(document.values()[8][3][1], 15)
        self.assertEqual(document.values()[9][0][0], 1)
        self.assertEqual(document.values()[9][0][1], 17)
        self.assertEqual(document.values()[9][1][0], 2)
        self.assertEqual(document.values()[9][1][1], 18)
        self.assertEqual(document.values()[9][2], {"field": (123, 19), "--begin": 19})
