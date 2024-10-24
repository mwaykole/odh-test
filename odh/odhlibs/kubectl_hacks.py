from odh.odhlibs.utils import execute_command


def kubectl_apply(path_to_file: str, namespace: str = None) -> None:
    """
    Apply a Kubernetes resource configuration file using kubectl.

    Args:
        path_to_file (str): The path to the YAML or JSON file to be applied.
        namespace (str, optional): The Kubernetes namespace in which to apply the resource.
                                   If None, the resource will be applied in the default namespace.

    Raises:
        ValueError: If the path_to_file is empty or invalid.
    """

    if not path_to_file:
        raise ValueError("The path to the configuration file cannot be empty.")
    # Construct the kubectl command
    cmd = ["kubectl", "apply", "-f", path_to_file]
    if namespace:
        cmd.extend(["-n", namespace])
    # Execute the command and return the result
    stdout, retcode, stderr = execute_command(" ".join(cmd))
    if retcode != 0:
        raise RuntimeError(f"Command failed with error: {stderr.strip()}")

    return stdout.strip()