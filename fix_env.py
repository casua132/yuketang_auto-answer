import requests
import json
import base64

s = requests.Session()
s.trust_env = False
try:
    print("Testing requests without env...")
    r = s.get("https://www.baidu.com")
    print("Success:", r.status_code)
except Exception as e:
    print("Error:", e)
