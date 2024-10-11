import random
import string
import datetime
import shlex
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class DeploymentManager:
    def __init__(self, kube_admin_conf_path, namespace):
        config.load_kube_config(config_file=kube_admin_conf_path)
        self.namespace = namespace

    def create_deployment(self, username, image, command = None):
        apps_v1 = client.AppsV1Api()
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        deployment_name = f"{username}-{now}-{image.split(':')[0].replace('_','.')}-{random_string}"
        if command is None:
            container = client.V1Container(
                name="container",
                image=image
            )
        else:
            container = client.V1Container(
                name="container",
                image=image,
                command = shlex.split(command)
            )
        deployment_manifest = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=deployment_name,
                labels={"owner": username}
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": deployment_name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={
                                                    "app": deployment_name,
                                                    "owner": username
                    }),
                    spec=client.V1PodSpec(containers=[container])
                )
            )
        )

        try:
            apps_v1.create_namespaced_deployment(namespace=self.namespace, body=deployment_manifest)
            return True
        except ApiException as e:
            print(f"Failed to create deployment: {e}")
            return False

    def delete_deployment(self, deployment_name):
        apps_v1 = client.AppsV1Api()

        try:
            apps_v1.delete_namespaced_deployment(name=deployment_name, namespace=self.namespace)
            return True
        except ApiException as e:
            print(f"Failed to delete deployment: {e}")
            return False

    def list_deployments(self, username):
        apps_v1 = client.AppsV1Api()

        try:
            deployments = apps_v1.list_namespaced_deployment(
                namespace=self.namespace,
                label_selector=f"owner={username}"
            )
            return [d.metadata.name for d in deployments.items]
        except ApiException as e:
            print(f"Failed to list deployments: {e}")
            return []

    def find_pod_by_deployment(self, deployment_name):
        apps_v1 = client.AppsV1Api()
        core_v1 = client.CoreV1Api()

        try:
            deployment = apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace
            )
            pod_label_selector = ",".join([
                f"{k}={v}" for k, v in deployment.spec.selector.match_labels.items()
            ])
            pods = core_v1.list_namespaced_pod(namespace=self.namespace,
                                               label_selector=pod_label_selector)

            if not pods.items:
                return None

            first_pod_name = pods.items[0].metadata.name
            return first_pod_name

        except ApiException as e:
            print(f"Error while searching for deployment {deployment_name}"
                   " in namespace {self.namespace}:", e)
            return None
