"""
api.py -- HP-12 V1 HIPAA-style substrate-KB API surface (in-process; the demo backend's 4 endpoints).

Wraps the substrate associative memory + RSA accumulator + append-only audit log into the four demo endpoints:
  POST /facts            -> post_fact(fact_id, key_vec, value_id): real-time write (<ms) + accumulator add
  POST /query            -> query(key_vec): substrate retrieval (Rule-8 combine) + answer + cert chain
  DELETE /facts/{id}     -> delete_fact(fact_id): substrate projection-out + accumulator deletion cert (third-party verifiable)
  GET /audit/{cert_id}   -> get_audit(cert_id): retrieve the stored deletion cert for independent verification

Substrate is dense Hebbian/cf-RPE at N (V1 = 10^4). Crypto via tools.hp12.rsa_accumulator. Audit log is append-only
(HMAC-style hash chain). numpy + pure-Python/gmpy2 crypto. ASCII-only.
"""
from __future__ import annotations
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple
from tools.hp12.rsa_accumulator import RSAAccumulator


def _softmax(x):
    e = np.exp(x - x.max()); return e / (e.sum() + 1e-12)


class SubstrateKB:
    def __init__(self, n: int, n_val: int, rsa_bits: int = 256, seed: int = 0):
        g = np.random.default_rng(seed)
        self.n = n
        self.EV = (g.integers(0, 2, (n_val, n)) * 2 - 1).astype(np.float32)
        self.EV /= np.linalg.norm(self.EV, axis=1, keepdims=True) + 1e-8
        self.W = np.zeros((n, n), dtype=np.float32)
        self.acc = RSAAccumulator(rsa_bits=rsa_bits)
        self.facts: Dict[str, Tuple[np.ndarray, int]] = {}
        self.audit: Dict[str, Dict] = {}                  # cert_id -> deletion cert
        self.chain_head = "genesis"

    # POST /facts
    def post_fact(self, fact_id: str, key_vec: np.ndarray, value_id: int) -> Dict:
        k = key_vec.astype(np.float32); k /= np.linalg.norm(k) + 1e-8
        self.W += np.outer(self.EV[value_id] - (self.W @ k), k)   # cf-RPE single-fact write
        self.acc.add(fact_id)
        self.facts[fact_id] = (k, value_id)
        return {"ok": True, "fact_id": fact_id, "members": len(self.facts)}

    # POST /query
    def query(self, key_vec: np.ndarray, k_top: int = 5) -> Dict:
        q = key_vec.astype(np.float32); q /= np.linalg.norm(q) + 1e-8
        r = self.W @ q
        scores = self.EV @ r
        value_id = int(np.argmax(scores)); conf = float(scores.max())
        cert_chain = {"query_state_hash": hashlib.sha256(self.W.tobytes()).hexdigest()[:16],
                      "retrieved_value": value_id, "confidence": round(conf, 4), "accumulator": str(self.acc.acc)[:24] + "..."}
        return {"value_id": value_id, "confidence": conf, "cert_chain": cert_chain, "found": conf > 0.30}

    # DELETE /facts/{id}
    def delete_fact(self, fact_id: str) -> Dict:
        if fact_id not in self.facts:
            return {"ok": False, "error": "unknown fact"}
        k, _ = self.facts[fact_id]
        for _ in range(3):                                 # project-out + stabilizing re-projection (0-phantom)
            self.W -= np.outer(self.W @ k, k)
        cert = self.acc.delete(fact_id)                    # cryptographic deletion cert
        cert_id = hashlib.sha256((self.chain_head + fact_id + str(cert["new_acc"])).encode()).hexdigest()[:24]
        cert["cert_id"] = cert_id; cert["prev_chain"] = self.chain_head
        self.chain_head = cert_id
        self.audit[cert_id] = cert
        del self.facts[fact_id]
        return {"ok": True, "cert_id": cert_id, "cert": cert}

    # GET /audit/{cert_id}
    def get_audit(self, cert_id: str) -> Optional[Dict]:
        return self.audit.get(cert_id)

    def verify_audit(self, cert_id: str) -> bool:
        c = self.audit.get(cert_id)
        return bool(c) and RSAAccumulator.verify_deletion(c)
