#!/usr/bin/env python3

import paramiko, secrets

UDOOIP = "10.27.151.101"
UDOOUSER = "udooer"
ATTEMPTS = 10


def ssh_connect(password):
    code = 0
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("trying to connect")
        ssh.connect(UDOOIP, 22, UDOOUSER, password)
    except paramiko.AuthenticationException:
        #password was incorrect
        code = 1

    ssh.close()
    return code


def main():
    for i in range(ATTEMPTS):
        password = secrets.token_hex(16)

        try:
            response = ssh_connect(password)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    main()


