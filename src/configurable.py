import os
import yaml
import json
import configparser
import csv
import urllib.request
from collections import OrderedDict


class Configurable:
    """The class providing all things configuration."""

    config = {}
    """The default class attribute for storing configurations."""

    @staticmethod
    def _is_url(filename):
        return filename.startswith(('file://', 'http://', 'https://'))

    @staticmethod
    def _get_filename_extension(filename):
        """Get the dot extension from a filename."""
        _, extension = os.path.splitext(filename)
        return extension.replace('.', '')

    @staticmethod
    def _get_file_descriptor(filename):
        """Get a file descriptor from either a file or URL."""
        if Configurable._is_url(filename):
            return urllib.request.urlopen(filename)
        else:
            return open(filename, 'r')

    @staticmethod
    def _store_yaml(obj, filename):
        """Write an object to a YAML config file."""
        with open(filename, 'w') as configfd:
            yaml.dump(obj, configfd, Dumper=GDumper)

    @staticmethod
    def _store_ini(obj, filename, allow_mixed_case=True):
        """Write an object to an INI formatted config file."""
        config = configparser.ConfigParser(allow_no_value=True)
        if allow_mixed_case:
            config.optionxform = str

        for section_key, section_value in obj.items():
            config.add_section(section_key)
            if isinstance(section_value, dict):
                for item_key, item_value in section_value.items():
                    config.set(section_key, item_key, item_value or '')
            else:
                for item in section_value:
                    config.set(section_key, item)

        with open(filename, 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def _store_json(obj, filename):
        """Write an object to a JSON formatted config file."""
        with open(filename, 'w') as configfd:
            json.dump(obj, configfd, indent=4, separators=(',', ': '))

    @staticmethod
    def _store_csv(obj, filename, header=True, fieldnames=None, delimiter=','):
        """Write a list of dictionaries to a CSV file."""
        field_names = fieldnames or list(obj[0].keys())
        with open(filename, 'w', newline='') as csvf:
            if isinstance(obj[0], dict):
                writer = csv.DictWriter(csvf, fieldnames=field_names, delimiter=delimiter)
                if header:
                    writer.writeheader()
            else:
                writer = csv.writer(csvf, delimiter=delimiter)
            writer.writerows(obj)

    @staticmethod
    def store_config(obj, filename, config_type=None, **kwargs):
        """Writes an object to a file format, automatically detects format based on filename extension."""
        file_extension = Configurable._get_filename_extension(filename)
        if config_type:
            file_extension = config_type

        if file_extension == "ini":
            Configurable._store_ini(obj, filename, **kwargs)
        elif file_extension in ("json",):
            Configurable._store_json(obj, filename)
        elif file_extension in ("yaml", "yml"):
            Configurable._store_yaml(obj, filename)
        elif file_extension == "csv":
            Configurable._store_csv(obj, filename, **kwargs)
        else:
            print("Filetype not recognized")
            return False
        return None

    @staticmethod
    def _load_ini(filename, allow_mixed_case=True):
        """Reads an INI file into a dictionary."""
        config = configparser.ConfigParser(allow_no_value=True)
        if allow_mixed_case:
            config.optionxform = str

        if Configurable._is_url(filename):
            with Configurable._get_file_descriptor(filename) as configfd:
                config.read_file(configfd)
        else:
            config.read(filename)

        return OrderedDict((section, OrderedDict(config.items(section))) for section in config.sections())

    @staticmethod
    def _load_yaml(filename):
        """Reads a YAML formatted file into a dictionary."""
        with Configurable._get_file_descriptor(filename) as configfd:
            return yaml.safe_load(configfd)

    @staticmethod
    def _load_json(filename):
        """Reads a JSON formatted file into a dictionary."""
        with Configurable._get_file_descriptor(filename) as configfd:
            return json.load(configfd)

    @staticmethod
    def _load_csv(filename, delimiter=',', header=True):
        """Reads a CSV file into a dictionary."""
        with open(filename, newline='') as csvfile:
            if header:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
            else:
                reader = csv.reader(csvfile, delimiter=delimiter)
            return list(reader)

    @staticmethod
    def _load_text(filename):
        """Reads a text file into a string."""
        with Configurable._get_file_descriptor(filename) as configfd:
            return configfd.read()

    @staticmethod
    def load_config(filename, config_type=None, **kwargs):
        """Reads a config from file, defaults to YAML, but detects other formats based on extension."""
        file_is_url = Configurable._is_url(filename)
        if os.path.exists(filename) or file_is_url:
            file_extension = Configurable._get_filename_extension(filename)
            if config_type:
                file_extension = config_type

            if file_extension == "ini":
                return Configurable._load_ini(filename, **kwargs)
            elif file_extension == "json":
                return Configurable._load_json(filename)
            elif file_extension in ("yaml", "yml"):
                return Configurable._load_yaml(filename)
            elif file_extension == "csv":
                return Configurable._load_csv(filename, **kwargs)
            else:
                return Configurable._load_text(filename)

        return None

    @staticmethod
    def load_yaml_string(yaml_string):
        """Reads a YAML formatted string into a dictionary."""
        return yaml.safe_load(yaml_string)

    @staticmethod
    def load_json_string(json_string):
        """Reads a JSON formatted string into a dictionary."""
        return json.loads(json_string)

    @staticmethod
    def load_configs(filelist):
        """Reads multiple configs from a list of filenames into a single configuration."""
        if isinstance(filelist, str):
            filelist = [filelist]
        config = {}
        for filename in filelist:
            config_part = Configurable.load_config(filename)
            if config_part:
                config.update(config_part)
        return config


    @classmethod
    def set_config(cls,  config):
        """Assigns a config to the config class attribute."""
        cls.config = config

    @classmethod
    def update_config(cls, config):
        """Adds a config to the config class attribute."""
        cls.config.update(config)

    @classmethod
    def log_config(cls, obj):
        """Writes a YAML formatted configuration to the log."""
        cls.log.debug(f"Configuration for object type {type(obj)}:\n{yaml.dump(obj, Dumper=GDumper)}")

    @staticmethod
    def get_config(obj):
        """Retrieves an object in YAML format."""
        return yaml.dump(obj, Dumper=GDumper)

    @staticmethod
    def show_config(obj):
        """Outputs a YAML formatted representation of an object on stdout."""
        print(yaml.dump(obj, Dumper=GDumper))

    @classmethod
    def clear_config(cls):
        """Clears the config class attribute with an empty dictionary."""
        cls.config = {}

    @staticmethod
    def show_file(filename):
        """Reads a file and prints the output."""
        with Configurable._get_file_descriptor(filename) as fd:
            data = fd.read()
            print(data)


class GDumper(yaml.Dumper):
    """Override the alias junk normally output by Dumper."""

    def ignore_aliases(self, data):
        """Overriding to skip aliases."""
        return True

    def prepare_tag(self, tag):
        """Overriding to skip tags."""
        return ''


class Intraconfig:
    """Class to provide instances with simple configuration utility and introspection in YAML config format."""

    def update_config(self, config):
        """Adds a config to the config class attribute."""
        self.__dict__.update(config)

    def show_config(self):
        """Outputs a YAML formatted representation of an instance on stdout."""
        Configurable.show_config(self)

    def get_config(self):
        """Retrieves an instance object in YAML format."""
        return Configurable.get_config(self)

    def load_config(self, filename):
        """Reads a YAML config from file and assigns to the config instance attribute."""
        config = Configurable.load_config(filename)
        self.update_config(config)

    def store_config(self, filename, config_type=None):
        """Writes attributes of a class instance to a file in a config format."""
        Configurable.store_config(self, filename, config_type)
