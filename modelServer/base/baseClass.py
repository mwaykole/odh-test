import os
from odh.odhlibs.utils import execute_command
from modelServer.base.odh_main import Odh as o
from unittest import TestCase


class OdhTestBase(o, TestCase):
    def __init_subclass__(cls, **kwargs):
        """Automatically initialize the logger when the subclass is created."""
        super().__init_subclass__(**kwargs)
        # Initialize the logger for the test class
        o.log = o.create_log(name=f'{o.__name__}Log', filename='/tmp/odh_test.log', level='DEBUG')
        o.log.info(f"Logger initialized for {o.__name__}")

    @classmethod
    def get_template_dir(cls, serving_runtime=False, inference_service=False):
        """
        Get the directory path for the Jinja2 templates.

        Args:
            serving_runtime (bool): If True, return the path to serving runtime templates.
            inference_service (bool): If True, return the path to inference service templates.

        Returns:
            str: The directory path for the specified template type.

        Raises:
            ValueError: If neither serving_runtime nor inference_service is True.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Determine the path to the templates directory based on the input flags
        if serving_runtime:
            return os.path.join(current_dir, '..', '..', 'odh', 'odhlibs', 'serving_runtime_templates')
        if inference_service:
            return os.path.join(current_dir, '..', '..', 'odh', 'odhlibs', 'inference_service_template')

        raise ValueError("Either 'serving_runtime' or 'inference_service' must be set to True.")

    @classmethod
    def get_template_path(cls, template_name, serving_runtime=False, inference_service=False):
        """
        Generate the full path for a specific template.

        Args:
            template_name (str): The name of the template file.
            serving_runtime (bool): If True, fetch the path from serving runtime templates.
            inference_service (bool): If True, fetch the path from inference service templates.

        Returns:
            str: The full path to the specified template.
        """
        template_dir = cls.get_template_dir(serving_runtime=serving_runtime, inference_service=inference_service)

        return os.path.join(template_dir, template_name)

    @classmethod
    def setup_class(cls):
        """
        Setup resources before any tests run.
        This is executed once before all tests in the class.
        """
        cls.log.info("Setting up resources for OdhTestBase tests.")
        # You can add any common setup logic here.
        # Example: Initializing environment variables, loading configurations, etc.

    @classmethod
    def teardown_class(cls):
        """
        Teardown resources after all tests in the class have run.
        This is executed once after all tests in the class.
        """
        execute_command("oc delete isvc,servingruntime --all -A")
        print("Tearing down resources for OdhTestBase tests.")
        # Add any cleanup logic here.
        # Example: Closing connections, deleting temporary files, etc.

    def setUp(self):
        """
        Set up specific resources for each test method.
        This method is called before every individual test method.
        """
        self.log.info("Setting up for individual test.+++++++++++++++++++++++++++++++++++++++++++++++++++++")