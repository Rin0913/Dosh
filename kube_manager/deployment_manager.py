import random
import string
import datetime
import shlex
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class DeploymentManager:
    def __init__(self, kube_conf_path, namespace, service_dns):
        config.load_kube_config(config_file=kube_conf_path)
        self.namespace = namespace
        self.service_dns = service_dns

    def create_deployment(self, username, image, deployment_name = None, command = None):
        apps_v1 = client.AppsV1Api()
        core_v1 = client.CoreV1Api()
        if not deployment_name:
            now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            img_name = image.split(':')[0].replace('_','.')
            deployment_name = f"{username}-{now}-{img_name}-{random_string}"

        resources = client.V1ResourceRequirements(
            requests={"ephemeral-storage": "6Gi", "cpu": "0.1", "memory": "512Mi"},
            limits={"ephemeral-storage": "6Gi", "cpu": "1", "memory": "512Mi"}
        )

        if command is None or command.lower() == 'false':
            container = client.V1Container(
                name="container",
                image=image,
                command=["/bin/sh", "-c", "while :; do sleep 10; done"],
                resources=resources
            )
        elif command.lower() == 'true':
            container = client.V1Container(
                name="container",
                image=image,
                resources=resources
            )
        else:
            container = client.V1Container(
                name="container",
                image=image,
                command = shlex.split(command),
                resources=resources
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

        service_manifest = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=deployment_name,
                labels={"app": deployment_name}
            ),
            spec=client.V1ServiceSpec(
                cluster_ip="None",
                selector={"app": deployment_name}
            )
        )

        try:
            apps_v1.create_namespaced_deployment(namespace=self.namespace, body=deployment_manifest)
        except ApiException as e:
            print("Failed to create deployment:", json.loads(e.body)['message'])
            return False

        try:
            core_v1.create_namespaced_service(namespace=self.namespace, body=service_manifest)
        except ApiException as e:
            print("Failed to create dns record:", json.loads(e.body)['message'])
            print("You can still use your cantainer.")

        return True

    def delete_deployment(self, deployment_name):
        apps_v1 = client.AppsV1Api()
        core_v1 = client.CoreV1Api()

        try:
            apps_v1.delete_namespaced_deployment(name=deployment_name, namespace=self.namespace)
            core_v1.delete_namespaced_service(name=deployment_name, namespace=self.namespace)
            return True
        except ApiException as e:
            print("Failed to delete deployment:", json.loads(e.body)['message'])
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
            print("Failed to list deployment:", json.loads(e.body)['message'])
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

            return pods.items[0]

        except ApiException as e:
            print("Failed to find pod from deployment:", json.loads(e.body)['message'])
            return None
