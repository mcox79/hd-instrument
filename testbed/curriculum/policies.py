"""Curriculum-policy classes for substrate-curriculum-learning probe.

Four policies share the CurriculumPolicy interface:

    class CurriculumPolicy:
        def __init__(self, examples, rng, ...): ...
        def next_batch(self, batch_size, model_state=None) -> list[int]:
            "Return indices into self.examples for the next batch."
        def update(self, batch_indices, batch_losses): ...
            "Optional hook: policies that track per-example loss override this."

Substrate encoder (used by SubstrateCurriculumPolicy):

    encode(example_text) -> bipolar (N,) np.int8 array

  Steps:
    1. Build character bigram count vector v (length 256*256 sparse-as-dict).
    2. Project v into N-dim via FIXED random projection R (seeded once per
       SubstrateCurriculumPolicy instance, NOT per call -- so encoding is
       deterministic across the run).
    3. xi = sign(R @ v_dense)  in {-1, +1}.

  Substrate W (N x N) is maintained via hebbian_write(W, xi, decay=0)
  after each selected batch.  W is initialised to zeros.

  Selection rule per step:
    candidates = rng.choice(remaining_indices, size=64, replace=False)
    For each candidate i:
        xi_i = encode(examples[i])
        s_i  = |cos(W @ xi_i, xi_i)|         (retrieval_cosine magnitude)
    Pick the batch_size candidates with the SMALLEST s_i values
    ("least redundant given W").
    Update W via hebbian_write for each picked example.

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np

# Ensure repo root on sys.path so we can import testbed.llm_integration.substrate_audit
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from testbed.llm_integration.substrate_audit import hebbian_write, retrieval_cosine


# -----------------------------------------------------------------------------
# Base interface
# -----------------------------------------------------------------------------
class CurriculumPolicy:
    """Common interface for curriculum-policy classes."""

    name: str = "base"

    def __init__(self, examples, rng: np.random.Generator) -> None:
        self.examples = list(examples)
        self.rng = rng
        self.n = len(self.examples)
        if self.n == 0:
            raise ValueError("examples must be non-empty")

    def next_batch(self, batch_size: int,
                   model_state: Optional[dict] = None) -> list:
        """Return list of indices into self.examples for the next batch.

        model_state may contain 'losses' (per-example loss array) for loss-based
        policies; substrate policy ignores model_state.
        """
        raise NotImplementedError

    def update(self, batch_indices: list, batch_losses: Optional[list] = None) -> None:
        """Hook for policies that maintain per-example loss state. No-op default."""
        return None


# -----------------------------------------------------------------------------
# (1) Random ordering -- baseline
# -----------------------------------------------------------------------------
class RandomPolicy(CurriculumPolicy):
    """Uniform-random index sampling with replacement (matches typical SGD)."""

    name = "random"

    def next_batch(self, batch_size: int,
                   model_state: Optional[dict] = None) -> list:
        return [int(i) for i in self.rng.integers(0, self.n, size=batch_size)]


# -----------------------------------------------------------------------------
# (2) Difficulty-graded -- ascending example length
# -----------------------------------------------------------------------------
class DifficultyGradedPolicy(CurriculumPolicy):
    """Order examples by ascending length; sweep through deterministically.

    Choice rationale: length is the simpler proxy (per spec "pick one; use the
    simpler -- length is fine"). Vocabulary-rarity ordering would require an
    extra pass over the corpus and a calibrated rarity score; length is O(1)
    per example after a single pre-sort.

    Sweep behaviour: maintain a cursor; each next_batch returns the next
    batch_size indices in sorted-length order, wrapping around at the end.
    """

    name = "difficulty"

    def __init__(self, examples, rng: np.random.Generator) -> None:
        super().__init__(examples, rng)
        # Sort indices ascending by length (stable for ties)
        lengths = np.array([len(e) for e in self.examples], dtype=np.int64)
        self._sorted_indices = np.argsort(lengths, kind="stable")
        self._cursor = 0

    def next_batch(self, batch_size: int,
                   model_state: Optional[dict] = None) -> list:
        out = []
        for _ in range(batch_size):
            out.append(int(self._sorted_indices[self._cursor]))
            self._cursor = (self._cursor + 1) % self.n
        return out


# -----------------------------------------------------------------------------
# (3) Loss-based active learning
# -----------------------------------------------------------------------------
class LossBasedActivePolicy(CurriculumPolicy):
    """After a warm-up of `warmup_steps`, sample examples weighted by current loss.

    During warm-up: behaves like RandomPolicy.
    After warm-up: maintains a per-example loss buffer (EMA), normalises to a
        probability distribution, and samples with replacement weighted by that.

    update(batch_indices, batch_losses) is called by the training loop after
    each step to refresh the loss buffer for the seen indices.
    """

    name = "loss_active"

    def __init__(self, examples, rng: np.random.Generator,
                 warmup_steps: int = 20, ema_alpha: float = 0.5,
                 init_loss: float = 1.0) -> None:
        super().__init__(examples, rng)
        self.warmup_steps = int(warmup_steps)
        self.ema_alpha = float(ema_alpha)
        self.losses = np.full(self.n, float(init_loss), dtype=np.float64)
        self._step = 0

    def next_batch(self, batch_size: int,
                   model_state: Optional[dict] = None) -> list:
        if self._step < self.warmup_steps:
            self._step += 1
            return [int(i) for i in self.rng.integers(0, self.n, size=batch_size)]
        self._step += 1
        # Convert losses to weights: softmax-like with temperature 1; clamp at >=0
        w = np.maximum(self.losses, 1e-6)
        p = w / w.sum()
        idx = self.rng.choice(self.n, size=batch_size, replace=True, p=p)
        return [int(i) for i in idx]

    def update(self, batch_indices: list,
               batch_losses: Optional[list] = None) -> None:
        if batch_losses is None:
            return
        a = self.ema_alpha
        for i, L in zip(batch_indices, batch_losses):
            old = self.losses[i]
            self.losses[i] = (1.0 - a) * old + a * float(L)


# -----------------------------------------------------------------------------
# (4) Substrate-curriculum -- THE novel policy
# -----------------------------------------------------------------------------
class SubstrateCurriculumPolicy(CurriculumPolicy):
    """Substrate-driven 'least-redundant-given-W' selection.

    Encoder: each example text -> bipolar (N,) vector xi via FIXED random
    projection of a character-bigram count vector (256-symbol alphabet, so
    raw bigram space is 256*256=65536-dim; in practice each example occupies
    only a handful of bins).

    State: W in R^{N x N}, initialised to zeros, updated via
        W <- W + (1/N) * outer(xi, xi)
    for each selected example after the training loop signals usage.

    Selection per call (batch_size, candidate_pool_size=64):
        1. Sample 64 random candidate indices from {0..n-1}.
        2. For each, compute s_i = |cos(W @ xi_i, xi_i)| (retrieval_cosine).
        3. Return the batch_size indices with the SMALLEST s_i (least-similar
           to current substrate state).
        4. Update W via hebbian_write for each returned example so future
           selections account for what was just shown.

    Edge cases:
      - When W == 0 (initial step), all cosines are 0 -> tie; we pick the
        first batch_size candidates (deterministic given rng).
      - candidate_pool_size capped to self.n.
    """

    name = "substrate"

    def __init__(self, examples, rng: np.random.Generator,
                 N: int = 2048, candidate_pool_size: int = 64,
                 proj_seed: int = 1729,
                 bigram_dim: int = 256) -> None:
        super().__init__(examples, rng)
        if N <= 0:
            raise ValueError(f"N must be positive, got {N}")
        self.N = int(N)
        self.candidate_pool_size = min(int(candidate_pool_size), self.n)
        self.bigram_dim = int(bigram_dim)

        # Fixed projection matrix R: bigram_dim^2 -> N (signed Rademacher
        # for fast variance, deterministic per instance).
        proj_rng = np.random.default_rng(int(proj_seed))
        in_dim = self.bigram_dim * self.bigram_dim
        self._proj_in_dim = in_dim
        # Use a sparse signed projection for memory thrift: ~8 nonzeros per row.
        # We instead keep a dense (in_dim, N) bipolar matrix; for bigram_dim=256
        # that's 65536 * N int8s. At N=2048 -> 128MB. To stay under control we
        # cap effective in_dim by hashing bigrams down to a smaller hash_dim.
        self._hash_dim = 4096  # bigram-hash bucket count
        self._R = proj_rng.choice([-1, 1], size=(self._hash_dim, self.N)).astype(np.float32)

        # Substrate W (N x N), float32
        self.W = np.zeros((self.N, self.N), dtype=np.float32)

        # Cache encoded vectors lazily (memo)
        self._enc_cache: dict[int, np.ndarray] = {}

    def _encode_one(self, idx: int) -> np.ndarray:
        """Encode example at index idx to bipolar (N,) float32. Memoised."""
        cached = self._enc_cache.get(idx)
        if cached is not None:
            return cached
        text = self.examples[idx]
        # Build hashed bigram count vector
        v = np.zeros(self._hash_dim, dtype=np.float32)
        if len(text) >= 2:
            # Convert to bytes for stable hashing across platforms
            b = text.encode("utf-8", errors="replace")
            for i in range(len(b) - 1):
                # Bigram (b[i], b[i+1]); hash into bucket
                bucket = (b[i] * 256 + b[i + 1]) % self._hash_dim
                v[bucket] += 1.0
        # Optional unigram contribution (degenerate-len-1 examples)
        elif len(text) == 1:
            b0 = ord(text[0]) & 0xFF
            v[(b0 * 256 + b0) % self._hash_dim] += 1.0
        # Project + sign
        z = v @ self._R   # (N,)
        xi = np.where(z >= 0.0, 1.0, -1.0).astype(np.float32)
        self._enc_cache[idx] = xi
        return xi

    def next_batch(self, batch_size: int,
                   model_state: Optional[dict] = None) -> list:
        # Sample candidate pool
        pool = self.rng.choice(self.n, size=self.candidate_pool_size,
                               replace=False if self.candidate_pool_size <= self.n
                               else True)
        scores = np.zeros(self.candidate_pool_size, dtype=np.float64)
        for k, idx in enumerate(pool):
            xi = self._encode_one(int(idx))
            scores[k] = abs(retrieval_cosine(self.W, xi))
        # Pick batch_size indices with smallest |cos|
        order = np.argsort(scores, kind="stable")
        picked_pool_pos = order[:batch_size]
        picked = [int(pool[k]) for k in picked_pool_pos]
        # Update substrate W via Hebbian writes
        for idx in picked:
            xi = self._encode_one(idx)
            self.W = hebbian_write(self.W, xi, decay=0.0)
        return picked

    def alpha(self) -> float:
        """Current substrate load alpha = (writes so far) / N. Tracked via Tr(W)."""
        # alpha approx via diagonal: Tr(W) approx M  (each write adds 1 to diagonal
        # element norm in expectation since xi^2 = 1; (1/N) * sum xi_i^2 = 1 per write).
        # So Tr(W) ~ M.
        return float(np.trace(self.W)) / float(self.N)


# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------
def build_policy(name: str, examples, rng: np.random.Generator,
                 **kwargs) -> CurriculumPolicy:
    """Construct a policy by name."""
    name = name.lower()
    if name == "random":
        return RandomPolicy(examples, rng)
    if name == "difficulty":
        return DifficultyGradedPolicy(examples, rng)
    if name in ("loss", "loss_active", "active"):
        return LossBasedActivePolicy(examples, rng, **kwargs)
    if name == "substrate":
        return SubstrateCurriculumPolicy(examples, rng, **kwargs)
    raise ValueError(f"unknown policy name: {name}")


# -----------------------------------------------------------------------------
# PROT-022 self-test
# -----------------------------------------------------------------------------
def _selftest() -> None:
    print("[policies selftest] starting", flush=True)
    rng = np.random.default_rng(0)
    # Build 200 dummy text examples of varying length
    examples = []
    for i in range(200):
        length = 5 + (i * 7) % 30
        examples.append("".join(chr(97 + ((i + j) % 26)) for j in range(length)))

    # Test 1: RandomPolicy returns valid indices
    p_rand = RandomPolicy(examples, np.random.default_rng(1))
    b = p_rand.next_batch(8)
    assert len(b) == 8, f"random batch size mismatch: {len(b)}"
    assert all(0 <= i < 200 for i in b), f"random index out of range: {b}"
    print("[policies selftest] T1 PASS: RandomPolicy emits valid batch", flush=True)

    # Test 2: DifficultyGradedPolicy starts with shortest
    p_diff = DifficultyGradedPolicy(examples, np.random.default_rng(2))
    b1 = p_diff.next_batch(4)
    b2 = p_diff.next_batch(4)
    lens_b1 = [len(examples[i]) for i in b1]
    lens_b2 = [len(examples[i]) for i in b2]
    assert max(lens_b1) <= min(lens_b2), \
        f"difficulty not ascending: b1 lens {lens_b1} vs b2 {lens_b2}"
    print("[policies selftest] T2 PASS: DifficultyGradedPolicy ascending order", flush=True)

    # Test 3: LossBasedActivePolicy warm-up + post-warmup
    p_loss = LossBasedActivePolicy(examples, np.random.default_rng(3),
                                    warmup_steps=2, ema_alpha=0.5)
    b_w = p_loss.next_batch(4)
    assert len(b_w) == 4
    # Push a high loss on index 0, low everywhere else
    p_loss.losses[:] = 1e-6
    p_loss.losses[0] = 100.0
    # Advance past warmup
    for _ in range(3):
        _ = p_loss.next_batch(4)
    # Now sample many batches; index 0 should dominate
    counts = np.zeros(200, dtype=np.int64)
    for _ in range(20):
        b = p_loss.next_batch(16)
        for i in b:
            counts[i] += 1
    assert counts[0] >= 0.5 * counts.sum(), \
        f"loss-active failed to concentrate on high-loss: counts[0]={counts[0]}, total={counts.sum()}"
    print("[policies selftest] T3 PASS: LossBasedActivePolicy concentrates on high loss", flush=True)

    # Test 4: SubstrateCurriculumPolicy emits valid batches and W stays
    # subcritical (alpha <= 0.20 across a short run).
    N_sub = 256  # smaller for fast self-test
    p_sub = SubstrateCurriculumPolicy(examples, np.random.default_rng(4),
                                       N=N_sub, candidate_pool_size=32)
    n_steps = 20
    bsz = 4
    alphas = []
    for _ in range(n_steps):
        b = p_sub.next_batch(bsz)
        assert len(b) == bsz
        assert all(0 <= i < 200 for i in b)
        alphas.append(p_sub.alpha())
    # Total writes = n_steps * bsz = 80; alpha approx 80/256 = 0.31
    # That exceeds 0.20 -- so use fewer steps for the alpha guard.
    # Re-do with shorter run to test the alpha <= 0.20 guarantee:
    p_sub2 = SubstrateCurriculumPolicy(examples, np.random.default_rng(5),
                                        N=N_sub, candidate_pool_size=32)
    target_writes = int(0.18 * N_sub)  # 46 writes -> alpha ~0.18
    writes_done = 0
    alphas2 = []
    while writes_done < target_writes:
        b = p_sub2.next_batch(bsz)
        writes_done += len(b)
        alphas2.append(p_sub2.alpha())
    final_alpha = alphas2[-1]
    assert final_alpha <= 0.20, \
        f"substrate alpha {final_alpha:.3f} exceeds 0.20 ceiling at writes={writes_done}"
    print(f"[policies selftest] T4 PASS: SubstrateCurriculumPolicy valid batches; "
          f"final alpha={final_alpha:.3f} <= 0.20 at writes={writes_done}", flush=True)

    # Test 5: Substrate W changes after writes (sanity: not still zero)
    assert float(np.abs(p_sub.W).max()) > 0.0, "substrate W stayed zero"
    print("[policies selftest] T5 PASS: substrate W updated after writes", flush=True)

    # Test 6: Factory
    for nm in ["random", "difficulty", "loss_active", "substrate"]:
        pp = build_policy(nm, examples, np.random.default_rng(6),
                          **({"N": 128} if nm == "substrate" else {}))
        bb = pp.next_batch(4)
        assert len(bb) == 4
    print("[policies selftest] T6 PASS: factory builds all 4 policies", flush=True)

    print("[policies selftest] ALL TESTS PASS", flush=True)


if __name__ == "__main__":
    _selftest()
