from kube_manager import DeploymentManager
import config

manager = DeploymentManager(config.K8S_ADMIN_CONF_PATH, 'dosh', config.K8S_SERVICE_DNS)

def test_create_deployment():
    try:
        assert manager.create_deployment("u31",
                                         "ubuntu:latest",
                                         "test3-11",
                                         "while true; do sleep 10; done")
        assert manager.create_deployment("u31",
                                         "ubuntu:latest",
                                         "test3-12",
                                         "while true; do sleep 10; done")
        deployment_list = manager.list_deployments("u31")
        for d in deployment_list:
            manager.delete_deployment(d)
    finally:
        deployment_list = manager.list_deployments("u31")
        for d in deployment_list:
            manager.delete_deployment(d)

def test_list_deployments():
    # Accuracy of test_list_deployments result depends on creation.
    try:
        assert manager.create_deployment("u32",
                                         "ubuntu:latest",
                                         "test3-21",
                                         "while true; do sleep 10; done")
        assert manager.create_deployment("u32",
                                         "ubuntu:latest",
                                         "test3-22",
                                         "while true; do sleep 10; done")
        deployment_list = manager.list_deployments("u32")
        assert len(deployment_list)
        for d in deployment_list:
            manager.delete_deployment(d)
    finally:
        deployment_list = manager.list_deployments("u32")
        for d in deployment_list:
            manager.delete_deployment(d)

def test_delete_deployment():
    # Accuracy of test_delete_deployment result depends on listing.
    try:
        assert manager.create_deployment("u33",
                                         "ubuntu:latest",
                                         "test3-31",
                                         "while true; do sleep 10; done")
        assert manager.create_deployment("u33",
                                         "ubuntu:latest",
                                         "test3-32",
                                         "while true; do sleep 10; done")
        deployment_list = manager.list_deployments("u33")
        assert len(deployment_list)
        for d in deployment_list:
            assert manager.delete_deployment(d)
        assert len(manager.list_deployments("u33")) == 0
    finally:
        deployment_list = manager.list_deployments("u33")
        for d in deployment_list:
            manager.delete_deployment(d)
