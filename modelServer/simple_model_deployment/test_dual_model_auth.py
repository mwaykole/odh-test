from modelServer.base.baseClass import OdhTestBase
from odh.odhlibs.cluster_roles_ops import use_authenticarion_for_model, get_service_account_token
from odh.odhlibs.inference_service_ops import create_inference_service
from odh.odhlibs.request_ops import infer_model
from odh.odhlibs.pods_ops import create_namespace, get_inference_service_url, \
    wait_for_custom_resource_ready, get_model_pod_restart_count
from odh.odhlibs.constant import OVMS_MNIST_INPUT, EXPECTED_OUTPUT_OVMS
from odh.odhlibs.serving_runtime_ops import create_serving_runtime_ovms_kserve

class TestAuthorinoWithTokenServerless(OdhTestBase):
    model_name_1 = "test-mnist-serverless-1"
    model_name_2 = "test-mnist-serverless-2"
    serving_runtime_1 = "test-serving-runtime-1"
    serving_runtime_2 = "test-serving-runtime-2"
    model_format = "onnx"
    min_replicas = 1
    storage_uri = "oci://quay.io/mwaykole/test:mnist-8-1"
    namespace = "test"

    role_name_1 = "models-bucket-sa1"
    sa_name_1 = "models-bucket-sa1"
    role_binding_name_1 = "models-bucket-sa-view1"

    role_name_2 = "models-bucket-sa2"
    sa_name_2 = "models-bucket-sa2"
    role_binding_name_2 = "models-bucket-sa-view2"

    def setUp(self):
        self.log.info("Starting TestAuthorinoWithTokenServerless...")

    def deploy_model_with_runtime(self, model_name, serving_runtime, role_name, sa_name, role_binding_name):
        # Create namespace
        self.namespace = create_namespace(self.namespace)

        # Create serving runtime
        create_serving_runtime_ovms_kserve(runtime_name=serving_runtime, namespace=self.namespace)

        # Create inference service for model
        create_inference_service(
            name=model_name,
            namespace=self.namespace,
            model_format=self.model_format,
            runtime=serving_runtime,
            storage_uri=self.storage_uri,
            min_replicas=self.min_replicas,
            labels={"opendatahub.io/dashboard": "true"},
            annotations={
                "openshift.io/display-name": model_name,
                "security.opendatahub.io/enable-auth": "true",
                "serving.knative.openshift.io/enablePassthrough": "true",
                "sidecar.istio.io/inject": "true",
                "sidecar.istio.io/rewriteAppHTTPProbers": "true",
                "serving.kserve.io/deploymentMode": "Serverless"
            },
            wait_for_ready=True,
        )

        # # Wait until the custom resource is ready
        # wait_for_custom_resource_ready(
        #     resource_name=model_name,
        #     namespace=self.namespace,
        #     group="serving.kserve.io",
        #     version="v1beta1",
        #     plural="inferenceservices",
        #     condition_key="conditions",
        #     expected_value="True",
        #     timeout=300,
        #     interval=5
        # )

        # Ensure minimal pod restart counts
        pods_restart_counts = get_model_pod_restart_count(namespace=self.namespace, model_name=model_name)
        self.assertLessEqual(pods_restart_counts["kserve-container"], 2)

        # Set up service account and authorization
        use_authenticarion_for_model(
            namespace=self.namespace,
            role_name=role_name,
            sa_name=sa_name,
            resource_names=model_name,
            role_binding_name=role_binding_name
        )

        # Retrieve the model's inference URL and token
        token = get_service_account_token(namespace=self.namespace, service_account_name=role_name)
        isvc_url = get_inference_service_url(model_name, self.namespace)

        return isvc_url, token

    def validate_model_inference(self, model_name, isvc_url,  token, should_fail=False):
        endpoint = f"v2/models/{model_name}/infer"
        response = infer_model(
            url=isvc_url,
            input_data=OVMS_MNIST_INPUT,
            endpoint=endpoint,
            token=token,
            retry_timeout=10
        )
        if should_fail:
            self.assertEqual(None, response)

        if not should_fail:
            self.assertEqual(response["outputs"], EXPECTED_OUTPUT_OVMS["outputs"])
        
        self.log.info(f"Inference response for model {model_name}: {response}")

    def test_dual_model_inference_with_tokens(self):
        # Deploy and test the first model with its own token
        isvc_url_1, token_1 = self.deploy_model_with_runtime(
            self.model_name_1,
            self.serving_runtime_1,
            self.role_name_1,
            self.sa_name_1,
            self.role_binding_name_1
        )
        self.validate_model_inference(self.model_name_1, isvc_url_1, token_1)

        # Deploy and test the second model with the same token as the first
        isvc_url_2, token_2 = self.deploy_model_with_runtime(
            self.model_name_2,
            self.serving_runtime_2,
            self.role_name_2,
            self.sa_name_2,
            self.role_binding_name_2
        )
        self.validate_model_inference(self.model_name_2, isvc_url_2, token_1 , should_fail=True)

        # Test second model with a new token
        token_2 = get_service_account_token(namespace=self.namespace, service_account_name=self.sa_name_2)
        self.log.info(token_2)
        self.validate_model_inference(self.model_name_2, isvc_url_2, token_2)


    # @classmethod
    # def teardown_class(cls):
    #     print("Do nothing")