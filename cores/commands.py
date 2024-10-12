import subprocess
import os
import sys
from texttable import Texttable

from kube_manager import DeploymentManager


class Command:
    # pylint: disable=too-few-public-methods

    command_list: dict = {}

    def __init__(self, username, admin_list, data_dir):
        self.kube_conf_path = os.path.join(data_dir, f'kube_configs/{username}.yaml')
        self.deployment_manager = DeploymentManager(self.kube_conf_path, 'dosh')
        self.username = username
        self.admin_list = admin_list
        self.data_dir = data_dir

    def __init_subclass__(cls):
        for method in vars(cls).values():
            if callable(method) and hasattr(method, 'name') and hasattr(method, 'help_text'):
                cls.command_list[getattr(method, 'name')] = (method, getattr(method, 'help_text'))

    def handle(self, command):
        if command[0] in self.command_list:
            try:
                method = self.command_list[command[0]]
                method[0](self, *command[1:])
            except TypeError:
                print(method[1]) # pylint: disable=unsubscriptable-object
        else:
            print(f"Invalid command: {command[0]}. Please enter `help` to get more information.")

def register_command(name, help_text):
    def decorator(func):
        func.name = name
        func.help_text = help_text
        return func
    return decorator

class ContainerManagementCommands(Command):
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
    def create_container(self, image, name = None, command = None):
        if name:
            name = f"{self.username}-{name}"
        if self.deployment_manager.create_deployment(self.username, image, name, command):
            print("Successfully create container.")
        else:
            print("If you believe it is the system's problem, please contact the administrator.")

    @register_command('list', 'list: List all containers.')
    def list_containers(self):
        result = [("Container Number", "Status")]

        for d in self.deployment_manager.list_deployments(self.username):
            pod = self.deployment_manager.find_pod_by_deployment(d)
            d = d[len(self.username) + 1:] # To remove "{self.username}-" prefix.
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
    def attach_container(self, target, command="sh"):
        kube_conf_path = os.path.join(self.data_dir, f"kube_configs/{self.username}.yaml")
        pod = self.deployment_manager.find_pod_by_deployment(f"{self.username}-{target}")

        if not pod:
            print(f"Container {target} is not ready.")
            return

        with subprocess.Popen(
            ["kubectl", "exec", "-it", pod.metadata.name,
             "-n", "dosh", "--", command],
            env={"KUBECONFIG": kube_conf_path},
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
    def delete_container(self, target):
        self.deployment_manager.delete_deployment(f"{self.username}-{target}")

class HelpCommand(Command):
    @register_command('help', 'help: Show this message.')
    def help(self):
        for cmd in self.command_list.items():
            print(cmd[1][1])

class ExitCommand(Command):
    @register_command('exit', 'exit: Exit Dosh.')
    def exit(self):
        print("Goodbye!")
        sys.exit(0)

class ShellCommand(Command):
    @register_command('shell', 'shell: Administrator only.')
    def shell(self, command="/bin/bash"):
        if self.username in self.admin_list:
            with subprocess.Popen(
                [command],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
                bufsize=1
            ) as process:
                process.wait()
        else:
            print("Administrator Only.")
