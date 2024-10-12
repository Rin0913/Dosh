import os
import pwd

from kube_manager import UserManager

class User:
    # pylint: disable=too-few-public-methods

    def __init__(self, k8s_admin_conf_path, data_dir, uid = None):

        if uid is None:
            uid = os.getuid()

        self.username = pwd.getpwuid(uid).pw_name

        kube_conf = os.path.join(data_dir, f"kube_configs/{self.username}.yaml")
        if not os.path.exists(kube_conf):
            user_manager = UserManager(k8s_admin_conf_path, data_dir)
            user_manager.create_user(self.username)
            user_manager.grant_user(self.username)
            del user_manager
