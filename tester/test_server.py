from requests.auth import HTTPDigestAuth
import requests
chal = {'realm': 'my_realm', 'nonce': '1389832695:d3c620a9e645420228c5c7da7d228f8c'}
a = HTTPDigestAuth('the_user', 'pass')
a.chal = chal
print(a.chal)
a.build_digest_header('GET', '/some/uri')
