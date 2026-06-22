"""Substrate-native KG traversal: ingest + single-hop + n-hop chain prediction.

Operationalizes the n8 ConceptNet ingest_eval_v1 mechanism (CERT 585 chain-grade
2026-06-22; cert_ledger row d87e41e3e33833b1). Verified at 36.49x ratio over
frozen-encoder MiniLM baseline + setrecall@M=100000 = 1.000 + refuse-OOD=0.999
across 3 seeds; held-out 2-hop chains with `heldout_in_compose_graph=0` enforced
per seed (genuine composition gain, not leakage).

Composes with `hdlab.memory.Codebook` (cleanup) + `hdlab.learning.HebbianAssociations`
(single-pair Hebbian; this module is the multi-pair multi-value Hebbian for (s, p, o)
triples). The U1 FB15k-237 ingest (CERT 584) used the same mechanism family; n8
ConceptNet promoted it to OPEN-C unlocked chain-grade.

Companion to `hdlab.sequence_memory.SequenceMatrix` (sequence-binding) — both are
offline-Hebbian-bound stores but with different binding semantics: SequenceMatrix
binds ordered (k_prev, k_next) pairs; KGStore binds (s, p, o) triples via the
binding op (E[s] * R[p] -> key; outer(E[o], key) -> W).
"""

from __future__ import annotations

import math
import time

import torch

from . import tracing


class KGStore:
    """Multi-value Hebbian (s, p, o) triple store; substrate-native KG primitive.

    Holds entity codebook E [n_ent, n_dim], relation codebook R [n_rel, n_dim],
    and a Hebbian W matrix [n_dim, n_dim]. Ingest is multi-value: many objects
    per (s, p) pair are bound via outer-product accumulation. Retrieval scores
    every entity against the bound representation; top-k yields candidate set.

    Key binding op (the n8/U1 family): key = E[s] * R[p] * sqrt(n_dim).
    Single-hop retrieval: scores = E @ (W @ key).
    """

    def __init__(self, n_ent: int, n_rel: int, n_dim: int, generator: torch.Generator) -> None:
        self.n_ent = n_ent
        self.n_rel = n_rel
        self.n_dim = n_dim
        self.sq = math.sqrt(n_dim)
        self.E = self._bipolar(n_ent, n_dim, generator)
        self.R = self._bipolar(n_rel, n_dim, generator)
        self.W = torch.zeros(n_dim, n_dim, dtype=torch.float32)
        self._n_triples_ingested = 0

    @staticmethod
    def _bipolar(m: int, n: int, generator: torch.Generator) -> torch.Tensor:
        """Bipolar {-1, +1} hypervectors of shape [m, n]; the standard substrate atom format."""
        return (torch.randint(0, 2, (m, n), generator=generator, dtype=torch.int8) * 2 - 1).to(torch.float32)

    def __len__(self) -> int:
        return self._n_triples_ingested

    def ingest_triples(self, triples: torch.Tensor, batch: int = 5000) -> None:
        """Bulk Hebbian-write of [N, 3] long-tensor of (s, p, o) indices; chunked matmul."""
        t0 = time.perf_counter_ns()
        if triples.ndim != 2 or triples.shape[1] != 3:
            raise ValueError(f"Expected triples shape [N, 3]; got {tuple(triples.shape)}")
        n = triples.shape[0]
        for b in range(0, n, batch):
            chunk = triples[b:b + batch]
            s_idx, p_idx, o_idx = chunk[:, 0], chunk[:, 1], chunk[:, 2]
            keys = (self.E[s_idx] * self.R[p_idx] * self.sq).to(torch.float32)
            self.W.add_((self.E[o_idx].T @ keys) / self.n_dim)
        self._n_triples_ingested += n
        tracing.emit(
            "kg_traversal.ingest_triples",
            {"n_triples": n, "n_dim": self.n_dim},
            {"total_ingested": self._n_triples_ingested},
            elapsed_ns=time.perf_counter_ns() - t0,
        )

    def key(self, s: int, p: int) -> torch.Tensor:
        """Bind (s, p) into a single-hop query key vector (shape [n_dim])."""
        return (self.E[s] * self.R[p] * self.sq).to(torch.float32)

    def score_all(self, key: torch.Tensor) -> torch.Tensor:
        """Score every entity against bound key; returns shape [n_ent] scores tensor."""
        return self.E @ (self.W @ key)

    def predict_one_hop(self, s: int, p: int) -> int:
        """Single-hop substrate recall: returns argmax entity index for (s, p)."""
        return int(self.score_all(self.key(s, p)).argmax())

    def predict_one_hop_topk(self, s: int, p: int, k: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Single-hop top-k recall; returns (topk_indices [k], topk_scores [k])."""
        scores = self.score_all(self.key(s, p))
        topk = torch.topk(scores, k=k)
        return topk.indices, topk.values

    def predict_n_hop(self, s: int, relations: list[int]) -> tuple[int, list[int]]:
        """Substrate-native n-hop chain prediction.

        Given (s, p1, p2, ..., pn), iteratively retrieves x1=argmax((s,p1)),
        x2=argmax((x1, p2)), ..., returns final entity + chain of intermediates.

        n8 CERT 585 evidence: 2-hop substrate=0.426 vs 1-hop-baseline=0.000 vs
        frozen-encoder=0.012 (ratio 36.49x); chain-grade-validated for n=2.
        Higher n is empirically open (drill #3 multi-hop iterative cleanup at K=3,4
        is MIDDLE_BAND; chain-grade only at K=2). Use with care for n > 2.
        """
        cur = s
        chain = []
        for p in relations:
            cur = self.predict_one_hop(cur, p)
            chain.append(cur)
        return cur, chain

    def predict_two_hop(self, s: int, p1: int, p2: int) -> tuple[int, int]:
        """Two-hop convenience: predict (s, p1, ?) -> x, (x, p2, ?) -> o; returns (x_hat, o_hat).

        This is the n8 CERT 585 ratified primitive — chain-grade-validated traversal.
        """
        x_hat = self.predict_one_hop(s, p1)
        o_hat = self.predict_one_hop(x_hat, p2)
        return x_hat, o_hat

    def refuse_gate_calibrate(
        self,
        in_kb_keys: list[tuple[int, int]],
        ood_keys: list[tuple[int, int]],
    ) -> dict:
        """Calibrate a confidence-threshold tau on in-KB vs OOD (s,p) pairs.

        Returns dict with tau, in_kb_accept, ood_refuse, and conf-mean diagnostics.
        Used by n8 to achieve refuse_OOD=0.999 + in-KB-accept=0.997 (CERT 585).

        Splits each list 50/50 into calibration / eval; sweeps tau over the union of
        calibration confidence scores; picks tau maximizing 0.5*(accept + refuse) on
        calibration; reports eval-set accept + refuse.
        """
        if not in_kb_keys or not ood_keys:
            raise ValueError("refuse_gate_calibrate requires both in_kb and ood key lists")
        in_kb_conf = torch.stack([self.score_all(self.key(s, p)).max() for (s, p) in in_kb_keys])
        ood_conf = torch.stack([self.score_all(self.key(s, p)).max() for (s, p) in ood_keys])
        h_in = len(in_kb_conf) // 2
        h_ood = len(ood_conf) // 2
        cal_in, ev_in = in_kb_conf[:h_in], in_kb_conf[h_in:]
        cal_ood, ev_ood = ood_conf[:h_ood], ood_conf[h_ood:]
        cands = torch.unique(torch.cat([cal_in, cal_ood]))
        best_tau = float(cands[0])
        best_bal = -1.0
        for tau in cands:
            tau_f = float(tau)
            acc = float((cal_in >= tau_f).float().mean())
            ref = float((cal_ood < tau_f).float().mean())
            bal = 0.5 * (acc + ref)
            if bal > best_bal:
                best_bal = bal
                best_tau = tau_f
        return {
            "tau": best_tau,
            "in_kb_accept": float((ev_in >= best_tau).float().mean()),
            "ood_refuse": float((ev_ood < best_tau).float().mean()),
            "in_kb_conf_mean": float(in_kb_conf.mean()),
            "ood_conf_mean": float(ood_conf.mean()),
        }

    def matrix_norm(self) -> float:
        """Frobenius norm of W; saturation / load diagnostic."""
        return float(torch.linalg.norm(self.W))

    def reset(self) -> None:
        """Zero W and triple counter; keep codebooks E, R."""
        self.W.zero_()
        self._n_triples_ingested = 0
