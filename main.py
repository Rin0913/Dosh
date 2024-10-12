#!/usr/bin/env python3

import readline # pylint: disable=unused-import
import shlex
import sys

import config
from cores.user import User
from cores.commands import Command

if len(sys.argv) > 1 and sys.argv[1].isnumeric():
    user = User(config.K8S_ADMIN_CONF_PATH, config.DATA_DIR, int(sys.argv[1]))
else:
    user = User(config.K8S_ADMIN_CONF_PATH, config.DATA_DIR)

commandHandler = Command(user.username, config.ADMIN_LIST, config.DATA_DIR)

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
