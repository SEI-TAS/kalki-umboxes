import httplib
from base64 import b64encode

connection = httplib.HTTPConnection('localhost', 9010, timeout=10)
userAndPass = b64encode(b"Username:Password").decode("ascii")
headers = {'Authorization': 'Basic %s' % userAndPass}
connection.request("GET", "/test_server.sh", headers=headers)
response = connection.getresponse()
print("Status: {} and reason: {}".format(response.status, response.reason))

connection.close()
