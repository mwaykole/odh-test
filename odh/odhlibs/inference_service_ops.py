from kubernetes import client, config
from .log_utils import create_log  # Use relative import

o = create_log(name='main_log', filename='/tmp/odh_test.log', level='DEBUG')

import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def create_inference_service(name: str, namespace: str, model_format: str, runtime: str,
                             storage_uri: str, min_replicas: int, labels: dict = None,
                             annotations: dict = None, wait_for_ready: bool = False, timeout: int = 300):
    """
    Create an InferenceService for KServe and optionally wait for it to be ready.

    Args:
        name (str): The name of the InferenceService.
        namespace (str): The namespace where the InferenceService will be deployed.
        model_format (str): The format of the model (e.g., "onnx", "tensorflow").
        runtime (str): The runtime for the model (e.g., "ovms-runtime").
        storage_uri (str): The URI of the model to be served.
        min_replicas (int): Minimum number of replicas for the predictor.
        labels (dict, optional): Labels to add to the InferenceService.
        annotations (dict, optional): Annotations to add to the InferenceService.
        wait_for_ready (bool, optional): Whether to wait for the service to be ready. Default is False.
        timeout (int, optional): Maximum time to wait for the service to be ready in seconds. Default is 300.

    Returns:
        dict: The response from the Kubernetes API server.
    """
    config.load_kube_config()  # Use config.load_incluster_config() if running inside a cluster

    o.info(f"Starting to create InferenceService '{name}' in namespace '{namespace}'.")

    # Define the InferenceService manifest
    inference_service = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": labels if labels else {},
            "annotations": annotations if annotations else {},
        },
        "spec": {
            "predictor": {
                "minReplicas": min_replicas,
                "model": {
                    "modelFormat": {
                        "name": model_format,
                    },
                    "runtime": runtime,
                    "storageUri": storage_uri,
                }
            }
        }
    }

    # Create a client for the KServe API
    api_instance = client.CustomObjectsApi()

    try:
        # Log the inference service manifest
        o.info(f"InferenceService manifest: {inference_service}")

        # Create the InferenceService
        api_response = api_instance.create_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            body=inference_service
        )

        o.info(f"InferenceService '{name}' created successfully.")

        if wait_for_ready:
            o.info(f"Waiting for InferenceService '{name}' to become ready.")
            start_time = time.time()

            while time.time() - start_time < timeout:
                # Get the current status of the InferenceService
                status_response = api_instance.get_namespaced_custom_object_status(
                    group="serving.kserve.io",
                    version="v1beta1",
                    namespace=namespace,
                    plural="inferenceservices",
                    name=name
                )

                status_conditions = status_response.get("status", {}).get("conditions", [])
                for condition in status_conditions:
                    if condition.get("type") == "Ready" and condition.get("status") == "True":
                        o.info(f"InferenceService '{name}' is ready.")
                        return api_response

                # Wait before checking again
                time.sleep(5)

            o.error(f"Timed out waiting for InferenceService '{name}' to become ready.")
            return None

        return api_response

    except ApiException as e:
        o.error(f"Exception when creating InferenceService: {e}")
        return None
