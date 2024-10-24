import pytest
from odh.odhlibs.namespace_ops import create_namespace
from odh.odhlibs.utils import render_jinja2_template_to_yaml, get_jinja_file_name
import subprocess
import logging


# Utility to apply the generated YAML using kubectl
def apply_yaml_with_kubectl(yaml_file):
    """
    Applies a YAML file using kubectl.
    """
    command = ["kubectl", "apply", "-f", yaml_file]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error applying YAML: {result.stderr}")
    print(f"YAML applied successfully: {result.stdout}")


# Function to verify if ServingRuntime was created successfully
def verify_serving_runtime(runtime_name):
    """
    Verifies if a ServingRuntime exists in the Kubernetes cluster.
    """
    command = ["kubectl", "get", "servingruntime", runtime_name]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, f"ServingRuntime {runtime_name} not found: {result.stderr}"
    print(f"ServingRuntime {runtime_name} exists: {result.stdout}")


# Test case for generating and applying ServingRuntime and InferenceService
@pytest.mark.parametrize("serving_runtime_context, inference_service_context", [
    (
            {
                'display_name': 'Test ServingRuntime 1',
                'runtime_name': 'test-serving-runtime-1',
                'grpc_enabled': 'false',
                'http_enabled': 'true',
                'image': 'quay.io/test-image-1@sha256:testhash1',
                'container_port': 8080
            },
            {
                'enablePassthrough': 'true',
                'istio_sidecar_inject': 'true',
                'deploymentMode': 'Serverless',
                'model_name': 'test-mnist-serverless-1',
                'min_replicas': 1,
                'model_format': 'onnx',
                'runtime': 'test-serving-runtime-1',
                'storage_uri': 'oci://quay.io/test:mnist-8-big'
            }
    ),
])
def test_dynamic_serving_runtime_creation(serving_runtime_context, inference_service_context):
    """
    Test dynamically creating and applying KServe ServingRuntime and InferenceService.
    """
    # Ensure the namespace is created
    try:
        create_namespace("caikit-standalone")
        logging.info("NameSpace created")
    except Exception as e:
        pytest.fail(f"Failed to create namespace: {str(e)}")
    TEMPLATE_DIR = '../odh/odhlibs/serving_runtime_templates'

    # Apply ServingRuntime and InferenceService
    sr_template_name = get_jinja_file_name("kserve_ovms")
    render_jinja2_template_to_yaml(template_path=TEMPLATE_DIR +"/"+ sr_template_name, context=serving_runtime_context)
