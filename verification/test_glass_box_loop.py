"""Scaffold-free witness for the glass-box self-auditing reasoning loop in hdlab.glass_box_loop.

Reproduces the CHAIN_GRADE certified properties in miniature (independent corpus built in-test):
  (1) the loop BEATS a single shot on a multi-hop task -- the discriminator FIRES: single-shot fails
      the HARD (bridge-keyed) trials near chance while the gated WM-requery resolves them,
  (2) a causal hand-edit of the logged bridge FLIPS the downstream recompute (log is load-bearing),
  (3) tamper is DETECTED and the Merkle root VERIFIES (any edited step breaks the committed root),
  (4) deterministic REPLAY (recomputing from the same inputs reproduces the answer + root).

Also checks a telemetry-sensitivity control (scramble re-query with a random bridge must NOT resolve)
so the resolution is attributable to the correct WM binding, not merely "a second try", and the
audit primitives directly (merkle_root / merkle_verify / AuditLog / sha256_bytes / go_nogo).

Passes with tracing=False (numpy-only; the loop touches no substrate tracing state).

Certified sources: exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1 (commit ba552930a),
exp_glass_box_micro_loop_conceptnet_multihop_v1 / _SCALE_v1 (real ConceptNet + 80x scale),
Merkle audit transcribed from exp_reasoning_chain_replay_v1 (HARD_PASS).
"""
from __future__ import annotations

import numpy as np

from hdlab.glass_box_loop import (
    AuditLog, bsc_bind, causal_hand_edit, cleanup_with_margin, glass_box_reason, go_nogo,
    make_codebook, merkle_root, merkle_verify, sha256_bytes,
)

N_DIM = 4096            # == the certified base-cell FULL N (discriminator preview at full scale)
V_NODES = 128           # concepts in the per-seed codebook (>= 5 + 4*M_STORE distinct ids per trial)
M_STORE = 20            # items per hop bundle (certified full config)
TAU = 0.30              # a-priori between the HARD noise-floor margin (~0.07) and EASY clean (~0.9)
SEEDS = (7, 17, 23)
N_TRIALS = 24           # per seed; balanced easy/hard


def _build_trial(E: np.ndarray, node_ids, easy: bool):
    """One weak-first trial over codebook E. EASY: answer keyed by the anchor (single shot resolves).
    HARD: answer keyed by the bridge (single shot lands on noise; only a WM re-query resolves it)."""
    ids = list(int(x) for x in node_ids)
    anchor_id, bridge_id, bridge_d_id, ans_id, wrong_id = ids[:5]
    pool = ids[5:]

    hop1 = bsc_bind(E[anchor_id], E[bridge_id]).copy()
    di = 0
    for _ in range(M_STORE - 1):
        hop1 = hop1 + bsc_bind(E[pool[di]], E[pool[di + 1]]); di += 2

    hop2 = (bsc_bind(E[anchor_id], E[ans_id]) if easy else bsc_bind(E[bridge_id], E[ans_id])).copy()
    hop2 = hop2 + bsc_bind(E[bridge_d_id], E[wrong_id])           # trap: wrong bridge -> wrong answer
    for _ in range(max(0, M_STORE - 2)):
        hop2 = hop2 + bsc_bind(E[pool[di]], E[pool[di + 1]]); di += 2

    rand_bridge_id = int(pool[di])
    return {"anchor_id": anchor_id, "bridge_id": bridge_id, "ans_id": ans_id,
            "rand_bridge_id": rand_bridge_id, "easy": bool(easy),
            "hop1": hop1.astype(np.float32), "hop2": hop2.astype(np.float32)}


def _run_seed(seed: int):
    rng = np.random.default_rng(seed)
    E = make_codebook(V_NODES, N_DIM, rng)
    n_needed = 5 + 4 * M_STORE
    assert n_needed <= V_NODES, "not enough distinct nodes for a trial"

    easy_flags = [True] * (N_TRIALS // 2) + [False] * (N_TRIALS - N_TRIALS // 2)
    rng.shuffle(easy_flags)

    accA = accB = accScr = 0
    accA_hard = 0
    n_hard = 0
    det_ok = tamper_ok = verify_ok = 0
    causal_flip = causal_tamper = n_causal = 0

    for easy in easy_flags:
        node_ids = rng.choice(V_NODES, size=n_needed, replace=False)
        tr = _build_trial(E, node_ids, bool(easy))

        res = glass_box_reason(E, tr["hop1"], tr["hop2"], tr["anchor_id"], tau=TAU)

        # arm accuracies
        accA += int(res.single_shot_answer == tr["ans_id"])
        accB += int(res.committed_answer == tr["ans_id"])
        # scramble control: gated, but re-query with a RANDOM bridge instead of the WM active slot
        scr_id, _ = cleanup_with_margin(bsc_bind(E[tr["rand_bridge_id"]], tr["hop2"]), E)
        scr_ans = res.single_shot_answer if res.go else int(scr_id)
        accScr += int(scr_ans == tr["ans_id"])

        if not tr["easy"]:
            n_hard += 1
            accA_hard += int(res.single_shot_answer == tr["ans_id"])

        # (3) audit: verify + tamper (edit the committed-answer step -> root must break)
        verify_ok += int(res.audit.verify())
        tampered = list(res.audit.steps)
        tampered[4] = "commit(answer=%d)" % (res.committed_answer + 1)
        tamper_ok += int(res.audit.tamper_detect(tampered))

        # (4) deterministic replay
        res2 = glass_box_reason(E, tr["hop1"], tr["hop2"], tr["anchor_id"], tau=TAU)
        det_ok += int(res2.audit.root == res.audit.root
                      and res2.committed_answer == res.committed_answer)

        # (2) causal hand-edit on HARD trials the loop got correct
        if (not tr["easy"]) and res.committed_answer == tr["ans_id"]:
            ce = causal_hand_edit(E, tr["hop2"], res, edited_bridge_id=tr["rand_bridge_id"])
            n_causal += 1
            causal_flip += int(ce["answer_flipped"])
            causal_tamper += int(ce["tamper_flag_fired"])

    nt = N_TRIALS
    return {
        "accA": accA / nt, "accB": accB / nt, "accScr": accScr / nt,
        "accA_hard": (accA_hard / n_hard) if n_hard else 0.0,
        "det": det_ok / nt, "verify": verify_ok / nt, "tamper": tamper_ok / nt,
        "causal_flip": (causal_flip / n_causal) if n_causal else 0.0,
        "causal_tamper": (causal_tamper / n_causal) if n_causal else 0.0,
        "n_causal": n_causal,
    }


def test_property_1_loop_beats_single_shot_discriminator_fires():
    """(1) The gated WM-requery loop beats a single shot; the discriminator FIRES (single-shot fails
    the HARD multi-hop trials near chance). Averaged over seeds."""
    res = [_run_seed(s) for s in SEEDS]
    accA = float(np.mean([r["accA"] for r in res]))
    accB = float(np.mean([r["accB"] for r in res]))
    accA_hard = float(np.mean([r["accA_hard"] for r in res]))
    # discriminator fires: single-shot cannot solve the bridge-keyed multi-hop
    assert accA_hard <= 0.10, f"discriminator DEAD: single-shot solved HARD (accA_hard={accA_hard:.3f})"
    # loop resolves both easy + hard -> substantial lift over single shot
    assert accB - accA >= 0.25, f"loop did not beat single shot: accB={accB:.3f} accA={accA:.3f}"
    assert accB >= 0.90, f"loop did not resolve the mixed corpus: accB={accB:.3f}"


def test_property_1b_telemetry_sensitive_scramble_does_not_resolve():
    """Telemetry control: re-querying with a RANDOM bridge (scramble) collapses toward the single
    shot -- the resolution is attributable to the correct WM binding, not merely a second try."""
    res = [_run_seed(s) for s in SEEDS]
    accB = float(np.mean([r["accB"] for r in res]))
    accScr = float(np.mean([r["accScr"] for r in res]))
    assert accB - accScr >= 0.25, f"scramble resolved too (tautological): accB={accB:.3f} accScr={accScr:.3f}"


def test_property_2_causal_hand_edit_flips_recompute():
    """(2) Hand-editing the logged bridge flips the downstream recompute (log is causally load-bearing)."""
    res = [_run_seed(s) for s in SEEDS]
    assert sum(r["n_causal"] for r in res) > 0, "no HARD-correct trials to demonstrate causal edit"
    flip = float(np.mean([r["causal_flip"] for r in res]))
    assert flip >= 0.80, f"causal hand-edit did not flip the recompute: causal_flip={flip:.3f}"


def test_property_3_tamper_detected_and_merkle_verifies():
    """(3) The Merkle root verifies for every un-edited log and a tampered log is always detected."""
    res = [_run_seed(s) for s in SEEDS]
    verify = float(np.mean([r["verify"] for r in res]))
    tamper = float(np.mean([r["tamper"] for r in res]))
    assert verify == 1.0, f"audit root failed to verify: verify={verify:.3f}"
    assert tamper == 1.0, f"tamper not always detected: tamper={tamper:.3f}"


def test_property_4_deterministic_replay():
    """(4) Recomputing a trial from the same inputs reproduces the committed answer and Merkle root."""
    res = [_run_seed(s) for s in SEEDS]
    det = float(np.mean([r["det"] for r in res]))
    assert det == 1.0, f"replay not deterministic: det={det:.3f}"


def test_audit_primitives_directly():
    """The promoted audit primitives behave as a Merkle hash-chain: verify holds, any edit breaks it,
    the chain extends past genesis, and AuditLog wraps them faithfully."""
    steps = ["query(anchor=1)", "hop1_retrieve(bridge=2)", "commit(answer=3)"]
    root = merkle_root(steps)
    assert merkle_verify(steps, root)
    assert not merkle_verify(steps[:-1] + ["commit(answer=4)"], root)
    assert merkle_root(["a"]) != sha256_bytes(b"genesis")
    log = AuditLog(steps=list(steps), root=root)
    assert log.verify()
    assert log.tamper_detect(["query(anchor=9)"] + steps[1:])
    assert not log.tamper_detect(steps)              # unedited -> no tamper


def test_go_nogo_gate_threshold():
    """The Go/NoGo value-gate is a clean margin threshold: Go iff margin >= tau."""
    assert go_nogo(0.5, 0.3) is True
    assert go_nogo(0.3, 0.3) is True
    assert go_nogo(0.29, 0.3) is False
    assert go_nogo(0.0, 0.3) is False
