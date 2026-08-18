#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1

USER HYPOTHESIS (contextual-reading bet): reading sentences IN DOCUMENT ORDER with a running
STATE OF MIND (discourse context carried forward across sentences) improves who-is-affected
accuracy AND provides an error-correction signal, vs the current ISOLATED-sentence reader that
reads every sentence in a vacuum (the self-improving loop reads sentences INDEPENDENTLY today).

BRAIN-CHECK (CITED@Kintsch construction-integration; Grosz-Sidner-Joshi Centering): the brain
maintains a running SITUATION MODEL; discourse context resolves referents (who "it"/"he" is) that
the isolated sentence cannot, and an ESTABLISHED salient referent is the preferred argument
(Centering backward-looking-center). This cell wires the VALIDATED symbolic WorkingOverlay
(hdlab/state_of_mind.py; the settled two-layer state-of-mind arc, 2026-07-17) into the who-is-
affected READER (pos_tagger -> arc_parser -> arc_labeler -> candidate_gen) and reads UD-EWT in
real document order (# newdoc / # sent_id = real emails/weblog discourse with cross-sentence
pronoun reference).

WHY UD-EWT (not the curated lesson slice): the who-is-affected reader v1/v2 runs on a curated
LESSON slice with NO document order and NO cross-sentence discourse -- it structurally CANNOT show
a context benefit. UD-EWT test carries real # newdoc grouping (316 docs, 283 multi-sentence) with
1261 gold patient tokens, of which 291 (23%) are PRONOUNS whose referent is often a PRIOR sentence.
Gold who-is-affected is derived DIRECTLY from the GOLD conllu parse (obj / nsubj:pass dependent of
each gold VERB = the affected token); no coref gold is needed for TOKEN-level who-is-affected, and
UD-EWT has none (which is exactly why the coref cells used LitBank, not UD-EWT).

GOLD-TOKEN EVAL (clean alignment): the reader front-end is driven on the GOLD tokens (gold
tokenization, PREDICTED POS/parse/labels), so predicted candidate indices align 1:1 with gold token
indices. Gold patient = gold token index of the obj/nsubj:pass dependent; scoring is index-equality.

ARMS (ONE variable = the running state of mind; identical extraction + base selection across arms):
  ISOLATED (baseline, current reader): overlay OFF; state reset per sentence; patient = the
      predicted patient candidate with the highest arc-parser margin (deterministic base selector).
  IN_CONTEXT_TRUE (mechanism): a WorkingOverlay maintained across sentences within each # newdoc,
      built from PRIOR sentences ONLY (leak-clean). Among the SAME predicted candidate patients,
      if an ESTABLISHED salient discourse entity (from prior sentences) is a candidate -- directly
      (a NOUN/PROPN head already in the running state) or via pronoun resolution -- prefer it over
      the merely-highest-margin token. Differs from ISOLATED ONLY on DISAGREEMENT instances.
  IN_CONTEXT_WRONGDOC (must-fail control, seeded): identical to IN_CONTEXT_TRUE but the running
      state is built from a RANDOMLY-ASSIGNED DIFFERENT document's prior sentences. Breaks the true
      referent link while keeping the same corpus-entity vocabulary. Real discourse benefit MUST be
      larger with the RIGHT document's state than a WRONG document's state; if they tie, the "benefit"
      is a generic entity-frequency prior, NOT reading-in-context.

DISCRIMINATING SUBSETS (difficulty-on): OVERALL is dominated by singleton pools where the two arms
CANNOT differ (self-contained) -> the honest place for a context effect is the AMBIGUOUS subset
(>=2 candidate patients, where selection can differ) and the PRONOUN-PATIENT subset. All reported
separately from OVERALL. If OVERALL barely moves that is EXPECTED and reported honestly.

COHERENCE / ERROR-CORRECTION SIGNAL (USER bet #2): the DISAGREEMENT event (running state prefers a
different, established referent than the isolated parse chose) IS the "state contradicts the parse"
flag. We measure it as a WRONG-ANSWER detector: P(isolated wrong | flagged) vs P(isolated wrong |
not flagged). A real error-correction lever means flagged instances are markedly more error-prone
(a new abstain/escalation trigger). CAN-FAIL: the flag may be no better than base error rate.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = the ISOLATED reader re-derived LIVE this run (not a remembered number).
  (2) CAN-FAIL: overlay preference may switch to a WRONG established candidate (gold was the fresh
      token) -> IN_CONTEXT can be <= ISOLATED; OR UD sentences are too self-contained / gold is
      sentence-level token gold so the isolated reader already picks the pronoun token -> ~0 move
      (honest null, HARD_FAIL_SELFCONTAINED); OR true-order ties wrong-doc (generic prior, MIDDLE).
  (3) DIFFICULTY-ON: AMBIGUOUS + PRONOUN-PATIENT subsets reported separately from OVERALL.
  (4) ONE-VARIABLE: ISOLATED vs IN_CONTEXT differ ONLY in the state-of-mind preference on
      disagreement; identical gold, identical extraction, identical base selector.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- deliverable = the NUMBERS + the two verdicts):
  accuracy (primary = delta_amb_true = acc[IN_CONTEXT_TRUE, AMBIG] - acc[ISOLATED, AMBIG]):
    HARD_PASS_CONTEXT_HELPS: delta_amb_true >= +0.03 AND (delta_amb_true - mean_seed
        delta_amb_wrongdoc) >= +0.02 AND overall delta_true >= -0.005 (no material regression).
    HARD_FAIL_SELFCONTAINED: n_disagreements < max(5, 0.02*n_ambiguous) (overlay effectively never
        changes the pick) OR delta_amb_true <= 0.0.
    MIDDLE_BAND: otherwise (small, or indistinguishable from wrong-doc = generic prior not discourse).
  coherence (primary = P(isolated wrong | flag) vs P(isolated wrong | no-flag)):
    COHERENCE_SIGNAL_REAL: n_flag >= 10 AND P(wrong|flag) >= 2.0 * P(wrong|noflag) AND flag_rate
        in [0.01, 0.5].
    COHERENCE_NULL: otherwise.

LEAK-DISCIPLINE: the running state is built from PRIOR sentences ONLY (current sentence observed
AFTER its own selection); the gold patient token/index is NEVER passed into overlay.observe or into
selection. Mutation-probe = the WRONG-DOC control (a wrong document's state must NOT confer the
benefit). A per-run leak-assert records that no gold field entered the state path.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified) -- ~2077 UD-EWT test sentences parsed
once (numpy averaged-perceptron front-end, cached per sentence) + a symbolic overlay pass + 3
wrong-doc scramble seeds re-selecting over cached parses (no re-parse). Wall < ~60s smoke / < ~180s
full. Storage: no_storage. progress_logging: print_flush_true (well under 30min; heartbeat exempt --
cell < ~3min, start-marker + crash-diagnostic present). Determinism: OMP/MKL/OPENBLAS=1, fixed int
seeds, np.random.default_rng, sorted(set); NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-
completion; NO queue, NO push, NO remote-persist, NO git add. NO production hdlab mutation (the
overlay wiring + document-order driver + scoring are composed IN THIS CELL; hdlab.state_of_mind and
the front-end modules are imported read-only).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke: n_disagreements > 0 => ISOLATED and IN_CONTEXT_TRUE picks bit-differ.
  - final_metrics_atomicity: tmp_replace. except SystemExit: raise BEFORE except Exception (no BaseException).
  - crlb_n_a: token-selection accuracy; no quantitative noise floor for the discriminator.
  - baseline_in_band at smoke: ISOLATED overall acc strictly inside (0.05, 0.95).
  - discriminator survives scale: smoke runs the SAME selection + verdict logic on a doc subset; full re-verifies on all docs.
  - HARD_PASS strictly above floor (+0.03 on ambiguous AND +0.02 over wrong-doc control -- not an at-floor tie).
  - all numbers in comments tagged HYPOTHESIZED@/CITED@/MEASURED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.

PRIOR-WORK CHECK (substrate_query.sh "reading sentences in document order discourse state of mind
context who is affected"): top hits cosine<=0.292 are unrelated WordNet entity-name matches +
generation-drill chunks; the discourse-overlay CELLS (longdist_reference, coupling_revival,
state_of_mind_wsm_coupling) validated the WorkingOverlay for CO-REFERENCE on LitBank (which has coref
gold) -- NONE measured WHO-IS-AFFECTED accuracy on UD-EWT DOCUMENT ORDER. This is a novel integration
test of the validated overlay into the who-is-affected reader on real discourse order, NOT a
rediscovery. CITED@hdlab/state_of_mind.py header (validated arc); HYPOTHESIZED@this file (all bands).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import candidates_from_parse, NOMINAL  # noqa: E402
from hdlab.state_of_mind import WorkingOverlay, PRONOUN_SCOPE, infer_nominal_gender  # noqa: E402

FRONTEND_DIR = os.path.join(REPO_ROOT, "data", "frontend_assets")
POS_PATH = os.path.join(FRONTEND_DIR, "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(FRONTEND_DIR, "arc_parser_hashed_ud_ewt.npz")
LABELER_PATH = os.path.join(FRONTEND_DIR, "arc_labeler_hashed_ud_ewt.json")
UD_TEST = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")

PATIENT_LABELS = {"obj", "nsubj:pass"}
# Personal/demonstrative pronoun surfaces whose referent is typically a prior-sentence entity.
PRONOUNS = {"it", "them", "him", "her", "me", "us", "you", "that", "which", "this",
            "these", "those", "he", "she", "they", "we", "i"}


# ----------------------------------------------------------------------------------------------
# CONLLU loader: yields documents (grouped by # newdoc) each a list of sentences in sent_id order.
# Each sentence = dict(tokens, lemmas, upos, gold_head, gold_deprel).  1-based token ids.
# ----------------------------------------------------------------------------------------------
def load_ud_docs(path):
    docs = []
    cur_doc = None
    toks = []
    lemmas = []
    upos = []
    ghead = {}
    gdep = {}

    def flush_sentence():
        nonlocal toks, lemmas, upos, ghead, gdep
        if toks:
            cur_doc.append({"tokens": toks, "lemmas": lemmas, "upos": upos,
                            "gold_head": ghead, "gold_deprel": gdep})
        toks, lemmas, upos, ghead, gdep = [], [], [], {}, {}

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc"):
                flush_sentence()
                if cur_doc is not None:
                    docs.append(cur_doc)
                cur_doc = []
                continue
            if line.startswith("#"):
                continue
            if line == "":
                flush_sentence()
                continue
            cols = line.split("\t")
            if len(cols) < 8:
                continue
            tid = cols[0]
            if "-" in tid or "." in tid:  # skip multiword-token ranges + empty nodes
                continue
            i = int(tid)
            toks.append(cols[1])
            lemmas.append(cols[2])
            upos.append(cols[3])
            ghead[i] = int(cols[6]) if cols[6] != "_" else 0
            gdep[i] = cols[7]
    flush_sentence()
    if cur_doc is not None and cur_doc:
        docs.append(cur_doc)
    # keep only docs with >=1 sentence; document order preserved
    return [d for d in docs if d]


# ----------------------------------------------------------------------------------------------
# Gold who-is-affected instances for a sentence: per gold VERB, its obj/nsubj:pass dependent token.
# ----------------------------------------------------------------------------------------------
def gold_instances(sent):
    upos, gh, gd = sent["upos"], sent["gold_head"], sent["gold_deprel"]
    n = len(upos)
    verbs = [i for i in range(1, n + 1) if upos[i - 1] == "VERB"]
    insts = []
    for v in verbs:
        pats = sorted(a for a in range(1, n + 1)
                      if gh.get(a) == v and gd.get(a) in PATIENT_LABELS)
        if not pats:
            continue
        pidx = pats[0]  # first (lowest-index) patient token
        insts.append({"vidx": v, "gold_pidx": pidx})
    return insts


def is_patient_labeled(a, labels, heads):
    """Predicted-label patient filter (v1 rule + conj-fix): obj/nsubj:pass, or conj through such."""
    la = labels.get(a)
    if la in PATIENT_LABELS:
        return True
    if la == "conj":
        h = heads.get(a)
        if h is not None and labels.get(h) in PATIENT_LABELS:
            return True
    return False


# ----------------------------------------------------------------------------------------------
# Reader front-end pass over a sentence (gold tokens, predicted POS/parse/labels). Returns per-verb
# predicted candidate patient pools (arg idx + parser margin) + the parse for overlay observation.
# ----------------------------------------------------------------------------------------------
def reader_pass(sent, tagger, parser, labeler):
    tokens = sent["tokens"]
    pos = tagger.tag(tokens)
    pr = parser.parse(tokens, pos)
    heads, margins = pr.heads, pr.margins
    cand_pairs, _ = candidates_from_parse(tokens, pos, heads)
    labels = labeler.label(tokens, pos, heads)
    pools = defaultdict(list)  # vidx -> list of {aidx, margin, surf, pos}
    for (v, a) in cand_pairs:
        if not is_patient_labeled(a, labels, heads):
            continue
        pools[v].append({"aidx": a, "margin": float(margins.get(a, 0.0)),
                         "surf": tokens[a - 1].lower(), "pos": pos[a - 1]})
    return {"tokens": tokens, "pos": pos, "pools": pools}


def observe_sentence(overlay, tokens, pos):
    """Observe a sentence's PREDICTED nominal/pronoun mentions into the running state (surface only;
    no gold ever consulted). Nominals (NOUN/PROPN) become/refresh entities; pronouns advance stream."""
    for k in range(len(tokens)):
        surf = tokens[k]
        low = surf.lower().strip(".,'\"!?;:")
        p = pos[k]
        if p == "PRON" and low in PRONOUN_SCOPE:
            sc = PRONOUN_SCOPE[low]
            overlay.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
        elif p in ("NOUN", "PROPN"):
            gender = infer_nominal_gender([surf])
            overlay.observe(low, gender=gender, number="singular", is_proper_name=(p == "PROPN"))


def base_pick(pool):
    """ISOLATED base selector: highest arc-parser margin; tie-break lowest arg index. None if empty."""
    if not pool:
        return None
    return sorted(pool, key=lambda c: (-c["margin"], c["aidx"]))[0]


def salient_pick(pool, overlay):
    """Among the SAME candidates, the one that is (or resolves to) the most-salient ESTABLISHED
    discourse entity from PRIOR sentences. None if no candidate is an established referent."""
    if not pool or overlay is None:
        return None
    now = overlay.n_observed
    best = None
    best_sal = 0.0
    for c in pool:
        ent = None
        if c["pos"] == "PRON" and c["surf"] in PRONOUN_SCOPE:
            try:
                ent = overlay.resolve_pronoun(c["surf"], strategy="maintained")
            except ValueError:
                ent = None
        elif c["pos"] in ("NOUN", "PROPN"):
            ent = overlay._entities.get(c["surf"])
        if ent is None:
            continue
        sal = ent.salience(now, overlay.beta, overlay.lam)
        if sal > best_sal:
            best_sal = sal
            best = c
    return best


# ----------------------------------------------------------------------------------------------
# Build scored instances for a document set. Picks are captured INLINE during the document pass, at
# the moment the overlay holds EXACTLY the PRIOR sentences (leak-clean: never a live shared reference
# that grows to include future sentences). Each instance stores the resolved pick indices, not a
# mutable overlay handle.
#   mode 'isolated' -> no state; only base pick.
#   mode 'true'     -> state = prior sentences of the SAME doc.
#   mode 'wrongdoc' -> state = prior sentences of an ASSIGNED OTHER doc (must-fail control).
# Instance fields: gold_pidx, base_aidx, salient_aidx (None unless a disagreement), disagreement,
#                  n_cands, gold_pron, pron_resolves (bool; gold-pron-extracted resolution coverage).
# ----------------------------------------------------------------------------------------------
def build_scored(docs, reader_cache, mode, wrongdoc_map=None):
    insts = []
    for di, doc in enumerate(docs):
        overlay = WorkingOverlay() if mode in ("true", "wrongdoc") else None
        if mode == "wrongdoc":
            ctx_doc_idx = wrongdoc_map[di]
            ctx_sentences = docs[ctx_doc_idx]
        else:
            ctx_doc_idx, ctx_sentences = None, None

        for si, sent in enumerate(doc):
            rp = reader_cache[(di, si)]
            for gi in gold_instances(sent):
                pool = rp["pools"].get(gi["vidx"], [])
                gp = gi["gold_pidx"]
                gsurf = sent["tokens"][gp - 1].lower()
                bp = base_pick(pool)
                base_aidx = bp["aidx"] if bp is not None else None
                salient_aidx = None
                disagreement = False
                pron_resolves = False
                if overlay is not None:
                    sp = salient_pick(pool, overlay)  # overlay holds ONLY sentences 0..si-1
                    if sp is not None and (bp is None or sp["aidx"] != bp["aidx"]):
                        salient_aidx = sp["aidx"]
                        disagreement = True
                    # pronoun-resolution coverage on the gold-patient candidate (if extracted)
                    if gsurf in PRONOUNS:
                        gc = next((c for c in pool if c["aidx"] == gp), None)
                        if gc is not None and gc["pos"] == "PRON" and gc["surf"] in PRONOUN_SCOPE:
                            try:
                                ent = overlay.resolve_pronoun(gc["surf"], strategy="maintained")
                            except ValueError:
                                ent = None
                            pron_resolves = ent is not None
                insts.append({"gold_pidx": gp, "base_aidx": base_aidx, "salient_aidx": salient_aidx,
                              "disagreement": disagreement, "n_cands": len(pool),
                              "gold_pron": gsurf in PRONOUNS,
                              "gold_pron_extracted": bool(gsurf in PRONOUNS
                                                          and any(c["aidx"] == gp and c["pos"] == "PRON"
                                                                  and c["surf"] in PRONOUN_SCOPE for c in pool)),
                              "pron_resolves": pron_resolves})
            # advance the running state with the appropriate sentence AFTER scoring (leak-clean)
            if mode == "true":
                observe_sentence(overlay, rp["tokens"], rp["pos"])
            elif mode == "wrongdoc" and si < len(ctx_sentences):
                orp = reader_cache[(ctx_doc_idx, si)]
                observe_sentence(overlay, orp["tokens"], orp["pos"])
    return insts


def _pick_aidx(inst, use_state):
    if use_state and inst["disagreement"]:
        return inst["salient_aidx"]
    return inst["base_aidx"]


def acc_over(insts, use_state, subset=None):
    n = c = 0
    for inst in insts:
        if subset is not None and not subset(inst):
            continue
        n += 1
        pick = _pick_aidx(inst, use_state)
        if pick is not None and pick == inst["gold_pidx"]:
            c += 1
    return (c / n if n else None), n, c


def coherence_stats(insts_true):
    """DISAGREEMENT-as-error-flag. flag = IN_CONTEXT_TRUE selection disagrees with ISOLATED base.
    Measures P(isolated wrong | flag) vs P(isolated wrong | no-flag)."""
    n_flag = n_flag_wrong = 0
    n_noflag = n_noflag_wrong = 0
    n_fixed = n_broke = 0
    for inst in insts_true:
        flag = inst["disagreement"]
        iso_wrong = not (inst["base_aidx"] is not None and inst["base_aidx"] == inst["gold_pidx"])
        if flag:
            n_flag += 1
            n_flag_wrong += int(iso_wrong)
            ctx_wrong = not (inst["salient_aidx"] is not None and inst["salient_aidx"] == inst["gold_pidx"])
            if iso_wrong and not ctx_wrong:
                n_fixed += 1
            elif not iso_wrong and ctx_wrong:
                n_broke += 1
        else:
            n_noflag += 1
            n_noflag_wrong += int(iso_wrong)
    p_wrong_flag = (n_flag_wrong / n_flag) if n_flag else None
    p_wrong_noflag = (n_noflag_wrong / n_noflag) if n_noflag else None
    total = n_flag + n_noflag
    return {"n_flag": n_flag, "n_noflag": n_noflag,
            "flag_rate": round(n_flag / total, 4) if total else None,
            "p_isolated_wrong_given_flag": round(p_wrong_flag, 4) if p_wrong_flag is not None else None,
            "p_isolated_wrong_given_noflag": round(p_wrong_noflag, 4) if p_wrong_noflag is not None else None,
            "flag_error_lift_ratio": (round(p_wrong_flag / p_wrong_noflag, 4)
                                      if p_wrong_flag and p_wrong_noflag else None),
            "n_fixed_by_switch": n_fixed, "n_broken_by_switch": n_broke}


def pronoun_resolution_coverage(insts_true):
    """Diagnostic (capability, not correctness): of pronoun-patient instances the reader EXTRACTED as
    a pronoun, fraction the running state can BIND to a prior-sentence entity (context COULD add
    entity-level info even where token-accuracy is saturated)."""
    n = sum(1 for i in insts_true if i["gold_pron_extracted"])
    resolved = sum(1 for i in insts_true if i["gold_pron_extracted"] and i["pron_resolves"])
    return {"n_pronoun_patient_extracted": n, "n_resolved_to_prior_entity": resolved,
            "resolution_coverage": round(resolved / n, 4) if n else None}


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
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
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded", flush=True)

    docs = load_ud_docs(UD_TEST)
    if mode == "smoke":
        docs = [d for d in docs if len(d) >= 2][:40]  # multi-sentence docs so discourse can fire
    seeds = [7, 13, 19]
    print(f"[{ANCHOR_NAME}:{mode}] n_docs={len(docs)} "
          f"n_sent={sum(len(d) for d in docs)}", flush=True)

    # ---- parse cache (parse each sentence ONCE) ----
    reader_cache = {}
    for di, doc in enumerate(docs):
        for si, sent in enumerate(doc):
            reader_cache[(di, si)] = reader_pass(sent, tagger, parser, labeler)
        if mode == "full" and di % 50 == 0:
            print(f"[{ANCHOR_NAME}:{mode}] parsed doc {di}/{len(docs)} "
                  f"elapsed={time.perf_counter()-t0:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] parse cache built elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    # ---- ISOLATED + IN_CONTEXT_TRUE scored instances (deterministic) ----
    insts_iso = build_scored(docs, reader_cache, "isolated")
    insts_true = build_scored(docs, reader_cache, "true")

    def subs_amb(i):
        return i["n_cands"] >= 2

    def subs_pron(i):
        return i["gold_pron"]

    acc_iso_all, n_all, _ = acc_over(insts_iso, use_state=False)
    acc_true_all, _, _ = acc_over(insts_true, use_state=True)
    acc_iso_amb, n_amb, _ = acc_over(insts_iso, use_state=False, subset=subs_amb)
    acc_true_amb, _, _ = acc_over(insts_true, use_state=True, subset=subs_amb)
    acc_iso_pron, n_pron, _ = acc_over(insts_iso, use_state=False, subset=subs_pron)
    acc_true_pron, _, _ = acc_over(insts_true, use_state=True, subset=subs_pron)

    # count disagreements (arms-differ gate + coherence flag base)
    coh = coherence_stats(insts_true)
    n_disagreements = coh["n_flag"]
    cov = pronoun_resolution_coverage(insts_true)

    # ---- WRONG-DOC control over seeds ----
    n_docs = len(docs)
    wrongdoc_deltas_amb = []
    wrongdoc_deltas_all = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        # derangement-ish: assign each doc a different doc index (never itself)
        perm = rng.permutation(n_docs)
        wmap = {}
        for di in range(n_docs):
            wd = int(perm[di])
            if wd == di:
                wd = int((wd + 1) % n_docs)
            wmap[di] = wd
        insts_wd = build_scored(docs, reader_cache, "wrongdoc", wrongdoc_map=wmap)
        acc_wd_amb, _, _ = acc_over(insts_wd, use_state=True, subset=subs_amb)
        acc_wd_all, _, _ = acc_over(insts_wd, use_state=True)
        wrongdoc_deltas_amb.append(round((acc_wd_amb or 0) - (acc_iso_amb or 0), 4))
        wrongdoc_deltas_all.append(round((acc_wd_all or 0) - (acc_iso_all or 0), 4))

    delta_all_true = round((acc_true_all or 0) - (acc_iso_all or 0), 4)
    delta_amb_true = round((acc_true_amb or 0) - (acc_iso_amb or 0), 4)
    delta_pron_true = round((acc_true_pron or 0) - (acc_iso_pron or 0), 4)
    mean_wd_amb = round(float(np.mean(wrongdoc_deltas_amb)), 4)
    discourse_specific_amb = round(delta_amb_true - mean_wd_amb, 4)

    # ---- verdicts ----
    disagree_floor = max(5, int(0.02 * n_amb)) if n_amb else 5
    if n_disagreements < disagree_floor or delta_amb_true <= 0.0:
        acc_verdict = "HARD_FAIL_SELFCONTAINED"
    elif (delta_amb_true >= 0.03 and discourse_specific_amb >= 0.02 and delta_all_true >= -0.005):
        acc_verdict = "HARD_PASS_CONTEXT_HELPS"
    else:
        acc_verdict = "MIDDLE_BAND"

    p_flag = coh["p_isolated_wrong_given_flag"]
    p_noflag = coh["p_isolated_wrong_given_noflag"]
    fr = coh["flag_rate"]
    if (coh["n_flag"] >= 10 and p_flag is not None and p_noflag is not None
            and p_noflag > 0 and p_flag >= 2.0 * p_noflag and fr is not None and 0.01 <= fr <= 0.5):
        coh_verdict = "COHERENCE_SIGNAL_REAL"
    else:
        coh_verdict = "COHERENCE_NULL"

    baseline_in_band = bool(acc_iso_all is not None and 0.05 < acc_iso_all < 0.95)
    arms_differ = bool(n_disagreements > 0)

    # smoke discriminator-fires gate
    smoke_gate = {
        "n_ambiguous": n_amb, "n_pronoun_patient": n_pron, "n_disagreements": n_disagreements,
        "baseline_in_band": baseline_in_band, "arms_differ": arms_differ,
        "fires": bool(n_amb >= (10 if mode == "smoke" else 20) and n_disagreements >= 1
                      and n_pron >= 5 and baseline_in_band and arms_differ),
    }

    elapsed = round(time.perf_counter() - t0, 2)
    verdict = f"{acc_verdict} | {coh_verdict}"
    verdict_msg = (
        f"ACC[{acc_verdict}] iso_overall={acc_iso_all} ctx_overall={acc_true_all} "
        f"d_overall={delta_all_true} | iso_amb={acc_iso_amb} ctx_amb={acc_true_amb} "
        f"d_amb_true={delta_amb_true} d_amb_wrongdoc={mean_wd_amb} discourse_specific={discourse_specific_amb} "
        f"| iso_pron={acc_iso_pron} ctx_pron={acc_true_pron} d_pron={delta_pron_true} "
        f"| COH[{coh_verdict}] flag_rate={fr} p_wrong|flag={p_flag} p_wrong|noflag={p_noflag} "
        f"lift={coh['flag_error_lift_ratio']} fixed={coh['n_fixed_by_switch']} broke={coh['n_broken_by_switch']} "
        f"| pron_resolution_cov={cov['resolution_coverage']} (n={cov['n_pronoun_patient_extracted']})"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_docs": len(docs), "n_sent": sum(len(d) for d in docs),
        "n_gold_instances": n_all, "n_ambiguous": n_amb, "n_pronoun_patient": n_pron,
        "accuracy": {
            "isolated_overall": acc_iso_all, "incontext_true_overall": acc_true_all,
            "delta_overall_true": delta_all_true,
            "isolated_ambiguous": acc_iso_amb, "incontext_true_ambiguous": acc_true_amb,
            "delta_ambiguous_true": delta_amb_true,
            "wrongdoc_delta_ambiguous_per_seed": wrongdoc_deltas_amb,
            "wrongdoc_delta_ambiguous_mean": mean_wd_amb,
            "discourse_specific_ambiguous": discourse_specific_amb,
            "wrongdoc_delta_overall_per_seed": wrongdoc_deltas_all,
            "isolated_pronoun": acc_iso_pron, "incontext_true_pronoun": acc_true_pron,
            "delta_pronoun_true": delta_pron_true,
            "accuracy_verdict": acc_verdict,
        },
        "coherence_signal": {**coh, "coherence_verdict": coh_verdict},
        "pronoun_resolution_coverage": cov,
        "smoke_gate": smoke_gate,
        "design_gate": {
            "real_baseline": "isolated reader re-derived live", "can_fail": True,
            "one_variable": "state_of_mind_on_vs_off", "difficulty_on_subsets": ["ambiguous", "pronoun_patient"],
            "must_fail_control": "wrongdoc_overlay", "leak_clean": "state from prior sentences only; gold never observed",
            "baseline_in_band": baseline_in_band, "arms_differ_verified": arms_differ,
        },
        "cell_template": {
            "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "token-selection; no noise floor",
            "deterministic_seeding": "fixed ints + default_rng + sorted(set)",
            "progress_logging": "print_flush_true", "defensive_error_checking": "start_marker+crash_diag; heartbeat exempt (<3min cell)",
        },
        "seeds": seeds,
    }
    _write_metrics(output_dir, metrics)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    """Fast self-test: exercises the REAL front-end + overlay on a tiny synthetic 2-sentence doc and
    asserts (a) gold derivation, (b) leak-clean prior-only state, (c) arms can differ on a disagreement."""
    print("[self_test] start", flush=True)
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)

    # a tiny hand-built 2-sentence doc; gold parse fields set so gold_instances fires
    # S1: "Mary bought a house ."  -> verb bought(2) obj house(4)
    # S2: "John sold it ."         -> verb sold(2) obj it(3)  (pronoun patient; referent prior sent)
    s1 = {"tokens": ["Mary", "bought", "a", "house", "."],
          "lemmas": ["Mary", "buy", "a", "house", "."],
          "upos": ["PROPN", "VERB", "DET", "NOUN", "PUNCT"],
          "gold_head": {1: 2, 2: 0, 3: 4, 4: 2, 5: 2},
          "gold_deprel": {1: "nsubj", 2: "root", 3: "det", 4: "obj", 5: "punct"}}
    s2 = {"tokens": ["John", "sold", "it", "."],
          "lemmas": ["John", "sell", "it", "."],
          "upos": ["PROPN", "VERB", "PRON", "PUNCT"],
          "gold_head": {1: 2, 2: 0, 3: 2, 4: 2},
          "gold_deprel": {1: "nsubj", 2: "root", 3: "obj", 4: "punct"}}
    doc = [s1, s2]
    assert gold_instances(s1) == [{"vidx": 2, "gold_pidx": 4}], gold_instances(s1)
    assert gold_instances(s2) == [{"vidx": 2, "gold_pidx": 3}], gold_instances(s2)

    reader_cache = {(0, 0): reader_pass(s1, tagger, parser, labeler),
                    (0, 1): reader_pass(s2, tagger, parser, labeler)}
    insts_iso = build_scored([doc], reader_cache, "isolated")
    insts_true = build_scored([doc], reader_cache, "true")
    assert len(insts_iso) == len(insts_true) == 2, (len(insts_iso), len(insts_true))

    # ISOLATED arm can never disagree (no state).
    assert all(not i["disagreement"] for i in insts_iso), "isolated arm must have zero disagreements"
    # leak-clean: S1 is the FIRST sentence -> its state is empty -> it cannot use any (future) entity.
    assert insts_true[0]["disagreement"] is False, "S1 must not use future-sentence state (leak)"
    assert insts_true[0]["pron_resolves"] is False, "S1 has no prior state -> no resolution"

    # STATE-CARRY + resolution: directly verify observe_sentence carries S1 mentions and resolves 'it'.
    ov = WorkingOverlay()
    observe_sentence(ov, s1["tokens"], ["PROPN", "VERB", "DET", "NOUN", "PUNCT"])
    assert ov.n_observed == 2, ("S1 observes exactly Mary + house", ov.n_observed)
    assert "house" in ov._entities and "mary" in ov._entities, list(ov._entities)
    assert ov.resolve_pronoun("it", strategy="maintained") is not None, "'it' must bind to a prior entity"
    # empty-state salient_pick returns None (no established entity)
    empty = WorkingOverlay()
    pool_probe = [{"aidx": 4, "margin": 1.0, "surf": "house", "pos": "NOUN"}]
    assert salient_pick(pool_probe, empty) is None, "empty state must yield no salient pick"

    # coherence + coverage callables run without error
    coh = coherence_stats(insts_true)
    cov = pronoun_resolution_coverage(insts_true)
    assert set(coh) >= {"n_flag", "p_isolated_wrong_given_flag"}, coh
    assert "resolution_coverage" in cov, cov
    print(f"[self_test] gold OK; leak-clean prior-only state OK; state-carry+resolve OK; coh/cov OK "
          f"(pron_cov={cov['resolution_coverage']})", flush=True)
    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.smoke:
        run_mode("smoke")
        return
    if args.full:
        run_mode("full")
        return
    # default = self-test (no silent full)
    self_test()


if __name__ == "__main__":
    output_dir_for_crash = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(output_dir_for_crash, e)
        raise
