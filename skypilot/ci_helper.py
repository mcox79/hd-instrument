"""Lambda Cloud quick instance check.

Usage: python3 /path/to/ci_helper.py
"""
import sys, json, urllib.request, urllib.error, re, base64

LAMBDA_KEY_PATH = "/root/.lambda_cloud/lambda_keys"


def _read_key():
    with open(LAMBDA_KEY_PATH, "r") as f:
        content = f.read()
    m = re.search(r"api_key\s*=\s*(\S+)", content)
    if not m:
        raise RuntimeError("api_key not found in " + LAMBDA_KEY_PATH)
    return m.group(1)


def main():
    try:
        key = _read_key()
    except Exception as e:
        print(f"ERROR reading Lambda key: {e}")
        sys.exit(1)

    # Lambda uses Basic auth with api_key as username, empty password
    auth = base64.b64encode((key + ":").encode("utf-8")).decode("utf-8")
    req = urllib.request.Request(
        "https://cloud.lambdalabs.com/api/v1/instances",
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": "curl/7.81.0",  # Cloudflare blocks plain urllib User-Agent
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"Lambda API error: HTTP {e.code} {e.reason}: {body}")
        sys.exit(2)
    except Exception as e:
        print(f"Lambda API error: {type(e).__name__}: {e}")
        sys.exit(2)

    instances = data.get("data", [])
    print(f"Lambda API reports {len(instances)} running instance(s)")
    for inst in instances:
        iid = inst.get("id", "?")
        itype = inst.get("instance_type", {}).get("name", "?")
        status = inst.get("status", "?")
        region = inst.get("region", {}).get("name", "?")
        ip = inst.get("ip", None) or "n/a"
        print(f"  id={iid} status={status} region={region} type={itype} ip={ip}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
