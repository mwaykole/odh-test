from kubernetes import client, config
import  yaml

def create_serving_runtime_ovms_kserve(runtime_name, display_name="OVMS-Runtime",
                                image="quay.io/modh/openvino_model_server@sha256:9086c1ba1ba30d358194c534f0563923aab02d03954e43e9f3647136b44a5daf",
                                namespace="default"):
    # Load kube config
    config.load_kube_config()

    # Define metadata and annotations
    metadata = client.V1ObjectMeta(
        name=runtime_name,
        annotations={
            "opendatahub.io/recommended-accelerators": '["nvidia.com/gpu"]',
            "openshift.io/display-name": display_name
        },
        labels={
            "opendatahub.io/dashboard": "true"
        }
    )

    # Define container spec
    container = client.V1Container(
        name="kserve-container",
        image=image,
        args=[
            "--model_name={{ .Name }}",
            "--port=8001",
            "--rest_port=8888",
            "--model_path=/mnt/models",
            "--file_system_poll_wait_seconds=0",
            "--grpc_bind_address=0.0.0.0",
            "--rest_bind_address=0.0.0.0",
            "--target_device=AUTO",
            "--metrics_enable"
        ],
        ports=[client.V1ContainerPort(container_port=8888, protocol="TCP")]
    )

    # Define spec for ServingRuntime
    spec = {
        "annotations": {
            "prometheus.io/path": "/metrics",
            "prometheus.io/port": "8888"
        },
        "containers": [container],
        "multiModel": False,
        "protocolVersions": ["v2", "grpc-v2"],
        "supportedModelFormats": [
            {"name": "openvino_ir", "version": "opset13", "autoSelect": True},
            {"name": "onnx", "version": "1"},
            {"name": "tensorflow", "version": "1", "autoSelect": True},
            {"name": "tensorflow", "version": "2", "autoSelect": True},
            {"name": "paddle", "version": "2", "autoSelect": True},
            {"name": "pytorch", "version": "2", "autoSelect": True}
        ]
    }

    # Create the ServingRuntime object
    serving_runtime = client.CustomObjectsApi().create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1alpha1",
        namespace=namespace,
        plural="servingruntimes",
        body={
            "apiVersion": "serving.kserve.io/v1alpha1",
            "kind": "ServingRuntime",
            "metadata": metadata,
            "spec": spec
        }
    )

    return serving_runtime


def create_tgis_serving_runtime(runtime_name="tgis-grpc-runtime",
                                display_name="TGIS Standalone ServingRuntime for KServe",
                                model_name="/mnt/models/",
                                grpc_port=8033,
                                prometheus_port=3000,
                                image="quay.io/modh/text-generation-inference@sha256:bc9970b7f6be38266cc0c02155d377ee1f96862ea96d166dd3130c5d83c9a723",
                                hf_home="/tmp/hf_home",
                                container_port=8033,
                                namespace="default",
                                custom_args=None):
    """
    Creates a ServingRuntime custom resource in a Kubernetes cluster for KServe.

    Args:
        runtime_name (str): The name of the ServingRuntime resource. Defaults to "tgis-grpc-runtime".
        display_name (str): A display name for the runtime to appear in OpenShift UI. Defaults to "TGIS Standalone ServingRuntime for KServe".
        model_name (str): Path to the model directory inside the container. Defaults to "/mnt/models/".
        grpc_port (int): The gRPC port for the runtime. Defaults to 8033.
        prometheus_port (int): The Prometheus metrics port for monitoring. Defaults to 3000.
        image (str): The container image for the ServingRuntime. Defaults to the TGIS image.
        hf_home (str): Path to the Hugging Face home directory inside the container. Defaults to "/tmp/hf_home".
        container_port (int): The container port to be exposed for gRPC. Defaults to 8033.
        namespace (str): The Kubernetes namespace where the ServingRuntime should be created. Defaults to "default".
        custom_args (list): Optional. A list of additional command-line arguments for the ServingRuntime container. If not provided, default arguments are used.

    Returns:
        dict or None: The created ServingRuntime custom resource as a dictionary if successful, or None if an error occurs.

    Example:
        custom_args = [
            "--model-name=/mnt/models/my_model",
            "--port=3000",
            "--grpc-port=8033"
        ]
        create_tgis_serving_runtime(custom_args=custom_args)
    """

    # Load kube config
    config.load_kube_config()

    # Default args if none are provided
    args = custom_args if custom_args is not None else [
        f"--model-name={model_name}",
        f"--port={prometheus_port}",
        f"--grpc-port={grpc_port}"
    ]

    # Define the YAML for ServingRuntime
    serving_runtime_yaml = {
        "apiVersion": "v1",
        "items": [
            {
                "apiVersion": "serving.kserve.io/v1alpha1",
                "kind": "ServingRuntime",
                "metadata": {
                    "annotations": {
                        "opendatahub.io/recommended-accelerators": '["nvidia.com/gpu"]',
                        "openshift.io/display-name": display_name
                    },
                    "labels": {
                        "opendatahub.io/dashboard": "true"
                    },
                    "name": runtime_name
                },
                "spec": {
                    "annotations": {
                        "prometheus.io/path": "/metrics",
                        "prometheus.io/port": str(prometheus_port)
                    },
                    "containers": [
                        {
                            "name": "kserve-container",
                            "image": image,
                            "args": args,
                            "command": ["text-generation-launcher"],
                            "env": [
                                {
                                    "name": "HF_HOME",
                                    "value": hf_home
                                }
                            ],
                            "ports": [
                                {
                                    "containerPort": container_port,
                                    "name": "h2c",
                                    "protocol": "TCP"
                                }
                            ]
                        }
                    ],
                    "multiModel": False,
                    "supportedModelFormats": [
                        {
                            "autoSelect": True,
                            "name": "pytorch"
                        }
                    ]
                }
            }
        ],
        "kind": "List",
        "metadata": {}
    }

    # Print the YAML file
    print("The following YAML will be applied:")
    print(yaml.dump(serving_runtime_yaml, sort_keys=False))

    # Check if the ServingRuntime already exists
    try:
        existing_runtime = client.CustomObjectsApi().get_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1alpha1",
            namespace=namespace,
            plural="servingruntimes",
            name=runtime_name
        )
        print(f"ServingRuntime '{runtime_name}' already exists. Updating it...")
        # Optionally, you can implement an update function here instead of creating a new one.

    except client.exceptions.ApiException as e:
        if e.status == 404:  # Not Found
            # Create the serving runtime if it does not exist
            serving_runtime = client.CustomObjectsApi().create_namespaced_custom_object(
                group="serving.kserve.io",
                version="v1alpha1",
                namespace=namespace,
                plural="servingruntimes",
                body=serving_runtime_yaml["items"][0]
            )
            print(f"ServingRuntime '{runtime_name}' created successfully.")
            return serving_runtime
        else:
            print(f"An error occurred: {e}")
            return None
