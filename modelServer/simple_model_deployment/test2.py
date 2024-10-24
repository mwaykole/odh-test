import pytest
from modelServer.base.baseClass import OdhTestBase
from odh.odhlibs.cluster_roles_ops import use_authenticarion_for_model, get_service_account_token
from odh.odhlibs.inference_service_ops import create_inference_service
from odh.odhlibs.request_ops import infer_model
from odh.odhlibs.utils import get_elements_with_prefix
from odh.odhlibs.pods_ops import create_namespace, get_pod_names_from_deployment, get_inference_service_url, \
    wait_for_custom_resource_ready, get_deployments_in_namespace, get_pod_restart_count
from odh.odhlibs.constant import OVMS_MNIST_INPUT, EXPECTED_OUTPUT_OVMS
from odh.odhlibs.serving_runtime_ops import create_serving_runtime_ovms_kserve


class TestAuthorinoWithTokenServerless(OdhTestBase):
    serving_runtime_context = {
        'display_name': 'Test ServingRuntime 1',
        'runtime_name': 'test-serving-runtime-1',
        'grpc_enabled': 'false',
        'http_enabled': 'true',
        'image': 'quay.io/modh/openvino_model_server@sha256:9086c1ba1ba30d358194c534f0563923aab02d03954e43e9f3647136b44a5daf',
        'container_port': 8080
    }
    model_name1 = "test-serving-runtime-1"
    model_name2 = "test-serving-runtime-1"
    token1= ""
    token2= ""

    @classmethod
    def teardown_class(cls):
        print("Do nothing")

    def setUp(self):
        self.log.info("test----------------------------------")

    def test_ovms_model_with_token_oci(self):
        inference_service_context = {
            'model_name': 'test-mnist-serverless-1',
            'min_replicas': 1,
            'model_format': 'onnx',
            'runtime': 'test-serving-runtime-1',
            'storage_uri': 'oci://quay.io/mwaykole/test:mnist-8-1'
        }
        self.namespace = create_namespace("test")

        # Get the Jinja2 template file name
        model_name = inference_service_context['model_name']

        runtime_name = "test-serving-runtime-1"
        create_serving_runtime_ovms_kserve(runtime_name=runtime_name, namespace=self.namespace)
        create_inference_service(name=model_name,
                                 namespace=self.namespace,
                                 model_format="onnx",
                                 runtime=runtime_name,
                                 storage_uri=inference_service_context["storage_uri"],
                                 min_replicas=1,
                                 labels={
                                     "opendatahub.io/dashboard": "true",
                                 },
                                 annotations={"openshift.io/display-name": model_name,
                                              "security.opendatahub.io/enable-auth": "true",
                                              "serving.knative.openshift.io/enablePassthrough": "true",
                                              "sidecar.istio.io/inject": "true",
                                              "sidecar.istio.io/rewriteAppHTTPProbers": "true",
                                              "serving.kserve.io/deploymentMode": "Serverless"
                                              },
                                 wait_for_ready=True,
                                 )

        wait_for_custom_resource_ready(resource_name=model_name, namespace=self.namespace, group="serving.kserve.io",
                                       version="v1beta1", plural="inferenceservices", condition_key="conditions",
                                       expected_value="True", timeout=300, interval=5)

        deployment_name = get_deployments_in_namespace(namespace=self.namespace)
        self.log.info("Deployment name {}".format(deployment_name))
        assert deployment_name, "The list 'deployment_name' is empty!"
        deployment_name = get_elements_with_prefix(deployment_name, model_name)[0]

        if not deployment_name:
            self.log.error("deployment name not found: {}".format(deployment_name))

        pod_name = get_pod_names_from_deployment(deployment_name,
                                                 namespace=self.namespace)[0]

        self.log.info("pod name {}".format(pod_name))
        pod_restart_count = get_pod_restart_count(pod_name, self.namespace)

        self.log.info(pod_restart_count)

        use_authenticarion_for_model(
            namespace=self.namespace,
            role_name="models-bucket-sa",
            sa_name="models-bucket-sa",
            resource_names=model_name,
            role_binding_name="models-bucket-sa-view"

        )
        token = get_service_account_token(namespace=self.namespace, service_account_name="models-bucket-sa")
        isvc_url = get_inference_service_url(inference_service_context['model_name'], self.namespace)
        endpoint = "v2/models/{}/infer".format(model_name)
        self.log.info(isvc_url)
        self.log.info(token)
        print(token)
        print(isvc_url)
        respond = infer_model(url=isvc_url, input_data=OVMS_MNIST_INPUT, endpoint=endpoint, token=token,
                              retry_timeout=10)
        self.assertEqual(respond, EXPECTED_OUTPUT_OVMS)
        self.log.info(respond)
        print(respond)


