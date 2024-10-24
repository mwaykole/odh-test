from kubernetes import client, config

def get_service_account_token(service_account_name, namespace='default'):
    try:
        # Load kubeconfig from default location
        config.load_kube_config()

        # Create a V1ServiceAccount object
        v1_service_account = client.CoreV1Api()

        # Retrieve the service account
        service_account = v1_service_account.read_namespaced_service_account(
            name=service_account_name, namespace=namespace)

        # Check if the service account has a secret associated with it
        if service_account.secrets:
            secret_name = service_account.secrets[0].name

            # Get the secret that contains the token
            v1_secret = v1_service_account.read_namespaced_secret(
                name=secret_name, namespace=namespace)

            # Extract the token from the secret data
            token = v1_secret.data
            return token
        else:
            print(f"No secrets found for service account '{service_account_name}'")
            return None

    except client.exceptions.ApiException as e:
        print(f"Exception when retrieving token for service account: {e}")
        return None


# Example usage
if __name__ == '__main__':
    token = get_service_account_token('models-bucket-sa', 'test')
    if token:
        print(f"Token for service account 'models-bucket-sa': {token}")
