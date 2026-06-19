"""
rsa_accumulator -- RSA cryptographic accumulator for HP-12 certified per-fact deletion (V1, pure-Python).

The accumulator over a set S = {x_1..x_n}: each element hashes to a distinct odd prime p_i; the accumulator is
  Acc = g^(prod p_i) mod N   (N = p*q RSA modulus; trapdoor phi = (p-1)(q-1) kept by the KB owner only).
Membership witness for x_i: w_i = g^(prod_{j!=i} p_j) mod N;  verify: w_i^{p_i} == Acc (mod N).
DELETION of x_i (owner, uses trapdoor): Acc' = Acc^{p_i^{-1} mod phi} mod N. A third-party verifier (NO trapdoor,
  NO KB access) confirms the deletion from the public cert by checking Acc'^{p_i} == Acc (mod N) -- i.e. re-multiplying
  the deleted element's prime reproduces the pre-deletion accumulator, proving x_i was the element removed.

Owner-side ops (add/delete) use gmpy2 (powmod/invert/is_prime) when available -> sub-ms certs at production 2048-bit;
pure-Python fallback keeps the module dependency-free + correct (the standalone verifier.py stays pure-Python for
third-party portability). ASCII-only.
"""
from __future__ import annotations
import hashlib
import secrets
from typing import Dict, List

try:
    import gmpy2  # owner-side acceleration (optional)
    _HAVE_GMPY2 = True
except Exception:
    _HAVE_GMPY2 = False

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def _powmod(b: int, e: int, m: int) -> int:
    return int(gmpy2.powmod(b, e, m)) if _HAVE_GMPY2 else pow(b, e, m)


def _invert(a: int, m: int) -> int:
    return int(gmpy2.invert(a, m)) if _HAVE_GMPY2 else pow(a, -1, m)


def is_prime(num: int, rounds: int = 16) -> bool:
    if num < 2:
        return False
    if _HAVE_GMPY2:
        return bool(gmpy2.is_prime(num))
    for p in _SMALL_PRIMES:
        if num % p == 0:
            return num == p
    d = num - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = 2 + secrets.randbelow(num - 3)
        x = pow(a, d, num)
        if x in (1, num - 1):
            continue
        for _ in range(r - 1):
            x = x * x % num
            if x == num - 1:
                break
        else:
            return False
    return True


def gen_prime(bits: int) -> int:
    while True:
        c = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(c):
            return c


def hash_to_prime(element: str, bits: int = 80) -> int:
    """Deterministic odd prime from an element id (SHA-256 -> candidate -> next prime). Same element -> same prime."""
    h = int(hashlib.sha256(("hp12:" + element).encode()).hexdigest(), 16) % (1 << bits)
    h |= (1 << (bits - 1)) | 1
    while not is_prime(h):
        h += 2
    return h


class RSAAccumulator:
    def __init__(self, rsa_bits: int = 1024, g: int = 3, _p: int = 0, _q: int = 0):
        # rsa_bits is the size of EACH prime factor; modulus N is ~2*rsa_bits. V1 default 1024 -> 2048-bit N.
        self.p = _p or gen_prime(rsa_bits)
        self.q = _q or gen_prime(rsa_bits)
        self.N = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.g = g
        self.acc = g % self.N
        self.primes: Dict[str, int] = {}     # element -> its prime (public)
        self.members: List[str] = []

    def add(self, element: str) -> int:
        if element in self.primes:
            return self.acc
        pi = hash_to_prime(element)
        self.primes[element] = pi
        self.members.append(element)
        self.acc = _powmod(self.acc, pi, self.N)
        return self.acc

    def add_many(self, elements: List[str]) -> int:
        for e in elements:
            self.add(e)
        return self.acc

    def delete(self, element: str) -> Dict:
        """Owner deletion via trapdoor. Returns a PUBLIC cert (no trapdoor inside) for third-party verification."""
        if element not in self.primes:
            raise KeyError("not a member: %s" % element)
        pi = self.primes[element]
        old_acc = self.acc
        new_acc = _powmod(old_acc, _invert(pi, self.phi), self.N)   # Acc^{p_i^{-1} mod phi}
        self.acc = new_acc
        self.members.remove(element)
        del self.primes[element]
        return {"scheme": "RSA-ACC-v1", "element": element, "prime": pi,
                "old_acc": old_acc, "new_acc": new_acc, "N": self.N, "g": self.g}

    @staticmethod
    def verify_deletion(cert: Dict) -> bool:
        """THIRD-PARTY verifier: no trapdoor, no KB. Confirms new_acc^prime == old_acc (mod N), and prime is the
        correct hash-to-prime of the named element (so the cert cannot lie about WHICH fact was deleted)."""
        try:
            pi = int(cert["prime"]); N = int(cert["N"])
            if hash_to_prime(cert["element"]) != pi:
                return False
            return _powmod(int(cert["new_acc"]), pi, N) == int(cert["old_acc"]) % N
        except Exception:
            return False
