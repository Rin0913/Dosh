import os
import pwd

from kube_manager import UserManager

class User:
    # pylint: disable=too-few-public-methods

    def __init__(self, config, uid = None):

        if uid is None:
            uid = os.getuid()

        self.username = pwd.getpwuid(uid).pw_name
        self.uid = uid

        kube_conf = os.path.join(config.DATA_DIR, f"kube_configs/{self.username}.yaml")
        if not os.path.exists(kube_conf):
            user_manager = UserManager(config.K8S_ADMIN_CONF_PATH, config.DATA_DIR)
            user_manager.create_user(self.username)
            user_manager.grant_user(self.username)
            del user_manager

    def get_home_directory(self):

        return pwd.getpwuid(self.uid).pw_dir
