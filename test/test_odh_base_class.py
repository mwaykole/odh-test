import os
import unittest
from src.core import OdhAssess as o


class shoots_with(o.CarteTestClass):
    """Decorator providing carteplex definition for carteplex functionality"""

    def __init__(self, value):
        axis_names = ['model_runtime']

        available_options = [['vllm', 'pytorch', 'tgis', 'caikit'],
                             'http', 'https', 'grpc']

        self.axis_names = o.config.get('axis_names', axis_names)

        self.available_options = o.config.get('available_options',
                                              available_options)

        self.limits = value


class ODHBaseClass(unittest.TestCase):
    model_runtime = None
    error_or_failure_exists = False

    @classmethod
    def setUpClass(cls):
        print("setUpClass BASE: %s" % cls.__name__)
        print("**IN SUPER Class name**: ", cls.__name__)
        print("***IN SUPER Class mro**: ", cls.__mro__)
        print("***IN SUPER Class bases**: ", cls.__bases__)
        print("***IN SUPER Class super**: ", cls.__mro__[1])
        o.log.info("=====================hello it is info")
        o.log.error("hello it is error")
        if not cls.model_runtime:
            cls.model_runtime = "tgis"

        cls.script_dir = os.path.dirname(os.path.realpath(__file__))
        print("SETUPCLASS ODH (BASE):  {}", cls.model_runtime)

    def setUp(self):
        """Setting this up"""
        print("\tsetUp BASE: %s - %s" % (self.id(), self.shortDescription()))
        print("SETUP ODH (BASE):  {} ", self.model_runtime)

    def tearDown(self):
        print("\ttearDown BASE: %s - %s" %
              (self.id(), self.shortDescription()))
        print("TEARDOWN ODH (BASE): %s with %s with %s", self.model_runtime)

    @classmethod
    def tearDownClass(cls):
        print("tearDownClass BASE: %s" % cls.__name__)
        print("TEARDOWNCLASS ODH (BASE): {}", cls.model_runtime)
