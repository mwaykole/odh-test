import time

from kubernetes.client import ApiException
from kubernetes import client, config

from odh.odhlibs.log_utils import create_log

o = create_log(name='main_log', filename='/tmp/odh_test.log', level='DEBUG')


def wait_until_pod_ready(pod_name, namespace):
    """Waits until the specified pod is ready.

    Args:
        pod_name (str): The name of the pod.
        namespace (str): The namespace of the pod.
    """

    config.load_kube_config()
    v1 = client.CoreV1Api()

    while True:
        pod = v1.read_namespaced_pod(pod_name, namespace)
        if pod.status.phase == "Running" and all(
                container.ready == True for container in pod.status.container_statuses):
            break
        time.sleep(5)


def create_namespace(namespace_name):
    """
    Creates a new namespace with the specified name if it doesn't already exist.

    Args:
        namespace_name (str): The name of the namespace.

    Returns:
        str: The name of the namespace.
    """
    # Load Kubernetes configuration
    config.load_kube_config()
    v1 = client.CoreV1Api()

    try:
        # Check if the namespace already exists
        v1.read_namespace(name=namespace_name)
        o.warn(f"Namespace '{namespace_name}' already exists.")
    except ApiException as e:
        if e.status == 404:
            # Namespace does not exist, proceed with creation
            o.info(f"Namespace '{namespace_name}' does not exist. Creating it...")
            body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
            v1.create_namespace(body=body)
            o.info(f"Namespace '{namespace_name}' created successfully.")
        else:
            # Handle other API exceptions
            o.error(f"Error occurred while checking/creating namespace: {e}")
            raise

    return namespace_name


def delete_namespace(namespace_name):
    """Deletes the specified namespace.

    Args:
        namespace_name (str): The name of the namespace.
    """

    config.load_kube_config()
    v1 = client.CoreV1Api()

    v1.delete_namespace(namespace_name)


def list_namespaces():
    """Lists all namespaces in the cluster.

    Returns:
        list[str]: A list of namespace names.
    """

    config.load_kube_config()
    v1 = client.CoreV1Api()

    namespaces = v1.list_namespace()
    return [namespace.metadata.name for namespace in namespaces.items]


def get_pod_status(pod_name, namespace):
    """Gets the status of the specified pod.

    Args:
        pod_name (str): The name of the pod.
        namespace (str): The namespace of the pod.

    Returns:
        str: The status of the pod (e.g., "Running", "Pending", "Failed").
    """

    config.load_kube_config()
    v1 = client.CoreV1Api()

    pod = v1.read_namespaced_pod(pod_name, namespace)
    return pod.status.phase


def get_pod_logs(pod_name, namespace):
    """Gets the logs of the specified pod.

    Args:
        pod_name (str): The name of the pod.
        namespace (str): The namespace of the pod.

    Returns:
        str: The logs of the pod.
    """

    config.load_kube_config()
    v1 = client.CoreV1Api()

    logs = v1.read_namespaced_pod_log(pod_name, namespace)
    return logs


def execute_command_in_pod(pod_name, namespace, command):
    """Executes a command in the specified pod.

    Args:
        pod_name (str): The name of the pod.
        namespace (str): The namespace of the pod.
        command (list[str]): The command to execute.
    """

    config.load_kube_config()
    v1 = client.CoreV1Api()

    exec_cmd = v1.read_namespaced_pod(pod_name, namespace)
    exec_cmd.metadata.name = pod_name
    exec_cmd.spec.containers[0].command = command

    v1.patch_namespaced_pod(pod_name, namespace, body=exec_cmd)


def get_pod_restart_count(pod_name, namespace):
    """
    Gets the restart count of each container in the specified pod.

    Args:
        pod_name (str): The name of the pod.
        namespace (str): The namespace of the pod.

    Returns:
        dict: A dictionary with container names as keys and their respective restart counts as values.
    """

    # Load the Kubernetes configuration
    config.load_kube_config()

    # Create an instance of the CoreV1Api
    v1 = client.CoreV1Api()

    # Get the pod details
    pod = v1.read_namespaced_pod(pod_name, namespace)

    # Extract restart counts for all containers
    container_restart_counts = {
        container_status.name: container_status.restart_count
        for container_status in pod.status.container_statuses
    }

    return container_restart_counts


def get_deployments_in_namespace(namespace):
    # Load the Kubernetes configuration
    config.load_kube_config()  # This assumes you're running the script locally with a kubeconfig file

    # Create an instance of the AppsV1Api
    v1_apps = client.AppsV1Api()

    try:
        # List all deployments in the specified namespace
        deployments = v1_apps.list_namespaced_deployment(namespace=namespace)
        deployment_names = [deployment.metadata.name for deployment in deployments.items]

        return deployment_names

    except client.exceptions.ApiException as e:
        print(f"Error fetching deployments: {e}")
        return []


def get_pod_names_from_deployment(deployment_name: str, namespace: str) -> list:
    """
    Get the names of all pods associated with a specific deployment.

    Args:
        deployment_name (str): The name of the deployment.
        namespace (str): The namespace in which the deployment exists.

    Returns:
        list: A list of pod names associated with the deployment.

    Raises:
        ApiException: If there is an error communicating with the Kubernetes API.
    """
    try:
        # Load Kubernetes configuration (from kubeconfig or in-cluster)
        config.load_kube_config()  # Use this for local kubeconfig
        # config.load_incluster_config()  # Use this for in-cluster config

        # Initialize the API client for accessing core and apps resources
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()

        # Get the deployment to extract the label selector
        deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        label_selector = deployment.spec.selector.match_labels

        # Convert the match_labels dictionary into a label selector string
        label_selector_str = ",".join([f"{key}={value}" for key, value in label_selector.items()])

        # List all the pods in the given namespace that match the label selector
        pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector_str)

        # Extract and return the names of the pods
        pod_names = [pod.metadata.name for pod in pods.items]
        return pod_names

    except ApiException as e:
        print(f"Exception when calling Kubernetes API: {e}")
        raise


def get_inference_service_url(service_name: str, namespace: str) -> str:
    """
    Retrieve the URL of the specified InferenceService.

    Args:
        service_name (str): The name of the InferenceService.
        namespace (str): The namespace where the InferenceService is deployed.

    Returns:
        str: The URL of the InferenceService, or an error message if not found.

    Raises:
        ApiException: If there is an error communicating with the Kubernetes API.
    """
    try:
        # Load kubeconfig
        config.load_kube_config()  # Use config.load_incluster_config() if running inside a pod

        # Create a client for the KServe API
        k8s_client = client.CustomObjectsApi()

        # Specify the group, version, and plural for InferenceServices
        group = "serving.kserve.io"
        version = "v1beta1"  # or the relevant version
        plural = "inferenceservices"

        # Get the InferenceService
        isvc = k8s_client.get_namespaced_custom_object(group, version, namespace, plural, service_name)

        # Extract and return the URL from the status
        url = isvc.get("status", {}).get("url", "URL not found.")
        return url

    except ApiException as e:
        return f"Exception when calling CustomObjectsApi->get_namespaced_custom_object: {e}"


def get_latest_ready_revision(resource_name: str, namespace: str, ) -> str:
    """
    Get the latest ready revision (LATESTREADYREVISION) of a specified InferenceService.

    Args:
        resource_name (str): The name of the InferenceService.
        namespace (str): The namespace where the InferenceService is deployed.

    Returns:
        str: The LATESTREADYREVISION of the InferenceService, or an error message if not found.
    """
    # Load kubeconfig for accessing the cluster
    config.load_kube_config()  # Use config.load_incluster_config() if running inside a pod

    # Create a client for the CustomObjects API
    k8s_client = client.CustomObjectsApi()

    group = "serving.kserve.io"  # Custom resource group for KServe
    version = "v1beta1"  # Custom resource version
    plural = "inferenceservices"  # Custom resource plural

    try:
        # Get the InferenceService object
        isvc = k8s_client.get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=resource_name
        )

        # Retrieve the status and access the predictor component
        status = isvc.get("status", {})
        components = status.get("components", {})
        predictor = components.get("predictor", {})
        print("_______________________________________________")
        print(predictor)
        print("_______________________________________________")
        # Retrieve the latest ready revision
        latest_ready_revision = predictor.get("latestReadyRevision", "No ready revision found")

        return latest_ready_revision

    except client.exceptions.ApiException as e:
        return f"Exception when calling CustomObjectsApi: {e}"

    except KeyError as e:
        return f"Key error: {e} not found in the InferenceService object."


from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time


def wait_for_custom_resource_ready(resource_name: str, namespace: str, group: str, version: str, plural: str,
                                   condition_key: str, expected_value: str, timeout: int = 300,
                                   interval: int = 5) -> bool:
    """
    Wait for a custom resource to reach a specified condition.

    Args:
        resource_name (str): The name of the custom resource.
        namespace (str): The namespace where the custom resource is deployed.
        group (str): The group of the custom resource.
        version (str): The version of the custom resource.
        plural (str): The plural form of the custom resource.
        condition_key (str): The key to check in the status.
        expected_value (str): The expected value of the condition key.
        timeout (int, optional): Maximum time to wait for the resource to be ready in seconds. Defaults to 300.
        interval (int, optional): Time to wait between checks in seconds. Defaults to 5.

    Returns:
        bool: True if the resource reaches the expected state, False if the timeout is reached.

    Raises:
        ApiException: If there is an error communicating with the Kubernetes API.
    """
    # Load kubeconfig for accessing the Kubernetes cluster
    config.load_kube_config()  # Use config.load_incluster_config() if running inside a pod

    # Initialize the CustomObjectsApi client
    k8s_client = client.CustomObjectsApi()

    start_time = time.time()

    while time.time() - start_time <= timeout:
        try:
            # Retrieve the custom resource
            resource = k8s_client.get_namespaced_custom_object(group, version, namespace, plural, resource_name)

            # Get the status section of the resource
            status = resource.get("status", {})

            # Extract the condition status if available
            condition_status = status.get(condition_key, [{}])[0].get("status")

            # Check if the condition meets the expected value
            if condition_status == expected_value:
                print(f"{resource_name} is in the '{expected_value}' state.")
                return True

            # Log the current state and wait for the next check
            print(f"Waiting for {resource_name} to be ready... Current state: {condition_status}")
            time.sleep(interval)

        except ApiException as e:
            print(f"Error when calling CustomObjectsApi: {e}")
            return False

    # Timeout reached, resource did not become ready
    print(f"Timeout: {resource_name} did not reach '{expected_value}' within {timeout} seconds.")
    return False
