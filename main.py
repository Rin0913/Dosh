#!/usr/bin/env python3

import readline # pylint: disable=unused-import
import shlex

import config
from cores import user, commands

user.init(config.K8S_ADMIN_CONF_PATH, config.DATA_DIR)
commands.init(user.username, config.ADMIN_LIST, config.DATA_DIR)

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

    if command[0] in commands.command_list:
        method = commands.command_list[command[0]]
        try:
            method[0](*command[1:])
        except TypeError as e:
            print(method[1], e)
    else:
        print("Invalid command:", command[0])
