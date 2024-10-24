from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


def create_namespace(namespace_name):
    """
    Create a Kubernetes namespace.

    Args:
        namespace_name (str): The name of the namespace to create.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        # Load kubeconfig
        config.load_kube_config()  # Use this for local development (e.g., kubectl config)

        # Create a V1Namespace object
        namespace = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace_name)
        )

        # Create the namespace in the cluster
        api_instance = client.CoreV1Api()
        api_instance.create_namespace(namespace)

        return None

    except ApiException as e:
        return f"Exception when creating namespace: {e.reason}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
