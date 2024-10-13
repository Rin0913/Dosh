#!/usr/bin/env python3

import readline # pylint: disable=unused-import
import shlex
import sys

import config
from cores import User, Command

if len(sys.argv) > 1 and sys.argv[1].isnumeric():
    user = User(config, int(sys.argv[1]))
else:
    user = User(config)


USER_HOME_DIRECTORY = None
if config.MOUNT_USER_HOME:
    USER_HOME_DIRECTORY = user.get_home_directory()

commandHandler = Command(config,
                         user.username,
                         USER_HOME_DIRECTORY)

def main():
    print(f"Hello, {user.username}.")
    print("Enter `help` to get more information.")

    command = ""

    while True:
        try:
            if command == "":
                command = input("dosh> ")
            else:
                command += "\n" + input()
            if not command:
                continue
            shlex.split(command)
        except ValueError as e:
            if str(e) != "No closing quotation":
                command = ""
            continue
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            command = "exit"
            print()

        commandHandler.handle(shlex.split(command))
        command = ""

if __name__ == '__main__':
    main()
