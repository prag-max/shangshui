import urllib.request
import urllib.error
import ssl

url = "https://api.shanwater.com:8443/api/inquiries"
data = {
    "name": "王测试",
    "company": "福州某供水有限公司",
    "phone": "13860642706",
    "email": "test@sum-water.com",
    "user_scale": "约 8 万用户",
    "requirement": "想了解抄表到收费一体化方案及报价",
    "website": "",
}

boundary = "----formboundary123456"
parts = []
for k, v in data.items():
    parts.append(f"--{boundary}".encode("utf-8"))
    parts.append(f'Content-Disposition: form-data; name="{k}"'.encode("utf-8"))
    parts.append(b"")
    parts.append(v.encode("utf-8"))
body = b"\r\n".join(parts) + f"\r\n--{boundary}--\r\n".encode("utf-8")

req = urllib.request.Request(url, data=body, method="POST")
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
req.add_header("Accept", "application/json")
req.add_header("Origin", "https://www.shanwater.com")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        print("HTTP", resp.status)
        print(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode("utf-8", errors="replace"))
except Exception as e:
    print("ERROR", repr(e))
