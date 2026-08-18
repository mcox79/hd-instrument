"""exp_multi_turn_conversational_loop_crossturn_qa_v1 -- FIRST end-to-end integration test
of the conversational substrate: do the validated reader components COMPOSE into a working
multi-turn loop that answers CROSS-TURN questions, or do the component-level MM ceilings
COMPOUND (parse err -> coref err -> wrong answer)?

This is an ENGINEERING integration test, NOT a new mechanism. Pipeline per turn:
  parse (ie_extract) -> extract entities+relations -> fold into a SALIENCE-weighted discourse
  memory (Centering decay) + a per-entity attribute state -> answer a cross-turn question by
  resolving its referring expression against the memory, then looking up the attribute.

GENUINE REUSE (credited):
  - ie_extract / _tokenize / _tag_token: glass-box symbolic SVO parser + COREF_UNRESOLVED
    detection (exp_read_grow_foundation_realprose_glassbox_ie_v2.py).
  - _mentions_from_triples / _pron_number: discourse-memory mention extraction + number
    agreement (exp_read_coref_hobbs_centering_resolver_v1.py, HARD_PASS coref).
  - Centering salience ranking (freq + grammatical role + recency decay): generalizes
    exp_coref_salience_rank_topicality_v1.py (salience-rank MM).

Prereg: preregs/2026-07-23_multi_turn_conversational_loop_crossturn_qa_v1.md (BOTH bands set
before running). All run-time numbers are MEASURED@this cell's metrics.json.

ARMS (each comparison isolates ONE variable):
  LOCAL        = salience resolver + memory/state RESET at each turn boundary (within-turn only).
  MEM_recency  = recency-only resolver + cross-turn memory (ablation: salience OFF).
  MEM_salience = salience resolver + cross-turn memory (THE ASSEMBLED LOOP).

BANDS (envelope-fail; cross_turn_answerable = clear + distractor):
  HARD_PASS (composition HOLDS): MEM_salience answerable_acc >= 0.80 AND
    (MEM_salience - LOCAL) answerable >= 0.50 AND MEM_salience ambiguous halluc == 0.0 AND
    LOCAL within_turn_control >= 0.80 AND (MEM_salience - MEM_recency) distractor >= 0.30.
  HARD_FAIL (composition COMPOUNDS/FAILS): MEM_salience answerable_acc < 0.50 OR
    (MEM_salience - LOCAL) answerable < 0.20 OR MEM_salience ambiguous halluc > 0.0.
  MIDDLE otherwise (localize which stage/class drops).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                 [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                            [META_RULE_AF]
# - discriminator CAN-FAIL (interfaces may drop triples; salience may fail to separate; eps
#   may guess ties) AND FIRES (MEM_salience vs MEM_recency on the distractor class)  [design-gate]
# - REAL code path exercised in self-test (ie_extract + resolver + state on real dialogues)  [F.1]
# - baseline_in_band: LOCAL cross-turn ~0, LOCAL within-turn ~1; discriminator fires  [META_RULE_AG]
# - deterministic (fixed corpus, no RNG, no hash()-seed, no list(set) ordering)       [F.5/PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 5s)
# - crlb_n/a: no quantitative HD noise floor (symbolic resolution). N/A KGStore/cardinality-sweep.
# - progress_logging: print_flush_true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# --- GENUINE REUSE of the validated parser + discourse-memory primitives ---
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (
    ie_extract, _tokenize, _tag_token,
)
from experiments.exp_read_coref_hobbs_centering_resolver_v1 import (
    _mentions_from_triples, _pron_number,
)

ANCHOR_NAME = "multi_turn_conversational_loop_crossturn_qa_v1"

# --- salience (Centering) parameters ---
ROLE_W = {"subject": 1.0, "object": 0.6}
DECAY = 0.75
TIE_EPS = 0.15

# --- pre-registered bands (HYPOTHESIZED@this prereg) ---
HP_ANSWERABLE_MIN = 0.80
HP_MEM_MINUS_LOCAL_MIN = 0.50
HP_LOCAL_CONTROL_MIN = 0.80
HP_SALIENCE_OVER_RECENCY_MIN = 0.30
HF_ANSWERABLE_MAX = 0.50
HF_MEM_MINUS_LOCAL_MAX = 0.20


# ===========================================================================================
# CORPUS: hand-constructed multi-turn dialogues over the closed animal register ie_extract
# handles. Each dialogue: id, cls, turns (list of turns; each turn a list of sentence strings;
# the last sentence is the cross-turn question), gold_parse (statement -> gold triple set),
# gold_entity (the referent the question pronoun should resolve to; None = must abstain),
# gold_answer (the object lemma; None = UNKNOWN/abstain).
# ===========================================================================================
def _D(did, cls, turns, gold_parse, gold_entity, gold_answer):
    return {"id": did, "cls": cls, "turns": turns,
            "gold_parse": {k: set(v) for k, v in gold_parse.items()},
            "gold_entity": gold_entity, "gold_answer": gold_answer}


DIALOGUES = [
    # ---- cross_turn_clear: single number-compatible antecedent (distractors made plural) ----
    _D("clear1", "cross_turn_clear",
       [["The owl eats worms."], ["The cows chase the owl."], ["What does it eat?"]],
       {"The owl eats worms.": [("owl", "eats", "worm")],
        "The cows chase the owl.": [("cow", "chases", "owl")]},
       "owl", "worm"),
    _D("clear2", "cross_turn_clear",
       [["The frog lives in the pond."], ["The dogs chase the frog."], ["Where does it live?"]],
       {"The frog lives in the pond.": [("frog", "lives_in", "pond")],
        "The dogs chase the frog.": [("dog", "chases", "frog")]},
       "frog", "pond"),
    _D("clear3", "cross_turn_clear",
       [["The cat eats seeds."], ["The birds chase the cat."], ["What does it eat?"]],
       {"The cat eats seeds.": [("cat", "eats", "seed")],
        "The birds chase the cat.": [("bird", "chases", "cat")]},
       "cat", "seed"),
    _D("clear4", "cross_turn_clear",
       [["The cows eat grass."], ["The dog chases the cows."], ["What do they eat?"]],
       {"The cows eat grass.": [("cow", "eats", "grass")],
        "The dog chases the cows.": [("dog", "chases", "cow")]},
       "cow", "grass"),
    _D("clear5", "cross_turn_clear",
       [["The bird lives in the nest."], ["The frog eats worms."], ["The cats chase the bird."],
        ["Where does it live?"]],
       {"The bird lives in the nest.": [("bird", "lives_in", "nest")],
        "The frog eats worms.": [("frog", "eats", "worm")],
        "The cats chase the bird.": [("cat", "chases", "bird")]},
       "bird", "nest"),
    _D("clear6", "cross_turn_clear",
       [["The mouse eats bread."], ["The owls chase the mouse."], ["What does it eat?"]],
       {"The mouse eats bread.": [("mouse", "eats", "bread")],
        "The owls chase the mouse.": [("owl", "chases", "mouse")]},
       "mouse", "bread"),

    # ---- cross_turn_distractor: protagonist (repeated subject, topical) vs same-number recent
    #      distractor (object, turn 2). Recency picks the distractor; salience recovers protagonist.
    _D("distr1", "cross_turn_distractor",
       [["The frog eats worms."], ["The frog chases a cow."], ["What does it eat?"]],
       {"The frog eats worms.": [("frog", "eats", "worm")],
        "The frog chases a cow.": [("frog", "chases", "cow")]},
       "frog", "worm"),
    _D("distr2", "cross_turn_distractor",
       [["The cat eats a seed."], ["The cat chases a mouse."], ["What does it eat?"]],
       {"The cat eats a seed.": [("cat", "eats", "seed")],
        "The cat chases a mouse.": [("cat", "chases", "mouse")]},
       "cat", "seed"),
    _D("distr3", "cross_turn_distractor",
       [["The owl lives in the barn."], ["The owl chases a mouse."], ["Where does it live?"]],
       {"The owl lives in the barn.": [("owl", "lives_in", "barn")],
        "The owl chases a mouse.": [("owl", "chases", "mouse")]},
       "owl", "barn"),
    _D("distr4", "cross_turn_distractor",
       [["The dog eats bread."], ["The dog chases a cat."], ["What does it eat?"]],
       {"The dog eats bread.": [("dog", "eats", "bread")],
        "The dog chases a cat.": [("dog", "chases", "cat")]},
       "dog", "bread"),
    _D("distr5", "cross_turn_distractor",
       [["The bird eats a seed."], ["The bird lives in a tree."], ["The bird chases a frog."],
        ["What does it eat?"]],
       {"The bird eats a seed.": [("bird", "eats", "seed")],
        "The bird lives in a tree.": [("bird", "lives_in", "tree")],
        "The bird chases a frog.": [("bird", "chases", "frog")]},
       "bird", "seed"),
    _D("distr6", "cross_turn_distractor",
       [["The cow eats grass."], ["The cow chases a dog."], ["What does it eat?"]],
       {"The cow eats grass.": [("cow", "eats", "grass")],
        "The cow chases a dog.": [("cow", "chases", "dog")]},
       "cow", "grass"),

    # ---- cross_turn_ambiguous: two equal-salience number-compatible entities -> MUST ABSTAIN ----
    _D("amb1", "cross_turn_ambiguous",
       [["The cat and the dog eat grass."], ["What does it eat?"]],
       {"The cat and the dog eat grass.": [("cat", "eats", "grass"), ("dog", "eats", "grass")]},
       None, None),
    _D("amb2", "cross_turn_ambiguous",
       [["The frog and the owl eat worms."], ["What does it eat?"]],
       {"The frog and the owl eat worms.": [("frog", "eats", "worm"), ("owl", "eats", "worm")]},
       None, None),
    _D("amb3", "cross_turn_ambiguous",
       [["The bird and the mouse eat seeds."], ["What does it eat?"]],
       {"The bird and the mouse eat seeds.": [("bird", "eats", "seed"), ("mouse", "eats", "seed")]},
       None, None),
    _D("amb4", "cross_turn_ambiguous",
       [["The cow and the cat eat bread."], ["What does it eat?"]],
       {"The cow and the cat eat bread.": [("cow", "eats", "bread"), ("cat", "eats", "bread")]},
       None, None),
    # multi-turn genuine tie: the SAME pair repeated (both stay top-salience) -> must abstain.
    _D("amb5", "cross_turn_ambiguous",
       [["The dog and the owl eat bread."], ["The dog and the owl chase a cat."], ["What does it eat?"]],
       {"The dog and the owl eat bread.": [("dog", "eats", "bread"), ("owl", "eats", "bread")],
        "The dog and the owl chase a cat.": [("dog", "chases", "cat"), ("owl", "chases", "cat")]},
       None, None),

    # ---- within_turn_control: single turn = [statement, question]; answerable within-turn.
    #      Proves LOCAL is a real working pipeline (objects plural -> single singular antecedent). ----
    _D("ctrl1", "within_turn_control",
       [["The frog eats worms.", "What does it eat?"]],
       {"The frog eats worms.": [("frog", "eats", "worm")]},
       "frog", "worm"),
    _D("ctrl2", "within_turn_control",
       [["The owl lives in the barn.", "Where does it live?"]],
       {"The owl lives in the barn.": [("owl", "lives_in", "barn")]},
       "owl", "barn"),
    _D("ctrl3", "within_turn_control",
       [["The cat eats seeds.", "What does it eat?"]],
       {"The cat eats seeds.": [("cat", "eats", "seed")]},
       "cat", "seed"),
    _D("ctrl4", "within_turn_control",
       [["The cows eat grass.", "What do they eat?"]],
       {"The cows eat grass.": [("cow", "eats", "grass")]},
       "cow", "grass"),
    _D("ctrl5", "within_turn_control",
       [["The dog lives in a nest.", "Where does it live?"]],
       {"The dog lives in a nest.": [("dog", "lives_in", "nest")]},
       "dog", "nest"),
]

ANSWERABLE_CLASSES = {"cross_turn_clear", "cross_turn_distractor"}
ARMS = ["LOCAL", "MEM_recency", "MEM_salience"]
SMOKE_IDS = {"clear1", "clear2", "distr1", "distr2", "amb1", "amb2", "ctrl1", "ctrl2"}


# ===========================================================================================
# Question parsing (glass-box; reuses _tag_token to identify the relation verb).
# ===========================================================================================
def parse_question(text):
    """Return (pron, relation) if text is a supported cross-turn question, else None."""
    toks = _tokenize(text)
    if not toks or toks[0] not in ("what", "where"):
        return None
    pron = next((t for t in toks if t in ("it", "they")), None)
    if pron is None:
        return None
    rel = None
    for t in toks:
        tag, lemma, _form = _tag_token(t)
        if tag == "VERB":
            if lemma == "live":
                rel = "lives_in"
            elif lemma in ("eats", "chases"):
                rel = lemma
            break
    if rel is None:
        return None
    return pron, rel


# ===========================================================================================
# Salience-weighted discourse memory + resolvers.
# memory entry: {"lemma","role","number","idx"} where idx = global reading position.
# ===========================================================================================
def _salience(memory, pnum, cur_idx):
    """Per-distinct-lemma Centering salience over number-compatible mentions."""
    sal = {}
    for m in memory:
        if m["number"] != pnum:
            continue
        sal[m["lemma"]] = sal.get(m["lemma"], 0.0) + ROLE_W[m["role"]] * (DECAY ** (cur_idx - m["idx"]))
    return sal


def resolve_salience(memory, pnum, cur_idx):
    """Bind highest-salience number-compatible antecedent; ABSTAIN on 0 survivors or genuine
    salience tie (top1 - top2 <= TIE_EPS). Returns lemma or None."""
    sal = _salience(memory, pnum, cur_idx)
    if not sal:
        return None
    ordered = sorted(sal.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ordered) >= 2 and (ordered[0][1] - ordered[1][1]) <= TIE_EPS:
        return None
    return ordered[0][0]


def resolve_recency(memory, pnum, cur_idx):
    """Ablation: pick the MOST RECENT number-compatible mention's lemma (no salience, no
    abstain-on-tie). Returns lemma or None (only None if 0 candidates)."""
    for m in reversed(memory):
        if m["number"] == pnum:
            return m["lemma"]
    return None


def _resolve(arm, memory, pnum, cur_idx):
    return resolve_recency(memory, pnum, cur_idx) if arm == "MEM_recency" \
        else resolve_salience(memory, pnum, cur_idx)


# ===========================================================================================
# The multi-turn loop over ONE dialogue for ONE arm.
# LOCAL resets memory+state at each turn boundary (within-turn only); MEM_* persist across turns.
# ===========================================================================================
def run_dialogue(d, arm):
    persist = (arm != "LOCAL")
    memory = []
    state = {}
    idx = 0
    parse_ok = []          # per statement sentence: emitted triples == gold
    q_pron = None
    q_rel = None
    resolved_entity = "NO_QUESTION"
    answer = None

    for turn in d["turns"]:
        if not persist:
            memory = []
            state = {}
            idx = 0
        for sent in turn:
            q = parse_question(sent)
            if q is not None:
                q_pron, q_rel = q
                pnum = _pron_number(q_pron)
                resolved_entity = _resolve(arm, memory, pnum, idx)
                answer = state.get(resolved_entity, {}).get(q_rel) if resolved_entity else None
            else:
                triples, _rule, _fr = ie_extract(sent)
                emitted = set(triples)
                gold = d["gold_parse"].get(sent, set())
                parse_ok.append(emitted == gold)
                for (s, r, o) in triples:
                    state.setdefault(s, {})[r] = o
                for men in _mentions_from_triples(triples, sent, idx):
                    memory.append({"lemma": men["lemma"], "role": men["role"],
                                   "number": men["number"], "idx": idx})
            idx += 1

    gold_entity = d["gold_entity"]
    gold_answer = d["gold_answer"]
    coref_correct = (resolved_entity == gold_entity) if gold_entity is not None \
        else (resolved_entity is None)
    answer_correct = (answer == gold_answer) if gold_answer is not None \
        else (answer is None)
    hallucinated = (gold_answer is None and answer is not None)  # guessed on a must-abstain item
    return {"id": d["id"], "cls": d["cls"], "arm": arm,
            "resolved_entity": resolved_entity, "answer": answer,
            "gold_entity": gold_entity, "gold_answer": gold_answer,
            "coref_correct": bool(coref_correct), "answer_correct": bool(answer_correct),
            "hallucinated": bool(hallucinated), "parse_ok": parse_ok}


def _acc(rows, key):
    rows = list(rows)
    return (sum(1 for r in rows if r[key]) / len(rows)) if rows else 0.0


def run_arms(dialogues):
    per_arm = {}
    for arm in ARMS:
        rows = [run_dialogue(d, arm) for d in dialogues]
        by_cls = {}
        for cls in ("cross_turn_clear", "cross_turn_distractor", "cross_turn_ambiguous",
                    "within_turn_control"):
            crows = [r for r in rows if r["cls"] == cls]
            by_cls[cls] = {
                "n": len(crows),
                "answer_acc": _acc(crows, "answer_correct"),
                "coref_acc": _acc(crows, "coref_correct"),
                "hallucination_rate": _acc(crows, "hallucinated"),
            }
        answerable = [r for r in rows if r["cls"] in ANSWERABLE_CLASSES]
        # parse_acc is arm-independent (same parser) but reported per arm for completeness.
        all_parse = [ok for r in rows for ok in r["parse_ok"]]
        per_arm[arm] = {
            "by_class": by_cls,
            "answerable_answer_acc": _acc(answerable, "answer_correct"),
            "answerable_coref_acc": _acc(answerable, "coref_correct"),
            "parse_acc": (sum(all_parse) / len(all_parse)) if all_parse else 0.0,
            "rows": rows,
        }
    return per_arm


# ===========================================================================================
# Verdict (envelope-fail-bands per prereg).
# ===========================================================================================
def compute_verdict(per_arm):
    S = per_arm["MEM_salience"]
    L = per_arm["LOCAL"]
    R = per_arm["MEM_recency"]

    s_answerable = S["answerable_answer_acc"]
    l_answerable = L["answerable_answer_acc"]
    mem_minus_local = s_answerable - l_answerable
    s_amb_halluc = S["by_class"]["cross_turn_ambiguous"]["hallucination_rate"]
    l_control = L["by_class"]["within_turn_control"]["answer_acc"]
    s_distr = S["by_class"]["cross_turn_distractor"]["answer_acc"]
    r_distr = R["by_class"]["cross_turn_distractor"]["answer_acc"]
    salience_over_recency = s_distr - r_distr

    hp = (s_answerable >= HP_ANSWERABLE_MIN and
          mem_minus_local >= HP_MEM_MINUS_LOCAL_MIN and
          s_amb_halluc == 0.0 and
          l_control >= HP_LOCAL_CONTROL_MIN and
          salience_over_recency >= HP_SALIENCE_OVER_RECENCY_MIN)
    hf = (s_answerable < HF_ANSWERABLE_MAX or
          mem_minus_local < HF_MEM_MINUS_LOCAL_MAX or
          s_amb_halluc > 0.0)

    if hp:
        tier = "HARD_PASS"
        outcome = "composes"
    elif hf:
        tier = "HARD_FAIL"
        outcome = "compounds-fails"
    else:
        tier = "MIDDLE_BAND"
        outcome = "partial"

    localize = []
    if s_answerable < HP_ANSWERABLE_MIN:
        localize.append("MEM_salience answerable_acc=%.3f < %.2f (parse=%.3f coref=%.3f -> answer drop localizes stage)"
                        % (s_answerable, HP_ANSWERABLE_MIN, S["parse_acc"], S["answerable_coref_acc"]))
    if mem_minus_local < HP_MEM_MINUS_LOCAL_MIN:
        localize.append("cross-turn memory benefit (MEM_salience-LOCAL)=%.3f < %.2f" % (mem_minus_local, HP_MEM_MINUS_LOCAL_MIN))
    if s_amb_halluc > 0.0:
        localize.append("ZERO-HALLUCINATION BROKEN: MEM_salience guessed on %.0f%% of ambiguous ties" % (s_amb_halluc * 100))
    if l_control < HP_LOCAL_CONTROL_MIN:
        localize.append("LOCAL within-turn control=%.3f < %.2f (baseline pipeline itself weak -> comparison unfair)" % (l_control, HP_LOCAL_CONTROL_MIN))
    if salience_over_recency < HP_SALIENCE_OVER_RECENCY_MIN:
        localize.append("salience NOT load-bearing (MEM_salience-MEM_recency on distractor)=%.3f < %.2f" % (salience_over_recency, HP_SALIENCE_OVER_RECENCY_MIN))
    weakest = localize if localize else ["none (clean composition across all gates)"]

    msg = ("%s (%s) | MEM_salience answerable=%.3f (clear=%.3f distr=%.3f) parse=%.3f coref=%.3f "
           "| LOCAL answerable=%.3f control=%.3f | mem_benefit(S-L)=%.3f "
           "| MEM_salience amb_halluc=%.3f (abstain) | salience_load(S-R distr)=%.3f "
           "| MEM_recency distr=%.3f" % (
               tier, outcome, s_answerable,
               S["by_class"]["cross_turn_clear"]["answer_acc"], s_distr,
               S["parse_acc"], S["answerable_coref_acc"],
               l_answerable, l_control, mem_minus_local, s_amb_halluc,
               salience_over_recency, r_distr))
    return tier, outcome, msg, weakest, {
        "mem_salience_answerable_acc": s_answerable,
        "local_answerable_acc": l_answerable,
        "mem_minus_local": mem_minus_local,
        "mem_salience_ambiguous_hallucination_rate": s_amb_halluc,
        "local_within_turn_control_acc": l_control,
        "mem_salience_distractor_acc": s_distr,
        "mem_recency_distractor_acc": r_distr,
        "salience_over_recency_distractor": salience_over_recency,
    }


# ===========================================================================================
# infra: markers / metrics / crash (atomic).
# ===========================================================================================
def _out_dir(run_mode):
    sub = ANCHOR_NAME + ("_smoke" if run_mode == "smoke" else "")
    d = REPO / "data" / ("exp_" + sub)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(out_dir, diag)


def _arms_differ_digests(per_arm):
    digests = {}
    for arm in ARMS:
        answers = [(r["id"], r["answer"], r["resolved_entity"]) for r in per_arm[arm]["rows"]]
        digests[arm] = hashlib.sha256(json.dumps(answers, sort_keys=True).encode()).hexdigest()
    assert digests["LOCAL"] != digests["MEM_salience"], \
        "META_RULE_AF: LOCAL == MEM_salience (memory-scope variable no-op)"
    assert digests["MEM_recency"] != digests["MEM_salience"], \
        "META_RULE_AF: MEM_recency == MEM_salience (salience variable no-op)"
    return digests


# ===========================================================================================
# self-test: exercise the REAL code path + assert the discriminators FIRE.
# ===========================================================================================
def self_test():
    print("[self-test] constructing REAL pipeline (ie_extract + salience memory + state) ...", flush=True)

    # (1) parser reused correctly: statement parses, question detected.
    tr, rule, _ = ie_extract("The frog eats worms.")
    assert set(tr) == {("frog", "eats", "worm")}, "parse reuse failed: %s" % (tr,)
    assert parse_question("What does it eat?") == ("it", "eats"), "question parse failed"
    assert parse_question("Where does it live?") == ("it", "lives_in"), "where/live parse failed"
    assert parse_question("The frog eats worms.") is None, "statement misread as question"

    # (2) cross-turn CLEAR: MEM_salience answers, LOCAL fails (no cross-turn antecedent).
    d_clear = next(d for d in DIALOGUES if d["id"] == "clear1")
    s = run_dialogue(d_clear, "MEM_salience")
    l = run_dialogue(d_clear, "LOCAL")
    assert s["resolved_entity"] == "owl" and s["answer"] == "worm" and s["answer_correct"], \
        "MEM_salience failed clear1: %s" % s
    assert l["answer"] is None and not l["answer_correct"], \
        "LOCAL should fail cross-turn clear1 (no antecedent): %s" % l

    # (3) cross-turn DISTRACTOR: salience recovers protagonist; recency picks the distractor.
    d_distr = next(d for d in DIALOGUES if d["id"] == "distr1")
    sd = run_dialogue(d_distr, "MEM_salience")
    rd = run_dialogue(d_distr, "MEM_recency")
    assert sd["resolved_entity"] == "frog" and sd["answer"] == "worm" and sd["answer_correct"], \
        "salience must recover protagonist frog on distr1: %s" % sd
    assert rd["resolved_entity"] == "cow" and not rd["answer_correct"], \
        "recency must mis-resolve to distractor cow on distr1 (discriminator): %s" % rd

    # (4) AMBIGUOUS: MEM_salience must ABSTAIN (zero-hallucination); recency guesses.
    d_amb = next(d for d in DIALOGUES if d["id"] == "amb1")
    sa = run_dialogue(d_amb, "MEM_salience")
    ra = run_dialogue(d_amb, "MEM_recency")
    assert sa["resolved_entity"] is None and sa["answer"] is None and not sa["hallucinated"], \
        "MEM_salience must abstain on ambiguous amb1: %s" % sa
    assert ra["hallucinated"], "MEM_recency should hallucinate on the ambiguous tie (contrast): %s" % ra

    # (5) within-turn CONTROL: LOCAL answers (real pipeline).
    d_ctrl = next(d for d in DIALOGUES if d["id"] == "ctrl1")
    lc = run_dialogue(d_ctrl, "LOCAL")
    assert lc["answer"] == "worm" and lc["answer_correct"], \
        "LOCAL must answer within-turn control ctrl1: %s" % lc

    # (6) ARMS-MUST-DIFFER + baseline-in-band on the full corpus.
    per_arm = run_arms(DIALOGUES)
    _arms_differ_digests(per_arm)
    l_cross = per_arm["LOCAL"]["answerable_answer_acc"]
    l_ctrl = per_arm["LOCAL"]["by_class"]["within_turn_control"]["answer_acc"]
    assert l_cross <= 0.05, "LOCAL should be at floor on cross-turn (in-band): %.3f" % l_cross
    assert l_ctrl >= 0.80, "LOCAL should answer within-turn control (real pipeline): %.3f" % l_ctrl
    s_ans = per_arm["MEM_salience"]["answerable_answer_acc"]
    assert s_ans > l_cross, "discriminator must fire: MEM_salience %.3f !> LOCAL %.3f" % (s_ans, l_cross)

    print("[self-test] PASS | MEM_salience answerable=%.3f LOCAL cross=%.3f control=%.3f | "
          "distractor salience=%.3f recency=%.3f | parse=%.3f"
          % (s_ans, l_cross, l_ctrl,
             per_arm["MEM_salience"]["by_class"]["cross_turn_distractor"]["answer_acc"],
             per_arm["MEM_recency"]["by_class"]["cross_turn_distractor"]["answer_acc"],
             per_arm["MEM_salience"]["parse_acc"]), flush=True)
    return True


# ===========================================================================================
# main.
# ===========================================================================================
def run(run_mode):
    dialogues = [d for d in DIALOGUES if d["id"] in SMOKE_IDS] if run_mode == "smoke" else DIALOGUES
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units=len(dialogues) * len(ARMS))
    t0 = time.perf_counter()

    per_arm = run_arms(dialogues)
    digests = _arms_differ_digests(per_arm)
    tier, outcome, msg, weakest, gates = compute_verdict(per_arm)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in per_arm[a].items() if k != "rows"}

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "composition_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_dialogues": len(dialogues),
        "arms": ARMS, "gates": gates, "weakest_interface": weakest,
        "salience_params": {"role_w": ROLE_W, "decay": DECAY, "tie_eps": TIE_EPS},
        "bands": {"HP_answerable_min": HP_ANSWERABLE_MIN, "HP_mem_minus_local_min": HP_MEM_MINUS_LOCAL_MIN,
                  "HP_local_control_min": HP_LOCAL_CONTROL_MIN,
                  "HP_salience_over_recency_min": HP_SALIENCE_OVER_RECENCY_MIN,
                  "HF_answerable_max": HF_ANSWERABLE_MAX, "HF_mem_minus_local_max": HF_MEM_MINUS_LOCAL_MAX},
        "per_arm": {a: strip(a) for a in ARMS},
        "per_dialogue": {a: [{k: r[k] for k in ("id", "cls", "resolved_entity", "answer",
                                                "gold_entity", "gold_answer", "coref_correct",
                                                "answer_correct", "hallucinated")}
                             for r in per_arm[a]["rows"]] for a in ARMS},
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "reuse_credited": {
            "ie_extract": "exp_read_grow_foundation_realprose_glassbox_ie_v2.py",
            "coref_memory": "exp_read_coref_hobbs_centering_resolver_v1.py (_mentions_from_triples/_pron_number)",
            "salience_rank": "exp_coref_salience_rank_topicality_v1.py (Centering freq+role+decay)"},
        "REQUIRED_FIELDS": ["verdict", "gates", "per_arm", "per_dialogue", "arms_differ_digests"],
        "notes": ("FIRST end-to-end multi-turn conversational loop integration test. Arms: LOCAL "
                  "(within-turn only), MEM_recency (cross-turn memory, salience OFF ablation), "
                  "MEM_salience (assembled loop). HARD_PASS=components compose; HARD_FAIL=MM ceilings "
                  "compound / no memory benefit / zero-hallucination broken. Glass-box, no LLM, no autograd. "
                  "CLAIM-VET-pending; hand-constructed dialogues (realistic register, not answer-leaking)."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    for a in ARMS:
        pa = per_arm[a]
        bc = pa["by_class"]
        print("  [%-12s] answerable=%.3f | clear=%.3f distr=%.3f amb_halluc=%.3f ctrl=%.3f | parse=%.3f coref=%.3f"
              % (a, pa["answerable_answer_acc"], bc["cross_turn_clear"]["answer_acc"],
                 bc["cross_turn_distractor"]["answer_acc"], bc["cross_turn_ambiguous"]["hallucination_rate"],
                 bc["within_turn_control"]["answer_acc"], pa["parse_acc"], pa["answerable_coref_acc"]), flush=True)
    print("  [weakest] %s" % weakest, flush=True)
    print("  [metrics] -> %s" % (out_dir / "metrics.json"), flush=True)
    return tier


def main():
    ap = argparse.ArgumentParser(description=ANCHOR_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)
    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    run(run_mode)
    sys.exit(0)


if __name__ == "__main__":
    _md = "smoke" if ("--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv)) else \
        ("self_test" if ("--self-test" in sys.argv or ("--run-mode" in sys.argv and "self_test" in sys.argv)) else "full")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
