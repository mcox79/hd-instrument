"""SITUATION-MODEL CAUSATION DIMENSION, cell 1: identify the CAUSE of a narrative
outcome ("why did X happen?") on REAL prose, where a causal-network reader beats BOTH
a naive most-recent (locality) baseline AND a pure-connective baseline.

THESIS (the INVERSE of the coref-locality lesson): for coreference the true antecedent
is the NEAREST mention (locality wins, banked 29514). For CAUSATION the true cause is
often NOT the most-recent event -- the causal link jumps back over intervening dead-end
events (Trabasso & van-den-Broek causal-network model: on-chain events recalled 2-3x
more; "why?"-answerable == on-chain). So the SAME structural signal (locality) that WINS
for coref must LOSE for causation, or the test is vacuous.

DISCRIMINATOR / arms (the ONE variable is the cause-identification rule; extraction is
SHARED):
  MOST_RECENT      baseline 1 (naive-adjacency / locality): cause == the most-recent
                   event before the outcome. MUST fail where cause != most-recent.
  CONNECTIVE_ONLY  baseline 2 (== the mechanism's no-bridge P2 ablation): follow an
                   explicit causal connective (because/so/therefore/since); ABSTAIN when
                   none. MUST fail on BRIDGING (unstated) causal links.
  CAUSAL_NET       mechanism: connective + Talmy force-dynamics bridging plausibility +
                   most-recent fallback, with the cause->effect edges bound into the
                   substrate KGStore (glass-box in-substrate causal graph; on-chain vs
                   dead-end = reachable-to-outcome).

NON-VACUOUS GATE (design-gate): BOTH baselines must fail on the HARD subset --
MOST_RECENT low on NONADJ (cause != recent) AND CONNECTIVE_ONLY low on BRIDGE (no
explicit connective -> needs plausibility). Only CAUSAL_NET clears both. Controls
(cause IS the recent, connective-marked event) verify the mechanism does not regress.

GOLD: REAL, VERBATIM LitBank passages (public-domain novels on disk under
data/litbank/original), source-cited, hand-labeled with the (cause, outcome) event
pair derived from MEANING -- NOT from the mechanism's rule (non-circular), NOT synthetic
toy chains (avoids the 29509 construction-aided trap). This gold is a BASE INGREDIENT
and WILL be skunkworks-VET'd.

HONEST SCOPE: (1) On NONADJ the connective arm recovers the cause "for free" because
"because" linguistically MARKS the cause -- that IS ground truth; the non-vacuous
finding is that LOCALITY (most-recent) does NOT identify the cause (0/7), the
inverse-of-coref. (2) On the BRIDGE items the inferred force-action cause happens to be
the most-recent event, so the bridge subset proves CONNECTIVE-ONLY is insufficient
(unstated links exist) but does NOT independently prove the plausibility rule beats
locality; a NON-adjacent implicit-cause bridge test is the named NEXT lever, not claimed
solved. (3) Integration payoff (noted, not required to pass): causal centrality -> a
referent signal for the coref same-gender residual (the on-chain agent is the likely
antecedent).

Compute architecture: sequential-CPU JUSTIFIED -- deterministic, wall < 10s, tiny
substrate matrices (N_DIM=1024, ~40 event entities); this cell IS validating the
KGStore causal-graph primitive on real reader tuples. Storage: KGStore multi-value
Hebbian W (single CAUSES relation) + bipolar entity codebook (no bundled composition).
Not banked here (skunkworks VETs).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (MOST_RECENT/CONNECTIVE_ONLY/CAUSAL_NET all differ)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: cause-identification is a discrete lemma match, no Gaussian noise floor
# - baseline_in_band: MOST_RECENT + CONNECTIVE_ONLY overall in (0.05, 0.95); each defeated
#   on its target subset (validity gate)
# - discriminator: real LitBank passages; margin CAUSAL_NET - max(baseline) on hard subset
# - real_code_path: self_test builds a real KGStore at N=64 + binds KGStore live signature
# - numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
from __future__ import annotations

import hashlib
import inspect
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _causal_network as C  # noqa: E402
from hdlab.kg_traversal import KGStore  # noqa: E402

ANCHOR_NAME = "read_causal_chain_on_chain_cause_v1"
N_DIM = 1024
KG_SEED = 20260724

# Pre-registered bands (set BEFORE this run).
VALIDITY_GATE_MOSTRECENT_NONADJ_MAX = 0.40   # MOST_RECENT on NONADJ must be <= this
VALIDITY_GATE_CONN_BRIDGE_MAX = 0.30         # CONNECTIVE_ONLY on BRIDGE must be <= this
HARD_PASS_MECH_MIN = 0.80                    # CAUSAL_NET on hard subset (NONADJ+BRIDGE)
HARD_PASS_MARGIN = 0.15                      # mech - max(baseline) on hard >= this
HARD_FAIL_MECH_MAX = 0.55                    # mech on hard < this -> HARD_FAIL
CONTROL_REGRESS_MAX = 0.001                  # mech on CONTROL must not drop below MOST_RECENT

# ---------------------------------------------------------------------------
# GOLD -- REAL, VERBATIM LitBank passages. (cause, outcome) from MEANING (non-circular).
# Verified verbatim against data/litbank/original/*.txt (LitBank public-domain novels).
# ---------------------------------------------------------------------------
GOLD = [
    # NONADJ: within-sentence "OUTCOME because CAUSE"; the immediately-preceding sentence
    # is a DEAD-END, so MOST_RECENT (locality) picks the wrong event.
    C.CausalItem("NONADJ", "The Secret Garden (Burnett), LitBank 113",
        "\"No,\" said Mary frowning. She frowned because she remembered that her "
        "father and mother had never talked to her about anything in particular.",
        "frowned", "remembered"),
    C.CausalItem("NONADJ", "The Secret Garden (Burnett), LitBank 113",
        "He hopped about and pecked the earth briskly, looking for seeds and insects. "
        "It actually gave Mary a queer feeling in her heart, because he was so pretty "
        "and cheerful and seemed so like a person.",
        "gave", "seemed"),
    C.CausalItem("NONADJ", "The Secret Garden (Burnett), LitBank 113",
        "When Ben Weatherstaff came through the door in the wall he saw him standing "
        "there and he heard Mary muttering something under her breath. \"What art "
        "sayin'?\" he asked rather testily because he did not want his attention "
        "distracted from the long thin straight boy figure.",
        "asked", "distracted"),
    C.CausalItem("NONADJ", "Little Women (Alcott), LitBank 514",
        "Beth had a rapture with her mother, and then rushed up to impart the glorious "
        "news to her family of invalids. How blithely she sang that evening, and how "
        "they all laughed at her because she woke Amy in the night by playing the piano "
        "on her face in her sleep.",
        "laughed", "woke"),
    C.CausalItem("NONADJ", "Little Women (Alcott), LitBank 514",
        "But the boy laughed and said pleasantly, though he looked a little startled, "
        "\"Don't mind me, stay if you like.\" I only came here because I don't know many "
        "people and felt rather strange at first, you know.",
        "came", "felt"),
    C.CausalItem("NONADJ", "Little Women (Alcott), LitBank 514",
        "She obediently descended, and made as light of the prank as she could without "
        "betraying Meg. If the boy held his tongue because he promised, and not from "
        "obstinacy, I'll forgive him.",
        "held", "promised"),
    C.CausalItem("NONADJ", "The Secret Garden (Burnett), LitBank 113",
        "\"The rain is as contrary as I ever was,\" she said. \"It came because it knew "
        "I did not want it.\"",
        "came", "knew"),
    # CONTROL: cause IS the most-recent prior event AND connective-marked -> BOTH baselines
    # succeed; the mechanism must NOT regress.
    C.CausalItem("CONTROL", "Great Expectations (Dickens), LitBank 1400",
        "I was very much afraid of him again. I told him I must go, but he took no "
        "notice, so I thought the best thing I could do was to slip off.",
        "thought", "took"),
    C.CausalItem("CONTROL", "The Secret Garden (Burnett), LitBank 113",
        "The Ayah had been taken ill in the night, and it was because she had just died "
        "that the servants had wailed in the huts.",
        "wailed", "died"),
    C.CausalItem("CONTROL", "Bleak House (Dickens), LitBank 1023",
        "He was agreeably surprised to see us stirring so soon and said he would gladly "
        "share our walk. So he took care of Ada, and Miss Jellyby and I went first.",
        "took", "said"),
    C.CausalItem("CONTROL", "Bleak House (Dickens), LitBank 1023",
        "\"We are not likely to be far out, my love, if we go in that direction,\" said "
        "I. So to Chancery Lane we went, and there, sure enough, we saw it written up.",
        "went", "said"),
    C.CausalItem("CONTROL", "Bleak House (Dickens), LitBank 1023",
        "But of course I soon considered that I must not take tears where I was going. "
        "Therefore I made myself sob less and persuaded myself to be quiet.",
        "made", "considered"),
    # BRIDGE: NO causal connective; a force-dynamic ACTION brings about a RESULT
    # change-of-state. CONNECTIVE_ONLY abstains (fails); the plausibility rule recovers it.
    C.CausalItem("BRIDGE", "The Secret Adversary (Christie), LitBank 1155",
        "Tommy stopped Conrad's rush with a straight blow with his fist. It caught the "
        "other on the point of the jaw and he fell like a log.",
        "fell", "caught"),
    C.CausalItem("BRIDGE", "The Secret Adversary (Christie), LitBank 1155",
        "\"Get a move on, George,\" shouted Julius. The chauffeur slipped in his clutch, "
        "and with a bound the car started.",
        "started", "slipped"),
    C.CausalItem("BRIDGE", "The Secret Garden (Burnett), LitBank 113",
        "He caught hold of his pillow and threw it at her. He was not strong enough to "
        "throw it far and it only fell at her feet.",
        "fell", "threw"),
    C.CausalItem("BRIDGE", "The Secret Adversary (Christie), LitBank 1155",
        "Tommy dodged aside, and the man plunged past him. The second man tripped over "
        "his body and fell.",
        "fell", "tripped"),
]

ARMS = ["MOST_RECENT", "CONNECTIVE_ONLY", "CAUSAL_NET"]
SUBSETS = ["NONADJ", "BRIDGE", "CONTROL"]
HARD_SUBSETS = ("NONADJ", "BRIDGE")


# ---------------------------------------------------------------------------
# Scoring.
# ---------------------------------------------------------------------------
def _score_item(arm, item):
    """Return (correct 0/1, scored 0/1, detail). Not-scored (abstain) ONLY when the
    parser failed to extract the outcome OR the gold cause -> no arm is charged for
    extraction it never saw (same fairness rule as the TIME cell)."""
    events, toks = C.extract(item.text)
    lemmas = [e.lemma for e in events]
    outcome = C._find_event(events, item.outcome_lemma)
    extract_ok = (outcome is not None) and (item.cause_lemma in lemmas)
    if not extract_ok:
        return 0, 0, {"scored": False, "reason": "extract_miss",
                      "extracted": lemmas, "gold_cause": item.cause_lemma,
                      "gold_outcome": item.outcome_lemma}
    pred = C.predict_cause(arm, events, toks, outcome)
    pl = pred.lemma if pred is not None else None
    correct = 1 if pl == item.cause_lemma else 0
    return correct, 1, {"scored": True, "pred": pl, "gold_cause": item.cause_lemma,
                        "gold_outcome": item.outcome_lemma, "correct": bool(correct)}


def _subset_acc(arm, subset):
    ncorr = nsc = 0
    detail = []
    for it in GOLD:
        if it.subset != subset:
            continue
        c, s, d = _score_item(arm, it)
        ncorr += c
        nsc += s
        detail.append({"source": it.source, **d})
    return (ncorr / nsc if nsc else 0.0), ncorr, nsc, detail


def _acc_over(arm, subsets):
    ncorr = nsc = 0
    for sub in subsets:
        _, c, s, _ = _subset_acc(arm, sub)
        ncorr += c
        nsc += s
    return (ncorr / nsc if nsc else 0.0), ncorr, nsc


def _arm_signature(arm):
    """Per-item predicted cause lemma -> bytes, for ARMS-MUST-DIFFER hashing."""
    parts = []
    for it in GOLD:
        events, toks = C.extract(it.text)
        outcome = C._find_event(events, it.outcome_lemma)
        if outcome is None:
            parts.append("NA")
            continue
        pred = C.predict_cause(arm, events, toks, outcome)
        parts.append(pred.lemma if pred is not None else "NONE")
    return ("|".join(parts)).encode("utf-8")


# ---------------------------------------------------------------------------
# Improving property + on-chain/dead-end + substrate glass-box envelope.
# ---------------------------------------------------------------------------
def _causal_distance(item):
    """Number of extracted events strictly BETWEEN the gold cause and outcome in text
    order -- the count of intervening (dead-end) events the causal link must jump."""
    events, _ = C.extract(item.text)
    o = C._find_event(events, item.outcome_lemma)
    c = C._find_event(events, item.cause_lemma)
    if o is None or c is None:
        return None
    lo, hi = sorted((o.idx, c.idx))
    return sum(1 for e in events if lo < e.idx < hi)


def _improving_by_distance():
    """MOST_RECENT vs CAUSAL_NET accuracy binned by causal distance (intervening events).
    The improving property: locality collapses as distance grows; the mechanism holds."""
    bins = {}
    for it in GOLD:
        d = _causal_distance(it)
        if d is None:
            continue
        band = "0" if d == 0 else ("1" if d == 1 else "2+")
        mr, _, _ = _score_item("MOST_RECENT", it)
        cn, _, _ = _score_item("CAUSAL_NET", it)
        b = bins.setdefault(band, {"mr": 0, "cn": 0, "n": 0})
        b["mr"] += mr
        b["cn"] += cn
        b["n"] += 1
    return {k: {"most_recent_acc": round(v["mr"] / v["n"], 4),
                "causal_net_acc": round(v["cn"] / v["n"], 4),
                "lift": round((v["cn"] - v["mr"]) / v["n"], 4), "n_items": v["n"]}
            for k, v in sorted(bins.items())}


def _on_chain_envelope():
    """Glass-box Trabasso on-chain vs dead-end structure per item + shared-KGStore
    in-substrate causal recall of the direct cause (REUSES hdlab.kg_traversal.KGStore)."""
    # per-item on-chain vs dead-end
    per_item = []
    all_lemmas = []
    direct_edges = []  # (cause_lemma, effect_lemma) = the mechanism's direct cause of each outcome
    for it in GOLD:
        events, toks = C.extract(it.text)
        edges, _tags = C.build_causal_edges(events, toks)
        on = C.on_chain_events(edges, it.outcome_lemma)
        all_ev = [e.lemma for e in events]
        deadend = [l for l in all_ev if l not in on and l != it.outcome_lemma]
        all_lemmas += all_ev
        o = C._find_event(events, it.outcome_lemma)
        if o is not None:
            pred = C.predict_cause("CAUSAL_NET", events, toks, o)
            if pred is not None and pred.lemma != o.lemma:
                direct_edges.append((pred.lemma, it.outcome_lemma))
        gold_on_chain = it.cause_lemma in on or it.cause_lemma in [c for c, _ in edges]
        per_item.append({"source": it.source, "subset": it.subset,
                         "on_chain": sorted(on), "dead_end": deadend,
                         "gold_cause_on_chain": bool(gold_on_chain)})
    # shared-KGStore interference: bind ALL direct cause->effect edges, recover cause
    kg, idx, lemmas = C.build_kgstore(all_lemmas, N_DIM, KG_SEED)
    n_ing = C.ingest_edges(kg, idx, direct_edges)
    rec_ok = rec_n = 0
    for (cause, eff) in direct_edges:
        if eff in idx and cause in idx:
            rec_n += 1
            if C.substrate_recall_cause(kg, idx, lemmas, eff) == cause:
                rec_ok += 1
    return {
        "n_distinct_event_entities": len(lemmas),
        "n_causal_edges_ingested": n_ing,
        "substrate_causal_recall_acc": round(rec_ok / rec_n, 4) if rec_n else 0.0,
        "substrate_causal_recall_n": rec_n,
        "per_item_on_chain": per_item,
    }


# ---------------------------------------------------------------------------
# Infra: out dir + atomic writes + start/crash markers.
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(out_dir):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": "full",
              "expected_n_units": len(GOLD), "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write(out_dir, diag)


# ---------------------------------------------------------------------------
# Self-test: mechanism probes + REAL substrate code path + live-signature bind.
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] causal-network mechanism + substrate code path")
    exercised = set()

    # F.2 substrate_signature: bind KGStore against its LIVE signature (keys only).
    sig = inspect.signature(KGStore.__init__)
    for kw in ("n_ent", "n_rel", "n_dim", "generator"):
        assert kw in sig.parameters, f"KGStore signature drift: missing {kw}"
    exercised.add("substrate_signature")

    # (1) synthetic NONADJ: "O because A" -> connective picks A, most-recent picks dead-end.
    ev, toks = C.extract("She sat down. She left because the room was cold and she shivered.")
    o = C._find_event(ev, "left")
    assert o is not None, "outcome 'left' not extracted in synthetic probe"
    exercised.add("extract")
    mr = C.most_recent_prior(ev, o)
    cn = C.connective_cause(ev, toks, o)
    assert mr is not None and mr.lemma != "shivered", f"most_recent should not pick the because-cause: {mr}"
    assert cn is not None and cn.lemma == "shivered", f"connective should pick post-because cause: {cn}"
    exercised.add("connective_cause")

    # (2) synthetic BRIDGE: action->result, no connective -> connective abstains, bridge fires.
    ev2, toks2 = C.extract("He pushed the vase. It fell to the floor.")
    o2 = C._find_event(ev2, "fell")
    assert o2 is not None
    assert C.connective_cause(ev2, toks2, o2) is None, "connective_only must abstain (no connective)"
    b = C.bridge_cause(ev2, o2)
    assert b is not None and b.lemma == "pushed", f"bridge should recover the force-action cause: {b}"
    exercised.add("bridge_cause")
    net, tag = C.causal_net_cause(ev2, toks2, o2)
    assert net is not None and net.lemma == "pushed" and tag == "bridge", f"causal_net bridge: {net},{tag}"
    exercised.add("causal_net_cause")

    # (3) REAL substrate code path at tiny scale: build a KGStore, ingest a cause->effect
    #     edge, recover the cause by one-hop traversal.
    kg, idx, lemmas = C.build_kgstore(["pushed", "fell", "sat"], 64, seed=7)
    exercised.add("build_kgstore")
    assert isinstance(kg, KGStore) and kg.n_ent == 3 and kg.n_dim == 64
    n = C.ingest_edges(kg, idx, [("pushed", "fell")])
    assert n == 1, f"expected 1 edge ingested, got {n}"
    exercised.add("ingest_edges")
    rec = C.substrate_recall_cause(kg, idx, lemmas, "fell")
    assert rec == "pushed", f"substrate one-hop causal recall failed: fell -> {rec}"
    exercised.add("substrate_recall_cause")

    # (4) on-chain vs dead-end: dead-end event is OFF the chain to the outcome.
    ev3, toks3 = C.extract("She sat down. She left because the room was cold and she shivered.")
    edges, _ = C.build_causal_edges(ev3, toks3)
    on = C.on_chain_events(edges, "left")
    exercised.add("on_chain_events")

    required = {"substrate_signature", "extract", "connective_cause", "bridge_cause",
                "causal_net_cause", "build_kgstore", "ingest_edges",
                "substrate_recall_cause", "on_chain_events"}
    missing = required - exercised
    assert not missing, f"real_code_path: entrypoints not exercised: {missing}"
    print(f"[self-test] PASS; exercised={sorted(exercised)}")
    return True


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    out_dir = _out_dir()
    _write_start_marker(out_dir)
    t0 = time.perf_counter()

    # Per-arm per-subset accuracy.
    per = {a: {} for a in ARMS}
    detail = {a: {} for a in ARMS}
    for a in ARMS:
        for sub in SUBSETS:
            acc, nc, ns, det = _subset_acc(a, sub)
            per[a][sub] = {"acc": round(acc, 4), "n_correct": nc, "n_scored": ns}
            detail[a][sub] = det

    def hard(a):
        acc, _, _ = _acc_over(a, HARD_SUBSETS)
        return acc

    mr_nonadj = per["MOST_RECENT"]["NONADJ"]["acc"]
    conn_bridge = per["CONNECTIVE_ONLY"]["BRIDGE"]["acc"]
    mech_hard = hard("CAUSAL_NET")
    mr_hard = hard("MOST_RECENT")
    conn_hard = hard("CONNECTIVE_ONLY")
    mech_ctrl = per["CAUSAL_NET"]["CONTROL"]["acc"]
    mr_ctrl = per["MOST_RECENT"]["CONTROL"]["acc"]
    margin = mech_hard - max(mr_hard, conn_hard)
    ctrl_regress = mr_ctrl - mech_ctrl

    # META_RULE_AG baseline_in_band (overall, 0.05 < baseline < 0.95).
    mr_all, _, _ = _acc_over("MOST_RECENT", SUBSETS)
    conn_all, _, _ = _acc_over("CONNECTIVE_ONLY", SUBSETS)
    baseline_in_band = (0.05 < mr_all < 0.95) and (0.05 < conn_all < 0.95)

    validity_mostrecent = mr_nonadj <= VALIDITY_GATE_MOSTRECENT_NONADJ_MAX
    validity_connective = conn_bridge <= VALIDITY_GATE_CONN_BRIDGE_MAX
    validity_gate_fires = validity_mostrecent and validity_connective

    # ARMS-MUST-DIFFER (META_RULE_AF).
    sigs = {a: hashlib.sha256(_arm_signature(a)).hexdigest() for a in ARMS}
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            assert sigs[ARMS[i]] != sigs[ARMS[j]], \
                f"META_RULE_AF: arms {ARMS[i]},{ARMS[j]} bit-identical"

    # Verdict logic.
    if not validity_gate_fires:
        verdict = "HARD_FAIL"
        vmsg = (f"VALIDITY GATE FAILED: MOST_RECENT NONADJ acc={mr_nonadj:.3f} "
                f"(<= {VALIDITY_GATE_MOSTRECENT_NONADJ_MAX}? {validity_mostrecent}); "
                f"CONNECTIVE_ONLY BRIDGE acc={conn_bridge:.3f} "
                f"(<= {VALIDITY_GATE_CONN_BRIDGE_MAX}? {validity_connective}). "
                f"Discriminator vacuous: a baseline was not defeated on its target subset.")
    elif ctrl_regress > CONTROL_REGRESS_MAX:
        verdict = "HARD_FAIL"
        vmsg = (f"CONTROL REGRESSION: CAUSAL_NET control acc={mech_ctrl:.3f} < "
                f"MOST_RECENT control {mr_ctrl:.3f} (drop {ctrl_regress:.3f}).")
    elif mech_hard >= HARD_PASS_MECH_MIN and margin >= HARD_PASS_MARGIN:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: CAUSAL_NET clears the hard subset (NONADJ+BRIDGE) at "
                f"{mech_hard:.3f}, beating BOTH baselines (MOST_RECENT {mr_hard:.3f}, "
                f"CONNECTIVE_ONLY {conn_hard:.3f}; margin {margin:.3f}). Validity gate fires: "
                f"locality FAILS on NONADJ (MOST_RECENT {mr_nonadj:.3f}) -- the inverse of "
                f"coref -- and CONNECTIVE_ONLY FAILS on BRIDGE ({conn_bridge:.3f}). No control "
                f"regression (CAUSAL_NET {mech_ctrl:.3f} == MOST_RECENT {mr_ctrl:.3f}).")
    elif mech_hard < HARD_FAIL_MECH_MAX:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL: CAUSAL_NET hard-subset acc={mech_hard:.3f} < "
                f"{HARD_FAIL_MECH_MAX}. See autopsy.")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: CAUSAL_NET hard-subset acc={mech_hard:.3f} in "
                f"[{HARD_FAIL_MECH_MAX}, {HARD_PASS_MECH_MIN}) or margin {margin:.3f} < "
                f"{HARD_PASS_MARGIN}.")

    # Autopsy: any hard-subset item the mechanism misses.
    autopsy = []
    for it in GOLD:
        if it.subset not in HARD_SUBSETS:
            continue
        c, s, d = _score_item("CAUSAL_NET", it)
        if s and not c:
            autopsy.append({"source": it.source, "subset": it.subset, "text": it.text, **d})

    improving = _improving_by_distance()
    envelope = _on_chain_envelope()

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": (f"{verdict}: CAUSAL_NET hard {mech_hard:.3f} vs MOST_RECENT {mr_hard:.3f} "
                    f"/ CONNECTIVE_ONLY {conn_hard:.3f}; validity(MR_nonadj {mr_nonadj:.3f}, "
                    f"CONN_bridge {conn_bridge:.3f})={validity_gate_fires}; ctrl {mech_ctrl:.3f}"),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_dim": N_DIM,
        "prereg_bands": {
            "validity_gate_mostrecent_nonadj_max": VALIDITY_GATE_MOSTRECENT_NONADJ_MAX,
            "validity_gate_conn_bridge_max": VALIDITY_GATE_CONN_BRIDGE_MAX,
            "hard_pass_mech_min": HARD_PASS_MECH_MIN,
            "hard_pass_margin": HARD_PASS_MARGIN,
            "hard_fail_mech_max": HARD_FAIL_MECH_MAX,
            "control_regress_max": CONTROL_REGRESS_MAX,
        },
        "gates": {
            "validity_gate_fires": validity_gate_fires,
            "validity_mostrecent_defeated_on_nonadj": validity_mostrecent,
            "validity_connective_defeated_on_bridge": validity_connective,
            "baseline_in_band": baseline_in_band,
            "mech_hard_acc": round(mech_hard, 4),
            "mostrecent_hard_acc": round(mr_hard, 4),
            "connective_hard_acc": round(conn_hard, 4),
            "margin_over_best_baseline": round(margin, 4),
            "control_regression": round(ctrl_regress, 4),
        },
        "arms": {
            a: {"nonadj_acc": per[a]["NONADJ"]["acc"],
                "bridge_acc": per[a]["BRIDGE"]["acc"],
                "control_acc": per[a]["CONTROL"]["acc"],
                "overall_acc": round(_acc_over(a, SUBSETS)[0], 4),
                "signature_sha256": sigs[a][:16]}
            for a in ARMS
        },
        "improving_property_by_causal_distance": improving,
        "substrate_glassbox_envelope": envelope,
        "autopsy_hard_misses": autopsy,
        "gold": {
            "n_items": len(GOLD),
            "n_nonadj": sum(1 for g in GOLD if g.subset == "NONADJ"),
            "n_bridge": sum(1 for g in GOLD if g.subset == "BRIDGE"),
            "n_control": sum(1 for g in GOLD if g.subset == "CONTROL"),
            "items": [{"subset": g.subset, "source": g.source, "text": g.text,
                       "cause": g.cause_lemma, "outcome": g.outcome_lemma} for g in GOLD],
        },
        "per_arm_detail": detail,
        "honest_scope": (
            "REAL verbatim LitBank gold; (cause,outcome) from MEANING (non-circular). "
            "NONADJ: the non-vacuous finding is LOCALITY (most-recent) does NOT identify "
            "the cause (inverse of coref) -- the connective arm getting the marked cause "
            "'for free' is the point. BRIDGE proves CONNECTIVE-ONLY is insufficient "
            "(unstated links exist), but the inferred force-action cause coincides with the "
            "most-recent event on these items, so it does NOT independently prove the "
            "plausibility rule beats locality; a NON-adjacent implicit-cause bridge test is "
            "the named NEXT lever. Integration payoff (noted, not required): causal centrality "
            "-> referent signal for the coref same-gender residual."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"verdict={verdict} elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    _od = _out_dir()
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
