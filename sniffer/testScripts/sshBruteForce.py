#!/usr/bin/env python3

import paramiko, secrets

global host, username

def ssh_connect(password):
    global host, username
    code = 0
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("trying to connect")
        ssh.connect(host, 22, username, password)
    except paramiko.AuthenticationException:
        #password was incorrect
        code = 1

    ssh.close()
    return code


def main():
    global host, username
    host = "128.237.200.5"
    username = "cfmullaly"
    number_of_attempts = int(input("Please enter the number of passwords you would like to try: "))

    for i in range(number_of_attempts):
        password = secrets.token_hex(16)

        try:
            response = ssh_connect(password)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    main()


