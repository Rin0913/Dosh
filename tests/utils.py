from kubernetes import client, config
from kubernetes.client.rest import ApiException


def create_busybox_deployment(username, namespace, deployment_name):
    """
    Create a Deployment in the default namespace with one busybox pod.
    Return True if successful, otherwise False.
    """
    apps_v1 = client.AppsV1Api()

    deployment_manifest = client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name=deployment_name,
            labels={"owner": username}
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": "busybox"}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "busybox", "owner": username}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="busybox",
                            image="busybox",
                            command=["sh", "-c", "while true; do echo hello; sleep 10;done"]
                        )
                    ]
                )
            )
        )
    )

    try:
        apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment_manifest)
        return True
    except ApiException as e:
        print(f"Failed to create deployment: {e}")
        return False

def delete_busybox_deployment(namespace, deployment_name):
    """
    Delete the busybox deployment in the default namespace.
    Return True if successful, otherwise False.
    """
    apps_v1 = client.AppsV1Api()

    try:
        apps_v1.delete_namespaced_deployment(name=deployment_name, namespace=namespace)
        return True
    except ApiException as e:
        print(f"Failed to delete deployment: {e}")
        return False

def list_deployments(namespace):
    """
    List all deployments in the given namespace.
    Return a list of deployment names.
    """
    apps_v1 = client.AppsV1Api()
    
    try:
        deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
        deployment_names = [deployment.metadata.name for deployment in deployments.items]
        return True
    except ApiException as e:
        print(f"Failed to list deployments: {e}")
        return False

def find_pod_by_deployment(namespace, deployment_name):
    """
    Find the first pod of a specific deployment in the given namespace.
    
    Parameters:
    deployment_name (str): The name of the deployment to search in.
    namespace (str): The namespace to search in. Default is "default".
    
    Returns:
    str: The name of the first pod found in the deployment, or None if no pod is found.
    """
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()

    try:
        deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        pod_label_selector = ",".join([f"{k}={v}" for k, v in deployment.spec.selector.match_labels.items()])
        pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=pod_label_selector)

        if not pods.items:
            raise Exception(f"No pod found in deployment {deployment_name}.")

        first_pod_name = pods.items[0].metadata.name
        return first_pod_name

    except ApiException as e:
        print(f"Error while searching for deployment {deployment_name} in namespace {namespace}: {e}")
        return False

def check_exec_permission(namespace, deployment_name):
    """
    Try to exec command on a given pod to check if the current user has permission.
    """
    pod_name = find_pod_by_deployment(namespace, deployment_name)

    api_instance = client.AuthorizationV1Api()

    access_review = client.V1SelfSubjectAccessReview(
        spec=client.V1SelfSubjectAccessReviewSpec(
            resource_attributes=client.V1ResourceAttributes(
                namespace=namespace,
                verb="create",
                resource="pods",
                subresource="exec",
                name=pod_name
            )
        )
    )

    try:
        response = api_instance.create_self_subject_access_review(access_review)

        if response.status.allowed:
            print("User has permission to create pods/exec")
            return True
        else:
            print("User does NOT have permission to create pods/exec")
            return False

    except ApiException as e:
        print(f"Exception when calling create_self_subject_access_review: {e}")
        return False

