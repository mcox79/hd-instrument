"""EVENTS SUPPLY-NER: does SUPPLYING entity-type knowledge (spaCy NER) reduce the AGENT-TYPING half
of the events noise that the spaCy-POS supply cell left untouched (n_inanimate_agent 196->195)?

The POS cell cut the PREDICATE half (nonverb_pred 160->70) but the extractor still assigns an AGENT
role to a place/thing (England/London as agent; shops/streets as agent). This cell SUPPLIES spaCy
NER (now installed) and TYPES each agent candidate (PERSON / GPE / LOC / ORG / FAC / ...). GATE: for
a person-selecting predicate, SUPPRESS an agent NER-typed as a non-person PLACE/ORG/thing.

NORTH-STAR FRAME (humans read via already-known world knowledge): spaCy NER = SUPPLIED PREPROCESSING
(a fixed typing of tokens), NOT a black-box LLM in the reasoning loop. The reader's REASONING (NLTK
POS + trained parser + role clf + subcat gate + selectional argmax) stays glass-box + UNCHANGED. The
suppression NULLS the emitted agent only; it does NOT alter the parse or the carried-agent chain.
ONE variable = NER-gate on/off.

DISCRIMINATOR (can-fail, pre-reg): does the spaCy-NER entity-type gate REDUCE the inanimate-agent
noise (196) vs no-gate, same 25 LitBank books, same base extractor?
  HARD_PASS      rel_reduction_196 >= 0.15 AND net_fix > 0  -> NER materially cuts it.
  MIDDLE_BAND    0 < rel_reduction_196 < 0.15 AND net_fix >= 0 -> small proper-noun slice fixed.
  CLEAN_NEGATIVE rel_reduction_196 <= 0 OR net_fix < 0 -> NER offset by own-errors / breaks dominate.
CAN-FAIL: spaCy en_core_web_sm MIS-TYPES 19c literary places as PERSON (Howard Grove/Kent verified
pre-build) so it CANNOT suppress them; and the common-noun residual (shops/streets) is NER-untaggable
(only WordNet-animacy could touch it, and 29513 REJECTED WordNet-animacy for polysemy). Report the
proper-vs-common split + spaCy's own PERSON-mistyping (no free lunch).
POSITIVE CONTROL (Gate D, FULL): no-gate arm reproduces POS-cell NLTK arm n_inanimate_agent~=196,
n_events~=2601 (CITED). If not, wiring drifted -> flag, distrust delta.

Pre-reg: preregs/2026-07-24_read_events_supply_ner_entitytype_litbank_v1.md
Contract: INLINE-LOCAL foreground-to-completion; LOCAL-ONLY (no bank/push/commit). ASCII-only.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (no-gate vs NER-gate event-list hashes differ when any suppression occurs)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - crlb_n/a: proxy inanimate-agent COUNT comparison; no Cramer-Rao floor applies
# - baseline_in_band N/A (noise count not accuracy) -> discriminator-fires + positive-control
# - discriminator can-fail (rel<=0 CLEAN_NEGATIVE / net_fix<0 reachable); FULL IS full-N (25 books)
# - HARD_PASS strictly above floor (rel>=0.15 vs CLEAN_NEG 0.0; gap)
# - real_code_path: self-test builds real reader (W/clf/gate/sel_fn) + real spaCy NER + extractor
# - calibration_check: default_ok_for_this_regime (pretrained spaCy NER + fixed WordNet; band=effect)
# - deterministic_seeding: fixed SEED; no hash()-seeded RNG; no list(set()) ordering
# - all numbers MEASURED@ / CITED@ / HYPOTHESIZED@
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402

# reuse the 29520 events-fix cell: score_events, is_inanimate_agent, is_nonverb_pred, build_reader,
# parse_conll_sentences, the D-chain (D.ORC / D.M / D.E), _PRONOUNS, _ANIM_ROOTS, LITBANK_DIR.
import experiments.exp_read_events_fix_role_reader_litbank_v1 as EF  # noqa: E402
D = EF.D
ORC = D.ORC
M = D.M
E = D.E

ANCHOR_NAME = "read_events_supply_ner_entitytype_litbank_v1"
SEED = 20260724
LITBANK_DIR = EF.LITBANK_DIR

# ---- pre-registered bands (see prereg) ----
HP_REL_REDUCTION_196 = 0.15         # HARD_PASS: NER cuts inanimate-agent count >=15% rel AND net>0
CLEAN_NEG_REL = 0.0                 # CLEAN_NEGATIVE: NER cuts nothing that was in the 196
# positive-control (Gate D) against POS-cell / 29520 NLTK real-reader arm (CITED)
CITED_NONVERB = 160    # CITED@data/exp_read_events_supply_grammar_spacy_pos_litbank_v1/metrics.json:gate.level2_full_extractor.nltk.n_nonverb_pred
CITED_INANIMATE = 196  # CITED@...nltk.n_inanimate_agent
CITED_NEVENTS = 2601   # CITED@...nltk.n_events
POS_CTRL_TOL = 0.15

# spaCy NER types that are non-person PLACE / ORG / thing -> suppress as agent
PLACE_ORG_TYPES = frozenset({"GPE", "LOC", "ORG", "FAC"})
# locative / existential / stative predicates that LEGITIMATELY take a place subject -> do NOT
# suppress (guards the person-selecting simplification against "England lies...", "the house stood")
LOCATIVE_STATIVE = frozenset({
    "be", "is", "are", "was", "were", "been", "being", "am",
    "stand", "stands", "stood", "standing",
    "lie", "lies", "lay", "lain", "lying",
    "remain", "remains", "remained", "exist", "exists", "existed",
    "sit", "sits", "sat", "sitting", "rest", "rests", "rested",
    "rise", "rises", "rose", "risen", "extend", "extends", "extended",
    "stretch", "stretches", "stretched", "border", "borders", "bordered",
    "overlook", "overlooks", "overlooked", "contain", "contains", "contained",
    "hold", "holds", "held", "surround", "surrounds", "surrounded", "lie_in", "adjoin"})


def _norm(tok: str) -> str:
    """Lowercase + strip surrounding punctuation (matches ORC low-token normalization)."""
    return tok.lower().strip(".,'\"!?;:")


def is_person_plausible(agent: str) -> bool:
    """True if the agent is clearly person/animate: a personal pronoun, or a WordNet-animate noun.
    Used for the OVER-SUPPRESSION break count (a suppressed person-plausible agent = a break)."""
    if agent is None:
        return False
    w = agent.strip().lower()
    if not w or w == "?":
        return False
    if w in EF._PRONOUNS:
        return True
    syns = wn.synsets(w, "n")
    if not syns:
        return False  # OOV -> cannot confirm person; a place-typed OOV is more likely a real place
    for s in syns[:4]:
        for path in s.hypernym_paths():
            for h in path:
                if h.name() in EF._ANIM_ROOTS:
                    return True
    return False


# ===========================================================================
# spaCy NER: run natively on each raw sentence (best NER context), map token -> entity type.
# NER is used ONLY to TYPE agent tokens; the extractor still uses NLTK POS (one variable = the gate).
# ===========================================================================
def make_spacy_ner():
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer"])

    def ent_map(raw):
        doc = nlp(raw)
        m = {}
        n_place = 0
        for ent in doc.ents:
            for t in ent:
                k = _norm(t.text)
                if k and k not in m:      # first occurrence wins (deterministic)
                    m[k] = ent.label_
            if ent.label_ in PLACE_ORG_TYPES:
                n_place += 1
        return m, n_place

    return ent_map


# ===========================================================================
# extractor parameterized by the NER-gate (ONE variable). gate_on=False reproduces the POS-cell
# NLTK arm bit-for-bit. gate_on=True suppresses agents NER-typed as PLACE/ORG for a non-locative pred.
# ===========================================================================
def extract_events_ner(raw, W, clf, gate_fn, sel_fn, emap, gate_on,
                       use_dohave=True, use_ecm=False):
    carried_agent = None
    tups = []
    supp = []   # (pred, agent, patient, ner_type) suppressed this sentence
    for clause_text in ORC.split_sentences(raw):
        tagged = ORC.pos_tag_sentence(clause_text)     # NLTK POS (the 196 baseline path)
        if not tagged:
            continue
        heads = M.decode_clause(tagged, W)
        clause_tups, carried_agent, _ev = E.clause_predicate_pass_v4(
            tagged, heads, clf, gate_fn, carried_agent, sel_fn=sel_fn,
            use_dohave=use_dohave, use_ecm=use_ecm)
        for t in clause_tups:
            pred, agent, patient = t[0], t[1], t[2]
            atype = emap.get(_norm(agent), "") if agent not in (None, "?") else ""
            if (gate_on and agent not in (None, "?") and atype in PLACE_ORG_TYPES
                    and _norm(pred) not in LOCATIVE_STATIVE):
                supp.append((pred, agent, patient, atype))
                agent = "?"     # SUPPRESS the place/org agent (glass-box supply gate)
            tups.append((pred, agent, patient))
    return tups, supp


def _events_hash(events):
    b = json.dumps(events, sort_keys=False, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


# ===========================================================================
# main gate: NER-gate off vs on over the LitBank books
# ===========================================================================
def run_gate(W, clf, gate_fn, sel_fn, ner_fn, max_books=None, collect_glass=12):
    books = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    books = [b for b in books if os.path.getsize(b) > 1000]
    if max_books is not None:
        books = books[:max_books]

    ev_nogate, ev_ner = [], []
    all_supp = []               # (pred, agent, patient, ner_type, book, sent) suppressed
    inan_cases = []             # per no-gate inanimate agent: (agent, ner_type, pred, book, sent)
    ner_total_place_tags = 0
    glass = []                  # sentences with a no-gate inanimate agent (proper vs common)

    for bi, path in enumerate(books):
        pid = os.path.splitext(os.path.basename(path))[0]
        sents = EF.parse_conll_sentences(path)
        for si, toks in enumerate(sents):
            raw = " ".join(toks)
            emap, n_place = ner_fn(raw)
            ner_total_place_tags += n_place

            e0, _ = extract_events_ner(raw, W, clf, gate_fn, sel_fn, emap, gate_on=False)
            e1, supp = extract_events_ner(raw, W, clf, gate_fn, sel_fn, emap, gate_on=True)
            ev_nogate.extend(e0)
            ev_ner.extend(e1)
            for s in supp:
                all_supp.append((s[0], s[1], s[2], s[3], pid, si))

            # classify every no-gate inanimate agent by its NER type (the proper/common split)
            sent_inan = []
            for (pred, agent, patient) in e0:
                if EF.is_inanimate_agent(agent):
                    atype = emap.get(_norm(agent), "")
                    inan_cases.append((agent, atype, pred, pid, si))
                    sent_inan.append((pred, agent, patient, atype))

            if sent_inan and len(glass) < collect_glass:
                glass.append({
                    "book": pid, "sent_idx": si, "text": raw[:220],
                    "nogate_events": e0, "ner_events": e1,
                    "inanimate_agents": [
                        {"pred": p, "agent": a, "patient": pt, "ner_type": atp or "UNTAGGED",
                         "class": ("proper_ner_place" if atp in PLACE_ORG_TYPES
                                   else "ner_person_mistyped" if atp == "PERSON"
                                   else "common_untagged" if atp == ""
                                   else "other_ner_" + atp),
                         "suppressed": atp in PLACE_ORG_TYPES and _norm(p) not in LOCATIVE_STATIVE}
                        for (p, a, pt, atp) in sent_inan],
                })

        if max_books is None:
            print(f"[gate] book {bi+1}/{len(books)} {pid} done "
                  f"(cum nogate_ev={len(ev_nogate)} suppressed={len(all_supp)} "
                  f"place_tags={ner_total_place_tags})", flush=True)

    # ---- scores ----
    sc0, _ = EF.score_events(ev_nogate)
    sc1, _ = EF.score_events(ev_ner)

    # ---- residual split of the no-gate inanimate agents by NER type ----
    split = {"proper_ner_place": 0, "ner_person_mistyped": 0, "common_untagged": 0, "other_ner": 0}
    split_examples = {"proper_ner_place": [], "ner_person_mistyped": [],
                      "common_untagged": [], "other_ner": []}
    for (agent, atype, pred, pid, si) in inan_cases:
        if atype in PLACE_ORG_TYPES:
            key = "proper_ner_place"
        elif atype == "PERSON":
            key = "ner_person_mistyped"
        elif atype == "":
            key = "common_untagged"
        else:
            key = "other_ner"
        split[key] += 1
        if len(split_examples[key]) < 15:
            split_examples[key].append({"agent": agent, "pred": pred,
                                        "ner_type": atype or "UNTAGGED", "book": pid, "sent": si})

    # ---- suppression accounting + over-suppression breaks ----
    n_suppressed = len(all_supp)
    n_supp_confirmed_inan = 0   # suppressed AND WordNet-inanimate (clearly correct; was in the 196)
    n_supp_ner_only = 0         # suppressed, NOT WordNet-inanimate, NOT person-plausible (NER-extra)
    n_supp_break = 0            # suppressed AND person-plausible (OVER-SUPPRESSION break)
    break_examples, ner_extra_examples = [], []
    for (pred, agent, patient, atype, pid, si) in all_supp:
        if is_person_plausible(agent):
            n_supp_break += 1
            if len(break_examples) < 20:
                break_examples.append({"agent": agent, "pred": pred, "ner_type": atype,
                                       "book": pid, "sent": si})
        elif EF.is_inanimate_agent(agent):
            n_supp_confirmed_inan += 1
        else:
            n_supp_ner_only += 1        # OOV proper place WordNet missed -> NER's extra value
            if len(ner_extra_examples) < 20:
                ner_extra_examples.append({"agent": agent, "pred": pred, "ner_type": atype,
                                           "book": pid, "sent": si})

    net_fix = (n_supp_confirmed_inan + n_supp_ner_only) - n_supp_break
    inan0 = sc0["n_inanimate_agent"]
    inan1 = sc1["n_inanimate_agent"]
    rel_reduction_196 = ((inan0 - inan1) / inan0) if inan0 > 0 else 0.0

    # combined place-agent noise (is_inanimate OR NER-place-typed) reduction -- fuller picture
    combined0 = inan0 + n_supp_ner_only   # no-gate: WordNet-inanimate + NER-only places (both wrong)
    combined1 = inan1                      # after gate the NER-only places are suppressed too
    combined_rel = ((combined0 - combined1) / combined0) if combined0 > 0 else 0.0

    # ---- verdict ----
    if rel_reduction_196 >= HP_REL_REDUCTION_196 and net_fix > 0:
        vg = "HARD_PASS"
    elif rel_reduction_196 <= CLEAN_NEG_REL or net_fix < 0:
        vg = "CLEAN_NEGATIVE"
    else:
        vg = "MIDDLE_BAND"

    pc_inan_ok = abs(inan0 - CITED_INANIMATE) <= POS_CTRL_TOL * CITED_INANIMATE
    pc_nev_ok = abs(sc0["n_events"] - CITED_NEVENTS) <= POS_CTRL_TOL * CITED_NEVENTS

    return {
        "n_books": len(books),
        "no_gate": sc0,
        "ner_gate": sc1,
        "rel_reduction_196": rel_reduction_196,
        "combined_place_agent_noise": {
            "no_gate": combined0, "ner_gate": combined1, "rel_reduction": combined_rel,
        },
        "residual_split_of_196": split,
        "residual_split_examples": split_examples,
        "suppression_accounting": {
            "n_suppressed": n_suppressed,
            "n_supp_confirmed_inanimate": n_supp_confirmed_inan,
            "n_supp_ner_only_extra_catches": n_supp_ner_only,
            "n_supp_break_over_suppression": n_supp_break,
            "net_fix": net_fix,
            "break_examples": break_examples,
            "ner_extra_catch_examples": ner_extra_examples,
        },
        "agent_unfilled": {"no_gate": sc0["n_agent_unfilled"], "ner_gate": sc1["n_agent_unfilled"]},
        "ner_total_place_tags": ner_total_place_tags,
        "positive_control_vs_pos_cell": {
            "cited_inanimate": CITED_INANIMATE, "measured_nogate_inanimate": inan0,
            "cited_n_events": CITED_NEVENTS, "measured_nogate_n_events": sc0["n_events"],
            "inanimate_reproduced": bool(pc_inan_ok), "n_events_reproduced": bool(pc_nev_ok),
        },
        "discriminator_fires": bool(inan0 > 0 and ner_total_place_tags > 0),
        "arms_differ": bool(_events_hash(ev_nogate) != _events_hash(ev_ner)),
        "n_suppressed": n_suppressed,
        "verdict_gate": vg,
        "glass_box": glass,
    }


# ===========================================================================
# atomic metrics + markers
# ===========================================================================
def _out_dir(run_mode):
    return os.path.join(_REPO, "data",
                        f"exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
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
    os.makedirs(output_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ===========================================================================
# formula self-test (REAL code path)
# ===========================================================================
def self_test():
    print("[self-test] building spaCy NER + hard-case typing ...", flush=True)
    ner_fn = make_spacy_ner()
    m, npl = ner_fn("England slept and London was silent while Parliament passed the bill.")
    assert m.get("england") == "GPE", f"spaCy: england not GPE ({m.get('england')})"
    assert m.get("parliament") == "ORG", f"spaCy: parliament not ORG ({m.get('parliament')})"
    assert npl >= 2, f"spaCy tagged <2 place/org entities ({npl})"
    # documented own-error (no free lunch): 19c literary place names typed PERSON, not GPE/LOC
    m2, _ = ner_fn("At Howard Grove the family gathered, and Kent received them warmly.")
    print(f"[self-test] spaCy own-error probe: howard={m2.get('howard')} grove={m2.get('grove')} "
          f"kent={m2.get('kent')} (expect PERSON = the wall this cell locates)", flush=True)
    # person-plausible detector
    assert is_person_plausible("he") and is_person_plausible("man"), "person-plausible miss"
    assert not is_person_plausible("england") and not is_person_plausible("?"), "place flagged person"

    print("[self-test] building REAL banked reader (smoke budget) ...", flush=True)
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = EF.build_reader("smoke")
    assert pinfo["uas_dev"] > 0.5, f"parser UAS suspiciously low: {pinfo}"

    # REAL code path: extractor both arms on a real clause
    raw0 = sent_text[order[0]]
    emap0, _ = ner_fn(raw0)
    e0, _ = extract_events_ner(raw0, W, clf, gate, sel_fn, emap0, gate_on=False)
    e1, _ = extract_events_ner(raw0, W, clf, gate, sel_fn, emap0, gate_on=True)
    print(f"[self-test] sample clause nogate={e0} ner={e1}", flush=True)

    # gate on a tiny book slice: discriminator fires; suppression => arms differ
    g = run_gate(W, clf, gate, sel_fn, ner_fn, max_books=3, collect_glass=3)
    assert g["discriminator_fires"], "GATE: no inanimate agents OR NER tagged 0 places (nothing to do)"
    ns = g["n_suppressed"]
    if ns > 0:
        assert g["arms_differ"], "META_RULE_AF: suppression occurred but event lists bit-identical"
    else:
        print("[self-test] NOTE: 0 suppressions in 3 smoke books -> arms identical (AF-exempt)",
              flush=True)
    sp = g["residual_split_of_196"]
    print(f"[self-test] (3 books) inan nogate={g['no_gate']['n_inanimate_agent']} "
          f"ner={g['ner_gate']['n_inanimate_agent']} rel={g['rel_reduction_196']:.3f} | "
          f"suppressed={ns} net_fix={g['suppression_accounting']['net_fix']} | "
          f"split proper={sp['proper_ner_place']} person_mistyped={sp['ner_person_mistyped']} "
          f"common={sp['common_untagged']} | verdict={g['verdict_gate']}", flush=True)
    print("[self-test] PASS", flush=True)
    return 0


# ===========================================================================
# full verdict
# ===========================================================================
def build_verdict(run_mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=25)
    print(f"[full] mode={run_mode} building spaCy NER + banked reader ...", flush=True)
    ner_fn = make_spacy_ner()
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = EF.build_reader(run_mode)
    print(f"[full] parser uas={pinfo['uas_dev']}", flush=True)

    max_books = 3 if run_mode == "smoke" else None
    g = run_gate(W, clf, gate, sel_fn, ner_fn, max_books=max_books, collect_glass=12)
    sc0, sc1 = g["no_gate"], g["ner_gate"]
    sp = g["residual_split_of_196"]
    sa = g["suppression_accounting"]
    pc = g["positive_control_vs_pos_cell"]

    print(f"[full] n_books={g['n_books']} ner_place_tags={g['ner_total_place_tags']}", flush=True)
    print(f"[full] inanimate_agent nogate={sc0['n_inanimate_agent']} ner={sc1['n_inanimate_agent']} "
          f"(rel_reduction={g['rel_reduction_196']:+.3f})", flush=True)
    print(f"[full] residual-split of the no-gate inanimate agents: proper_ner_place="
          f"{sp['proper_ner_place']} ner_person_mistyped={sp['ner_person_mistyped']} "
          f"common_untagged={sp['common_untagged']} other={sp['other_ner']}", flush=True)
    print(f"[full] suppression: n={sa['n_suppressed']} confirmed_inan={sa['n_supp_confirmed_inanimate']} "
          f"ner_extra={sa['n_supp_ner_only_extra_catches']} breaks={sa['n_supp_break_over_suppression']} "
          f"net_fix={sa['net_fix']}", flush=True)
    print(f"[full] agent_unfilled nogate={g['agent_unfilled']['no_gate']} "
          f"ner={g['agent_unfilled']['ner_gate']} (honest cost: suppression -> unfilled)", flush=True)
    print(f"[full] positive-control: nogate_inan={pc['measured_nogate_inanimate']} "
          f"(cited {pc['cited_inanimate']}, reproduced={pc['inanimate_reproduced']}) "
          f"nogate_n_events={pc['measured_nogate_n_events']} (cited {pc['cited_n_events']}, "
          f"reproduced={pc['n_events_reproduced']})", flush=True)

    # tier
    if not (pc["inanimate_reproduced"] and pc["n_events_reproduced"]):
        tier = "HARD_FAIL_POSITIVE_CONTROL"
        summary = (f"no-gate arm did NOT reproduce POS-cell NLTK (inanimate "
                   f"{pc['measured_nogate_inanimate']} vs cited {pc['cited_inanimate']}; n_events "
                   f"{pc['measured_nogate_n_events']} vs {pc['cited_n_events']}); delta untrusted")
    else:
        vg = g["verdict_gate"]
        if vg == "HARD_PASS":
            tier = "HARD_PASS"
            summary = (f"SUPPLY-NER VALIDATED: NER gate cuts inanimate-agent noise "
                       f"{sc0['n_inanimate_agent']}->{sc1['n_inanimate_agent']} "
                       f"(rel {g['rel_reduction_196']:+.3f} >= {HP_REL_REDUCTION_196}, net_fix "
                       f"{sa['net_fix']}); proper-noun places suppressed")
        elif vg == "CLEAN_NEGATIVE":
            tier = "CLEAN_NEGATIVE"
            summary = (f"NER gate does NOT reduce inanimate-agent noise "
                       f"{sc0['n_inanimate_agent']}->{sc1['n_inanimate_agent']} "
                       f"(rel {g['rel_reduction_196']:+.3f}, net_fix {sa['net_fix']}); spaCy own-errors "
                       f"/ common-noun residual / breaks dominate")
        else:
            tier = "MIDDLE_BAND"
            summary = (f"NER gate PARTIAL: inanimate-agent {sc0['n_inanimate_agent']}->"
                       f"{sc1['n_inanimate_agent']} (rel {g['rel_reduction_196']:+.3f}, below "
                       f"{HP_REL_REDUCTION_196}); residual = {sp['common_untagged']} common-noun + "
                       f"{sp['ner_person_mistyped']} spaCy-PERSON-mistyped")

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"{tier}: {summary}. Split-of-196: proper_ner_place={sp['proper_ner_place']} "
                   f"(NER-fixable) vs ner_person_mistyped={sp['ner_person_mistyped']} (spaCy own-error) "
                   f"vs common_untagged={sp['common_untagged']} (NER can't tag). Suppressed "
                   f"{sa['n_suppressed']} (ner-extra {sa['n_supp_ner_only_extra_catches']} places WordNet "
                   f"missed; {sa['n_supp_break_over_suppression']} breaks; net_fix {sa['net_fix']}); "
                   f"{g['n_books']} books.")

    metrics = {
        "verdict": tier,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": SEED,
        "parser_uas_dev": pinfo["uas_dev"],
        "gate": g,
        "bands": {
            "HP_REL_REDUCTION_196": HP_REL_REDUCTION_196,
            "CLEAN_NEG_REL": CLEAN_NEG_REL,
            "positive_control_tol": POS_CTRL_TOL,
            "place_org_types": sorted(PLACE_ORG_TYPES),
        },
        "arms_differ_verified": bool(g["arms_differ"] or g["n_suppressed"] == 0),
        "arms_differ_exempted": (g["n_suppressed"] == 0),
        "baseline_in_band": "n/a_noise_count_metric; discriminator_fires + positive_control used",
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "proxy inanimate-agent count comparison; no Cramer-Rao floor applies",
        "calibration_check": "default_ok_for_this_regime",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "deterministic_seeding": True,
        "progress_logging": "per-book flush prints in run_gate",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "notes": ("SUPPLY-NER cell. ONE variable = NER-gate on/off. Base extractor = 29520/POS-cell "
                  "NLTK path (ORC.pos_tag_sentence + banked reader W/clf/gate/sel_fn); gate_on=False "
                  "reproduces the POS-cell NLTK arm (inanimate=196 positive control). spaCy NER "
                  "(en_core_web_sm) run natively on each raw sentence types agent tokens; agents typed "
                  "GPE/LOC/ORG/FAC for a non-locative predicate are SUPPRESSED (agent->'?'). NER = "
                  "SUPPLIED preprocessing (fixed typing), NOT an LLM in the glass-box reasoning. "
                  "HONEST WALL (pre-build MEASURED): spaCy MIS-TYPES 19c literary places (Howard "
                  "Grove/Kent) as PERSON -> NOT suppressed; and common-noun things (shops/streets) are "
                  "NER-UNTAGGED -> NER cannot fix them (only WordNet-animacy could, which 29513 "
                  "REJECTED for polysemy). Suppression trades a wrong place-agent for an unfilled "
                  "agent (n_agent_unfilled rises); NER's own PERSON-mistyping + common-noun residual "
                  "reported (no free lunch). Combined place-agent-noise metric (is_inanimate OR "
                  "NER-place) shows NER's extra catches beyond WordNet."),
    }
    _write_metrics(output_dir, metrics)
    print(f"[full] wrote {os.path.join(output_dir, 'metrics.json')} elapsed={elapsed:.1f}s", flush=True)

    print("[full] === GLASS-BOX: no-gate inanimate agents (proper_ner_place vs common_untagged) ===",
          flush=True)
    for gb in g["glass_box"][:10]:
        print(f"  [{gb['book']} S{gb['sent_idx']}] {gb['text']}", flush=True)
        for r in gb["inanimate_agents"]:
            print(f"    inan-agent '{r['agent']}' pred='{r['pred']}' NER={r['ner_type']} "
                  f"class={r['class']} suppressed={r['suppressed']}", flush=True)
    print("[full] === spaCy NER own-error / over-suppression breaks ===", flush=True)
    for r in sa["break_examples"][:8]:
        print(f"  BREAK: '{r['agent']}' (NER {r['ner_type']}) pred='{r['pred']}' "
              f"[{r['book']} S{r['sent']}]", flush=True)
    print("[full] === NER-extra catches (place-agents WordNet-animacy MISSED) ===", flush=True)
    for r in sa["ner_extra_catch_examples"][:8]:
        print(f"  EXTRA: '{r['agent']}' (NER {r['ner_type']}) pred='{r['pred']}' "
              f"[{r['book']} S{r['sent']}]", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return build_verdict("smoke" if args.smoke else "full")


if __name__ == "__main__":
    _od = _out_dir("smoke" if ("--smoke" in sys.argv) else "full")
    try:
        rc = main()
        sys.exit(rc)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
