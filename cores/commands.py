import subprocess
import os
import sys
from texttable import Texttable

from kube_manager import DeploymentManager

command_list = {}

# These variables are not constant.
deploymentManager = None    # pylint: disable=C0103
username = None             # pylint: disable=C0103
admin_list = None           # pylint: disable=C0103

def init(username_from_main, admin_list_from_main, data_dir):
    global deploymentManager, username, admin_list # pylint: disable=W0603
    # As a temporary solution, I will fix it later
    kube_conf_path = os.path.join(data_dir, f'kube_configs/{username_from_main}.yaml')
    deploymentManager = DeploymentManager(kube_conf_path, 'dosh')
    username = username_from_main
    admin_list = admin_list_from_main

def register_command(name, help_text):
    def decorator(func):
        command_list[name] = (func, help_text)
        return func
    return decorator

@register_command(
        'create',
        'create <image> {name} {command}: Create a container from the image.\n\t'
        'image: The image you would like to use on DockerHub.\n\t'
        'name: The name of container. Default: {Datetime}-{Image}-{ID}\n\t'
        'command: The command for container.\n\t\t'
        'False->Keep running. (Default)\n\t\t'
        'True->Use image command.\n\t\t'
        'Custom String->Use customized command.\n\n\t'
        'You can simpily use: create ubuntu:latest my-ubuntu')
def create_container(image, name = None, command = None):
    if name:
        name = f"{username}-{name}"
    if deploymentManager.create_deployment(username, image, name, command):
        print("Successfully create container.")
    else:
        print("If you believe it is the system's problem, please contact the administrator.")

@register_command('list', 'list: List all containers.')
def list_containers():
    result = [("Container Number", "Status")]

    for d in deploymentManager.list_deployments(username):
        pod = deploymentManager.find_pod_by_deployment(d)
        d = d[len(username) + 1:] # To remove "{username}-" prefix.
        result.append((d, pod.status.phase if pod else "Stopped"))

    table = Texttable()
    table.set_cols_dtype(['t', 't'])
    table.add_rows(result)
    print(table.draw())

@register_command(
        'attach', 
        'attach <target> {command}: Attach to a container.\n\t'
        'target: The container you would like to attach.\n\t'
        'command: The command you would like to use in the container. Default: sh')
def attach_command(target, command="sh"):
    pod = deploymentManager.find_pod_by_deployment(f"{username}-{target}")

    if not pod:
        print(f"Container {target} has been terminated. Please destroy it manually.")
        return

    with subprocess.Popen(
        ["kubectl", "exec", "-it", pod.metadata.name,
         "-n", "dosh", "--", command],
        env={"KUBECONFIG": f"./data/kube_configs/{username}.yaml"},
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        bufsize=1
    ) as process:
        process.wait()

@register_command(
        'delete',
        'delete <target>: Destroy a container permanently.\n\t'
        '<target>: The container you would like to destroy.')
def destroy_container_command(target):
    deploymentManager.delete_deployment(f"{username}-{target}")

@register_command('help', 'help: Show this message.')
def show_help():
    for cmd in command_list.items():
        print(cmd[1][1])

@register_command('exit', 'exit: Exit Dosh.')
def exit_dosh():
    print("Goodbye!")
    sys.exit(0)

@register_command('shell', 'shell: Administrator only.')
def shell(command="/bin/bash"):
    if username in admin_list:
        with subprocess.Popen(
            [command],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            bufsize=1
        ) as process:
            process.wait()
