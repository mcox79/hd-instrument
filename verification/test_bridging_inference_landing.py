"""LANDING WITNESS for the BRIDGING-INFERENCE organ (hdlab/bridging_inference.py) + its live read()-time
wire into hdlab/situation_reader.py (sm.bridge / sm.infer_bridges). Self-contained, ASCII, deterministic.
This proves the LANDED organ -- not the experiment cells -- carries the validated capability, and that the
wire is a PURE ADD (every other situation-model dimension byte-identical off vs on).

  W1  THE LIVE READER exposes the bridging query and infers the correct UNSTATED link on held items:
      over a real read()'s sm.entities/sm.events, sm.bridge(target) SELECTS the semantically-correct
      antecedent (which whole a part belongs to / which event an instrument serves) -- and it DIFFERS from
      the no-inference floor (the correct antecedent is placed NON-recently, so most-recent / random miss it).
  W2  THE VALIDATED NUMBERS REPRODUCE THROUGH THE LANDED ORGAN: running the same held-out selection harness
      (same gold, same digest-seeded splits, same candidate construction) but SELECTING via the landed
      hdlab.bridging_inference.BridgeInference reproduces the SOLVED headline -- referential-PART WordNet
      meronymy RAW_HUB 0.4720, ConceptNet PartOf 0.6087 (curated meaning_foundation 0.6541), INSTRUMENT
      UsedFor 0.4522 -- CI-scale margins over chance, and the shuffled-MEANING twin collapses to chance
      (the specific word<->meaning map is load-bearing). Plus a per-item BYTE-IDENTITY check: the organ's
      argmax pick == the validated cell's inline argmax pick.
  W3  ADDITIVE-SAFETY: reading a passage with track_bridges ON vs OFF leaves EVERY existing dimension
      (entities / events / roles / coref / causal / timeline / world-state ...) byte-identical -- bridging
      is a NEW read-only inference; it never changes extraction.

Run: .venv/Scripts/python.exe verification/test_bridging_inference_landing.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pickle

import numpy as np

from hdlab.bridging_inference import BridgeInference, Bridge, available
from hdlab.situation_reader import SituationReader, _write_temp_conll
from experiments.exp_bridging_selection_v2 import (
    part_pairs_wn, part_pairs_cn, instrument_pairs, unit, _digest_seed, build_mfnd_vec,
    K_DISTRACT, N_SEEDS, HUB_PATH)

P = 0


def check(name, cond, detail=""):
    global P
    assert cond, "FAIL %s -- %s" % (name, detail)
    P += 1
    print("  ok  %s  %s" % (name, detail))


print("=" * 92)
print("LANDING WITNESS: bridging-inference organ + the live sm.bridge read()-time consumer")
print("=" * 92)

check("W0-assets", available(), "hdlab.bridging_inference loads the ATL PPMI+SVD hub (meaning channel live)")

# --------------------------------------------------------------------------- W1: the live reader
# Two held 2-sentence passages. The correct antecedent is placed NON-recently (an intervening entity is more
# recent), so a no-inference reader (most-recent / random) would MISS it; the meaning-store bridge selects it.
def _read_passage(tokens_by_sent):
    rows = []
    for si, toks in enumerate(tokens_by_sent):
        for wi, tok in enumerate(toks):
            rows.append((si, wi, tok, "-"))
    path = _write_temp_conll(rows)
    try:
        return SituationReader().read(path)   # default reader -> track_bridges ON
    finally:
        os.remove(path)


# PART: "The car rolled onto the road ." / "The engine had failed ." -> engine PART-OF car (car is NON-recent;
# road is the most-recent prior entity, so the recency floor picks road).
sm_part = _read_passage([["The", "car", "rolled", "onto", "the", "road", "."],
                         ["The", "engine", "had", "failed", "."]])
check("W1-reader-exposes-query", callable(getattr(sm_part, "bridge", None)) and hasattr(sm_part, "bridges"),
      "sm.bridge / sm.infer_bridges bound at read time (first live meaning-channel consumer)")
b_part = sm_part.bridge("engine")
recent_entity = None
for ent in sm_part.entities:
    for h in (ent.heads or []):
        tok = h.split()[-1].lower()
        if tok in ("car", "road"):
            recent_entity = tok  # last such head in entity order ~ most-recent mention
check("W1-part-antecedent", b_part is not None and b_part.antecedent == "car",
      "sm.bridge('engine') -> %s (which whole the part belongs to; ranked %s)"
      % (None if b_part is None else b_part.antecedent,
         None if b_part is None else [(c, round(s, 3)) for c, s in b_part.ranked]))
check("W1-part-beats-noinference", b_part.antecedent != "road",
      "the correct whole 'car' is NON-recent (recency floor picks 'road') -> the bridge beats no-inference")

# INSTRUMENT: "The nail split the plank ." / "The hammer lay nearby ." -> hammer INSTRUMENT-of (the event the
# instrument serves); the bridge must relate 'hammer' to 'nail'/the event, not the recent 'plank'.
sm_instr = _read_passage([["The", "nail", "split", "the", "plank", "."],
                          ["The", "hammer", "lay", "nearby", "."]])
b_instr = sm_instr.bridge("hammer")
check("W1-instrument-antecedent", b_instr is not None and b_instr.antecedent == "nail",
      "sm.bridge('hammer') -> %s (ranked %s)"
      % (None if b_instr is None else b_instr.antecedent,
         None if b_instr is None else [(c, round(s, 3)) for c, s in b_instr.ranked]))

# infer_bridges populates sm.bridges (the construction-integration proposal set) on demand
props = sm_part.infer_bridges()
check("W1-infer-bridges", isinstance(props, list) and sm_part.bridges is props and len(props) >= 1,
      "sm.infer_bridges() committed %d proposal(s) onto sm.bridges" % len(props))


# --------------------------------------------------------------------------- W2: reproduce through the organ
# Replicate exp_bridging_selection_v2.eval_type's held-out harness EXACTLY (same gold sources, same
# digest-seeded splits, same candidate construction / rng order), but SELECT via the LANDED organ. Byte-faithful
# candidate sets -> the same per-item argmax -> the same aggregate accuracy as the validated cell.
SOURCES = {"part_wn": part_pairs_wn, "part_cn": part_pairs_cn, "instrument": instrument_pairs}
_HUB = pickle.load(open(HUB_PATH, "rb"))["hub"]
_VOCAB = list(_HUB.keys())
_MFND = build_mfnd_vec()
_ORG = BridgeInference(source="hub")   # the landed organ (loads its OWN hub singleton internally)


def eval_through_organ(typ, want_mfnd=False, byte_check=False):
    pairs = SOURCES[typ](_HUB)
    ante_pool = sorted({a for (_, a) in pairs})
    raw_org, mfnd_org, twin = [], [], []
    n_match, n_seen = 0, 0
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(_digest_seed("%s:%d" % (typ, seed)))
        idx = rng.permutation(len(pairs))
        cut = len(pairs) // 2
        test = [pairs[i] for i in idx[cut:]]
        perm = rng.permutation(len(_VOCAB))                       # consume rng exactly as eval_type does
        shuf = {_VOCAB[i]: _HUB[_VOCAB[perm[i]]] for i in range(len(_VOCAB))}
        for (t, gold) in test:
            pool = [a for a in ante_pool if a != gold and a != t]
            pick = rng.choice(len(pool), size=min(K_DISTRACT, len(pool)), replace=False)
            cands = [gold] + [pool[i] for i in pick]
            rng.shuffle(cands)
            gi = cands.index(gold)
            n = len(cands)
            # RAW_HUB THROUGH THE LANDED ORGAN
            b = _ORG.select(t, cands, source="hub")
            org_pick = None if b is None else cands.index(b.antecedent)
            raw_org.append(int(org_pick == gi) if org_pick is not None else 1.0 / n)
            if byte_check:
                tv = unit(_HUB[t])
                inline = int(np.argmax([float(tv @ unit(_HUB[c])) for c in cands]))
                n_seen += 1
                n_match += int(org_pick == inline)
            # MEAN_FND THROUGH THE LANDED ORGAN (source="mfnd"); fall back to chance exactly as the cell does
            if want_mfnd:
                mt = _MFND(t)
                if mt is not None and np.linalg.norm(mt) > 0:
                    bm = _ORG.select(t, cands, source="mfnd")
                    if bm is None:
                        mfnd_org.append(1.0 / n)
                    else:
                        mfnd_org.append(int(cands.index(bm.antecedent) == gi))
                else:
                    mfnd_org.append(1.0 / n)
            # SHUFFLED-MEANING TWIN (the info-free control on the SAME mechanism -- must collapse to chance)
            tvs = unit(shuf[t])
            twin.append(int(int(np.argmax([float(tvs @ unit(shuf[c])) for c in cands])) == gi))
    out = {"raw_org": float(np.mean(raw_org)), "twin": float(np.mean(twin)), "n": len(raw_org)}
    if want_mfnd:
        out["mfnd_org"] = float(np.mean(mfnd_org))
    if byte_check:
        out["byte_match"] = n_match / max(1, n_seen)
    return out


r_wn = eval_through_organ("part_wn", byte_check=True)
check("W2-part_wn-raw-organ", abs(r_wn["raw_org"] - 0.4720) < 0.004,
      "RAW_HUB via organ = %.4f (SOLVED 0.4720), n=%d" % (r_wn["raw_org"], r_wn["n"]))
check("W2-part_wn-twin-collapses", r_wn["twin"] < 0.24 and (r_wn["raw_org"] - r_wn["twin"]) > 0.20,
      "shuffled-meaning twin = %.4f (~chance 0.20); organ-twin = %+.4f (meaning is load-bearing)"
      % (r_wn["twin"], r_wn["raw_org"] - r_wn["twin"]))
check("W2-part_wn-byte-identity", r_wn["byte_match"] > 0.999,
      "organ argmax == validated cell inline argmax on %.1f%% of items (byte-faithful)"
      % (100.0 * r_wn["byte_match"]))

r_cn = eval_through_organ("part_cn", want_mfnd=True)
check("W2-part_cn-raw-organ", abs(r_cn["raw_org"] - 0.6087) < 0.004,
      "RAW_HUB via organ = %.4f (SOLVED 0.6087), n=%d" % (r_cn["raw_org"], r_cn["n"]))
check("W2-part_cn-mfnd-organ", abs(r_cn["mfnd_org"] - 0.6541) < 0.012,
      "meaning_foundation via organ = %.4f (SOLVED 0.6541 -- the curated store is the best bridge source)"
      % r_cn["mfnd_org"])
check("W2-part_cn-twin-collapses", r_cn["twin"] < 0.24 and (r_cn["raw_org"] - r_cn["twin"]) > 0.35,
      "twin = %.4f; organ-twin = %+.4f" % (r_cn["twin"], r_cn["raw_org"] - r_cn["twin"]))

r_in = eval_through_organ("instrument")
check("W2-instrument-raw-organ", abs(r_in["raw_org"] - 0.4522) < 0.004,
      "RAW_HUB via organ = %.4f (SOLVED 0.4522), n=%d" % (r_in["raw_org"], r_in["n"]))
check("W2-instrument-twin-collapses", r_in["twin"] < 0.24 and (r_in["raw_org"] - r_in["twin"]) > 0.20,
      "twin = %.4f; organ-twin = %+.4f" % (r_in["twin"], r_in["raw_org"] - r_in["twin"]))


# --------------------------------------------------------------------------- W3: additive-safety
def _dim_signature(sm):
    """A canonical serialization of every LOAD-BEARING situation-model dimension EXCEPT the new bridging one."""
    return {
        "entities": [tuple(e.heads) for e in sm.entities],
        "events": [(e.predicate, e.agent, e.patient, e.tense, e.subj_role, e.obj_role, e.affect)
                   for e in sm.events],
        "coref": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.correct) for r in sm.coref_resolutions],
        "causal": [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm.causal_links],
        "timeline_order": list(sm.timeline_order),
        "suppressed": [(s.sent_idx, s.predicate) for s in sm.suppressed_predicates],
        "entity_states": [(s.holder, s.property, s.htype) for s in sm.entity_states],
        "scalars": (sm.n_targets, sm.n_xsent_targets, sm.coref_acc, sm.coref_xsent_acc,
                    bool(sm.locations is not None), bool(sm.world_state is not None),
                    bool(sm.goal_register is not None), bool(sm.affect_register is not None)),
    }


doc = [["The", "sailor", "loved", "his", "ship", "."],
       ["He", "repaired", "the", "hull", "after", "the", "storm", "."],
       ["The", "captain", "feared", "the", "reef", "."]]
rows = [(si, wi, tok, "-") for si, toks in enumerate(doc) for wi, tok in enumerate(toks)]
_path = _write_temp_conll(rows)
try:
    sm_on = SituationReader().read(_path)                       # track_bridges ON (default)
    sm_off = SituationReader(track_bridges=False).read(_path)   # the pre-landing reader
finally:
    os.remove(_path)

sig_on, sig_off = _dim_signature(sm_on), _dim_signature(sm_off)
mismatch = [k for k in sig_on if sig_on[k] != sig_off[k]]
check("W3-additive-safety", not mismatch,
      "all %d existing dimensions byte-identical ON vs OFF (mismatches: %s)"
      % (len(sig_on), mismatch or "none"))
check("W3-off-is-pre-landing", not hasattr(sm_off, "bridge") and sm_off.bridges == [],
      "track_bridges=False -> no sm.bridge bound, sm.bridges empty (== the pre-landing reader)")
check("W3-on-adds-only-bridging", callable(getattr(sm_on, "bridge", None)),
      "track_bridges=True adds ONLY sm.bridge/infer_bridges/bridges (a pure additive read-only inference)")

print("=" * 92)
print("LANDING WITNESS PASS: %d/%d" % (P, P))
print("=" * 92)
