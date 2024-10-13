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

print(f"Hello, {user.username}.")
print("Enter `help` to get more information.")

while True:
    try:
        command = shlex.split(input("dosh> "))
        if not command:
            continue
    except ValueError as e:
        print(f"Invalid Command: {e}")
        continue
    except KeyboardInterrupt:
        print()
        continue
    except EOFError:
        command = ["exit"]

    commandHandler.handle(command)
