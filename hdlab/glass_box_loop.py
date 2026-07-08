"""Glass-box self-auditing reasoning loop: retrieve -> gate -> audit -> requery -> commit.

The operational promotion of the CHAIN_GRADE glass-box micro-loop
(exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1, commit ba552930a; certified on
real ConceptNet and non-ceiling at 80x scale via the _conceptnet_multihop / _SCALE variants).
It composes already-certified substrate parts into one inspectable + causal-hand-editable loop:

  hop-1 retrieve (bridge into working-memory active-slot)
    -> gate (basal-ganglia Go/NoGo value-gate reads the arbitration MARGIN of the single shot)
    -> audit (every hop logged as a step, Merkle-chained; deterministic replay; tamper-detect)
    -> WM-mediated re-query (re-bind the WM active-slot content into the hop-2 store)
    -> commit (the audited answer).

BRAIN GROUNDING (notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md):
  - PFC->hippocampus retrieval-in-service-of-inference: an anchor cue reaches a CA3 attractor;
    the arbitration/match-mismatch margin is the "stop vs re-query" evaluator (thread 1).
  - Working memory holds the retrieved bridge (active slot) and re-binds it into the second store
    to bias the hop-2 completion (thread 2 active-slot; thread 4 offline re-completion over the
    same stored weights, not a separate planner).
  - Cortico-BG-thalamic Go/NoGo value-gate decides WHETHER to commit the single shot or re-query
    (thread 3): high arbitration margin => Go (commit); low margin => NoGo (WM-mediated re-query).

DEPENDENCY COMPOSITION (which certified hdlab primitives this loop composes, and the two minimal
faithful pieces promoted alongside it):
  - binding (BSC bipolar): the loop's bind is elementwise product of bipolar {-1,+1} vectors --
    identical semantics to hdlab.binding.bsc_bind / bsc_unbind (self-inverse for bipolar). Realized
    here in numpy (bsc_bind below) to match the numpy-CPU convention of hdlab.cleanup_family, the
    readout dependency this loop most directly composes; the torch binding.bsc_bind is bit-identical
    in semantics.
  - cleanup / readout (argmax): hdlab.cleanup_family.k_NN_lookup(k=1) is the argmax cleanup this
    loop's retrieval uses. BUT k_NN_lookup returns only the argmax index; the loop's gate reads the
    top1-top2 arbitration MARGIN (the combinedgate_v8 "why-signal", which is exp-only per the
    integration audit -- not yet in hdlab). So this module promotes a MINIMAL faithful margin-cleanup
    (cleanup_with_margin) alongside the loop: same argmax as k_NN_lookup, plus the arbitration margin
    the value-gate needs. (Dependency-handling path (b): promote the one genuinely-missing gate
    quantity, additive + witnessed.)
  - gate (basal-ganglia Go/NoGo value-gate): margin >= tau => Go. hdlab.refuse_gate calibrates the
    same margin-discipline threshold but with accept/REFUSE action-semantics (refuse = do not answer);
    the loop's NoGo instead GATHERS MORE (re-queries) then answers, so the decision is promoted here
    as go_nogo (minimal; same threshold discipline, re-query action).
  - working memory (active-slot): the loop carries ONE retrieved id (the bridge) in a single active
    slot and re-binds it. This is the minimal single-slot form of the content-addressed hold in
    hdlab.working_memory (whose chain-grade envelope is the multi-bank K-extension); composed inline
    here because the loop uses only the single-slot rebind, not the multi-bank capacity guarantee.
  - audit (Merkle hash-chain + deterministic replay + tamper-detect): NO merkle/hash-chain audit
    module exists in hdlab. The audit primitives (sha256_bytes, merkle_root, merkle_verify, AuditLog)
    are transcribed verbatim from the HARD_PASS exp_reasoning_chain_replay_v1 and promoted here as the
    glass-box wrapper. This is the deep-prize capability: the loop is inspectable + hand-editable.

CERTIFIED PROPERTIES this module reproduces (witnessed in verification/test_glass_box_loop.py):
  (1) the loop beats a single shot on a multi-hop task (single-shot fails HARD trials; the gated
      WM-requery resolves them) -- the discriminator fires (single-shot must fail),
  (2) a causal hand-edit of the logged bridge flips the downstream recompute (the log is causally
      load-bearing, monitor-not-control),
  (3) tamper is detected and the Merkle root verifies (any edited step breaks the committed root),
  (4) deterministic replay (recomputing the trial from the same inputs reproduces answer + root).

STORAGE (per USER-locked CG_META storage-strategy law): mixed. Each hop store is a per-hop BUNDLED
single-hop associative memory (a single-hop read within a hop; no downstream composition WITHIN a
hop); cross-hop composition is SHARDED via WM re-binding -- the bridge is carried in the active slot
and re-bound into the second store, never fused into one global chain bundle.

Convention: numpy CPU, bipolar {-1,+1} float32 (matches hdlab.cleanup_family). Import-safe (no
selftest at import; run `python -m hdlab.glass_box_loop` for the formula selftest). No tracing state.
ASCII-only. No emojis, no em dashes.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


# ============================================================================
# Audit primitives (PROMOTED; the glass-box wrapper).
# Transcribed verbatim from experiments/exp_reasoning_chain_replay_v1.py (HARD_PASS: 100pct
# deterministic replay + Merkle verify + tamper detect). No merkle/hash-chain audit module
# existed in hdlab before this; these are the deep-prize audit surface.
# ============================================================================
def sha256_bytes(b: bytes) -> bytes:
    """SHA-256 digest of raw bytes."""
    return hashlib.sha256(b).digest()


def merkle_root(steps: Sequence[str]) -> bytes:
    """Chain audit steps into one Merkle-style root: c=h(genesis); c=h(c + step) for each step."""
    c = sha256_bytes(b"genesis")
    for s in steps:
        c = sha256_bytes(c + s.encode("utf-8"))
    return c


def merkle_verify(steps: Sequence[str], root: bytes) -> bool:
    """Recompute the root from the recorded steps and confirm it matches the committed root."""
    return merkle_root(steps) == root


@dataclass
class AuditLog:
    """Glass-box audit log: the ordered hop-record steps + their committed Merkle root.

    The log is the inspectable, hand-editable record of one loop run. verify() confirms the
    committed root reproduces from the steps; tamper_detect(edited_steps) returns True iff an
    edited step-list no longer reproduces the committed root (the tamper flag fires)."""
    steps: List[str]
    root: bytes

    def verify(self) -> bool:
        """True iff the recorded steps reproduce the committed root."""
        return merkle_verify(self.steps, self.root)

    def tamper_detect(self, edited_steps: Sequence[str]) -> bool:
        """True iff edited_steps do NOT reproduce the committed root (i.e. tampering is detected)."""
        return not merkle_verify(edited_steps, self.root)


# ============================================================================
# BSC bipolar substrate binding (COMPOSED; same semantics as hdlab.binding.bsc_bind, numpy flavor).
# bind = elementwise product of bipolar {-1,+1} vectors; self-inverse for bipolar b.
# ============================================================================
def bsc_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """BSC bind: elementwise product of bipolar {-1,+1} vectors (self-inverse). Matches
    hdlab.binding.bsc_bind semantics in numpy."""
    return a * b


def make_codebook(n_nodes: int, n_dim: int, rng: np.random.Generator) -> np.ndarray:
    """(n_nodes, n_dim) bipolar +/-1 float32 codebook (sharded; each concept its own random vector)."""
    return (rng.integers(0, 2, size=(n_nodes, n_dim)).astype(np.float32) * 2.0 - 1.0)


# ============================================================================
# Arbitration-margin cleanup gate (PROMOTED minimal faithful piece).
# cleanup_with_margin = argmax cleanup (same index as hdlab.cleanup_family.k_NN_lookup) PLUS the
# top1-top2 arbitration margin the value-gate reads (the combinedgate_v8 "why-signal", exp-only).
# go_nogo = the basal-ganglia Go/NoGo value-gate decision on that margin.
# ============================================================================
def cleanup_with_margin(probe: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    """Argmax cleanup over the codebook, returning (best_id, arbitration_margin).

    margin = (top1_score - top2_score) / N over the codebook dot scores -- the arbitration
    "why-signal" the value-gate reads. The best_id is the same argmax hdlab.cleanup_family.
    k_NN_lookup(k=1) returns; this adds the margin the gate needs."""
    scores = codebook @ probe                       # (V,)
    n_dim = codebook.shape[1]
    if scores.shape[0] < 2:
        return int(np.argmax(scores)), 1.0
    top2 = np.argpartition(scores, -2)[-2:]
    a, b = top2[np.argsort(scores[top2])[::-1]]
    margin = float((scores[a] - scores[b]) / n_dim)
    return int(a), margin


def go_nogo(margin: float, tau: float) -> bool:
    """Basal-ganglia Go/NoGo value-gate: True (Go: commit the single shot) iff margin >= tau,
    else False (NoGo: gather more / re-query). Same margin-threshold discipline as
    hdlab.refuse_gate, but NoGo re-queries rather than refusing to answer."""
    return bool(margin >= tau)


# ============================================================================
# The glass-box loop: retrieve -> gate -> audit -> requery -> commit.
# ============================================================================
@dataclass
class LoopResult:
    """Result of one glass-box loop run.

    committed_answer: the audited, committed answer id (the loop's output).
    go: gate decision -- True = committed the single shot; False = committed the WM re-query.
    bridge_hat_id: the hop-1 bridge retrieved into the WM active slot.
    single_shot_answer / requery_answer: the two candidate answers (for inspection / measurement).
    margin_hop1 / margin_single_shot / margin_requery: arbitration margins at each cleanup.
    audit: the AuditLog (steps + committed Merkle root); inspectable + hand-editable.
    """
    committed_answer: int
    go: bool
    bridge_hat_id: int
    single_shot_answer: int
    requery_answer: int
    margin_hop1: float
    margin_single_shot: float
    margin_requery: float
    audit: AuditLog
    extra: Dict[str, float] = field(default_factory=dict)


def glass_box_reason(codebook: np.ndarray, hop1_store: np.ndarray, hop2_store: np.ndarray,
                     anchor_id: int, *, tau: float) -> LoopResult:
    """Run the retrieve -> gate -> audit -> requery -> commit loop for one query.

    Args:
        codebook: (V, N) bipolar codebook; row i is concept id i.
        hop1_store: (N,) bundled associative memory keyed by anchor -> bridge (the WM source).
        hop2_store: (N,) bundled associative memory keyed by (bridge OR anchor) -> answer.
        anchor_id: the query anchor concept id.
        tau: Go/NoGo value-gate threshold on the single-shot arbitration margin.

    Returns:
        LoopResult with the committed answer, gate telemetry, candidate answers, and the AuditLog.
    """
    anchor = codebook[anchor_id]

    # hop-1: retrieve the bridge into the WM active slot.
    bridge_hat_id, margin_hop1 = cleanup_with_margin(bsc_bind(anchor, hop1_store), codebook)

    # single-shot attempt: raw anchor into the hop-2 store -- the gate's "why-signal".
    single_shot_id, margin_single = cleanup_with_margin(bsc_bind(anchor, hop2_store), codebook)

    # gate (basal-ganglia Go/NoGo value-gate).
    go = go_nogo(margin_single, tau)

    # WM-mediated re-query: re-bind the WM active-slot content (bridge_hat) into the hop-2 store.
    requery_id, margin_requery = cleanup_with_margin(bsc_bind(codebook[bridge_hat_id], hop2_store),
                                                     codebook)

    committed = single_shot_id if go else requery_id

    # glass-box audit log: one hop_record per step, Merkle-chained.
    steps = [
        "query(anchor=%d)" % int(anchor_id),
        "hop1_retrieve(bridge=%d,margin1=%.4f)" % (bridge_hat_id, margin_hop1),
        "gate(marginA=%.4f,tau=%.4f,decision=%s,ansA=%d)" % (
            margin_single, tau, "GO" if go else "NOGO", single_shot_id),
        "hop2_requery(bridge_used=%d,ansB=%d,marginB=%.4f)" % (
            bridge_hat_id, requery_id, margin_requery),
        "commit(answer=%d)" % int(committed),
    ]
    audit = AuditLog(steps=steps, root=merkle_root(steps))

    return LoopResult(
        committed_answer=int(committed), go=go, bridge_hat_id=int(bridge_hat_id),
        single_shot_answer=int(single_shot_id), requery_answer=int(requery_id),
        margin_hop1=float(margin_hop1), margin_single_shot=float(margin_single),
        margin_requery=float(margin_requery), audit=audit,
    )


def causal_hand_edit(codebook: np.ndarray, hop2_store: np.ndarray, result: LoopResult,
                     edited_bridge_id: int) -> Dict[str, object]:
    """Hand-edit the logged hop-1 bridge to a different id and re-run the downstream hop-2 recompute.

    The glass-box demonstration (monitor-not-control): editing the load-bearing logged step changes
    the recomputed downstream answer AND breaks the committed Merkle root.

    Returns:
        {"answer_flipped": bool,          # recomputed answer differs from the committed WM re-query
         "tamper_flag_fired": bool,       # the edited step-list no longer reproduces the root
         "recomputed_answer": int}        # the downstream answer under the edited bridge
    """
    recomputed_id, margin_re = cleanup_with_margin(bsc_bind(codebook[edited_bridge_id], hop2_store),
                                                   codebook)
    answer_flipped = bool(recomputed_id != result.requery_answer)
    edited_steps = list(result.audit.steps)
    edited_steps[1] = "hop1_retrieve(bridge=%d,margin1=%.4f)" % (edited_bridge_id, result.margin_hop1)
    edited_steps[3] = "hop2_requery(bridge_used=%d,ansB=%d,marginB=%.4f)" % (
        edited_bridge_id, recomputed_id, margin_re)
    tamper_flag_fired = result.audit.tamper_detect(edited_steps)
    return {"answer_flipped": answer_flipped, "tamper_flag_fired": tamper_flag_fired,
            "recomputed_answer": int(recomputed_id)}


# ============================================================================
# formula selftests (import-safe: run only under __main__, NOT at import time).
# ============================================================================
def _build_toy_trial(codebook: np.ndarray, node_ids: Sequence[int], m_store: int,
                     easy: bool, rng: np.random.Generator) -> Dict[str, object]:
    """Build one weak-first toy trial (hop1 anchor->bridge store; hop2 answer store).

    EASY: answer keyed by the anchor (single shot resolves). HARD: answer keyed by the bridge
    (single shot lands on noise; only a WM-mediated re-query resolves it)."""
    ids = list(node_ids)
    anchor_id, bridge_id, bridge_d_id, ans_id, wrong_id = ids[:5]
    pool = ids[5:]
    anchor = codebook[anchor_id]

    hop1 = bsc_bind(anchor, codebook[bridge_id]).copy()
    di = 0
    for _ in range(m_store - 1):
        hop1 = hop1 + bsc_bind(codebook[pool[di]], codebook[pool[di + 1]]); di += 2

    if easy:
        hop2 = bsc_bind(anchor, codebook[ans_id]).copy()
    else:
        hop2 = bsc_bind(codebook[bridge_id], codebook[ans_id]).copy()
    hop2 = hop2 + bsc_bind(codebook[bridge_d_id], codebook[wrong_id])
    for _ in range(max(0, m_store - 2)):
        hop2 = hop2 + bsc_bind(codebook[pool[di]], codebook[pool[di + 1]]); di += 2

    rand_bridge_id = int(pool[di])
    return {"anchor_id": anchor_id, "bridge_id": bridge_id, "ans_id": ans_id,
            "rand_bridge_id": rand_bridge_id, "easy": easy,
            "hop1": hop1.astype(np.float32), "hop2": hop2.astype(np.float32)}


def _selftest() -> None:
    """Formula self-tests: (1) merkle chains + tamper; (2) bsc_bind self-inverse; (3) weak-first
    regime fires (single-shot fails HARD, WM re-query resolves); (4) causal edit flips + tamper fires;
    (5) deterministic replay."""
    tau = 0.30
    # (1) Merkle chains + tamper
    r = merkle_root(["a", "b", "c"])
    assert merkle_verify(["a", "b", "c"], r), "merkle verify"
    assert not merkle_verify(["a", "b", "X"], r), "tamper detected"
    assert merkle_root(["a"]) != sha256_bytes(b"genesis"), "merkle chains beyond genesis"

    # (2) bsc_bind is self-inverse for bipolar
    rng = np.random.default_rng(0)
    E = make_codebook(16, 256, rng)
    x, k = E[3], E[5]
    assert np.array_equal(bsc_bind(k, bsc_bind(k, x)), x), "bsc_bind self-inverse"

    # (3)+(4)+(5) weak-first regime on a tiny toy
    E = make_codebook(48, 1024, np.random.default_rng(1))
    node_ids = list(np.random.default_rng(2).choice(48, size=5 + 4 * 6, replace=False))
    tr = _build_toy_trial(E, node_ids, 6, easy=False, rng=np.random.default_rng(2))
    res = glass_box_reason(E, tr["hop1"], tr["hop2"], tr["anchor_id"], tau=tau)
    assert res.margin_single_shot < tau, "HARD single-shot margin below gate (weak-first fires)"
    assert res.bridge_hat_id == tr["bridge_id"], "hop1 retrieves the correct bridge"
    assert res.requery_answer == tr["ans_id"], "WM re-query resolves HARD"
    assert not res.go, "HARD trial routed NoGo (re-query)"
    assert res.committed_answer == tr["ans_id"], "committed answer correct on HARD via re-query"
    assert res.single_shot_answer != tr["ans_id"], "single shot fails HARD (discriminator fires)"
    assert res.audit.verify(), "audit root verifies"

    ce = causal_hand_edit(E, tr["hop2"], res, edited_bridge_id=tr["rand_bridge_id"])
    assert ce["tamper_flag_fired"], "causal hand-edit fires tamper flag"
    assert ce["answer_flipped"], "causal hand-edit flips downstream answer"

    res2 = glass_box_reason(E, tr["hop1"], tr["hop2"], tr["anchor_id"], tau=tau)
    assert res2.audit.root == res.audit.root, "deterministic replay: identical Merkle root"
    assert res2.committed_answer == res.committed_answer, "deterministic replay: identical answer"

    # easy single-shot resolves with high margin (gate commits the shot)
    node_ids_e = list(np.random.default_rng(3).choice(48, size=5 + 4 * 6, replace=False))
    tre = _build_toy_trial(E, node_ids_e, 6, easy=True, rng=np.random.default_rng(3))
    rese = glass_box_reason(E, tre["hop1"], tre["hop2"], tre["anchor_id"], tau=tau)
    assert rese.margin_single_shot >= tau, "EASY single-shot margin above gate"
    assert rese.go, "EASY trial routed GO (commit shot)"
    assert rese.committed_answer == tre["ans_id"], "EASY single-shot resolves"

    print("[hdlab.glass_box_loop selftest] PASS: merkle+tamper, bsc-inverse, weak-first regime "
          "fires (single-shot fails HARD, WM re-query resolves), causal edit flips + tamper, "
          "deterministic replay", flush=True)


if __name__ == "__main__":
    _selftest()
