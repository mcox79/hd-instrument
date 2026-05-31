"""Create a Lambda-registered SSH key and save the private half locally.

Lambda's API generates a new RSA key-pair, registers the public half under
the given name, and returns the PRIVATE half in the API response. The
private key is returned ONLY ONCE -- subsequent list_ssh_keys() calls do
not surface it. This script captures it on creation and writes it to
~/.ssh/<name>.pem with 0600 permissions (best effort on Windows).

Usage:
  python tools/cloud/create_ssh_key.py <name> [--key-file .env.lambda]

After it succeeds, pass the saved path to the canary:
  python tools/cloud/canary_lifecycle.py \\
    --ssh-key-name <name> \\
    --ssh-key-path ~/.ssh/<name>.pem
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import LambdaClient, LambdaClientError  # noqa: E402


def _load_key(key_file_arg: str) -> str | None:
    key = os.environ.get("LAMBDA_CLOUD_API_KEY", "").strip()
    if key:
        return key
    kp = Path(key_file_arg)
    if not kp.is_absolute():
        kp = _REPO_ROOT / kp
    if not kp.is_file():
        return None
    for ln in kp.read_text(encoding="utf-8").splitlines():
        if ln.startswith("LAMBDA_CLOUD_API_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Lambda SSH key")
    parser.add_argument("name", help="Name to register the key under at Lambda")
    parser.add_argument("--key-file", default=".env.lambda",
                        help="Env-file with LAMBDA_CLOUD_API_KEY")
    parser.add_argument("--out-dir",
                        default=str(Path.home() / ".ssh"),
                        help="Local dir to save the .pem file (default ~/.ssh)")
    args = parser.parse_args()

    api_key = _load_key(args.key_file)
    if not api_key:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY in env or key file.")
        return 1
    try:
        client = LambdaClient(api_key=api_key)
    except LambdaClientError as exc:
        print(f"[ERROR] {exc}")
        return 1

    # If a key with this name already exists, refuse rather than overwrite.
    try:
        existing = client.list_ssh_keys()
    except LambdaClientError as exc:
        print(f"[ERROR] list_ssh_keys failed: {exc}")
        return 1
    if any(k.get("name") == args.name for k in existing):
        print(f"[ERROR] an SSH key named {args.name!r} already exists at Lambda. "
              f"Pick a different name OR delete the existing one via the web "
              f"console.")
        return 1

    print(f"[1/3] Asking Lambda to generate + register a new key-pair as {args.name!r}...")
    try:
        result = client.add_ssh_key(args.name)  # public_key=None -> Lambda generates
    except LambdaClientError as exc:
        print(f"[ERROR] add_ssh_key failed: {exc}")
        return 1

    # Lambda's response carries the private key in 'private_key'. If that's
    # absent we can't proceed -- the key already lives at Lambda but we lack
    # the private half locally, so SSH would fail.
    private_key = result.get("private_key")
    if not private_key:
        print("[ERROR] response did not include 'private_key'. The key exists at")
        print("        Lambda but we have no way to ssh in. Delete it via the web")
        print("        console and either retry or use option A (web console).")
        print(f"        response keys: {list(result.keys())}")
        return 1

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    priv_path = out_dir / f"{args.name}.pem"

    print(f"[2/3] Writing private key to {priv_path}...")
    if priv_path.is_file():
        print(f"[ERROR] refusing to overwrite existing {priv_path}.")
        print("        Move or delete it manually then retry, OR use a different name.")
        return 1
    # Write binary with explicit LF normalization. write_text on Windows
    # translates \n -> \r\n by default, which makes libcrypto reject the
    # PEM file with 'error in libcrypto' at ssh time.
    pk_bytes = private_key.replace("\r\n", "\n").encode("utf-8")
    priv_path.write_bytes(pk_bytes)
    # Tighten permissions; SSH refuses keys that are world-readable.
    # On Windows chmod is a no-op but ssh.exe also accepts the file.
    try:
        os.chmod(priv_path, 0o600)
    except Exception:
        pass
    print(f"  saved: {priv_path}  ({priv_path.stat().st_size} bytes)")

    print(f"[3/3] Verifying registration via list_ssh_keys()...")
    try:
        keys_after = client.list_ssh_keys()
    except LambdaClientError as exc:
        print(f"[WARN] list_ssh_keys failed post-create: {exc}")
        keys_after = []
    found = next((k for k in keys_after if k.get("name") == args.name), None)
    if found:
        print(f"  OK: Lambda lists {args.name!r} with id={found.get('id', '?')[:12]}")
    else:
        print(f"  [WARN] could not confirm registration via list (may be eventual-consistency)")

    print()
    print(f"Next step: canary launch")
    print(f"  python tools/cloud/canary_lifecycle.py \\")
    print(f"    --ssh-key-name {args.name} \\")
    print(f"    --ssh-key-path {priv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
