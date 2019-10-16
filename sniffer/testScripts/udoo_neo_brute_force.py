#!/usr/bin/env python

from os import urandom
import paramiko

UDOOIP = "10.27.151.101"
UDOOUSER = "udooer"
ATTEMPTS = 20


def ssh_connect(password):
    code = 0
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("trying to connect")
        ssh.connect(hostname=UDOOIP, port=22, username=UDOOUSER, password=password, timeout=3)
        print("finished connection attempt")
        ssh.close()
    except paramiko.AuthenticationException:
        print("password was incorrect")
        code = 1
        
    return code


def main():
    for i in range(ATTEMPTS):
        password = urandom(16).encode('hex')

        try:
            response = ssh_connect(password)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    main()


