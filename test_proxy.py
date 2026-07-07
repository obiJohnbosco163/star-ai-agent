import json
import urllib.request

req = urllib.request.Request(
    'http://localhost:5173/api/research-company',
    data=json.dumps({'companyUrl': 'https://example.com'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.status)
        print(resp.read().decode('utf-8'))
except Exception as e:
    print(type(e).__name__)
    print(e)
