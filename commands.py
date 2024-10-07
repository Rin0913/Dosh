import subprocess
import sys

command_list = {}

def register_command(name, help_text):
    def decorator(func):
        command_list[name] = (func, help_text)
        return func
    return decorator

@register_command(
        'attach', 
        'attach <target>: Attach to a container.\n\t'
        'target: The container you would like to attach.')
def attach_command(target):
    with subprocess.Popen(
        [target],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        bufsize=1
    ) as process:
        process.wait()

@register_command('help', 'help: Show this message.')
def show_help():
    for cmd in command_list.items():
        print(cmd[1][1])

@register_command('exit', 'exit: Exit Dosh.')
def exit_dosh():
    print("Goodbye!")
    sys.exit(0)
