"""
verifier.py -- HP-12 standalone third-party deletion-cert verifier (shareable; NO KB / NO trapdoor access).

A third-party reviewer runs this on a deletion cert (JSON) and gets a pure-mathematical verdict that the named fact was
removed from the accumulator -- without ever seeing the knowledge base, the substrate W matrix, or the RSA trapdoor.

Usage:
  python verifier.py cert.json
  python verifier.py --batch certs_dir/
Exit code 0 = all certs VERIFIED; 1 = any REJECTED. ASCII-only, stdlib-only (self-contained: no repo imports).
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def _is_prime(num: int, rounds: int = 16) -> bool:
    if num < 2:
        return False
    for p in _SMALL_PRIMES:
        if num % p == 0:
            return num == p
    d = num - 1; r = 0
    while d % 2 == 0:
        d //= 2; r += 1
    import secrets
    for _ in range(rounds):
        a = 2 + secrets.randbelow(num - 3); x = pow(a, d, num)
        if x in (1, num - 1):
            continue
        for _ in range(r - 1):
            x = x * x % num
            if x == num - 1:
                break
        else:
            return False
    return True


def _hash_to_prime(element: str, bits: int = 80) -> int:
    h = int(hashlib.sha256(("hp12:" + element).encode()).hexdigest(), 16) % (1 << bits)
    h |= (1 << (bits - 1)) | 1
    while not _is_prime(h):
        h += 2
    return h


def verify_cert(cert: dict) -> bool:
    try:
        pi = int(cert["prime"]); N = int(cert["N"])
        if _hash_to_prime(cert["element"]) != pi:
            return False
        return pow(int(cert["new_acc"]), pi, N) == int(cert["old_acc"]) % N
    except Exception:
        return False


def main(argv):
    if not argv:
        print("usage: python verifier.py <cert.json> | --batch <dir>", flush=True)
        return 2
    if argv[0] == "--batch":
        files = sorted(Path(argv[1]).glob("*.json"))
    else:
        files = [Path(a) for a in argv]
    all_ok = True
    for f in files:
        cert = json.loads(Path(f).read_text(encoding="utf-8"))
        ok = verify_cert(cert)
        all_ok = all_ok and ok
        print("%s  element=%s  -> %s" % ("VERIFIED" if ok else "REJECTED", cert.get("element"), f.name), flush=True)
    print("\n%s (%d cert%s)" % ("ALL VERIFIED" if all_ok else "SOME REJECTED", len(files), "" if len(files) == 1 else "s"), flush=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
