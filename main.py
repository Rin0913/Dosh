import readline # pylint: disable=unused-import
import shlex
from commands import command_list

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

    if command[0] in command_list:
        method = command_list[command[0]]
        try:
            method[0](*command[1:])
        except TypeError:
            print(method[1])
    else:
        print("Invalid command:", command[0])
