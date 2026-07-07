import json
import urllib.request

req = urllib.request.Request(
    'http://localhost:3001/api/research-company',
    data=json.dumps({'companyUrl': 'https://example.com'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode('utf-8'))
