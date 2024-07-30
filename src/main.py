import argparse
import unittest
import pytest
import xmlrunner
import importlib
import shlex
import sys

from src.core import OdhAssess as o


def handle_configs(config_list):
    """Load default and user-specified configuration files"""
    o.log.info("Loading default configuration files.")

    # load user specified configs (can also override defaults)
    if config_list:
        o.log.info("Loading user specified configuration files.")
        config_files = config_list.split()
        config = o.load_configs(config_files)
        o.update_config(config)


def configure_logging(args):
    """Configure logging based on defaults, config, and CLI options"""
    log_name = "odhlog"
    log_filename = "/tmp/odhlog.log"
    log_level = "INFO"

    log_filename = o.config.get('log_filename', log_filename)
    log_level = o.config.get('log_level', log_level)

    if args.log_filename:
        log_filename = args.log_filename
    if args.log_level:
        log_level = args.log_level

    o.log = o.create_log(name=log_name, filename=log_filename, level=log_level)
    print("Log %s created as %s with log level %s" % (log_name, log_filename, log_level))

    o.log.info("Starting odh-test via main()")
    print("Starting odh-test via main()")

    o.show_config(o.config)


def load_tests_from_module(loader, tsuite, run_module):
    """Load tests from a specified module"""
    o.log.debug('unittest - load_tests_from_module')
    module_name = run_module.get('module_name')
    use_load_tests = run_module.get('use_load_tests', True)

    module = importlib.import_module(module_name)
    tests_from_module = loader.loadTestsFromModule(module, use_load_tests)
    tsuite.addTests(tests_from_module)


def main():
    """Entry point console script for setuptools."""
    epilog = ('NOTE: If encountering an "unknown option" issue '
              'with the -t and -n options, use param=\'args\' syntax.'
              '(e.g., -t="-v -x tests")')
    parser = argparse.ArgumentParser(description="ODH test framework", epilog=epilog)
    parser.add_argument("-c", "--config", help="Config file(s) to read.", action="store", dest="config_list", default=None)
    parser.add_argument("-l", "--log", help="Default logfile location.", action="store", dest="log_filename", default=None)
    parser.add_argument("--log-level", help="Default log level.", action="store", dest="log_level", default=None)
    parser.add_argument("--pytest", help="Run tests using the pytest framework.", action="store", dest="run_pytest")
    parser.add_argument("--unittest", help="Run tests using the unittest framework.", action="store", dest="run_unittest")
    parser.add_argument("-u", help="Run unittests per provided config file.", action="store_true", dest="run_unittest_config")
    parser.add_argument("-d", "--discover", help="Discover unittests from directory.", action="store", dest="discover_dir")
    args = parser.parse_args()

    handle_configs(args.config_list)
    configure_logging(args)

    if args.run_unittest_config or args.discover_dir:
        tsuite = unittest.TestSuite()
        unittest_config = {'cli_discover': 'true'} if args.discover_dir else o.config.get('unittest', False)

        if not unittest_config:
            print("ERROR: Unittest option requires a unittest configuration.")
            return False

        output_junit = unittest_config.get('output_junit', False)
        trunner = xmlrunner.XMLTestRunner(output='/tmp/odhreports') if output_junit else unittest.TextTestRunner(verbosity=2)
        loader = unittest.TestLoader()
        loader.testMethodPrefix = unittest_config.get('test_method_prefix', 'test')

        if args.discover_dir:
            o.log.debug('unittest - discover')
            start_dir = args.discover_dir
            pattern = 'test_*'
            top_level_dir = None
            discovered_tests = loader.discover(start_dir, pattern, top_level_dir)
            tsuite.addTests(discovered_tests)

        run_list = unittest_config.get('load_tests_from_list')
        if run_list:
            o.log.debug('unittest - load_tests_from_list')
            unittest_list = o.config['unittest_list']
            module_name = unittest_list['module_name']
            test_list = unittest_list['list']
            test_module_obj = importlib.import_module(module_name)
            tests_to_run = loader.loadTestsFromNames(test_list, test_module_obj)
            tsuite.addTests(tests_to_run)

        run_module = unittest_config.get('load_tests_from_module')
        if run_module:
            load_tests_from_module(loader, tsuite, run_module)

        test_name = unittest_config.get('load_tests_from_name')
        if test_name:
            o.log.debug('unittest - load_tests_from_name')
            tests_from_name = loader.loadTestsFromName(test_name)
            tsuite.addTests(tests_from_name)

        test_name_list = unittest_config.get('load_tests_from_names')
        if test_name_list:
            o.log.debug('unittest - load_tests_from_names')
            tests_from_names = loader.loadTestsFromNames(test_name_list)
            tsuite.addTests(tests_from_names)

        trunner.run(tsuite)

    retcode = 0
    if args.run_pytest:
        print("pytest: {}", args.run_pytest)
        argv = shlex.split(args.run_pytest)
        result = pytest.main(argv)
        if result > 0:
            retcode |= 1

    if args.run_unittest:
        print("unittest: {}", args.run_unittest)
        argv = shlex.split(args.run_unittest)
        argv.insert(0, 'odh-unittest')
        print("argv : {}", argv)
        test_object = unittest.main(exit=False, argv=argv)
        if test_object.result.errors or test_object.result.failures:
            retcode |= 4

    o.log.info("Ending odh-test via main()")
    print("Ending odh-test via main()")

    return retcode


if __name__ == '__main__':
    exitcode = main()
    sys.exit(exitcode)
