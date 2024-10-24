import pytest
from base.baseClass import OdhTestBase  # Import the base class
from odh.odhlibs.utils import get_jinja_file_name , render_jinja2_template_to_yaml

class TestServingRuntime(OdhTestBase):

    def test_render_jinja2_template(self):
        kserve_ovms_template_value = {
            'display_name': 'OpenVINO Model Server',
            'runtime_name': 'kserve-ovms',
            'image': 'quay.io/modh/openvino_model_server@sha256:9086c1ba1ba30d358194c534f0563923aab02d03954e43e9f3647136b44a5daf',
            'container_port': 8080
        }
       # Get the Jinja2 template file name
        sr_template_name = get_jinja_file_name("kserve_ovms")

        # Use the base class method to get the full template path
        template_path = self.get_template_path(sr_template_name)

        # Render and convert Caikit Standalone ServingRuntime to YAML
        yaml_content = render_jinja2_template_to_yaml(template_path=template_path, context=kserve_ovms_template_value)

        # Assert that the YAML content is not empty
        assert yaml_content is not None
