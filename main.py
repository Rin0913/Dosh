import readline # pylint: disable=unused-import
from commands import command_list

while True:
    try:
        command = input("dosh> ").split()
        if not command:
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
