"""ROLES chain-grade DRIVE-3: SUPPLIED-LEXICON VERB VALENCY (subcat arity) as a brain-faithful precision/recall
lever on the best current who-did-what reader (V3_INTEGRATED; landed end-to-end patient-F1=0.5738,
MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1).

WHY DRIVE-2 DID NOT CLOSE THE GAP (autopsy diagnosis, MEASURED@data/exp_reader_role_frame_gated_valency_v2 +
  Director ruling 2026-07-23): drive-2 DERIVED valency from the PARSE -- it declared a clause DITRANSITIVE when
  the parser routed >=2 post-verbal "cores" (len(post_core)>=2) and then picked the LAST core as the theme.
  The out-of-domain parser (UAS~0.79) mis-routes verb PARTICLES ("knock castles DOWN"), APPOSITIVES ("boy whose
  NAME was JOE"), and embedded-clause nouns INTO the core set, so len(post_core)>=2 FALSE-FIRES on genuinely
  TRANSITIVE verbs and the last-core theme pick DEMOTES the correct post_core[0] patient (within_frame_fp 6->24,
  F1 0.43). Deriving verb arity from a noisy parse does not work.

THE ROLE_ORACLE HEADROOM (MEASURED@data/exp_reader_role_wordorder_valency_v1/metrics.json:roleora_recovered):
  6 gold (verb,patient) pairs BASE misses that ROLE_ORACLE recovers. FIVE are genuinely TRANSITIVE -- they need
  ONLY post_core[0]->PATIENT: L04_12 rub/castle, L05_16 knock/castles, L05_22 see/child, L07_09 meet/boys,
  L10_11 find/boy. ONE is fronted/OSV (L04_01 build/blockhouse; blockhouse is PRE-verbal so post_core is empty
  -> out of this cell's canonical-order scope, it is drive-1's FRONTED_OSV territory). A blunt post_core[0]
  override recovers the 5 transitive misses, BUT un-gated blunt OVER-STEALS on ditransitive/light clauses
  (drive-1 CANONICAL_BLUNT regressed give/books, show/seeds, show/way, hold/hands, give/hour -> F1 0.5312).

THE BRAIN-FAITHFUL MECHANISM THIS CELL BUILDS (role_valency_reassign; glass-box; the ONLY word-identity input is
  the SUPPLIED verb-valency lexicon lookup): the brain KNOWS a verb's argument structure (give is ditransitive)
  as a SUPPLIED LEXICAL VALENCY FACT retrieved from the mental lexicon; it does NOT count nouns from a noisy
  parse. Supplied subcat-VALENCY is ADMISSIBLE (Director ruling 2026-07-23): it is structural argument-structure
  ARITY (syntactic), DISTINCT from the forbidden selectional-PREFERENCE (semantic patient-fit, proven REDUNDANT
  for this reader CITED@29491); a SUPPLIED FACT per the throughline "structure composes, facts get supplied";
  sourced from the AUTHORIZED foundation KB (VerbNet via nltk). Mechanism (canonical, non-passive clause with
  a post-verbal core):
    DITRANSITIVE verb (supplied set): PATIENT <- post_core[-1] (theme = LAST core); earlier post-verbal core(s)
      (recipient) demoted from any perceptron-PATIENT -> NONE (recipient PROTECTED). Recovers give/books etc.
    LIGHT/SUPPORT verb (supplied set, ditransitive precedence): NEUTRALIZE -- do NOT apply the override; defer
      the clause to the BASE reader (a support verb's NP complement is not a thematic patient). This can NEVER
      regress vs BASE (it equals BASE on light clauses) and protects hold/hands from the blunt over-steal.
    EVERYTHING ELSE (transitive): PATIENT <- post_core[0] (blunt). Recovers the 5 transitive misses. Because a
      transitive verb is NEVER classified ditransitive (it is not in the supplied set), it is IMMUNE to the
      parser mis-route that broke drive-2 -- it ALWAYS takes post_core[0]. That is the whole fix.
  Frame/arity comes ONLY from the SUPPLIED lexicon lookup (verb lemma -> valency class). Position, governing-
  preposition (prev_prep), passive, and the reader's OWN learned admissibility gate are the only structural
  signals. NO selectional/animacy/patient-fit knowledge anywhere.

SUPPLIED VERB-VALENCY LEXICON (small, auditable, VerbNet-sourced; see _extract_ditransitive_from_verbnet for
  provenance): DITRANSITIVE = the VerbNet double-object dative frames filtered by the NP thematic-role sequence
  [Recipient|Beneficiary, Theme|Topic] (109 lemmas from classes give-13.1/future_having-13.3/get-13.5.1/
  transfer_mesg-37.1.1/tell-37.2/advise-37.9/instr_communication-37.4/inquire-37.1.2/help-72/contribute-13.2/
  performance-26.7), UNION the Director's named caused-motion transfer datives {bring, send, hand}. Excludes the
  contact verbs (throw/knock/hit) to keep the transitive-headroom knock/castles safe. LIGHT = the canonical
  closed-class English support verbs (CITED: light-verb-construction literature; Jespersen; Butt 2003). AUDIT
  (MEASURED@ this run's metrics.json:lexicon_audit): give/show/tell/bring/send/hand/offer/teach all IN
  DITRANSITIVE; the 5 transitive-headroom verbs (rub/see/meet/knock/build) all OUT of DITRANSITIVE (find is a
  VerbNet benefactive dative, harmless single-core -> theme==post_core[0]).

ARMS (five; BASE / ROLE_ORACLE reuse the AUDIT's byte-identical machinery; CANONICAL_BLUNT reuses DRIVE-1's own
  build_arm_wo byte-identically):
  BASE            = AUDIT REAL arm (== V3_INTEGRATED). P1 FAIRNESS ANCHOR (reproduces F1=0.5738 byte-identical).
  VALENCY_GATED   = BASE + role_valency_reassign with the REAL supplied lexicon (HEADLINE).
  CANONICAL_BLUNT = drive-1's UN-GATED blunt (post_core[0]->PATIENT for every admissible verb; NO lexicon).
                    THE ABLATION: VALENCY_GATED vs CANONICAL_BLUNT isolates EXACTLY what the supplied valency
                    fact contributes (ditransitive theme-pick + recipient-protection + light-verb neutralize).
  VALENCY_SCRAMBLE= same mechanism, lexicon SCRAMBLED (same #ditransitive + #light corpus verbs, but RANDOM
                    membership, fixed seed). P2 FAIRNESS CONTROL: if scrambling the supplied set does NOT
                    degrade the result, the valency fact is a no-op/redundant -> report, do NOT ship.
  ROLE_ORACLE     = AUDIT oracle_role arm on the SAME parser weights = the +0.0391 CEILING (F1=0.6129).

KEEP-DIGGING MANDATE (USER 07-23): if VALENCY_GATED does NOT close the +0.0391, this cell runs a DEEP PER-ITEM
  AUTOPSY (autopsy_roleora_headroom) of EACH ROLE_ORACLE-headroom item -- parser tokens, valency class assigned,
  post/pre core sets, perceptron role of the gold patient, final role after the override, whether emitted, and
  the SPECIFIC mechanism gap (supplied set wrong/incomplete? post_core[0] wrong for some transitive (parser)?
  light-neutralize forwent a recovery?) -- so a failure NAMES the next mechanism gap. A brain-faithful mechanism
  cannot fail where the brain succeeds; a miss = our FIDELITY is still wrong, NOT a real bound.

MEASURED (per arm, SAME independent LCCP gold / split as audit/V3): F1, precision, recall, recall_ceiling,
  subcat/within_frame/spurious FP; n_recovered / n_regressed vs BASE; the blunt-vs-valency ablation delta; the
  scramble-degrade delta; FRACTION OF THE +0.0391 GAP CLOSED = (F1(VALENCY_GATED)-F1(BASE))/(F1(ROLE_ORACLE)-
  F1(BASE)); per-item outcome on the 6 headroom items.

PRE-REGISTERED BANDS (set BEFORE the VALENCY_GATED full run; grounded on audit MEASURED anchors f1_REAL=0.5738,
  f1_ROLE_ORACLE=0.6129, gap=0.0391):
  HARD_PASS_SUPPLIED_VALENCY_LIFT requires ALL of:
    (P1) abs(F1(BASE)-0.5738) <= 0.02                                   # base reproduces V3
    (a)  F1(VALENCY_GATED) >= F1(BASE) + 0.0196                         # closes >= 50% of the 0.0391 gap
    (b)  recall(VALENCY_GATED) >= recall(BASE) - 0.005                  # no recall regression
    (c)  precision(VALENCY_GATED) >= precision(BASE)                    # no precision regression
    (d)  F1(VALENCY_GATED) >= F1(CANONICAL_BLUNT) + 0.01                # supplied valency beats un-gated blunt
    (P2) F1(VALENCY_GATED) >= F1(VALENCY_SCRAMBLE) + 0.01 AND F1(VALENCY_SCRAMBLE) <= F1(BASE)  # correct
                                                                        # membership earns its keep
  HARD_FAIL_SUPPLIED_VALENCY_NULL if ANY of:
    F1(VALENCY_GATED) <= F1(BASE)                                       # no lift (mechanism null on this corpus)
    recall(VALENCY_GATED) < recall(BASE) - 0.02                         # regressed recall
    F1(VALENCY_SCRAMBLE) >= F1(VALENCY_GATED)                           # scramble not worse -> valency is a NO-OP
    abs(F1(BASE)-0.5738) > 0.02                                         # P1 broke
  MIDDLE_BAND_PARTIAL_VALENCY_LIFT otherwise (genuine but partial gap-closure, controls fire, no HARD_FAIL) --
  the honest 'drove toward the ceiling, name the residual wall from the autopsy' outcome.

FAIRNESS: SAME reader / gold (data/gold_mcguffey_lccp_argstruct_v1.json) / split (FULL_SLICE=
  L04/L05/L07/L08/L09/L10/L12, SMOKE_SLICE=L04/L05) as audit / V3 / drive-1/2. BASE and ROLE_ORACLE are
  byte-identical reuse of AUDIT.build_arm_audit; CANONICAL_BLUNT is byte-identical reuse of WO.build_arm_wo; the
  shared admissibility gate is built ONCE (pass-through-gate evidence pass, exactly as drive-1/2) and held
  identical; the pre-existing >=2-patient selectional argmax is held CONSTANT (NOT my variable). ONE variable =
  the SUPPLIED verb-valency lexicon. No selectional/animacy/patient-fit knowledge added. No cross-base compare.

COMPUTE ARCHITECTURE: class (b) sequential-CPU -- ONE arc-eager parser train (~68s FULL, MEASURED@drive-1/2
  parser_info) + ms/clause decode + per-predicate perceptron + O(cand) position/prep lookups + O(1) lexicon
  lookups. NO matmul/GPU/storage. 5 scored arms + 1 evidence pass + 1 corpus-verb pass + 1 autopsy trace pass.
  drive-2 FULL elapsed ~210s MEASURED -> est wall < 4.5min. Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED,
  random.Random(SEED) for the scramble (no hash()-seeded RNG), sorted() iteration. Storage: no_storage. Runtime
  invariant: glass-box, NO LLM/network/autograd. LOCAL-ONLY foreground-to-completion, NOT banked (skunkworks
  VETs separately), NO queue_add.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash over the 5 arms; small-sample WARN permitted)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASE) < 0.95)
  - P1 reproduction self-test: BASE via AUDIT REAL == WO override-disabled (hash-identical)
  - discriminator fires at smoke: VALENCY_GATED recovers >=1 gold item BASE misses (3 of the 5 transitive
    headroom items -- rub/castle L04_12, knock/castles L05_16, see/child L05_22 -- are IN SMOKE_SLICE L04/L05)
  - scaffold-free witnesses: transitive ("girl saw the child" -> child->PATIENT overriding animacy); ditransitive
    ("give the boy books" -> books(theme)->PATIENT, boy(recipient) protected); light-neutralize ("hold hands" ->
    override does NOT fire, defers to BASE, unlike blunt which would force hands->PATIENT); scramble differs
  - deterministic seeding (fixed int SEED; random.Random(SEED) scramble; sorted() where order matters)
  - progress_logging: line_buffered_stdout (sys.stdout.reconfigure) -- FULL est < 4.5min < 30min so not gated
  - all numbers tagged MEASURED@ / CITED@ in this docstring
  - N/A: KGStore (no KG); CRLB (discrete count/precision, no HD noise floor); multi-seed (single-seed parser
    budget, accepted per M/V3/audit/drive-1/2); GPU-batching (sequential parse, no matmul)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import random
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "reader_role_valency_supplied_lexicon_v3"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3             # noqa: E402
from experiments import exp_reader_component_oracle_ablation_audit_v1 as AUDIT       # noqa: E402
from experiments import exp_reader_role_wordorder_valency_v1 as WO                   # noqa: E402  (drive-1; reuse only)

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260726

# ---- Pre-registered bands (set BEFORE the VALENCY_GATED full run) ----------------------------
CITED_AUDIT_F1_REAL = 0.5738         # MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/metrics.json:f1.REAL
CITED_AUDIT_F1_ROLE_ORACLE = 0.6129  # MEASURED@ same:f1.ROLE_ORACLE
CITED_ROLE_GAP = 0.0391              # MEASURED@ same:uplift.ROLE_ORACLE
P1_REPRO_TOL = 0.02
HP_GAP_CLOSE_FRAC = 0.50
HP_F1_MIN_LIFT = round(CITED_ROLE_GAP * HP_GAP_CLOSE_FRAC, 4)   # 0.0196
HP_RECALL_TOL = 0.005
HP_ABLATION_MARGIN = 0.01
HP_SCRAMBLE_MARGIN = 0.01
HF_RECALL_REGRESS = 0.02
BASELINE_BAND = (0.05, 0.95)
EXPECTED_N_ARMS = 5
HEADLINE = "VALENCY_GATED"

# ================================================================================================
# SUPPLIED VERB-VALENCY LEXICON (VerbNet-sourced; frozen literal for determinism + self-containment;
# _extract_ditransitive_from_verbnet reproduces the DITRANSITIVE frozen set from nltk for audit).
# ================================================================================================
# DITRANSITIVE: VerbNet double-object dative frames filtered by NP thematic-role sequence
#   [Recipient|Beneficiary, Theme|Topic] (109 lemmas) UNION the Director's named caused-motion transfer
#   datives {bring, send, hand}. Contact verbs (throw/knock/hit) EXCLUDED to keep knock/castles transitive.
DITRANSITIVE_SET = frozenset({
    "advance", "alert", "allocate", "allot", "apportion", "ask", "assign", "assure", "attain", "award",
    "bequeath", "book", "brief", "bring", "broadcast", "buy", "cable", "call", "catch", "cede", "charter",
    "choose", "concede", "conserve", "consult", "dance", "dictate", "disburse", "draw", "encourage", "enquire",
    "entice", "extend", "fax", "find", "gather", "give", "grant", "guarantee", "hand", "hire", "hock", "hum",
    "inform", "inquire", "issue", "lease", "leave", "lend", "loan", "modem", "netmail", "notify", "offer",
    "order", "owe", "paint", "pass", "pawn", "peddle", "phone", "pick", "play", "pluck", "portion", "procure",
    "proffer", "promise", "pry", "pull", "quote", "radio", "ration", "reach", "read", "recite", "refund",
    "relay", "render", "rent", "reserve", "return", "satellite", "secure", "sell", "semaphore", "send", "shoot",
    "show", "sign", "signal", "sing", "slaughter", "spin", "succor", "support", "teach", "telecast", "telegraph",
    "telephone", "telex", "tell", "transfer", "volunteer", "vote", "whistle", "will", "win", "wire", "wireless",
    "write", "yield",
})
# LIGHT/SUPPORT verbs: canonical closed grammatical class (CITED: light-verb-construction literature;
#   Jespersen 1954; Butt 2003). Ditransitive membership takes PRECEDENCE (give/take/get are datives here).
LIGHT_VERB_SET = frozenset({"do", "have", "make", "take", "give", "get", "hold", "keep", "put", "let"})


def _extract_ditransitive_from_verbnet():
    """Provenance/audit: reproduce the VerbNet role-filtered dative lemma set (Recipient|Beneficiary + Theme|Topic
    double-object). Returns None if nltk verbnet is unavailable (LOCAL cell; audit-only). CITED@VerbNet 3.x."""
    try:
        from nltk.corpus import verbnet as vn
    except Exception:
        return None
    first_roles = {"Recipient", "Beneficiary"}
    second_roles = {"Theme", "Topic"}

    def role(el):
        return el.get("modifiers", {}).get("value", "")

    def is_dative(cid):
        for fr in vn.frames(cid):
            syn = fr["syntax"]
            iv = next((i for i, el in enumerate(syn) if el["pos_tag"] == "VERB"), None)
            if iv is None:
                continue
            nps = []
            for el in syn[iv + 1:]:
                pt = el["pos_tag"]
                if pt in ("PREP", "LEX"):
                    break
                if pt == "NP":
                    nps.append(role(el))
            if len(nps) >= 2 and nps[0] in first_roles and nps[1] in second_roles:
                return True
        return False

    lemmas = set()
    for cid in vn.classids():
        if is_dative(cid):
            for lm in vn.lemmas(cid):
                w = lm.lower()
                if w.isalpha():
                    lemmas.add(w)
    return lemmas


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# ================================================================================================
# SUPPLIED-LEXICON verb-valency role mapping. Mutates `roles` in place. The ONLY word-identity input is
# the ditrans_fn / light_fn lexicon lookup (supplied subcat-VALENCY arity, not selectional preference).
# Returns a trace dict (valency class + constituents) for the per-item autopsy.
# ================================================================================================
def role_valency_reassign(roles, local_cand, tagged, v0, passive, gate_fn, ditrans_fn, light_fn):
    tr = {"frame": None, "post_core": [], "pre_core": [], "pat": None, "ag": None, "applied": False}
    if passive:
        tr["frame"] = "passive_skip"       # non-canonical: parietal reanalysis, out of scope -> BASE
        return tr
    post_core = sorted(i for i in local_cand if i > v0 and ORC.prev_prep(tagged, i) is None)
    pre_core = sorted(i for i in local_cand if i < v0 and ORC.prev_prep(tagged, i) is None)
    tr["post_core"] = post_core
    tr["pre_core"] = pre_core
    if not post_core:
        tr["frame"] = "no_postverbal_core"  # fronted/OSV/intransitive -> out of canonical-order scope -> BASE
        return tr
    vl = L.lemma_verb(tagged[v0][1])
    if not gate_fn(vl):
        tr["frame"] = "gate_blocked"        # learned admissibility gate: verb admits no patient -> BASE
        return tr

    # ---- SUPPLIED-LEXICON valency retrieval + word-order->role map (ditransitive precedence) ----
    if ditrans_fn(vl):
        tr["frame"] = "ditransitive"
        pat = post_core[-1]                 # theme = LAST core; earlier core(s) = recipient, protected below
    elif light_fn(vl):
        tr["frame"] = "light_verb_skip"     # support verb: neutralize -> defer to BASE (no forced patient)
        return tr
    else:
        tr["frame"] = "transitive"
        pat = post_core[0]                  # blunt: the single/first post-verbal object

    ag = pre_core[-1] if pre_core else None  # nearest pre-verbal core = subject
    tr["pat"] = pat
    tr["ag"] = ag
    roles[pat] = "PATIENT"
    for j in local_cand:
        if j != pat and roles.get(j) == "PATIENT":
            roles[j] = "NONE"               # THE patient is determined; un-steal any ditransitive recipient
    if ag is not None and ag != pat:
        roles[ag] = "AGENT"
    tr["applied"] = True
    return tr


# ================================================================================================
# One clause pass. Mirrors AUDIT.clause_predicate_pass_audit's REAL (all-oracle-False) path plus the single
# supplied-valency override. trace_sink: optional dict populated when sid in trace_sids (autopsy).
# ================================================================================================
def clause_predicate_pass_valency(sid, tagged, heads, clf, gate_fn, carried_agent_in, sel_fn,
                                  ditrans_fn, light_fn, trace_sink=None, trace_sids=None):
    lows = [t[1] for t in tagged]
    predicates = M.content_verb_indices(tagged)
    candidates = ORC.candidate_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    route = AUDIT.real_route(tagged, heads, predicates, candidates, False)

    pred_1based = set(p + 1 for p in predicates)
    by_pred = defaultdict(list)
    for c0 in candidates:
        c1 = c0 + 1
        if c1 in pred_1based:
            continue
        target = route.get(c0)
        if target is not None:
            by_pred[target].append(c0)

    tracing = (trace_sink is not None and trace_sids is not None and sid in trace_sids)
    out = []
    carried_agent = carried_agent_in
    evidence = {}
    for v0 in predicates:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        vl = L.lemma_verb(low)
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)
        perceptron_roles = dict(roles) if tracing else None

        tr = role_valency_reassign(roles, local_cand, tagged, v0, passive, gate_fn, ditrans_fn, light_fn)

        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True
        kept_patients = patients_local
        if sel_fn is not None and len(patients_local) >= 2:
            def _score(i):
                s = sel_fn(vl, tagged[i][1])
                return -1.0 if s is None else s
            best_i = max(patients_local, key=lambda i: (_score(i), -i))
            kept_patients = [best_i]
        emitted = None
        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                emitted = []
                for pi in kept_patients:
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
                    emitted.append(tagged[pi][1])
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]

        if tracing:
            def _w(idxs):
                return [tagged[i][1] for i in idxs]
            trace_sink.setdefault(sid, []).append(dict(
                sid=sid, verb=vl, verb_low=low, verb_idx=v0, passive=passive,
                frame=tr["frame"], gate_admits=bool(gate_fn(vl)),
                is_ditransitive=bool(ditrans_fn(vl)), is_light=bool(light_fn(vl)),
                local_cand=_w(local_cand), post_core=_w(tr["post_core"]), pre_core=_w(tr["pre_core"]),
                perceptron_roles={tagged[i][1]: perceptron_roles[i] for i in local_cand},
                final_roles={tagged[i][1]: roles[i] for i in local_cand},
                override_pat=(tagged[tr["pat"]][1] if tr["pat"] is not None else None),
                override_ag=(tagged[tr["ag"]][1] if tr["ag"] is not None else None),
                resolved_agent=resolved_agent,
                kept_patients=[tagged[i][1] for i in kept_patients],
                emitted_patients=emitted))
    return out, carried_agent, evidence


def build_arm_valency(slice_lessons, W, clf, gate_fn, sel_fn, ditrans_fn, light_fn,
                      trace_sink=None, trace_sids=None):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    out = {}
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            clause_tups, carried_agent, _ = clause_predicate_pass_valency(
                sid, tagged, heads, clf, gate_fn, carried_agent, sel_fn, ditrans_fn, light_fn,
                trace_sink=trace_sink, trace_sids=trace_sids)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
        out[sid] = tups
    return order, out


# ================================================================================================
# Corpus verb vocabulary (for the fair scramble) + scramble builder.
# ================================================================================================
def collect_corpus_verbs(slice_lessons):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    vocab = set()
    for sid in order:
        for clause_text in ORC.split_sentences(sent_text[sid]):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            for v0 in M.content_verb_indices(tagged):
                vocab.add(L.lemma_verb(tagged[v0][1]))
    return vocab


def build_scramble_fns(vocab, seed):
    """Fair P2 scramble: mark the SAME NUMBER of corpus verbs ditransitive / light as the real lexicon does,
    but choose RANDOM (wrong) members. Deterministic (random.Random(seed); sorted vocab)."""
    v = sorted(vocab)
    real_ditrans = [w for w in v if w in DITRANSITIVE_SET]
    real_light = [w for w in v if (w in LIGHT_VERB_SET and w not in DITRANSITIVE_SET)]
    n_d, n_l = len(real_ditrans), len(real_light)
    rng = random.Random(seed)
    shuffled = list(v)
    rng.shuffle(shuffled)
    fake_ditrans = set(shuffled[:n_d])
    fake_light = set(shuffled[n_d:n_d + n_l])
    info = dict(n_ditrans_marked=n_d, n_light_marked=n_l,
                real_ditrans_in_corpus=sorted(real_ditrans), real_light_in_corpus=sorted(real_light),
                fake_ditrans=sorted(fake_ditrans), fake_light=sorted(fake_light))
    return (lambda w: w in fake_ditrans), (lambda w: w in fake_light), info


def real_ditrans_fn(vl):
    return vl in DITRANSITIVE_SET


def real_light_fn(vl):
    return vl in LIGHT_VERB_SET and vl not in DITRANSITIVE_SET   # ditransitive precedence


# ================================================================================================
# Deep per-item autopsy of the ROLE_ORACLE headroom set (KEEP-DIGGING deliverable).
# ================================================================================================
def autopsy_roleora_headroom(slice_lessons, W, clf, gate_fn, sel_fn, roleora_recovered, head_recovered):
    trace_sids = set(sid for (sid, v, p) in roleora_recovered)
    trace_sink = {}
    build_arm_valency(slice_lessons, W, clf, gate_fn, sel_fn, real_ditrans_fn, real_light_fn,
                      trace_sink=trace_sink, trace_sids=trace_sids)
    head_set = set((sid, v, p) for (sid, v, p) in head_recovered)
    report = []
    for (sid, gverb, gpat) in roleora_recovered:
        recovered = (sid, gverb, gpat) in head_set
        preds = trace_sink.get(sid, [])
        matches = [pr for pr in preds if pr["verb"] == gverb]
        item = dict(sid=sid, gold_verb=gverb, gold_patient=gpat, recovered_by_valency_gated=recovered)
        if not matches:
            item["diagnosis"] = ("NO_PREDICATE_TRACE: VALENCY_GATED produced no predicate with lemma "
                                 f"{gverb!r} in {sid} -> upstream (parser routing / predicate detection / clause "
                                 "segmentation) never presented this verb. Not a role-assignment gap.")
            item["predicate_traces"] = []
            report.append(item)
            continue
        pdiag = []
        for pr in matches:
            gpat_in_local = gpat in pr["local_cand"]
            gpat_in_post = gpat in pr["post_core"]
            perc_role = pr["perceptron_roles"].get(gpat)
            fin_role = pr["final_roles"].get(gpat)
            emitted_ok = pr["emitted_patients"] is not None and gpat in (pr["emitted_patients"] or [])
            if not gpat_in_local:
                why = ("ROUTING_GAP: gold patient not among this predicate's routed local candidates "
                       f"(local={pr['local_cand']}) -> parser routing / mention gate dropped it.")
            elif not gpat_in_post:
                why = ("NON_POSTVERBAL: gold patient is routed but NOT a post-verbal core "
                       f"(post_core={pr['post_core']}, pre_core={pr['pre_core']}) -> fronted/OSV/prep-governed, "
                       "out of this cell's canonical post-verbal scope.")
            elif pr["frame"] == "gate_blocked":
                why = ("GATE_BLOCKED: post-verbal core present but the learned admissibility gate says the verb "
                       "admits no patient -> override suppressed.")
            elif pr["frame"] == "light_verb_skip":
                why = ("LIGHT_NEUTRALIZE: verb in the supplied LIGHT set -> override deferred to BASE, forwent "
                       f"the post_core[0] recovery of {gpat!r} (light-verb false-membership OR a genuine "
                       "recovery the neutralize gave up).")
            elif pr["frame"] == "ditransitive" and pr["override_pat"] != gpat:
                why = (f"DITRANSITIVE_THEME_MISPICK: supplied set marks {gverb!r} ditransitive, theme (last core) "
                       f"={pr['override_pat']!r} but gold patient is {gpat!r} (post_core={pr['post_core']}) -> the "
                       "verb is transitive in THIS clause OR the parser mis-routed a 2nd post-core.")
            elif fin_role != "PATIENT":
                why = (f"OVERRIDE_NOT_APPLIED: post-verbal core, frame={pr['frame']}, but gold-patient final role"
                       f"={fin_role!r} (perceptron={perc_role!r}) -> override did not set it PATIENT.")
            elif not emitted_ok:
                why = (f"POST_OVERRIDE_FILTER: gold patient set PATIENT (frame={pr['frame']}) but not emitted "
                       f"(kept_patients={pr['kept_patients']}, emitted={pr['emitted_patients']}) -> the >=2-patient "
                       "selectional argmax OR the emit gate dropped it.")
            else:
                why = (f"EMITTED_OK: frame={pr['frame']}, perceptron={perc_role!r} -> PATIENT; emitted "
                       f"{pr['emitted_patients']} (recovered by VALENCY_GATED = {recovered}).")
            pdiag.append(dict(frame=pr["frame"], is_ditransitive=pr["is_ditransitive"], is_light=pr["is_light"],
                              gate_admits=pr["gate_admits"], post_core=pr["post_core"], pre_core=pr["pre_core"],
                              perceptron_role_of_gold_patient=perc_role, final_role_of_gold_patient=fin_role,
                              override_pat=pr["override_pat"], emitted_patients=pr["emitted_patients"],
                              diagnosis=why))
        item["predicate_traces"] = pdiag
        report.append(item)
    return report


# ================================================================================================
# Full 5-arm experiment.
# ================================================================================================
def run_experiment(slice_lessons, W, clf, ratings_table, gold, with_autopsy=True):
    sel_fn = V3.build_sel_fn(ratings_table)
    # Gate built EXACTLY as drive-1/2: pass-through-gate evidence pass via WO.build_arm_wo -> byte-identical gate.
    _, _, evidence_real = WO.build_arm_wo(slice_lessons, W, clf, lambda v: True, None, override=None,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)

    vocab = collect_corpus_verbs(slice_lessons)
    scr_ditrans_fn, scr_light_fn, scramble_info = build_scramble_fns(vocab, SEED)

    arms = {}
    _, base_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                         oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, roleora_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                            oracle_enum=False, oracle_parse=False, oracle_role=True)
    _, blunt_kept = WO.build_arm_wo(slice_lessons, W, clf, gate_fn, sel_fn,
                                    override=dict(mode="canonical", anti=False))
    _, gated_kept = build_arm_valency(slice_lessons, W, clf, gate_fn, sel_fn, real_ditrans_fn, real_light_fn)
    _, scramble_kept = build_arm_valency(slice_lessons, W, clf, gate_fn, sel_fn, scr_ditrans_fn, scr_light_fn)

    arms["BASE"] = base_kept
    arms["VALENCY_GATED"] = gated_kept
    arms["VALENCY_SCRAMBLE"] = scramble_kept
    arms["CANONICAL_BLUNT"] = blunt_kept
    arms["ROLE_ORACLE"] = roleora_kept

    scored = {}
    for name, kept in arms.items():
        rc, miss, npos, misses = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                            kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    base_covered = M.covered_set(arms["BASE"], gold)
    roleora_recovered = sorted(M.covered_set(arms["ROLE_ORACLE"], gold) - base_covered)
    head_recovered = sorted(M.covered_set(arms[HEADLINE], gold) - base_covered)
    head_regressed = sorted(base_covered - M.covered_set(arms[HEADLINE], gold))
    head_of_roleora = sorted(set(head_recovered) & set(roleora_recovered))
    blunt_recovered = sorted(M.covered_set(arms["CANONICAL_BLUNT"], gold) - base_covered)
    blunt_regressed = sorted(base_covered - M.covered_set(arms["CANONICAL_BLUNT"], gold))
    scramble_recovered = sorted(M.covered_set(arms["VALENCY_SCRAMBLE"], gold) - base_covered)
    scramble_regressed = sorted(base_covered - M.covered_set(arms["VALENCY_SCRAMBLE"], gold))

    autopsy = None
    if with_autopsy:
        autopsy = autopsy_roleora_headroom(slice_lessons, W, clf, gate_fn, sel_fn,
                                           roleora_recovered, head_recovered)

    return dict(arms=arms, scored=scored, gate_fn=gate_fn, scramble_info=scramble_info, vocab=sorted(vocab),
                roleora_recovered=roleora_recovered, head_recovered=head_recovered,
                head_regressed=head_regressed, head_of_roleora=head_of_roleora,
                blunt_recovered=blunt_recovered, blunt_regressed=blunt_regressed,
                scramble_recovered=scramble_recovered, scramble_regressed=scramble_regressed,
                autopsy=autopsy)


# ================================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# ================================================================================================
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


# ================================================================================================
# Self-test (design-gate; smoke scale = SMOKE_SLICE).
# ================================================================================================
def self_test():
    print("[self-test] auditing supplied verb-valency lexicon ...")
    vn_set = _extract_ditransitive_from_verbnet()
    for w in ("give", "show", "tell", "bring", "send", "hand", "offer", "teach"):
        assert w in DITRANSITIVE_SET, f"lexicon audit: seed ditransitive {w!r} missing from DITRANSITIVE_SET"
    for w in ("see", "rub", "meet", "knock", "build"):
        assert w not in DITRANSITIVE_SET, f"lexicon audit: transitive-headroom {w!r} wrongly in DITRANSITIVE_SET"
    if vn_set is not None:
        # every role-filtered VerbNet dative lemma must be in the frozen set (frozen = VerbNet UNION {bring,send,hand})
        missing = sorted(vn_set - DITRANSITIVE_SET)
        assert not missing, f"lexicon audit: frozen DITRANSITIVE_SET drifted from VerbNet role-filter; missing {missing}"
        print(f"[self-test] lexicon audit: frozen set reproduces VerbNet role-filter ({len(vn_set)} lemmas) "
              f"UNION {{bring,send,hand}} = {len(DITRANSITIVE_SET)}")
    else:
        print("[self-test] lexicon audit: nltk verbnet unavailable; frozen set used (seed/headroom checks passed)")

    print("[self-test] loading SMOKE_SLICE reader + gold + knowledge table ...")
    gold, meta = L.load_gold(SMOKE_SLICE)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)

    print("[self-test] training arc-eager parser (smoke budget, reused M code) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    # (P1 REPRODUCTION) BASE via AUDIT REAL must equal WO.build_arm_wo(override=None) (both reproduce V3).
    _, _, evidence_real = WO.build_arm_wo(SMOKE_SLICE, W, clf, lambda v: True, None, override=None,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)
    _, audit_base = AUDIT.build_arm_audit(SMOKE_SLICE, W, clf, gate_fn, sel_fn, gold,
                                          oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, wo_base = WO.build_arm_wo(SMOKE_SLICE, W, clf, gate_fn, sel_fn, override=None)
    assert M.arm_hash(audit_base) == M.arm_hash(wo_base), \
        (f"P1 REPRODUCTION FAIL: AUDIT REAL != WO override-disabled "
         f"(audit={M.arm_hash(audit_base)} wo={M.arm_hash(wo_base)})")
    print(f"[self-test] P1 reproduction: AUDIT REAL == WO override-disabled (hash {M.arm_hash(audit_base)})")

    res = run_experiment(SMOKE_SLICE, W, clf, ratings_table, gold, with_autopsy=True)
    for name in ("BASE", "VALENCY_GATED", "VALENCY_SCRAMBLE", "CANONICAL_BLUNT", "ROLE_ORACLE"):
        assert name in res["scored"], f"arm {name} missing from smoke run"
    f1s = {k: v["score"]["f1"] for k, v in res["scored"].items()}
    print(f"[self-test] 5-arm run on SMOKE_SLICE: f1={f1s}")
    print(f"[self-test] scramble_info: {res['scramble_info']}")

    prec_base = res["scored"]["BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"BASE precision {prec_base} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(BASE)={prec_base}")

    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    print(f"[self-test] kept_hashes: {hashes}")
    if len(set(hashes.values())) != len(hashes):
        print("[self-test] WARN: >=2 arms share a kept_hash at SMOKE_SLICE scale (small-sample) -- FULL slice "
              "is the load-bearing arms-differ check")

    # scaffold-free witness A: TRANSITIVE "the girl saw the child" -> child->PATIENT overriding animacy.
    tagged_t = [("The", "the", "DT"), ("girl", "girl", "NN"), ("saw", "saw", "VBD"),
                ("the", "the", "DT"), ("child", "child", "NN"), (".", ".", ".")]
    v0t = 2
    local_t = [1, 4]
    assert ORC.prev_prep(tagged_t, 4) is None, "witness: 'child' must be a core (no governing prep)"
    roles_t = {1: "AGENT", 4: "AGENT"}   # perceptron animacy-mislabels animate post-verbal 'child' AGENT
    tr_t = role_valency_reassign(roles_t, local_t, tagged_t, v0t, False, lambda v: True,
                                 lambda v: False, lambda v: False)
    assert tr_t["frame"] == "transitive", f"witness A: expected transitive, got {tr_t['frame']}"
    assert roles_t[4] == "PATIENT" and roles_t[1] == "AGENT", \
        f"WITNESS-A FAIL: transitive did not map post-verbal 'child'->PATIENT subj 'girl'->AGENT; got {roles_t}"
    print(f"[self-test] witness A transitive: {roles_t} (frame={tr_t['frame']})")

    # scaffold-free witness B: DITRANSITIVE "give the boy books" -> books(theme)->PATIENT; boy(recipient) NOT.
    tagged_d = [("give", "give", "VB"), ("the", "the", "DT"), ("boy", "boy", "NN"),
                ("books", "books", "NNS"), (".", ".", ".")]
    v0d = 0
    local_d = [2, 3]
    assert ORC.prev_prep(tagged_d, 2) is None and ORC.prev_prep(tagged_d, 3) is None, \
        "witness: 'boy' and 'books' must both be core"
    roles_d = {2: "PATIENT", 3: "NONE"}  # perceptron mis-steals recipient 'boy' as PATIENT
    tr_d = role_valency_reassign(roles_d, local_d, tagged_d, v0d, False, lambda v: True,
                                 real_ditrans_fn, real_light_fn)
    assert tr_d["frame"] == "ditransitive", f"witness B: expected ditransitive, got {tr_d['frame']}"
    assert roles_d[3] == "PATIENT" and roles_d[2] != "PATIENT", \
        f"WITNESS-B FAIL: ditransitive did not map theme 'books'->PATIENT + protect 'boy'; got {roles_d}"
    print(f"[self-test] witness B ditransitive: {roles_d} (frame={tr_d['frame']}, theme=post_core[-1])")

    # scaffold-free witness C: LIGHT "hold hands" -> override NEUTRALIZES (defers to BASE), unlike blunt.
    tagged_l = [("hold", "hold", "VB"), ("hands", "hands", "NNS"), (".", ".", ".")]
    v0l = 0
    local_l = [1]
    assert real_light_fn("hold") and not real_ditrans_fn("hold"), "witness C: 'hold' must be light, not ditransitive"
    roles_l = {1: "NONE"}                 # BASE (perceptron) did NOT emit 'hands' as patient
    tr_l = role_valency_reassign(roles_l, local_l, tagged_l, v0l, False, lambda v: True,
                                 real_ditrans_fn, real_light_fn)
    assert tr_l["frame"] == "light_verb_skip", f"witness C: expected light_verb_skip, got {tr_l['frame']}"
    assert roles_l[1] == "NONE", f"WITNESS-C FAIL: light-neutralize altered roles (should defer to BASE); {roles_l}"
    roles_l_blunt = {1: "NONE"}           # same clause treated transitive (blunt) WOULD force 'hands'->PATIENT
    tr_lb = role_valency_reassign(roles_l_blunt, local_l, tagged_l, v0l, False, lambda v: True,
                                  lambda v: False, lambda v: False)
    assert roles_l_blunt[1] == "PATIENT" and tr_lb["frame"] == "transitive", \
        f"WITNESS-C FAIL: blunt control did not force 'hands'->PATIENT; got {roles_l_blunt}"
    print(f"[self-test] witness C light-neutralize: light={roles_l} vs blunt={roles_l_blunt} (mechanism live)")

    # scramble differs from real on a ditransitive verb it drops (arms-differ live at the mechanism level).
    if res["scored"]["VALENCY_GATED"]["kept_hash"] == res["scored"]["VALENCY_SCRAMBLE"]["kept_hash"]:
        print("[self-test] WARN: VALENCY_GATED == VALENCY_SCRAMBLE kept_hash at SMOKE_SLICE (few ditransitive "
              "verbs in L04/L05) -- FULL slice is the load-bearing P2 check")
    else:
        print("[self-test] scramble live: VALENCY_GATED != VALENCY_SCRAMBLE kept_hash at SMOKE_SLICE")

    if not res["head_recovered"]:
        print(f"[self-test] WARN: {HEADLINE} recovered 0 gold items BASE misses at SMOKE_SLICE scale")
    else:
        print(f"[self-test] discriminator fires: {HEADLINE} recovers {len(res['head_recovered'])} gold items "
              f"BASE misses: {res['head_recovered']}")

    assert res["autopsy"] is not None, "autopsy did not run in smoke"
    print(f"[self-test] autopsy produced {len(res['autopsy'])} roleora-headroom item reports")

    _, k2 = build_arm_valency(SMOKE_SLICE, W, clf, gate_fn, sel_fn, real_ditrans_fn, real_light_fn)
    _, k3 = build_arm_valency(SMOKE_SLICE, W, clf, gate_fn, sel_fn, real_ditrans_fn, real_light_fn)
    assert M.arm_hash(k2) == M.arm_hash(k3), "non-deterministic VALENCY_GATED output across identical runs"
    print("[self-test] deterministic (two VALENCY_GATED runs produce identical kept-tuple hash)")

    print("[self-test] PASS")
    return 0


# ================================================================================================
# Verdict.
# ================================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=EXPECTED_N_ARMS)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    gold, meta = L.load_gold(slice_lessons)
    W, parser_info = M.train_dep_parser(run_mode)
    res = run_experiment(slice_lessons, W, clf, ratings_table, gold, with_autopsy=True)
    scored = res["scored"]

    f1 = {n: v["score"]["f1"] for n, v in scored.items()}
    prec = {n: v["score"]["precision"] for n, v in scored.items()}
    rec = {n: v["score"]["recall"] for n, v in scored.items()}
    rc = {n: v["recall_ceiling"] for n, v in scored.items()}

    f1_base = f1["BASE"]
    f1_head = f1[HEADLINE]
    f1_scram = f1["VALENCY_SCRAMBLE"]
    f1_blunt = f1["CANONICAL_BLUNT"]
    f1_oracle = f1["ROLE_ORACLE"]

    role_gap = round(f1_oracle - f1_base, 4)
    head_lift = round(f1_head - f1_base, 4)
    gap_closed_frac = round(head_lift / role_gap, 4) if role_gap > 1e-9 else None
    ablation_delta = round(f1_head - f1_blunt, 4)     # supplied valency contribution over un-gated blunt
    scramble_degrade = round(f1_head - f1_scram, 4)   # how much correct membership earns

    p1_ok = abs(f1_base - CITED_AUDIT_F1_REAL) <= P1_REPRO_TOL

    hard_fail_reasons = []
    if not p1_ok:
        hard_fail_reasons.append(f"P1 reproduction broke: |F1(BASE)={f1_base} - {CITED_AUDIT_F1_REAL}| > {P1_REPRO_TOL}")
    if f1_head <= f1_base:
        hard_fail_reasons.append(f"F1({HEADLINE})={f1_head} <= F1(BASE)={f1_base} (supplied-valency lever null)")
    if rec[HEADLINE] < rec["BASE"] - HF_RECALL_REGRESS:
        hard_fail_reasons.append(f"recall({HEADLINE})={rec[HEADLINE]} < recall(BASE)={rec['BASE']} - "
                                  f"{HF_RECALL_REGRESS} (recall regressed)")
    if f1_scram >= f1_head:
        hard_fail_reasons.append(f"F1(VALENCY_SCRAMBLE)={f1_scram} >= F1({HEADLINE})={f1_head} (scrambling the "
                                  "supplied set did NOT degrade -> the valency fact is a NO-OP/redundant)")

    hard_pass_conditions = dict(
        p1_reproduces=p1_ok,
        closes_half_gap=(head_lift >= HP_F1_MIN_LIFT),
        no_recall_regress=(rec[HEADLINE] >= rec["BASE"] - HP_RECALL_TOL),
        precision_holds=(prec[HEADLINE] >= prec["BASE"]),
        beats_ungated_blunt=(f1_head >= f1_blunt + HP_ABLATION_MARGIN),
        scramble_degrades=(f1_head >= f1_scram + HP_SCRAMBLE_MARGIN and f1_scram <= f1_base),
    )

    if hard_fail_reasons:
        verdict = "HARD_FAIL_SUPPLIED_VALENCY_NULL"
        vmsg = ("HARD_FAIL: " + "; ".join(hard_fail_reasons) +
                f". F1 BASE={f1_base} {HEADLINE}={f1_head} VALENCY_SCRAMBLE={f1_scram} CANONICAL_BLUNT={f1_blunt} "
                f"ROLE_ORACLE={f1_oracle}. precision BASE={prec['BASE']} {HEADLINE}={prec[HEADLINE]}. recall "
                f"BASE={rec['BASE']} {HEADLINE}={rec[HEADLINE]}. gap_closed_frac={gap_closed_frac} "
                f"ablation_delta(vs blunt)={ablation_delta} scramble_degrade={scramble_degrade}. "
                f"n_head_recovered={len(res['head_recovered'])} n_head_regressed={len(res['head_regressed'])}. "
                "SEE autopsy[] for the per-item mechanism gap (KEEP-DIGGING deliverable).")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_SUPPLIED_VALENCY_LIFT"
        vmsg = (f"HARD_PASS: supplied verb-valency lexicon lifts F1 BASE={f1_base} -> {HEADLINE}={f1_head} "
                f"(+{head_lift}, closes {gap_closed_frac} of the +{role_gap} ROLE_ORACLE gap); recall "
                f"{rec['BASE']}->{rec[HEADLINE]}; precision {prec['BASE']}->{prec[HEADLINE]}; beats un-gated "
                f"CANONICAL_BLUNT={f1_blunt} (ablation +{ablation_delta}); scramble degrades "
                f"(VALENCY_SCRAMBLE={f1_scram}, -{scramble_degrade}). Brain-faithful SUPPLIED subcat-valency "
                "(VerbNet), no selectional/animacy/patient-fit knowledge.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL_VALENCY_LIFT"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND: no HARD_FAIL trigger, but not all HARD_PASS held (failing: {failing}). "
                f"F1 BASE={f1_base} -> {HEADLINE}={f1_head} (+{head_lift}, closes {gap_closed_frac} of the "
                f"+{role_gap} gap); recall {rec['BASE']}->{rec[HEADLINE]}; precision "
                f"{prec['BASE']}->{prec[HEADLINE]}; VALENCY_SCRAMBLE={f1_scram} (degrade {scramble_degrade}); "
                f"CANONICAL_BLUNT={f1_blunt} (ablation {ablation_delta}). n_head_recovered="
                f"{len(res['head_recovered'])} n_head_regressed={len(res['head_regressed'])}. "
                "SEE autopsy[] for the per-item residual wall (KEEP-DIGGING deliverable).")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: f1 BASE={f1_base} {HEADLINE}={f1_head} (+{head_lift}) VALENCY_SCRAMBLE={f1_scram} "
                 f"CANONICAL_BLUNT={f1_blunt} ROLE_ORACLE={f1_oracle} | gap_closed_frac={gap_closed_frac} "
                 f"(role_gap={role_gap}) | ablation_delta={ablation_delta} scramble_degrade={scramble_degrade} | "
                 f"precision BASE={prec['BASE']} {HEADLINE}={prec[HEADLINE]} | recall BASE={rec['BASE']} "
                 f"{HEADLINE}={rec[HEADLINE]} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["BASE"]), headline_arm=HEADLINE,
        one_variable="role_valency_reassign: the ONLY word-identity input is a SUPPLIED verb-valency lexicon "
                     "lookup (subcat ARITY, not selectional preference). DITRANSITIVE verb -> PATIENT=post_core"
                     "[-1] (theme, last core), earlier core (recipient) protected; LIGHT verb -> neutralize "
                     "(defer to BASE); else transitive -> PATIENT=post_core[0]. "
                     "parser/perceptron/routing/admissibility-gate/>=2-patient selectional argmax held constant.",
        bands=dict(CITED_AUDIT_F1_REAL=CITED_AUDIT_F1_REAL,
                   CITED_AUDIT_F1_ROLE_ORACLE=CITED_AUDIT_F1_ROLE_ORACLE, CITED_ROLE_GAP=CITED_ROLE_GAP,
                   P1_REPRO_TOL=P1_REPRO_TOL, HP_GAP_CLOSE_FRAC=HP_GAP_CLOSE_FRAC,
                   HP_F1_MIN_LIFT=HP_F1_MIN_LIFT, HP_RECALL_TOL=HP_RECALL_TOL,
                   HP_ABLATION_MARGIN=HP_ABLATION_MARGIN, HP_SCRAMBLE_MARGIN=HP_SCRAMBLE_MARGIN,
                   HF_RECALL_REGRESS=HF_RECALL_REGRESS),
        f1=f1, precision=prec, recall=rec, recall_ceiling=rc,
        role_gap=role_gap, head_lift=head_lift, gap_closed_frac=gap_closed_frac,
        ablation_delta_vs_blunt=ablation_delta, scramble_degrade=scramble_degrade, p1_reproduces=p1_ok,
        hard_pass_conditions=hard_pass_conditions, hard_fail_reasons=hard_fail_reasons,
        n_roleora_recovered=len(res["roleora_recovered"]),
        roleora_recovered=[list(x) for x in res["roleora_recovered"][:40]],
        n_head_recovered=len(res["head_recovered"]),
        head_recovered=[list(x) for x in res["head_recovered"][:40]],
        n_head_regressed=len(res["head_regressed"]),
        head_regressed=[list(x) for x in res["head_regressed"][:40]],
        n_head_of_roleora=len(res["head_of_roleora"]),
        head_of_roleora=[list(x) for x in res["head_of_roleora"][:40]],
        n_blunt_recovered=len(res["blunt_recovered"]),
        blunt_recovered=[list(x) for x in res["blunt_recovered"][:40]],
        n_blunt_regressed=len(res["blunt_regressed"]),
        blunt_regressed=[list(x) for x in res["blunt_regressed"][:40]],
        n_scramble_recovered=len(res["scramble_recovered"]),
        scramble_recovered=[list(x) for x in res["scramble_recovered"][:40]],
        n_scramble_regressed=len(res["scramble_regressed"]),
        scramble_regressed=[list(x) for x in res["scramble_regressed"][:40]],
        roleora_headroom_coverage=(round(len(res["head_of_roleora"]) / len(res["roleora_recovered"]), 4)
                                   if res["roleora_recovered"] else None),
        lexicon_audit=dict(n_ditransitive=len(DITRANSITIVE_SET), n_light=len(LIGHT_VERB_SET),
                           seed_in_ditrans={w: (w in DITRANSITIVE_SET)
                                            for w in ("give", "show", "tell", "bring", "send", "hand",
                                                      "offer", "teach")},
                           headroom_out_of_ditrans={w: (w not in DITRANSITIVE_SET)
                                                    for w in ("see", "rub", "meet", "knock", "build")},
                           scramble=res["scramble_info"]),
        autopsy=res["autopsy"],
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"],
                         n_gold_pos=v["n_gold_pos"], precision=v["score"]["precision"],
                         recall=v["score"]["recall"], f1=v["score"]["f1"], n_pred=v["n_pred"],
                         subcat_fp=v["score"]["subcat_fp"], within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        parser_info=parser_info,
        cited_audit=dict(source="data/exp_reader_component_oracle_ablation_audit_v1/metrics.json",
                         f1_real=CITED_AUDIT_F1_REAL, f1_role_oracle=CITED_AUDIT_F1_ROLE_ORACLE,
                         role_uplift=CITED_ROLE_GAP),
        drive_note="Drive-2 (exp_reader_role_frame_gated_valency_v2) DERIVED valency from the noisy parse "
                   "(len(post_core)>=2 -> ditransitive), which false-fired on mis-routed particles/appositives "
                   "and demoted the correct patient (F1 0.43). This v3 SUPPLIES the valency as a VerbNet lexical "
                   "fact: a transitive verb is never classified ditransitive so it is immune to the mis-route "
                   "and always takes post_core[0]. CANONICAL_BLUNT reuses drive-1's build_arm_wo -> the ablation "
                   "VALENCY_GATED vs CANONICAL_BLUNT isolates exactly the supplied-valency contribution; "
                   "VALENCY_SCRAMBLE proves correct membership (not just having-a-set) earns its keep.",
        brain_check="the brain retrieves a verb's argument-structure frame (give is ditransitive) as a SUPPLIED "
                    "lexical valency fact from the mental lexicon; it does NOT count nouns from a noisy parse. "
                    "Supplied subcat-VALENCY (syntactic arity) is DISTINCT from selectional-PREFERENCE (semantic "
                    "patient-fit, redundant per 29491). Lever = supplied verb arity, structural mapping.",
        scope_caveat=("Parser trained on UD-EWT out-of-domain to McGuffey. The supplied lexicon is VerbNet-sourced "
                      "(Recipient+Theme double-object role-filter UNION {bring,send,hand}); 'find' is a VerbNet "
                      "benefactive dative -> harmless single-core (theme==post_core[0]) but flagged. Light-verb "
                      "neutralize can never regress vs BASE (equals BASE on light clauses) but forgoes speculative "
                      "recoveries there; polysemous give ('give an hour' light vs 'give the boy books' ditransitive) "
                      "resolves to ditransitive by precedence -> single-core light-give is an anticipated residual "
                      "(see autopsy). Passive/fronted-OSV left to the perceptron/coref (build/blockhouse OSV is "
                      "drive-1's FRONTED arm). MEASUREMENT cell, NOT banked; CLAIM-VET-pending; strategic read = "
                      "HYPOTHESIS pending landed-VET (skunkworks VETs separately)."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("gap_closed_frac:", gap_closed_frac, "role_gap:", role_gap, "head_lift:", head_lift)
    print("ablation_delta_vs_blunt:", ablation_delta, "scramble_degrade:", scramble_degrade)
    print("head_recovered:", res["head_recovered"])
    print("head_regressed:", res["head_regressed"])
    print("roleora_recovered:", res["roleora_recovered"])
    print("scramble_info:", json.dumps(res["scramble_info"], indent=1))
    print("AUTOPSY (roleora headroom per-item):")
    print(json.dumps(res["autopsy"], indent=1))
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
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
