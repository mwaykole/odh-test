import unittest

from src.core import OdhAssess as g


class TestODHBasics(unittest.TestCase):
    """ODH basics test class"""
    @classmethod
    def setUpClass(cls):
        """unittest standard setUpClass method
        Runs before all test_ methods in the class
        """
        print("Setting Up Class: %s" % cls.__name__)
        g.log.info("infooo")
        g.log.error("error")
        g.log.warning("warning")
        g.log.debug("debug")
        cls.non_color_message = 'this is a test'
        cls.color_message = '\x1b[43;31;1mthis is a test\x1b[0m'

    def setUp(self):
        """unittest standard setUp method
        Runs before each test_ method
        """
        print("Setting Up: %s" % self.id())

    def test_log_color_true(self):
        g.config['log_color'] = True
        print(":====================================")
        print(g.config["available_options"])
        print(":====================================")
        message = g.colorfy(g.RED | g.BG_YELLOW | g.BOLD,
                            self.non_color_message)

        self.assertEqual(message, self.color_message,
                         "color message does not match expectation")

    def test_log_color_false(self):
        g.config['log_color'] = False
        g.log.info("infooo")
        g.log.error("error")
        g.log.warning("warning")
        g.log.debug("debug")
        message = g.colorfy(g.RED, self.non_color_message)

        self.assertEqual(message, self.non_color_message,
                         "non color message does not match expectation")

    def tearDown(self):
        """Unittest tearDown override"""
        print("Tearing Down: %s" % self.id())

    @classmethod
    def tearDownClass(cls):
        """unittest tearDownClass override"""
        print("Tearing Down Class: %s" % cls.__name__)