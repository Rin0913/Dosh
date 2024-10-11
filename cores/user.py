import os
import pwd

from kube_manager import UserManager

# These variables are not constant.
username = None # pylint: disable=C0103

def init(k8s_admin_conf_path):
    global username # pylint: disable=W0603
    # As a temporary solution, I will fix it later

    username = pwd.getpwuid(os.getuid()).pw_name

    if not os.path.exists(f"./data/kube_configs/{username}.yaml"):
        user_manager = UserManager(k8s_admin_conf_path)
        user_manager.create_user(username)
        user_manager.grant_user(username)
        del user_manager
