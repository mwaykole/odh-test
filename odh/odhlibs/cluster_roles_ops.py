import base64
import json

from odh.odhlibs.log_utils import create_log
from odh.odhlibs.utils import execute_command
from kubernetes import client, config
from kubernetes.client.rest import ApiException

o = create_log(name='cluster_role', filename='/tmp/odh_test.log', level='DEBUG')


def create_service_account(namespace, sa_name):
    """Create a ServiceAccount."""
    v1 = client.CoreV1Api()
    service_account = client.V1ServiceAccount(
        metadata=client.V1ObjectMeta(name=sa_name, namespace=namespace)
    )
    try:
        print(f"Creating ServiceAccount: {sa_name}")
        v1.create_namespaced_service_account(namespace=namespace, body=service_account)
    except ApiException as e:
        if e.status == 409:
            print(f"ServiceAccount '{sa_name}' already exists.")
        else:
            print(f"Error creating ServiceAccount: {e}")


def create_role(namespace, role_name, rules):
    """Create a Role with specified rules."""
    rbac_v1 = client.RbacAuthorizationV1Api()
    role = client.V1Role(
        metadata=client.V1ObjectMeta(name=role_name, namespace=namespace),
        rules=rules
    )
    try:
        print(f"Creating Role: {role_name}")
        rbac_v1.create_namespaced_role(namespace=namespace, body=role)
    except ApiException as e:
        if e.status == 409:
            print(f"Role '{role_name}' already exists.")
        else:
            print(f"Error creating Role: {e}")


def create_role_binding(namespace, role_binding_name, sa_name, role_name):
    """Create a RoleBinding that binds a Role to a ServiceAccount."""
    rbac_v1 = client.RbacAuthorizationV1Api()
    role_binding = client.V1RoleBinding(
        metadata=client.V1ObjectMeta(name=role_binding_name, namespace=namespace),
        subjects=[client.RbacV1Subject(kind="ServiceAccount", name=sa_name, namespace=namespace)],
        role_ref=client.V1RoleRef(
            api_group="rbac.authorization.k8s.io",
            kind="Role",
            name=role_name
        )
    )
    try:
        print(f"Creating RoleBinding: {role_binding_name}")
        rbac_v1.create_namespaced_role_binding(namespace=namespace, body=role_binding)
    except ApiException as e:
        if e.status == 409:
            print(f"RoleBinding '{role_binding_name}' already exists.")
        else:
            print(f"Error creating RoleBinding: {e}")


def use_authenticarion_for_model(namespace, sa_name, role_name, role_binding_name, resource_names):
    """Main function to create the ServiceAccount, Role, and RoleBinding."""
    config.load_kube_config()

    # Step 1: Create ServiceAccount
    create_service_account(namespace, sa_name)

    # Step 2: Define Role Rules
    rules = [
        client.V1PolicyRule(
            api_groups=["serving.kserve.io"],
            resources=["inferenceservices"],
            resource_names=[resource_names],
            verbs=["get", "list", "watch"]
        )
    ]

    # Step 3: Create Role
    create_role(namespace, role_name, rules)

    # Step 4: Create RoleBinding
    create_role_binding(namespace, role_binding_name, sa_name, role_name)

    print(f"Resources created: ServiceAccount='{sa_name}', Role='{role_name}', RoleBinding='{role_binding_name}'")


def delete_service_account(namespace, sa_name):
    """Delete a ServiceAccount."""
    v1 = client.CoreV1Api()
    try:
        print(f"Deleting ServiceAccount: {sa_name}")
        v1.delete_namespaced_service_account(name=sa_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            print(f"ServiceAccount '{sa_name}' not found.")
        else:
            print(f"Error deleting ServiceAccount: {e}")


def delete_role(namespace, role_name):
    """Delete a Role."""
    rbac_v1 = client.RbacAuthorizationV1Api()
    try:
        print(f"Deleting Role: {role_name}")
        rbac_v1.delete_namespaced_role(name=role_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            print(f"Role '{role_name}' not found.")
        else:
            print(f"Error deleting Role: {e}")


def delete_role_binding(namespace, role_binding_name):
    """Delete a RoleBinding."""
    rbac_v1 = client.RbacAuthorizationV1Api()
    try:
        print(f"Deleting RoleBinding: {role_binding_name}")
        rbac_v1.delete_namespaced_role_binding(name=role_binding_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            print(f"RoleBinding '{role_binding_name}' not found.")
        else:
            print(f"Error deleting RoleBinding: {e}")


def delete_token_resources(namespace, sa_name, role_name, role_binding_name):
    """Main function to delete the ServiceAccount, Role, and RoleBinding."""
    config.load_kube_config()

    # Step 1: Delete RoleBinding
    delete_role_binding(namespace, role_binding_name)

    # Step 2: Delete Role
    delete_role(namespace, role_name)

    # Step 3: Delete ServiceAccount
    delete_service_account(namespace, sa_name)

    print(f"Resources deleted: ServiceAccount='{sa_name}', Role='{role_name}', RoleBinding='{role_binding_name}'")


def get_service_account_token(namespace, service_account_name, additional_args=None):
    """
    Retrieve the token for a specified Kubernetes service account.

    Args:
        namespace (str): The Kubernetes namespace where the service account resides.
        service_account_name (str): The name of the service account.
        additional_args (str, optional): Additional command-line arguments for the `kubectl create token` command.

    Returns:
        str: The token for the service account, or None if an error occurred.
    """
    # Build the kubectl command
    command = f"kubectl create token -n {namespace} {service_account_name}"

    # Add additional command arguments if provided
    if additional_args:
        command += f" {additional_args}"

    # Execute the command using the external function
    stdout, return_code, stderr = execute_command(command)

    # Check the return code for success
    if return_code == 0:
        return stdout.strip()
    else:
        o.log.error(
            f"Error retrieving token for service account '{service_account_name}' in namespace '{namespace}': {stderr.strip()}")
        return None


# def get_service_account_token(namespace, sa_name):
#     """Get the 'auth' value from the .dockercfg secret of a ServiceAccount in the specified namespace."""
#     config.load_kube_config()
#     v1 = client.CoreV1Api()
#
#     try:
#         # Get the ServiceAccount object
#         sa = v1.read_namespaced_service_account(name=sa_name, namespace=namespace)
#
#         # Extract the secret name from the ServiceAccount
#         if not sa.secrets:
#             raise Exception(f"No secrets found for ServiceAccount '{sa_name}'")
#
#         secret_name = sa.secrets[0].name  # Assume the first secret contains the .dockercfg
#         print(f"Found Secret: {secret_name}")
#
#         # Get the Secret object
#         secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)
#
#         # Extract and decode the .dockercfg file from the secret
#         dockercfg_b64 = secret.data.get(".dockercfg")
#         if not dockercfg_b64:
#             raise Exception(f"No .dockercfg found in secret '{secret_name}'")
#
#         dockercfg_json = base64.b64decode(dockercfg_b64).decode("utf-8")
#         dockercfg = json.loads(dockercfg_json)
#
#         # Extract the auth value from the first entry (assumes one registry entry)
#         auth_value = list(dockercfg.values())[0].get("auth")
#         if not auth_value:
#             raise Exception(f"No 'auth' value found in .dockercfg")
#
#         print(f"Retrieved 'auth' value: {auth_value}")
#         return auth_value
#
#     except ApiException as e:
#         print(f"Error retrieving .dockercfg for ServiceAccount '{sa_name}': {e}")
#         return None

    # useage
    #
    # if __name__ == "__main__":
    namespace = "test"
    sa_name = "models-bucket-sa"
    role_name = "models-bucket-sa"
    role_binding_name = "models-bucket-sa-view"


#
#     # Create resources
#     use_authenticarion_for_model(
#         namespace=namespace,
#         sa_name=sa_name,
#         role_name=role_name,
#         role_binding_name=role_binding_name,
#         resource_names=" mnist-test"
#     )
#     # To delete the resources after they are no longer needed
#     delete_token_resources(
#         namespace=namespace,
#         sa_name=sa_name,
#         role_name=role_name,
#         role_binding_name=role_binding_name
#     )
# token = get_service_account_token(namespace="test", service_account_name="models-bucket-sa")
# print(token)
