"""
END-TO-END READER RE-EVALUATION (post-coref-fix): now that coref is FIXED, does the reader hold up on
REAL (hand-rule) mentions, or is MENTION DETECTION the NEXT bottleneck (unmasked by the coref fix)? ONE
variable = the MENTION SOURCE (gold vs hand-rule); COREF FIXED (agreement + salience-rank/topical) in
BOTH arms. This re-measures the oracle-mention test's conclusion under the FIXED coref cues.

WHY (the picture CHANGED after the coref fix):
  - Oracle test (a68f9fe72, PRE-coref-fix) concluded mention-detection is NOT the primary v4 bottleneck;
    COREF was -- but that oracle-vs-handrule delta was measured with BROKEN coref.
  - Coref is now FIXED + VET-confirmed: agreement fix (0775bc894) + salience-rank/topical (3529ef65a).
    With GOLD mentions + FIXED coref the reader WORKS on the REAL 2nd-reader:
      CC 0.600, CO 0.667, ref-acc 0.912, RELF1 0.580, CMP 1.000, all 0.839
      MEASURED@data/exp_coref_salience_rank_topicality_v1/metrics.json:attribution.topical
  - OPEN QUESTION (this cell): does it hold with REAL (hand-rule) mentions + FIXED coref? I.e. now that
    coref no longer masks it, IS mention-detection the next bottleneck? Re-measure the gold-vs-handrule
    DELTA with coref FIXED = the honest prize a learned mention-detector would capture, re-evaluated.

ONE VARIABLE = mention_mode:
  gold_mentions     : mention_mode="oracle"   (GOLD hand-annotated referring-entity heads) [THE CEILING;
                      POSITIVE CONTROL -> must reproduce the salience-cell topical arm byte-identically]
  handrule_mentions : mention_mode="handrule" (v4 candidate_indices + v4 grounding observe-gate VERBATIM)
                      [THE HONEST END-TO-END]
  COREF FIXED IN BOTH: prefer_agreement=True (agreement fix) + prefer_topical case-routed (salience fix)
  + possessive-timing fix ON in both. The ONLY thing that differs is which tokens are MENTIONS.

The mention gate controls BOTH (a) role-assigner argument candidates + relation args AND (b) the overlay
observe loop (coref antecedent pool) -- the two places mentions feed downstream. Everything else (learned
AveragedPerceptron role-assigner, WorkingOverlay agreement+topical coref, relation emission, RELF1 scorer,
comprehension-Q engine) is BYTE-IDENTICAL to the salience/oracle pipeline (imported / verbatim-copied +
byte-identity self-test guard). The coref-fixed overlay + the v4 hand-rule detector are REUSED VERBATIM;
neither is re-tuned. The optional emission fix (has->poss) is DEFERRED to preserve the one-variable
positive-control reproduction of the salience ceiling (applying it would move BOTH arms off that ceiling).

DELTA (with coref now fixed) = gold_ceiling - handrule = how much mention-detection ACTUALLY costs the
reader end-to-end = the honest prize a learned mention-detector would capture, re-evaluated post-coref-fix.

BRANCHES (decisive either way; genuinely can-fail both):
  END_TO_END_DECENT = handrule + fixed coref lands CLOSE to the gold ceiling (retains >= 80% of the
    ceiling comprehension AND CMP >= 0.70 AND RELF1 >= 0.45) -> the reader WORKS end-to-end on real text;
    coref was the key; mentions are OK enough -> a genuine (scoped) end-to-end reader capability on
    grade-2 narrative.
  MENTION_BOUND = handrule + fixed coref COLLAPSES vs the gold ceiling (retains <= 65% of ceiling
    comprehension OR CMP <= 0.50 OR RELF1 <= 0.35) -> mention-detection is NOW the next bottleneck (the
    coref fix unmasked it) -> the learned mention-detector IS worth building; the oracle test's
    "secondary lever" was measured under broken coref -> re-evaluate. The DELTA = the prize.
  PARTIAL = mentions cost some but not a collapse -> localize what the noise breaks.

DESIGN-GATE (verified at self-test/smoke BEFORE the full run; USER: fair tests every time):
  (1) POSITIVE-CONTROL: gold_mentions arm reproduces the salience-cell topical arm BYTE-IDENTICALLY
      (store + resolutions) per passage -> confirms one-variable-off the salience ceiling; the arm's
      slices reproduce CC 0.600 / CO 0.667 / ref 0.912 / CMP 1.000 / RELF1 0.580.
  (2) REAL baseline = the honest handrule end-to-end (v4 detector VERBATIM), NOT a strawman.
  (3) CAN-FAIL BOTH WAYS: handrule can land close (DECENT) or collapse (MENTION_BOUND) -- both reachable.
  (4) TELEMETRY-SENSITIVE: swapping mention_mode MUST move the answers (ARMS-MUST-DIFFER hash gate).
  (5) ONE variable = mention_mode; agreement + topical + possessive-fix held ON in BOTH arms.
  (6) COREF FIXED in both (NOT varied); real passages verbatim (imported from ORC).
  (7) INDEPENDENT gold: mention gold = referring-entity rule; comprehension gold = separate annotation.
  (8) anti-copy-divergence: self-test asserts my parameterized extract == SAL.extract_passage_cfg
      byte-identically in the oracle config (guards against silent copy drift).
  (9) determinism OMP=1, fixed seed, sorted(set).

Glass-box (POS + tiny perceptron + symbolic coref/query; NO external LLM; NO torch/GPU). Local /
foreground-to-completion. NO push / NO remote-persist. Reported CLAIM-VET-pending (NOT self-declared
chain-grade); strategic read reported as hypothesis-pending-VET.

ANCHOR: reader_mention_source_gold_vs_handrule_corefixed_v1
CEILING context: salience cell 3529ef65a (VET-confirmed); agreement 0775bc894; oracle-mention a68f9fe72.
CORPUS: reuses the oracle cell's REAL McGuffey second-reader passages + gold (verbatim import).
COMPUTE: sequential-CPU (POS-tag + tiny perceptron fit + symbolic coref/query); wall < 120s; no HD.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                        [META_RULE_AF]
# - discriminator CAN-FAIL (handrule can land close OR collapse) [design-gate]
# - POSITIVE-CONTROL: gold arm reproduces salience topical store byte-identical [reproduce_prior / Gate D]
# - deterministic seeding (fixed int seed, fixed order, sorted set)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay (agreement+topical) + REAL
#   perceptron fit + REAL POS tagger + the REAL v4 handrule candidate gate on the REAL passages  [F.1]
# - substrate_signature: binds WorkingOverlay/resolve_pronoun sigs (prefer_agreement/prefer_topical) [F.2]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - all reported numbers MEASURED@this metrics.json; ceiling CITED@salience cell metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import hashlib
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the oracle cell's REAL passages + gold + downstream pipeline + the salience cell's coref-fixed
# extract (agreement + topical) VERBATIM. The ONLY change vs SAL.extract_passage_cfg: mention_mode is a
# PARAMETER (SAL hardcodes "oracle"); a self-test asserts byte-identity in the oracle config.
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402
from experiments import exp_coref_salience_rank_topicality_v1 as SAL    # noqa: E402
from hdlab.state_of_mind import (  # noqa: E402
    WorkingOverlay, SetKnownBase, PRONOUN_SCOPE,
)

# Reuse the salience cell's coref-fixed helpers VERBATIM (NOT re-tuned).
_prefers_topical = SAL._prefers_topical
_agreement_attrs = SAL._agreement_attrs
GOLD_ANTECEDENTS = SAL.GOLD_ANTECEDENTS
_RESOLVABLE = SAL._RESOLVABLE
_RESOLVABLE_SO = SAL._RESOLVABLE_SO
_RESOLVABLE_POSS = SAL._RESOLVABLE_POSS

ANCHOR_NAME = "reader_mention_source_gold_vs_handrule_corefixed_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 12345

# ---- Pre-registered bands (set BEFORE the final run; HYPOTHESIZED@this prereg) ----------------------
# ONE variable = mention_mode. gold_mentions = THE CEILING (measured; must reproduce salience topical).
# handrule_mentions = the honest end-to-end. Primary = overall comprehension `all` retention vs the
# gold ceiling, corroborated by CMP (composition) + RELF1 (relation extraction). Bands are decisive +
# can-fail both ways; classification uses BOUND-first (mutually exclusive with DECENT by construction).
DECENT_RETENTION_MIN = 0.80   # handrule `all` >= 0.80 * gold `all`  (retains >= 80% of ceiling)
DECENT_CMP_MIN = 0.70         # AND handrule composition >= 0.70
DECENT_RELF1_MIN = 0.45       # AND handrule RELF1 micro-F1 >= 0.45
BOUND_RETENTION_MAX = 0.65    # handrule `all` <= 0.65 * gold `all`  (retains <= 65% of ceiling) OR ...
BOUND_CMP_MAX = 0.50          # ... composition <= 0.50 OR ...
BOUND_RELF1_MAX = 0.35        # ... RELF1 micro-F1 <= 0.35
TELEMETRY_MIN_MOVE = 0.05     # swapping mention_mode must move at least one primary metric by this
# POSITIVE CONTROL: gold arm reproduces the salience-cell topical ceiling (CITED; re-measured here).
CEILING = dict(CC=0.600, CO=0.6667, ref_acc=0.9118, CMP=1.000, RELF1=0.580, all=0.8387)
CEILING_TOL = 0.005          # gold arm slices must land within this of the measured ceiling

ARMS = {
    "gold_mentions":     dict(mention_mode="oracle",   fix_possessive=True, agreement=True, topical=True),
    "handrule_mentions": dict(mention_mode="handrule", fix_possessive=True, agreement=True, topical=True),
}


# =======================================================================================
# Parameterized extract: EXACT copy of SAL.extract_passage_cfg with mention_mode as a PARAMETER.
# (SAL hardcodes mention_mode="oracle" at the top; that is the ONLY change. Self-test asserts
#  byte-identity vs SAL in the oracle config to guard against silent copy divergence.)
# =======================================================================================
def extract_passage_cfg_mm(passage_text, clf, pid, fix_possessive, agreement, topical, mention_mode):
    """Coref pass + role assignment + relation emission on ONE real passage. ONE variable across arms =
    mention_mode (oracle=GOLD heads; handrule=v4 candidate_indices + grounding gate VERBATIM). agreement
    + topical + fix_possessive held per config. Body byte-identical to SAL.extract_passage_cfg except
    mention_mode is a parameter."""
    gold_heads = ORC.GOLD_MENTIONS.get(pid, frozenset())
    coref_strategy = ORC.FIXED_COREF_STRATEGY  # 'maintained' (validated; not tuned)
    pref = bool(agreement)

    known = set()
    for txt in list(ORC.TEST_PASSAGES.values()):
        for s in ORC.split_sentences(txt):
            for _su, lo, _po in ORC.pos_tag_sentence(s):
                if ORC.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))

    rels = []
    res_by_pos = {}
    offset = 0
    for sent in ORC.split_sentences(passage_text):
        tagged = ORC.pos_tag_sentence(sent)
        pron_res = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:
                if low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    pron_res[i] = ent.head if ent is not None else None
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in ORC.PRONOUNS_POSS:
                pass
            else:
                if not ORC.observe_as_mention(low, pos, mention_mode, gold_heads):
                    continue
                is_name = (low in ORC.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                if agreement:
                    g, num, anim = _agreement_attrs(low, pos, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name, animacy=anim)
                else:
                    g, num = ORC.grounded_gender_number(low, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name)

        roles, verb_idx, verb, passive, cand = ORC.assign_roles_learned(
            tagged, clf, mention_mode, gold_heads)

        def head_of(i):
            surf, low, pos = tagged[i]
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            return low

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)
        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                rels.append(("svo", verb, head_of(agents[0]), head_of(pi)))
        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or ORC.prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        rels.append(("svo", "kind", subj_head, head_of(i)))
        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        rels.append(("poss", head_of(owner_idx), head_of(pi)))
        for ri in recips:
            if verb is not None and agents:
                rels.append(("recipient", verb, head_of(agents[0]), head_of(ri)))
        for li in locs:
            figure = subj_head
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
            if figure is not None and figure != head_of(li):
                rels.append(("loc", figure, head_of(li)))

        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in ORC.PRONOUNS_POSS:
                if fix_possessive and low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    owner = pron_res.get(i)
                    owner = owner if owner is not None else low
                elif low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
                if low in _RESOLVABLE:
                    res_by_pos[offset + i] = (low, owner if owner != low else None)
        for i in range(len(tagged) - 1):
            if ORC.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break

        for i, (surf, low, pos) in enumerate(tagged):
            if low in _RESOLVABLE_SO and low not in _RESOLVABLE_POSS:
                res_by_pos[offset + i] = (low, pron_res.get(i))

        offset += len(tagged)

    sorted_rels = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return sorted_rels, res_by_pos


# =======================================================================================
# Mention-quality telemetry (glass-box; localizes WHY handrule differs; does NOT affect the arms).
# =======================================================================================
def _mention_heads(pid, mention_mode):
    """Set of noun-mention head lemmas selected by mention_mode for passage pid (pronouns excluded;
    same observe_as_mention gate the arms use)."""
    gold_heads = ORC.GOLD_MENTIONS.get(pid, frozenset())
    heads = set()
    for sent in ORC.split_sentences(ORC.TEST_PASSAGES[pid]):
        for surf, low, pos in ORC.pos_tag_sentence(sent):
            if low in PRONOUN_SCOPE or low in ORC.PRONOUNS_POSS:
                continue
            if low in ORC.PRONOUNS_SUBJ_OBJ:
                continue
            if ORC.observe_as_mention(low, pos, mention_mode, gold_heads):
                heads.add(low)
    return heads


def mention_quality():
    """handrule noun-mention precision/recall vs the gold (oracle) mention set, micro over passages."""
    tp = fp = fn = 0
    per_passage = {}
    for pid in ORC.TEST_PASSAGES:
        gold = _mention_heads(pid, "oracle")
        hand = _mention_heads(pid, "handrule")
        p_tp = len(gold & hand)
        p_fp = len(hand - gold)
        p_fn = len(gold - hand)
        tp += p_tp
        fp += p_fp
        fn += p_fn
        per_passage[pid] = dict(gold=sorted(gold), hand=sorted(hand),
                                extra=sorted(hand - gold), missed=sorted(gold - hand))
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return dict(precision=round(prec, 4), recall=round(rec, 4), f1=round(f1, 4),
                tp=tp, fp=fp, fn=fn, per_passage=per_passage)


# =======================================================================================
# Arm runner (scoring mirrors SAL.run_config; mention-mode-independent scorers reused from ORC).
# =======================================================================================
def run_arm(arm_name, clf):
    cfg = ARMS[arm_name]
    store = {}
    res_by_pos = {}
    for pid, text in ORC.TEST_PASSAGES.items():
        rels, rbp = extract_passage_cfg_mm(text, clf, pid, cfg["fix_possessive"], cfg["agreement"],
                                           cfg["topical"], cfg["mention_mode"])
        store[pid] = rels
        res_by_pos[pid] = rbp
    correct = []
    answers = []
    for q in ORC.TEST_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = ORC._relf1_for_store(store)
    slices = ORC._slices(correct)
    n_tot = n_ok = 0
    ref_detail = {}
    for pid in ORC.TEST_PASSAGES:
        gold = GOLD_ANTECEDENTS.get(pid, [])
        pred_sorted = [res_by_pos[pid][k] for k in sorted(res_by_pos[pid].keys())]
        det = []
        for gi, (g_surf, g_head) in enumerate(gold):
            p_surf, p_head = (pred_sorted[gi] if gi < len(pred_sorted) else (None, None))
            ok = (p_head is not None and ORC.normalize(p_head) == ORC.normalize(g_head))
            n_tot += 1
            n_ok += 1 if ok else 0
            det.append(dict(surf=g_surf, gold=g_head, pred=p_head, ok=ok))
        ref_detail[pid] = det
    ref_acc = (n_ok / n_tot) if n_tot else 0.0
    return dict(store=store, correct=correct, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_n=n_tot, ref_ok=n_ok,
                ref_detail=ref_detail, answers=answers)


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _arms_must_differ(named_outputs):
    digests = {}
    for name, out in named_outputs.items():
        b = json.dumps(out, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], \
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical"
    return digests


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] constructing REAL WorkingOverlay + oracle/salience pipeline ...")
    import inspect
    rp_params = set(inspect.signature(WorkingOverlay.resolve_pronoun).parameters)
    assert {"prefer_agreement", "prefer_topical"} <= rp_params, \
        "resolve_pronoun() must accept prefer_agreement + prefer_topical kwargs (F.2)"

    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    # (8) ANTI-COPY-DIVERGENCE: my parameterized extract == SAL.extract_passage_cfg byte-identically in
    # BOTH the oracle-config (fix_possessive+agreement+topical) AND the raw config. Guards silent drift.
    n_ok = 0
    for pid, text in ORC.TEST_PASSAGES.items():
        for fp, ag, tp in [(True, True, True), (False, False, False)]:
            mine = extract_passage_cfg_mm(text, clf, pid, fp, ag, tp, "oracle")
            sal = SAL.extract_passage_cfg(text, clf, pid, fp, ag, tp)
            assert mine == sal, (
                f"COPY-DIVERGENCE {pid} (fp={fp},ag={ag},tp={tp}): parameterized extract != "
                f"SAL.extract_passage_cfg\n  mine={mine}\n  sal={sal}")
            n_ok += 1
    print(f"[self-test] anti-copy-divergence: extract == SAL byte-identical on {n_ok} (passage x config)")

    # (1) POSITIVE-CONTROL: gold_mentions arm reproduces the salience topical ceiling within tol.
    gold = run_arm("gold_mentions", clf)
    gcc, gco = gold["slices"]["CC"], gold["slices"]["CO"]
    gcmp, gall = gold["slices"]["CMP"], gold["slices"]["all"]
    gref, grelf1 = gold["ref_acc"], gold["relf1"]["micro_f1"]
    for k, got in dict(CC=gcc, CO=gco, ref_acc=gref, CMP=gcmp, RELF1=grelf1, all=gall).items():
        assert abs(got - CEILING[k]) <= CEILING_TOL, \
            f"POSITIVE-CONTROL FAIL: gold_mentions {k}={got:.4f} != ceiling {CEILING[k]:.4f} (salience topical)"
    print(f"[self-test] POSITIVE-CONTROL: gold arm reproduces ceiling CC={gcc:.3f} CO={gco:.3f} "
          f"ref={gref:.3f} CMP={gcmp:.3f} RELF1={grelf1:.3f} all={gall:.3f}")

    # (4) TELEMETRY-SENSITIVE + (3) CAN-FAIL: gold vs handrule answers must differ.
    hand = run_arm("handrule_mentions", clf)
    _arms_must_differ({"gold_mentions": gold["answers"], "handrule_mentions": hand["answers"]})
    moved = max(abs(hand["slices"]["all"] - gall), abs(hand["relf1"]["micro_f1"] - grelf1),
                abs(hand["slices"]["CMP"] - gcmp))
    assert moved >= TELEMETRY_MIN_MOVE, \
        f"telemetry-insensitive: mention_mode swap moved primary metrics < {TELEMETRY_MIN_MOVE} ({moved:.3f})"
    print(f"[self-test] telemetry-sensitive: mention_mode swap moved a primary metric by {moved:.3f}")
    print(f"[self-test]   handrule: all={hand['slices']['all']:.3f} CMP={hand['slices']['CMP']:.3f} "
          f"RELF1={hand['relf1']['micro_f1']:.3f} CC={hand['slices']['CC']:.3f} CO={hand['slices']['CO']:.3f}")

    # mention-quality telemetry sanity (handrule differs from gold mention set).
    mq = mention_quality()
    assert mq["fp"] > 0 or mq["fn"] > 0, "handrule mention set identical to gold (no mention variable)"
    print(f"[self-test] mention-quality: handrule P={mq['precision']:.3f} R={mq['recall']:.3f} "
          f"(tp={mq['tp']} fp={mq['fp']} fn={mq['fn']})")

    # determinism: two runs identical.
    r1 = run_arm("handrule_mentions", clf)
    r2 = run_arm("handrule_mentions", clf)
    assert r1["correct"] == r2["correct"] and r1["ref_acc"] == r2["ref_acc"], "non-deterministic run"
    print("[self-test] deterministic (two handrule runs identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=len(ARMS))

    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    results = {name: run_arm(name, clf) for name in ARMS}
    digests = _arms_must_differ({name: results[name]["answers"] for name in ARMS})

    g = results["gold_mentions"]
    h = results["handrule_mentions"]

    def S(r, s):
        return r["slices"][s]

    g_all, h_all = S(g, "all"), S(h, "all")
    g_cmp, h_cmp = S(g, "CMP"), S(h, "CMP")
    g_cc, h_cc = S(g, "CC"), S(h, "CC")
    g_co, h_co = S(g, "CO"), S(h, "CO")
    g_nc, h_nc = S(g, "NC"), S(h, "NC")
    g_ref, h_ref = g["ref_acc"], h["ref_acc"]
    g_relf1, h_relf1 = g["relf1"]["micro_f1"], h["relf1"]["micro_f1"]
    g_relf1_r, h_relf1_r = g["relf1"]["micro_recall"], h["relf1"]["micro_recall"]

    retention_all = (h_all / g_all) if g_all else 0.0

    # POSITIVE CONTROL re-check in verdict (must reproduce ceiling).
    pc_ok = all(abs(v - CEILING[k]) <= CEILING_TOL for k, v in
                dict(CC=g_cc, CO=g_co, ref_acc=g_ref, CMP=g_cmp, RELF1=g_relf1, all=g_all).items())

    # telemetry
    moved = max(abs(h_all - g_all), abs(h_relf1 - g_relf1), abs(h_cmp - g_cmp))
    telemetry_ok = moved >= TELEMETRY_MIN_MOVE

    bound_any = (retention_all <= BOUND_RETENTION_MAX) or (h_cmp <= BOUND_CMP_MAX) or \
                (h_relf1 <= BOUND_RELF1_MAX)
    decent_all = (retention_all >= DECENT_RETENTION_MIN) and (h_cmp >= DECENT_CMP_MIN) and \
                 (h_relf1 >= DECENT_RELF1_MIN)

    mq = mention_quality()

    if not pc_ok:
        verdict = "INVALID_POSITIVE_CONTROL_FAIL"
        vmsg = (f"gold_mentions arm did NOT reproduce the salience ceiling (CC={g_cc:.3f} CO={g_co:.3f} "
                f"ref={g_ref:.3f} CMP={g_cmp:.3f} RELF1={g_relf1:.3f} all={g_all:.3f}); one-variable "
                f"basis broken -> do NOT trust the delta")
    elif not telemetry_ok:
        verdict = "INVALID_TELEMETRY_INSENSITIVE"
        vmsg = f"mention_mode swap moved primary metrics < {TELEMETRY_MIN_MOVE} (max {moved:.3f}); vacuous"
    elif bound_any:
        verdict = "MENTION_BOUND"
        vmsg = (f"handrule COLLAPSES vs the gold ceiling: all {g_all:.3f}->{h_all:.3f} "
                f"(retention {retention_all:.2f}), CMP {g_cmp:.3f}->{h_cmp:.3f}, RELF1 {g_relf1:.3f}->"
                f"{h_relf1:.3f}, CC {g_cc:.3f}->{h_cc:.3f}, CO {g_co:.3f}->{h_co:.3f}. With coref FIXED, "
                f"mention-detection is NOW the next bottleneck (handrule mention P={mq['precision']:.2f} "
                f"R={mq['recall']:.2f}). The DELTA = the prize a learned mention-detector would capture.")
    elif decent_all:
        verdict = "END_TO_END_DECENT"
        vmsg = (f"handrule lands CLOSE to the gold ceiling: all {g_all:.3f}->{h_all:.3f} "
                f"(retention {retention_all:.2f}), CMP {g_cmp:.3f}->{h_cmp:.3f}, RELF1 {g_relf1:.3f}->"
                f"{h_relf1:.3f}. Coref was the key; hand-rule mentions are OK enough -> a genuine (scoped) "
                f"end-to-end reader capability on grade-2 narrative. mention P={mq['precision']:.2f} "
                f"R={mq['recall']:.2f}.")
    else:
        verdict = "PARTIAL_MENTION_COST"
        vmsg = (f"handrule costs some but not a collapse: all {g_all:.3f}->{h_all:.3f} "
                f"(retention {retention_all:.2f}), CMP {g_cmp:.3f}->{h_cmp:.3f}, RELF1 {g_relf1:.3f}->"
                f"{h_relf1:.3f}. Localize what the mention noise breaks (mention P={mq['precision']:.2f} "
                f"R={mq['recall']:.2f}).")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: all {g_all:.3f}->{h_all:.3f} (ret {retention_all:.2f}) | "
                 f"CMP {g_cmp:.3f}->{h_cmp:.3f} | RELF1 {g_relf1:.3f}->{h_relf1:.3f} | "
                 f"CC {g_cc:.3f}->{h_cc:.3f} | CO {g_co:.3f}->{h_co:.3f} | ref {g_ref:.3f}->{h_ref:.3f}"),
        elapsed_s=round(elapsed, 2),
        ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME, run_mode=run_mode,
        seed=SEED,
        one_variable="mention_mode (gold oracle vs handrule); coref FIXED (agreement+topical) both arms",
        bands=dict(DECENT_RETENTION_MIN=DECENT_RETENTION_MIN, DECENT_CMP_MIN=DECENT_CMP_MIN,
                   DECENT_RELF1_MIN=DECENT_RELF1_MIN, BOUND_RETENTION_MAX=BOUND_RETENTION_MAX,
                   BOUND_CMP_MAX=BOUND_CMP_MAX, BOUND_RELF1_MAX=BOUND_RELF1_MAX,
                   TELEMETRY_MIN_MOVE=TELEMETRY_MIN_MOVE),
        positive_control_ok=pc_ok, telemetry_ok=telemetry_ok, telemetry_move=round(moved, 4),
        arms_differ_digests=digests,
        retention_all=round(retention_all, 4),
        delta=dict(all=round(g_all - h_all, 4), CMP=round(g_cmp - h_cmp, 4),
                   RELF1=round(g_relf1 - h_relf1, 4), CC=round(g_cc - h_cc, 4),
                   CO=round(g_co - h_co, 4), NC=round(g_nc - h_nc, 4),
                   ref_acc=round(g_ref - h_ref, 4), RELF1_recall=round(g_relf1_r - h_relf1_r, 4)),
        arms={name: dict(slices=results[name]["slices"], ref_acc=results[name]["ref_acc"],
                         ref_ok=results[name]["ref_ok"], ref_n=results[name]["ref_n"],
                         relf1_micro_f1=results[name]["relf1"]["micro_f1"],
                         relf1_micro_precision=results[name]["relf1"]["micro_precision"],
                         relf1_micro_recall=results[name]["relf1"]["micro_recall"])
              for name in ARMS},
        mention_quality=mq,
        cited_ceiling=dict(source="data/exp_coref_salience_rank_topicality_v1/metrics.json:attribution.topical",
                           salience_cell="3529ef65a", **CEILING),
        reference_detail={name: results[name]["ref_detail"] for name in ARMS},
        n_pronouns_scored=g["ref_n"], n_questions=len(ORC.TEST_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=2))
    print("delta:", json.dumps(metrics["delta"], indent=2))
    print("mention_quality:", json.dumps({k: mq[k] for k in ("precision", "recall", "f1", "tp", "fp", "fn")}))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    return build_verdict(OUTPUT_DIR, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
