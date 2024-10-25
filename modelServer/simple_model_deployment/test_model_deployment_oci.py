from modelServer.base.baseClass import OdhTestBase
from odh.odhlibs.cluster_roles_ops import use_authenticarion_for_model, get_service_account_token
from odh.odhlibs.inference_service_ops import create_inference_service
from odh.odhlibs.request_ops import infer_model
from odh.odhlibs.pods_ops import create_namespace, get_inference_service_url, \
    wait_for_custom_resource_ready, get_model_pod_restart_count, get_model_pod_restart_count
from odh.odhlibs.constant import OVMS_MNIST_INPUT, EXPECTED_OUTPUT_OVMS
from odh.odhlibs.serving_runtime_ops import create_serving_runtime_ovms_kserve


class TestAuthorinoWithTokenServerless(OdhTestBase):
    # @classmethod
    # def teardown_class(cls):
    #     print("Do nothing")
    
    model_name_1= "test-mnist-serverless-1"
    model_name_2="test-mnist-serverless-2"
    serving_runtime_1="test-serving-runtime-1" 
    serving_runtime_2="test-serving-runtime-2"
    model_format="onnx"
    min_replicas=1
    storage_uri = "oci://quay.io/mwaykole/test:mnist-8-1"
    namespace = "test"

    role_name_1="models-bucket-sa1",
    sa_name_1="models-bucket-sa1",
    role_binding_name_1="models-bucket-sa-view1"



    def setUp(self):
        self.log.info("test----------------------------------")

    def test_ovms_model_with_token_oci(self):

        self.namespace = create_namespace(self.namespace)

        create_serving_runtime_ovms_kserve(runtime_name=self.serving_runtime_1, namespace=self.namespace)
        create_inference_service(name=self.model_name_1,
                                 namespace=self.namespace,
                                 model_format=self.model_format,
                                 runtime=self.serving_runtime_1,
                                 storage_uri=self.storage_uri,
                                 min_replicas=self.min_replicas,
                                 labels={
                                     "opendatahub.io/dashboard": "true",
                                 },
                                 annotations={"openshift.io/display-name": self.model_name_1,
                                              "security.opendatahub.io/enable-auth": "true",
                                              "serving.knative.openshift.io/enablePassthrough": "true",
                                              "sidecar.istio.io/inject": "true",
                                              "sidecar.istio.io/rewriteAppHTTPProbers": "true",
                                              "serving.kserve.io/deploymentMode": "Serverless"
                                              },
                                 wait_for_ready=True,
                                 )

        
        wait_for_custom_resource_ready(resource_name=self.model_name_1, namespace=self.namespace, group="serving.kserve.io",
                                       version="v1beta1", plural="inferenceservices", condition_key="conditions",
                                       expected_value="True", timeout=300, interval=5)



        pods_restart_counts=get_model_pod_restart_count(namespace= self.namespace, model_name= self.model_name_1)
        
        self.assertLessEqual(pods_restart_counts["kserve-container"],2)
        


        use_authenticarion_for_model(
            namespace=self.namespace,
            role_name=self.role_name_1,
            sa_name=self.sa_name_1,
            resource_names=self.model_name_1,
            role_binding_name=self.role_binding_name_1

        )
        token = get_service_account_token(namespace=self.namespace, service_account_name=self.role_name_1)
        isvc_url = get_inference_service_url(self.model_name_1, self.namespace)
        endpoint = "v2/models/{}/infer".format(self.model_name_1)


        respond = infer_model(url=isvc_url, input_data=OVMS_MNIST_INPUT, endpoint=endpoint, token=token,
                              retry_timeout=10)
        self.assertEqual(respond, EXPECTED_OUTPUT_OVMS)
        self.log.info(respond)
        print(respond)


