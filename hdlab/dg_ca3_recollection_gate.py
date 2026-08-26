"""Dentate-gyrus pattern separation + CA3 completion: a self-certifying recollection gate.

WHAT IT IS. Episodic recollection whose CONFIDENCE self-certifies, built as the hippocampus does it.
  - DG (dentate gyrus): an idf-weighted word-presence vector -> a fixed random EXPANSIVE projection
    -> k-WTA (~2% active) = a sparse, pattern-SEPARATED code. Two episodes that share frequent words
    are orthogonalised, so a partial cue stops blurring across them.
  - CA3 (completion): a cue is DG-encoded the same way and COMPLETED to the nearest stored code; the
    completion OVERLAP is an intrinsic confidence -- no learned estimator, no labels.
  - Dual-process routing: trust recollection when it fires confidently, else a familiarity fallback.

BRAIN. Treves & Rolls (DG separation / CA3 auto-associative completion); Yonelinas dual-process
recognition; McClelland / O'Reilly / Norman complementary learning systems. PINNED that DG separates
and CA3 completes; the exact projection, k, and one-step-vs-iterated completion are OURS-UNDER-TEST
(swept, not adopted -- D~2048, k~2%, one-step here).

PROVENANCE. Promoted verbatim from experiments/exp_dg_ca3_recollection_gate_v1.py
(problem `no_automatic_reliability_signal_reaches_the_source_oracle`, SOLVED + integrated EXCELLENT
2026-08-26). There: DG/CA3 recollection SELF-CERTIFIES (top-5% precision 0.938 vs familiarity 0.533 on
the same items; word-overlap recollection self-certifies at NONE), and dual-process routing beats the
first-order counting floor CI-separated (route 0.365 vs floor UB 0.336), capturing ~half the oracle
headroom; the info-free twin loses and a scramble-content cue collapses confident precision to 0.00.
Answers board Q118: a label-free per-item selection signal IS CA3 completion confidence. The lever for
more is reading VOLUME (coverage grows with episodic reading), not a cleverer gate.

WIRING STATUS. OFF the live retrieval path -- a WIRE_CANDIDATE. Callers construct and query it
explicitly; importing this module changes NO existing behaviour. Wire it into retrieval when the
episodic path is built out (see notes/BRAIN_FOUNDATIONAL_AUDIT.md deviation #2/#3). Glass-box, no LLM,
deterministic given the projection seed.
"""
from __future__ import annotations

import numpy as np
from scipy import sparse


def weight_by_idf(binary_csr, idf):
    """(n x V) binary word-presence -> idf-weighted sparse (each present word scaled by its idf)."""
    return (binary_csr @ sparse.diags(np.asarray(idf, dtype=np.float32))).tocsr()


class DGCA3RecollectionGate:
    """DG pattern separation + CA3 completion recollection with a self-certifying confidence.

    Usage:
        g = DGCA3RecollectionGate(vocab_size).build(episode_idf, lemma_offsets)
        pick, confidence = g.recollect(cue_idf)
        pred, fired, confidence = g.route(cue_idf, familiarity_pred, fire_fraction=0.10)

    `episode_idf` is (n_epi x V) idf-weighted sparse presence, ordered so episodes of the same answer
    (lemma) are contiguous; `lemma_offsets` are the reduceat start indices grouping episodes -> lemmas.
    """

    def __init__(self, vocab_size, d_dg=2048, k_wta=41, seed=7):
        self.V = int(vocab_size)
        self.D = int(min(int(d_dg), max(256, self.V // 4)))
        self.k = int(k_wta)
        rng = np.random.default_rng(int(seed))
        self.P = (rng.standard_normal((self.V, self.D)).astype(np.float32) / np.sqrt(self.D))
        self._codes = None
        self._offsets = None

    def encode(self, x_idf):
        """(n x V) idf-weighted sparse -> (n x D) sparse binary DG code (k-WTA per row)."""
        proj = x_idf @ self.P
        n, D = proj.shape
        k = self.k
        if k >= D:
            return sparse.csr_matrix((proj > proj.mean(axis=1, keepdims=True)).astype(np.float32))
        idx = np.argpartition(-proj, k, axis=1)[:, :k]
        rows = np.repeat(np.arange(n), k)
        cols = idx.ravel()
        data = np.ones(rows.size, np.float32)
        return sparse.csr_matrix((data, (rows, cols)), shape=(n, D))

    def build(self, episode_idf, lemma_offsets, batch=4096):
        """Store the DG codes for every episode (pattern-separated)."""
        n = episode_idf.shape[0]
        parts = [self.encode(episode_idf[b0:b0 + batch]) for b0 in range(0, n, batch)]
        self._codes = sparse.vstack(parts).tocsr()
        self._offsets = np.asarray(lemma_offsets, dtype=np.int64)
        return self

    def recollect(self, cue_idf, batch=256):
        """CA3 one-step completion. Returns (pick (m,), confidence (m,)): pick = argmax lemma by
        completion overlap; confidence = that overlap (higher => more certain, and self-certifying)."""
        if self._codes is None:
            raise RuntimeError("call build() before recollect()")
        m = cue_idf.shape[0]
        pick = np.zeros(m, np.int64)
        conf = np.zeros(m, dtype=float)
        for b0 in range(0, m, batch):
            b1 = min(m, b0 + batch)
            qcode = self.encode(cue_idf[b0:b1])
            seg = np.maximum.reduceat((self._codes @ qcode.T).toarray(), self._offsets, axis=0)
            pk = seg.argmax(axis=0)
            for c, i in enumerate(range(b0, b1)):
                pick[i] = pk[c]
                conf[i] = seg[pk[c], c]
        return pick, conf

    def route(self, cue_idf, familiarity_pred, fire_fraction=0.10):
        """Dual-process gate: trust recollection for the top `fire_fraction` of cues by confidence,
        else the familiarity fallback. Returns (prediction (m,), fired (m,) bool, confidence (m,))."""
        pick, conf = self.recollect(cue_idf)
        m = len(pick)
        order = np.argsort(-conf)
        k = max(1, int(round(float(fire_fraction) * m)))
        fired = np.zeros(m, dtype=bool)
        fired[order[:k]] = True
        pred = np.where(fired, pick, np.asarray(familiarity_pred))
        return pred, fired, conf


def self_test():
    """DG must ORTHOGONALISE two episodes sharing frequent words; a partial cue must COMPLETE to the
    right one. Mirrors exp_dg_ca3_recollection_gate_v1.self_test on the organ's own methods."""
    V, D, k = 300, 1024, 20
    g = DGCA3RecollectionGate(V, d_dg=D, k_wta=k, seed=0)
    shared = list(range(20))                  # frequent shared words (LOW idf)
    a = shared + [50, 51, 52]                  # episode A distinctive (HIGH idf)
    b = shared + [200, 201, 202]               # episode B distinctive, same generic overlap
    w = np.ones(V, np.float32) * 4.0
    for j in shared:
        w[j] = 0.3

    def code(words):
        x = sparse.csr_matrix(([w[j] for j in words], (np.zeros(len(words), int), list(words))), shape=(1, V))
        return g.encode(x)

    ca, cb = code(a), code(b)
    raw_overlap = len(set(a) & set(b)) / float(len(set(a) | set(b)))
    dg_overlap = float((ca.multiply(cb)).sum()) / k
    cue = code([50, 51, shared[0]])            # A's distinctive words + a generic
    ov_a = float((ca.multiply(cue)).sum())
    ov_b = float((cb.multiply(cue)).sum())
    assert dg_overlap < raw_overlap, "DG must reduce overlap of generic-sharing episodes: dg %.2f vs raw %.2f" % (dg_overlap, raw_overlap)
    assert ov_a > ov_b, "a partial cue of A must complete to A, not B: %.0f vs %.0f" % (ov_a, ov_b)
    print("[self-test] PASS: raw jaccard=%.2f -> DG overlap=%.2f (separated); cue completes to A (%.0f vs %.0f)"
          % (raw_overlap, dg_overlap, ov_a, ov_b))
    return 0


if __name__ == "__main__":
    raise SystemExit(self_test())
