import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("http://127.0.0.1:8000/api/v1/analyze/email", 
                             data=json.dumps({"text": "Verify your bank account immediately"}).encode('utf-8'),
                             headers={"Content-Type": "application/json", "Authorization": "Bearer test"})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
