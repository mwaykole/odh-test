"""Test glusto config functionality"""
import unittest
import xmlrunner

import os
from collections import OrderedDict

from src.core import OdhAssess as g
from test.test_odh_base_class import ODHBaseClass


class TestODHConfigs(ODHBaseClass):
    """ODH basics test class"""

    @classmethod
    def setUpClass(cls):
        """unittest standard setUpClass method
        Runs before all test methods in the class
        """
        print(f"Setting Up Class: {cls.__name__}")
        # Setting class attributes for use across all test methods
        cls.yaml_file = '/tmp/testconfig.yml'
        cls.json_file = '/tmp/testconfig.json'
        cls.ini_file = '/tmp/testconfig.ini'
        cls.ini_novalue_file = '/tmp/testconfig_novalue.ini'
        cls.ini_ordered_file = '/tmp/testconfig_ordered.ini'
        cls.ini_mixedcase_file = '/tmp/testconfig_mixedcase.ini'
        cls.ini_lowercase_file = '/tmp/testconfig_lowercase.ini'

        cls.yaml_noext = '/tmp/testyaml'
        cls.json_noext = '/tmp/testjson'
        cls.ini_noext = '/tmp/testini'

        cls.config = {}
        cls.config['defaults'] = {}
        cls.config['defaults']['this'] = 'yada1'
        cls.config['defaults']['that'] = 'yada2'
        cls.config['globals'] = {}
        cls.config['globals']['the_other'] = 'yada3'
        # to test ini substitution
        cls.config['defaults']['this_and_that'] = '%(this)s and %(that)s'
        # to test mixedcase
        cls.config['mixed'] = {}
        cls.config['mixed']['mixed_CASE'] = "mixedCaseValue"

        g.show_config(cls.config)

        cls.config_novalue = {}
        cls.config_novalue['defaults'] = ['this', 'that']
        cls.config_novalue['globals'] = ['the_other', 'and_one_more_thing']

        g.show_config(cls.config_novalue)

        cls.ordered_config = OrderedDict()
        cls.ordered_config['defaults'] = OrderedDict()
        cls.ordered_config['defaults']['this'] = 'yada1'
        cls.ordered_config['defaults']['that'] = 'yada2'
        cls.ordered_config['globals'] = OrderedDict()
        cls.ordered_config['globals']['the_other'] = 'yada3'
        # to test ini substitution
        cls.ordered_config['defaults']['this_and_that'] = \
            '%(this)s and %(that)s'

        g.show_config(cls.ordered_config)

        # cleanup files if they exist
        '''
        if os.path.exists(cls.yaml_file):
            os.unlink(cls.yaml_file)
        if os.path.exists(cls.ini_file):
            os.unlink(cls.ini_file)
        '''

    def setUp(self):
        """unittest standard setUp method
        Runs before each test method
        """
        print(f"Setting Up: {self.id()}")

    def test_yaml(self):
        """Testing yaml config file"""
        print(f"Running: {self.id()} - {self.shortDescription()}")

        g.show_config(self.config)

        # write the config file
        g.store_config(self.config, self.yaml_file)
        self.assertTrue(os.path.exists(self.yaml_file))

        # read the config file
        config = g.load_config(self.yaml_file)
        g.show_config(config)
        self.assertEqual(config['defaults']['this'], 'yada1')
        self.assertEqual(config['defaults']['that'], 'yada2')
        self.assertEqual(config['globals']['the_other'], 'yada3')
    #
    # def test_yaml_noext(self):
    #     """Testing yaml config file without extension"""
    #     print(f"Running: {self.id()} - {self.shortDescription()}")
    #
    #     g.show_config(self.config)
    #
    #     # write the config files
    #     g.store_config(self.config, self.yaml_file)
    #     self.assertTrue(os.path.exists(self.yaml_file))
    #     g.store_config(self.config, self.yaml_noext, config_type='yaml')
    #     self.assertTrue(os.path.exists(self.yaml_noext))
    #
    #     print("--------------")
    #     g.show_file(self.yaml_file)
    #     print("--------------")
    #     g.show_file(self.yaml_noext)
    #     print("--------------")
    #
    #     # read the config file
    #     config = g.load_config(self.yaml_file)
    #     g.show_config(config)
    #     self.assertEqual(config['defaults']['this'], 'yada1')
    #     self.assertEqual(config['defaults']['that'], 'yada2')
    #     self.assertEqual(config['globals']['the_other'], 'yada3')
    #
    #     config_noext = g.load_config(self.yaml_noext, config_type='yaml')
    #     g.show_config(config_noext)
    #     self.assertEqual(config_noext['defaults']['this'], 'yada1')
    #     self.assertEqual(config_noext['defaults']['that'], 'yada2')
    #     self.assertEqual(config_noext['globals']['the_other'], 'yada3')
    #
    #     self.assertEqual(config, config_noext, 'config files are not the same')
    #
    # def test_json(self):
    #     """Testing json config file"""
    #     print(f"Running: {self.id()} - {self.shortDescription()}")
    #
    #     g.show_config(self.config)
    #
    #     # write the config file
    #     g.store_config(self.config, self.json_file)
    #     self.assertTrue(os.path.exists(self.json_file))
    #
    #     # read the config file
    #     config = g.load_config(self.json_file)
    #     g.show_config(config)
    #     self.assertEqual(config['defaults']['this'], 'yada1')
    #     self.assertEqual(config['defaults']['that'], 'yada2')
    #     self.assertEqual(config['globals']['the_other'], 'yada3')
    #
    # def test_json_noext(self):
    #     """Testing json config file without extension"""
    #     print(f"Running: {self.id()} - {self.shortDescription()}")
    #
    #     g.show_config(self.config)
    #
    #     # write the config files
    #     g.store_config(self.config, self.json_file)
    #     self.assertTrue(os.path.exists(self.json_file))
    #     g.store_config(self.config, self.json_noext, config_type='json')
    #     self.assertTrue(os.path.exists(self.json_noext))
    #
    #     print("--------------")
    #     g.show_file(self.json_file)
    #     print("--------------")
    #     g.show_file(self.json_noext)
    #     print("--------------")
    #
    #     # read the config file
    #     config = g.load_config(self.json_file)
    #     g.show_config(config)
    #     self.assertEqual(config['defaults']['this'], 'yada1')
    #     self.assertEqual(config['defaults']['that'], 'yada2')
    #     self.assertEqual(config['globals']['the_other'], 'yada3')
    #
    #     config_noext = g.load_config(self.json_noext, config_type='json')
    #     g.show_config(config_noext)
    #     self.assertEqual(config_noext['defaults']['this'], 'yada1')
    #     self.assertEqual(config_noext['defaults']['that'], 'yada2')
    #     self.assertEqual(config_noext['globals']['the_other'], 'yada3')
    #
    #     self.assertEqual(config, config_noext, 'config files are not the same')
    #
    # def test_ini(self):
    #     """Testing ini config file(s)"""
    #     print(f"Running: {self.id()} - {self.shortDescription()}")
    #
    #     g.store_config(self.config, self.ini_file)
    #     self.assertTrue(os.path.exists(self.ini_file))
    #
    #     # read the config file
    #     config = g.load_config(self.ini_file)
    #     g.show_config(config)
    #     self.assertEqual(config['defaults']['this'], 'yada1')
    #     self.assertEqual(config['defaults']['that'], 'yada2')
    #     self.assertEqual(config['defaults']['this_and_that'],
    #                      'yada1 and yada2')
    #     self.assertEqual(config['globals']['the_other'], 'yada3')
    #
    # def test_ini_novalue(self):
    #     """Testing ini config file(s) without values"""
    #     print(f"Running: {self.id()} - {self.shortDescription()}")
    #
    #     g.store_config(self.config_novalue, self.ini_novalue_file)
    #     self.assertTrue(os.path.exists(self.ini_novalue_file))
    #
    #     print("--------------")
    #     g.show_file(self.ini_novalue_file)
    #     print("--------------")
    #
    #     # read the config file
    #     config = g.load_config(self.ini_novalue_file)
    #     g.show_config(config)
    #     self.assertEqual(config['defaults'].get('this'), '')
    #     self.assertEqual(config['defaults'].get('that'), '')
    #     self.assertEqual(config['globals'].get('and_one_more_thing'), '')
    #     self.assertEqual(config['globals'].get('the_other'), '')
    #
    # def test_ini_noext(self):
    #     """Testing ini config file(s) without extension"""
    #     print(f"Running: {self.id()} - {self.shortDescription()}")
    #
    #     g.store_config(self.config, self.ini_file)
    #     self.assertTrue(os.path.exists(self.ini_file))
    #     g.store_config(self.config, self.ini_noext, config_type='ini')
    #     self.assertTrue(os.path.exists(self.ini_noext))
    #
    #     print("--------------")
    #     g.show_file(self.ini_file)
    #
