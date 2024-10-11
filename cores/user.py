import os
import pwd

from kube_manager import UserManager

# These variables are not constant.
username = None # pylint: disable=C0103

def init(k8s_admin_conf_path, data_dir, uid = None):
    global username # pylint: disable=W0603
    # As a temporary solution, I will fix it later

    if uid is None:
        uid = os.getuid()

    username = pwd.getpwuid(uid).pw_name

    kube_conf = os.path.join(data_dir, f"kube_configs/{username}.yaml")
    if not os.path.exists(kube_conf):
        user_manager = UserManager(k8s_admin_conf_path, data_dir)
        user_manager.create_user(username)
        user_manager.grant_user(username)
        del user_manager
