"""Test the behavir of command arguments."""

from command.args import CommandArgs, ArgumentError
from test.base import BaseTest

class TestCommandArgs(BaseTest):

    def test_text(self):
        """Test to parse one argument as text."""
        # Try to enter a single word
        args = CommandArgs()
        args.add_argument("text", dest="simple")
        namespace = args.parse(None, "something")
        self.assertEqual(namespace.simple, "something")

        # Try to enter several words
        args = CommandArgs()
        args.add_argument("text")
        namespace = args.parse(None, "something else")
        self.assertEqual(namespace.text, "something else")

    def test_word(self):
        """Test one or several words in arguments."""
        # Try to enter a single word
        args = CommandArgs()
        args.add_argument("word", dest="simple")
        namespace = args.parse(None, "something")
        self.assertEqual(namespace.simple, "something")

        # Try to enter several words
        args = CommandArgs()
        args.add_argument("word", dest="first")
        args.add_argument("word", dest="second")
        namespace = args.parse(None, "something else")
        self.assertEqual(namespace.first, "something")
        self.assertEqual(namespace.second, "else")

    def test_options(self):
        """Test options arguments."""
        # Try to enter a single option
        args = CommandArgs()
        options = args.add_argument("options")
        options.add_option("t", "title", dest="title")
        namespace = args.parse(None, "title=ok")
        self.assertEqual(namespace.title, "ok")

        # Try again, but with two words in the title
        namespace = args.parse(None, "title=a title")
        self.assertEqual(namespace.title, "a title")

        # Try short options
        namespace = args.parse(None, "t=ok")
        self.assertEqual(namespace.title, "ok")

        # Try again, but with two words in the title
        namespace = args.parse(None, "t=a title")
        self.assertEqual(namespace.title, "a title")

        # Try with several options
        args = CommandArgs()
        options = args.add_argument("options")
        options.add_option("t", "title", optional=False, dest="title")
        options.add_option("d", "description", dest="description")
        namespace = args.parse(None, "title=ok d=a description")
        self.assertEqual(namespace.title, "ok")
        self.assertEqual(namespace.description, "a description")

        # Try again, but with two words in the title
        namespace = args.parse(None, "title=a title description=something")
        self.assertEqual(namespace.title, "a title")
        self.assertEqual(namespace.description, "something")

        # Try short options
        namespace = args.parse(None, "description=well t=ok")
        self.assertEqual(namespace.title, "ok")
        self.assertEqual(namespace.description, "well")

        # Try again, but with two words in the title
        namespace = args.parse(None, "t=a title description=hi")
        self.assertEqual(namespace.title, "a title")
        self.assertEqual(namespace.description, "hi")

        # Test with word argument
        args = CommandArgs()
        args.add_argument("word")
        options = args.add_argument("options")
        options.add_option("t", "title", dest="title")
        options.add_option("d", "description", dest="description")
        namespace = args.parse(None, "and d=something else title=ok")
        self.assertEqual(namespace.word, "and")
        self.assertEqual(namespace.title, "ok")
        self.assertEqual(namespace.description, "something else")

        # Test mandatory and optional options
        args = CommandArgs()
        options = args.add_argument("options")
        options.add_option("t", "title", default="nothing", dest="title")
        options.add_option("d", "description", dest="description")
        namespace = args.parse(None, "d=a description")
        self.assertEqual(namespace.title, "nothing")
        self.assertEqual(namespace.description, "a description")

    def test_number(self):
        """Test a number argument."""
        args = CommandArgs()
        args.add_argument("number")
        namespace = args.parse(None, "38")
        self.assertEqual(namespace.number, 38)

        # Try an invalid number
        args = CommandArgs()
        number = args.add_argument("number")
        result = args.parse(None, "no")
        self.assertIsInstance(result, ArgumentError)
        self.assertEqual(str(result), number.msg_invalid_number.format(number="no"))

        # Try with an optional number
        args = CommandArgs()
        args.add_argument("number", optional=True, default=1)
        args.add_argument("text")
        namespace = args.parse(None, "2 red apples")
        self.assertEqual(namespace.number, 2)
        self.assertEqual(namespace.text, "red apples")
        namespace = args.parse(None, "red apple")
        self.assertEqual(namespace.number, 1)
        self.assertEqual(namespace.text, "red apple")

        # Try with words and an optional number
        args = CommandArgs()
        args.add_argument("number", dest="left", optional=True, default=1)
        args.add_argument("word")
        args.add_argument("number", dest="right")
        namespace = args.parse(None, "2 times 3")
        self.assertEqual(namespace.left, 2)
        self.assertEqual(namespace.word, "times")
        self.assertEqual(namespace.right, 3)
        namespace = args.parse(None, "neg 5")
        self.assertEqual(namespace.left, 1)
        self.assertEqual(namespace.word, "neg")
        self.assertEqual(namespace.right, 5)

    def test_search(self):
        """Test to search elements."""
        char1 = self.create_character()
        char2 = self.create_character()
        char3 = self.create_character()
        room = self.create_room()
        char1.location = room
        char2.location = room
        char3.location = room

        # Register names on characters
        char1.names.register("a blue rabbit")
        char2.names.register("a pink rabbit")
        char3.names.register("a blue dog")

        # Test searching
        args = CommandArgs()
        search = args.add_argument("search")
        search.search_in = lambda ch: ch.location.contents

        # Try searching for 'blue'
        namespace = args.parse(char1, "blue")
        result = namespace.search
        self.assertIn(char1, result)
        self.assertNotIn(char2, result)
        self.assertIn(char3, result)

        # Try searching for pink
        namespace = args.parse(char1, "pink")
        result = namespace.search
        self.assertNotIn(char1, result)
        self.assertIn(char2, result)
        self.assertNotIn(char3, result)

        # Try searching for 'a' (all should work)
        namespace = args.parse(char1, "a")
        result = namespace.search
        self.assertIn(char1, result)
        self.assertIn(char2, result)
        self.assertIn(char3, result)

        # Check the error, whe no match is found.
        res = args.parse(char1, "cyan")
        self.assertIsInstance(res, ArgumentError)

    def test_complex_search(self):
        """Search for two objects in the same command."""
        char1 = self.create_character()
        char2 = self.create_character()
        char3 = self.create_character()
        room = self.create_room()
        char1.location = room
        char2.location = room
        char3.location = room

        # Register names on characters
        char1.names.register("a blue rabbit")
        char2.names.register("a pink rabbit")
        char3.names.register("a blue dog")

        # Test searching
        args = CommandArgs()
        obj1 = args.add_argument("search", dest="obj1")
        obj1.search_in = lambda ch: ch.location.contents
        args.add_argument("keyword", "to")
        obj2 = args.add_argument("search", dest="obj2")
        obj2.search_in = lambda ch: ch.location.contents

        # Now try to parse single words
        namespace = args.parse(char1, "blue to pink")
        self.assertIn(char1, namespace.obj1)
        self.assertNotIn(char2, namespace.obj1)
        self.assertIn(char3, namespace.obj1)
        self.assertNotIn(char1, namespace.obj2)
        self.assertIn(char2, namespace.obj2)
        self.assertNotIn(char3, namespace.obj2)

        # Try closing on with multiple-word searches.
        namespace = args.parse(char1, "blue rabbit to pink rabbit")
        self.assertIn(char1, namespace.obj1)
        self.assertNotIn(char2, namespace.obj1)
        self.assertNotIn(char3, namespace.obj1)
        self.assertNotIn(char1, namespace.obj2)
        self.assertIn(char2, namespace.obj2)
        self.assertNotIn(char3, namespace.obj2)
