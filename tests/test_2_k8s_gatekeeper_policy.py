from kubernetes import config as kube_config
from kube_manager import UserManager
from tests.utils import (create_busybox_deployment,
                         delete_busybox_deployment)

import config

manager = UserManager(config.K8S_ADMIN_CONF_PATH, "./data")

def test_quota_exceeding():
    manager.create_user("u21")
    kube_config.load_kube_config(config_file=config.K8S_ADMIN_CONF_PATH)

    manager.grant_user("u21")
    kube_config.load_kube_config(config_file="./data/kube_configs/u21.yaml")

    try:
        assert create_busybox_deployment("u21", "dosh", "test21")
        assert create_busybox_deployment("u21", "dosh", "test22")
        assert create_busybox_deployment("u21", "dosh", "test23")
        assert not create_busybox_deployment("u21", "dosh", "test24")
    finally:
        kube_config.load_kube_config(config_file=config.K8S_ADMIN_CONF_PATH)
        delete_busybox_deployment("dosh", "test21")
        delete_busybox_deployment("dosh", "test22")
        delete_busybox_deployment("dosh", "test23")
        delete_busybox_deployment("dosh", "test24")
        manager.revoke_user("u21")

def test_unauthorized_access():
    manager.create_user("u22")
    manager.create_user("u23")
    kube_config.load_kube_config(config_file=config.K8S_ADMIN_CONF_PATH)

    manager.grant_user("u22")
    manager.grant_user("u23")
    kube_config.load_kube_config(config_file="./data/kube_configs/u22.yaml")
    create_busybox_deployment("u22", "dosh", "test24")

    try:
        kube_config.load_kube_config(config_file="./data/kube_configs/u23.yaml")
        assert not delete_busybox_deployment("dosh", "test24")
        kube_config.load_kube_config(config_file="./data/kube_configs/u22.yaml")
        assert delete_busybox_deployment("dosh", "test24")
    finally:
        kube_config.load_kube_config(config_file=config.K8S_ADMIN_CONF_PATH)
        delete_busybox_deployment("dosh", "test24")
        manager.revoke_user("u22")
        manager.revoke_user("u23")
