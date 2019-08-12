#!/usr/bin/env python3

import os
import hashlib

from getpass import getpass

global FILENAME
FILENAME = "../passwords"

def main():
    #ask for username
    username = input("Username: ")

    md5 = hashlib.md5()
    password = getpass("Password: ")
    md5.update(password.encode("utf-8"))
    password = md5.hexdigest()

    credentials = username +":"+ password + "\n"

    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, FILENAME)

    mode = 'r' if os.path.exists(file_path) else 'a+'

    #read current data from file
    with open(file_path, mode) as file:
        data = file.readlines()

    #look for an already existing username
    found = False
    for i in range(0, len(data)):
        stored_credentials = data[i].split(":")
        stored_user = stored_credentials[0]

        if stored_user == username:
            data[i] = credentials
            found = True

    if not found:
        data.append(credentials)

    #write data back to file
    with open(file_path, 'w') as file:
        file.writelines(data)


if __name__ == '__main__':
    main()