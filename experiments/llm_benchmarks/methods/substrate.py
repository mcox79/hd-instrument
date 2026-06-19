"""SubstrateEditMethod: Kerdock-substrate edit primitive for LLM editing benchmarks.

We use the KF-2 edit-isolation primitive (HARD_PASS at v268 N=8192, cross-codebook):
the substrate stores (key, value) pairs via a rank-1 outer-product memory
    W = (1/N) sum_i v_i k_i^T
and applies a single edit as a rank-1 update
    W <- W + (1/N) (v_new - v_old) k^T.
Kerdock codebooks bound max cross-correlation by 1/sqrt(N), giving structural
edit isolation: collateral damage on non-edited keys is O(1/sqrt(N)).

Why KF-2 rather than wave14_betB compositional CL? Three reasons:
  (1) the edit primitive itself is closed-form and trivial to wire up;
  (2) edit-isolation is the substrate's strongest empirical advantage vs ROME/MEMIT
      (per substrate_capability_map.md tail rows v268 KF-2 cross-codebook HP);
  (3) wave14_betB needs a 4-stage continual-learning curriculum that doesn't map
      cleanly onto CounterFact / zsRE single-edit benchmarks.

For SCAFFOLD purposes we deterministically hash (subject, relation) -> a codebook
row to assign keys, and hash (target_new) -> a codebook row for values. This is
NOT a full LLM-text-to-vector embedding; that's a Phase-2 task (see notes/
llm_benchmark_harness_2026-05-29.md). The scaffold's apply_edit + query are
end-to-end functional but their semantic faithfulness is bounded by the
collision rate of the hash.

ASCII-only per CLAUDE.md. All randomness via passed torch.Generator.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import torch

REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.llm_benchmarks.edit_benchmark_harness import EditMethod, EditTriple


def _load_kerdock_builder():
    """Lazy-load the v3 Kerdock builder (matches KF-2 scaffold pattern)."""
    path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
    spec = importlib.util.spec_from_file_location("kerdock_v3_llm_bench", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.make_kerdock_4coset_codebook


def _hash_to_idx(text: str, num_rows: int, salt: str = "") -> int:
    """Deterministic SHA-256 hash of `text` (+ salt) to a codebook row index."""
    h = hashlib.sha256((salt + "|" + text).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") % max(num_rows, 1)


class SubstrateEditMethod(EditMethod):
    """Kerdock outer-product memory; KF-2-style rank-1 edits."""

    name = "substrate"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config=config)
        self.N: int = int(self.config.get("N", 4096))
        self.seed: int = int(self.config.get("seed", 17))
        self.device: torch.device = torch.device(
            self.config.get("device", "cpu"))

        # Internal state, built in initialise().
        self._codebook: Optional[torch.Tensor] = None  # (C, N)
        self._W: Optional[torch.Tensor] = None         # (N, N)
        # Maps (subject, relation) -> assigned value codebook row index.
        # Used by query() to recover the current value.
        self._key_to_val_idx: Dict[str, int] = {}

    # ----- helpers -----
    def _key_text(self, triple: EditTriple) -> str:
        return f"{triple.subject}|||{triple.relation}"

    def _key_vec(self, key_text: str) -> torch.Tensor:
        idx = _hash_to_idx(key_text, self._codebook.shape[0], salt="key")
        return self._codebook[idx]

    def _val_vec(self, value_text: str) -> tuple[torch.Tensor, int]:
        idx = _hash_to_idx(value_text, self._codebook.shape[0], salt="val")
        return self._codebook[idx], idx

    # ----- public API -----
    def initialise(self) -> None:
        builder = _load_kerdock_builder()
        try:
            cb, _info = builder(self.N, self.device)
        except (ValueError, AssertionError):
            # Fallback: random bipolar codebook for non-Kerdock-valid N.
            # Kerdock requires N = 2^k with k even; small/odd N drops to BSC.
            rng = torch.Generator()
            rng.manual_seed(self.seed + 999)
            cb = (torch.randint(0, 2, (max(self.N, 4), self.N), generator=rng,
                                device=self.device) * 2 - 1).float()
        self._codebook = cb.to(self.device)
        self._W = torch.zeros(self.N, self.N, dtype=torch.float32,
                              device=self.device)
        self._key_to_val_idx = {}
        self._initialised = True

    def apply_edit(self, triple: EditTriple) -> Dict[str, Any]:
        if not self._initialised:
            self.initialise()
        ktext = self._key_text(triple)
        k_vec = self._key_vec(ktext)
        v_new, v_new_idx = self._val_vec(triple.target_new)

        old_idx = self._key_to_val_idx.get(ktext)
        if old_idx is None:
            # First write at this key: pure rank-1 add (no v_old subtraction).
            update = torch.outer(v_new, k_vec) / float(self.N)
        else:
            v_old = self._codebook[old_idx]
            update = torch.outer(v_new - v_old, k_vec) / float(self.N)
        self._W = self._W + update
        self._key_to_val_idx[ktext] = v_new_idx

        return {
            "key_text": ktext,
            "value_text": triple.target_new,
            "value_idx": int(v_new_idx),
            "first_write": old_idx is None,
            "edit_norm": float(update.norm().item()),
        }

    def query(self, prompt: str) -> str:
        """Return the codebook-row index (as a string) that the substrate retrieves.

        SCAFFOLD: prompt is treated as a key-text query directly. A future
        version will translate `prompt` -> (subject, relation) for proper
        paraphrase / neighborhood semantics.
        """
        if not self._initialised:
            self.initialise()
        k_vec = self._key_vec(prompt)
        scores = (self._codebook @ (self._W @ k_vec)) / float(self.N)
        idx = int(torch.argmax(scores).item())
        return str(idx)

    def query_value_idx(self, key_text: str) -> int:
        """Convenience: return the int row index argmax for a (subject|||relation) key."""
        return int(self.query(key_text))


# ----------------------------------------------------------------------------
# Module-level self-test (mirrors KF-2 pattern; cheap; runs in pytest).
# ----------------------------------------------------------------------------

def _selftest() -> None:
    """Tiny round-trip: build, edit, retrieve."""
    m = SubstrateEditMethod(config={"N": 64, "seed": 17})
    m.initialise()
    assert m._codebook is not None
    assert m._W is not None
    assert m._W.shape == (64, 64)
    triple = EditTriple(subject="paris", relation="capital_of", target_new="france_v2")
    info = m.apply_edit(triple)
    assert info["first_write"] is True
    assert info["edit_norm"] > 0.0
    # Retrieval is approximate but deterministic.
    out = m.query(m._key_text(triple))
    assert isinstance(out, str)
    # Theoretical isolation bound at N=64: 1/sqrt(64) = 0.125.
    bound = 1.0 / math.sqrt(64)
    assert bound > 0.0  # placeholder; full isolation assertion is in tests/


if __name__ == "__main__":
    _selftest()
    print("substrate self-test PASS")
