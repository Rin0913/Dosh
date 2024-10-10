from kube_manager import UserManager
from tests.utils import *
import config
import os
from kubernetes import config as kube_config

manager = UserManager(config.k8s_admin_conf_path)

def test_create_user():
    assert manager.create_user("u11")  == 1
    assert os.path.exists("./data/kube_configs/u11.yaml")
    assert manager.create_user("u11")  == 0
    manager.revoke_user("u11")

def test_revoke_user():
    manager.create_user("u13") == 1
    assert manager.revoke_user("u13") == 1
    assert manager.revoke_user("u13") == 0
    assert not os.path.exists("./data/kube_configs/u13.yaml")

def test_grant_user():
    manager.create_user("u14")
    kube_config.load_kube_config(config_file=config.k8s_admin_conf_path)
    create_busybox_deployment("kubernetes-admin", "default", "test1")
    try:
        assert manager.grant_user("u14")
        kube_config.load_kube_config(config_file="./data/kube_configs/u14.yaml")
        # RBAC Testing
        assert create_busybox_deployment("u14", "dosh", "test1")
        assert not create_busybox_deployment("u14", "default", "test1")
        assert list_deployments("dosh")
        assert not list_deployments("default")
        assert check_exec_permission("dosh", "test1")
        assert not check_exec_permission("default", "test1")
        assert delete_busybox_deployment("dosh", "test1")
        assert not delete_busybox_deployment("default", "test1")
    finally:
        kube_config.load_kube_config(config_file=config.k8s_admin_conf_path)
        delete_busybox_deployment("default", "test1")
        delete_busybox_deployment("dosh", "test1")
        manager.revoke_user("u14")
