import base64
import os
from io import StringIO
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from ruamel.yaml import YAML
from kubernetes import client, config

class UserManager():

    def __init__(self, admin_conf_path, data_dir):
        self.yaml_parser = YAML()
        self.yaml_parser.preserve_quotes = True

        self.yaml_parser.representer.add_representer(
                str,
                lambda dumper, data:
                    dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        )

        config.load_kube_config(config_file=admin_conf_path)
        with open(admin_conf_path, "r", encoding="utf-8") as stream:
            self.admin_conf = self.yaml_parser.load(stream)

        with open(os.path.join(data_dir, 'ca/private.key'), 'rb') as ca_key_file:
            self.ca_key = serialization.load_pem_private_key(
                ca_key_file.read(),
                password=None,
                backend=default_backend()
            )

        with open(os.path.join(data_dir, 'ca/certificate.crt'), 'rb') as ca_cert_file:
            self.ca_cert = x509.load_pem_x509_certificate(
                ca_cert_file.read(),
                default_backend()
            )

        self.data_dir = data_dir

    def __generate_cert_key_pair(self, username):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "TW"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "sandb0x.tw"),
            x509.NameAttribute(NameOID.COMMON_NAME, username),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=36500)
        ).sign(self.ca_key, hashes.SHA256())

        private_key = base64.b64encode(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

        cert_pem = base64.b64encode(cert.public_bytes(serialization.Encoding.PEM))

        return private_key, cert_pem

    def create_user(self, username):
        kube_conf_path = os.path.join(self.data_dir, f"kube_configs/{username}.yaml")
        if os.path.exists(kube_conf_path):
            return 0

        private_key, cert_pem = self.__generate_cert_key_pair(username)

        kube_config = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "cluster": {
                        "certificate-authority-data": 
                            self.admin_conf["clusters"][0]["cluster"]["certificate-authority-data"],
                        "server": self.admin_conf["clusters"][0]["cluster"]["server"],
                    },
                    "name": self.admin_conf["clusters"][0]["name"]
                }
            ],
            "contexts": [
                {
                    "context": {
                        "cluster": self.admin_conf["contexts"][0]["context"]["cluster"],
                        "user": username,
                    },
                    "name": username + "-context"
                }
            ],
            "current-context": username + "-context",
            "users": [
                {
                    "name": username,
                    "user": {
                        "client-certificate-data": cert_pem,
                        "client-key-data": private_key
                    }
                }
            ]
        }


        with open(kube_conf_path, "w", encoding="utf-8") as kube_config_file:
            stream = StringIO()
            self.yaml_parser.dump(kube_config, stream)
            kube_config_file.write(stream.getvalue())
        print(f"User {username} is created.")

        return 1

    def grant_user(self, username, namespace="dosh"):
        role = client.V1Role(
            metadata=client.V1ObjectMeta(namespace=namespace, name=f"{username}-deployment-role"),
            rules=[
                client.V1PolicyRule(
                    api_groups=["apps"],
                    resources=["deployments"],
                    verbs=["get", "list", "create", "delete"]
                ),
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["pods", "pods/exec", "pods/attach"],
                    verbs=["get", "list", "create", "delete"]
                ),
            ]
        )

        role_binding = client.V1RoleBinding(
            metadata=client.V1ObjectMeta(namespace=namespace, name=f"{username}-rolebinding"),
            subjects=[client.RbacV1Subject(kind="User", name=username)],
            role_ref=client.V1RoleRef(
                kind="Role",
                name=f"{username}-deployment-role",
                api_group="rbac.authorization.k8s.io"
            )
        )

        rbac_api = client.RbacAuthorizationV1Api()

        try:
            rbac_api.create_namespaced_role(namespace=namespace, body=role)
            print(f"Role created for user {username} in namespace {namespace}")
        except client.exceptions.ApiException as e:
            print(f"Error creating role: {e}")
            return 0

        try:
            rbac_api.create_namespaced_role_binding(namespace=namespace, body=role_binding)
            print(f"RoleBinding created for user {username} in namespace {namespace}")
        except client.exceptions.ApiException as e:
            print(f"Error creating role binding: {e}")
            return 0

        return 1

    def revoke_user(self, username, namespace = "dosh"):

        kube_conf_path = os.path.join(self.data_dir, f"kube_configs/{username}.yaml")
        if not os.path.exists(kube_conf_path):
            return 0

        flag = 1

        rbac_api = client.RbacAuthorizationV1Api()

        rolebindings = rbac_api.list_role_binding_for_all_namespaces().items

        for rolebinding in rolebindings:
            for subject in rolebinding.subjects:
                if subject.kind == "User" and subject.name == username:
                    try:
                        rbac_api.delete_namespaced_role_binding(
                            name=rolebinding.metadata.name,
                            namespace=rolebinding.metadata.namespace
                        )
                        print(f"RoleBinding {rolebinding.metadata.name} deleted from"
                               " namespace {rolebinding.metadata.namespace}")
                    except client.exceptions.ApiException as e:
                        print(f"Error deleting RoleBinding {rolebinding.metadata.name}"
                               " in namespace {rolebinding.metadata.namespace}:", e)
                        flag = 0

        try:
            rbac_api.delete_namespaced_role(
                name=f"{username}-deployment-role",
                namespace=namespace,
                body=client.V1DeleteOptions()
            )
        except client.exceptions.ApiException as e:
            if e.status != 404:
                print(f"Error code {e.status} occurs when deleting role: {e}")
                flag = 0

        os.remove(kube_conf_path)
        return flag
