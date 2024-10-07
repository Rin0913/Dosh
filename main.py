import subprocess
import threading
import sys
import readline

def attach(target):
    process = subprocess.Popen(
        [target],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        bufsize=1
    )

    process.wait()

commands = {
    "help": (lambda: print("\n".join([commands[command][1] for command in commands])), "help: Show this message."),
    "exit": (lambda: print("Goodbye!") or exit(0), "exit: Exit Dosh."),
    "attach": (lambda target: attach(target), "attach <target>: Attach to a container.\n\ttarget: The container you would like to attach."),
}

while True:
    command = input("dosh> ").split()
    if not command: continue
    if command[0] in commands:
        method = commands[command[0]]
        try:
            method[0](*command[1:])
        except TypeError:
            print(method[1])
    else:
        print("Invalid command:", command[0])
