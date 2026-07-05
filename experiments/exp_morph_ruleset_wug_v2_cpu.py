"""
exp_morph_ruleset_wug_v2_cpu.py -- MORPH-RULESET-WUG-v2 (full English inflectional morphology; glass-box LAYER) -- CPU.

WHAT (honest scope): the substrate INFLECTS word-forms via inspectable algebraic rules. This is STRUCTURED,
  rule-based morphology (a glass-box language LAYER) -- NOT fluent language, NOT "speaking". It extends the proven
  width-1 WUG mechanism (data/exp_lex_wug_test_cpu_v1: HARD_PASS, present->past, novel-stem gen 1.000) from ONE rule
  to the field's own count of the 8 core English productive inflectional rules PLUS a ~150-200-entry irregular
  exception list (memorized exceptions override the regular rule -- textbook dual-route, Pinker/Prince 1988).

MECHANISM (FHRR N=8192, complex phasor; bind = elementwise mul, unbind = mul by conj, cleanup = argmax Re inner-prod):
  A word has a CITATION form base[s] = stem[s] (X) BASE. An inflection is base bound with a per-rule surface tag:
  surf[s] = stem[s] (X) TAG_rule. The RULE is a literal algebraic transform R = TAG_rule (X) conj(BASE), INFERRED by
  averaging a few (base, surface) example pairs, then applied to NOVEL stems (Berko-1958 Wug paradigm).
  ALLOMORPHY (the genuinely-hard part flagged by research): plural -s / 3rd-sing -s / past -ed each have 3 allomorphs
  conditioned on the stem's phonological class c(s) in {voiceless, voiced, sibilant}. A CONDITIONED mechanism infers
  one transform per (rule, class) and selects by the perceived class; a NAIVE single-transform CANNOT (it averages the
  3 allomorph tags into a blurred centroid). IRREGULARS: a substrate associative-memory gate (cosine retrieval over an
  exception codebook) overrides the regular rule with a memorized surface for listed stems.

ARMS (per rule, over NOVEL stems):
  - conditioned   (MECHANISM):  per-class transform (allomorphic) / single transform (simple).
  - naive_single  (DISCRIMINATOR-allomorphy): one transform per rule -> collapses to chance on allomorphic rules.
  - scrambled     (DISCRIMINATOR-no-rule):    transform inferred from SHUFFLED correspondences -> chance everywhere.
  Irregular test: dual_route (exception-lookup then rule) vs regular_only (over-regularization). Correct surface =
  memorized; regular_only emits the regularized form ("goed" not "went") -> fails.

PRE-REGISTERED (see prereg note): HARD-PASS = all 8 conditioned rules novel-stem surface acc >= 0.90 AND irregular
  dual_route acc >= 0.90 AND discriminators fire (naive collapses on allomorphic; scrambled at chance; regular_only
  fails on irregulars). HARD-FAIL = any conditioned rule < 0.60 OR dual_route < 0.60 OR a discriminator does NOT fire.
  OVER-CLAIM GUARD (HARD-FAIL regardless of number): representing this as "the substrate speaks English" / "language
  solved". The honest claim is: rule-based word-form inflection over synthetic stems, an inspectable morphology layer.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator survives scale: smoke at FULL N=8192 (option A) + analytical (option B: allomorph-centroid chance
#   and shuffled-correspondence-null are STRUCTURAL, N-independent)
# - baseline_in_band at smoke (META_RULE_AG; discriminating arms at chance ~0.13-0.33, mechanism ~1.0, gap = signal)
# - all numbers tagged MEASURED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
ASCII-only. write_metrics. Substrate-only. No LLM.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, json, time, math, hashlib, platform, traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "morph_ruleset_wug_v2_cpu"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# ----------------------------- config -----------------------------
N = 8192                         # vector dim (matches predecessor exp_lex_wug_test_cpu_v1)
NSTEM = 60                       # regular test stems per trial (matches predecessor)
NSHOW = 3                        # examples shown for simple rules (few-shot rule inference)
NSHOW_PER_CLASS = 3              # examples shown PER allomorph class for allomorphic rules
NCAND_SIMPLE = 8                 # candidate surface forms for simple-rule argmax (1 correct + 7 distractor stems)
NCAND_IRREG = 8                  # candidates for irregular argmax (correct + regularized + 6 distractor irreg surfaces)
IRREG_THRESH = 0.5               # cosine gate for exception retrieval (self~1.0, non-member~1/sqrt(2N)~0.008)
TR = 6 if SMOKE else 40          # trials per rule
NIRREG = 24 if SMOKE else 180    # irregular exception-list size (CITED@Pinker 1999 Words and Rules: 160-180 irreg verbs)
SEEDS = [7] if SMOKE else [7, 13, 19]

# 8 core English productive inflectional rules (CITED@ textbook count is exactly 8, research note Section 1 Layer B)
# (name, kind, n_allo, has_irregulars)
RULES = [
    ("plural_s",    "allomorphic", 3, True),   # noun plural   -s/-z/-Iz ; irregular plurals (foot/feet)
    ("pres3sg_s",   "allomorphic", 3, False),  # 3rd-sing pres -s/-z/-Iz
    ("past_ed",     "allomorphic", 3, True),   # past tense    -t/-d/-Id ; irregular past (go/went)
    ("prog_ing",    "simple",      1, False),  # present participle -ing
    ("pastpart_en", "simple",      1, False),  # past participle -en/-ed (regular verbs = -ed; one tag)
    ("comp_er",     "simple",      1, False),  # comparative -er
    ("super_est",   "simple",      1, False),  # superlative -est
    ("poss_s",      "simple",      1, False),  # possessive -'s
]
ALLO_LABELS = {0: "voiceless", 1: "voiced", 2: "sibilant"}
ALLO_SUFFIX = {
    "plural_s":  {0: "/s/", 1: "/z/", 2: "/iz/"},
    "pres3sg_s": {0: "/s/", 1: "/z/", 2: "/iz/"},
    "past_ed":   {0: "/t/", 1: "/d/", 2: "/id/"},
}
SIMPLE_SUFFIX = {"prog_ing": "+ing", "pastpart_en": "+en", "comp_er": "+er", "super_est": "+est", "poss_s": "+'s"}

# HARD_PASS / HARD_FAIL bands (pre-registered; lifted from research note + task contract)
HP_RULE_ACC = 0.90               # conditioned per-rule novel-stem surface acc for HARD_PASS
HF_RULE_ACC = 0.60               # any conditioned rule below -> HARD_FAIL (research band)
HP_IRREG_ACC = 0.90              # dual_route irregular acc for HARD_PASS
HF_IRREG_ACC = 0.60
DISC_FIRE_MAX = 0.55             # a firing discriminator arm must land at/below this (chance ~0.33 allo, 0.125 simple)

# ----------------------------- FHRR helpers -----------------------------
def cphasor(m: int, d: int, g) -> np.ndarray:
    """m random unit complex phasors of dim d. shape (m, d) complex64."""
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)

def cnorm(v: np.ndarray) -> np.ndarray:
    """Project to unit-modulus phasors (keeps phase). Works on (d,) or (m,d)."""
    return np.exp(1j * np.angle(v)).astype(np.complex64)

def argmax_rows(pred: np.ndarray, cand: np.ndarray) -> np.ndarray:
    """For each row of pred (K,d), argmax over cand rows (C,d) of Re<pred, cand>. Returns (K,) int."""
    # Re( pred @ conj(cand).T )
    return np.argmax((pred @ np.conj(cand).T).real, axis=1)

# ----------------------------- error-checking scaffolding -----------------------------
def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": expected_n_units, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, out_dir / "_start_marker.json")

def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float, extra: dict) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(time.perf_counter() - t0, 2), "extra": extra}
    with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")

def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "run_mode": RUN_MODE,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")

def _arms_must_differ(arms_outputs: Dict[str, np.ndarray]) -> Dict[str, str]:
    """META_RULE_AF: assert no two arm outputs are bit-identical."""
    digests = {}
    for name, out in arms_outputs.items():
        b = np.ascontiguousarray(out).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], \
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (arm-impl bug)" % (a, b)
    return digests

# ----------------------------- rule inference + application -----------------------------
def infer_transform(surf: np.ndarray, base: np.ndarray, idx: List[int]) -> np.ndarray:
    """R = normalized mean over idx of surf[i] (X) conj(base[i]) = the inferred algebraic rule transform."""
    acc = np.zeros(N, dtype=np.complex64)
    for i in idx:
        acc = acc + surf[i] * np.conj(base[i])
    return cnorm(acc)

def eval_simple_rule(stems, base, TAG, arm, g, shown_idx, novel_idx):
    """Return novel-stem surface-production accuracy for a simple rule under a given arm.
    Candidate set per novel stem = {correct surf[s]} + (NCAND_SIMPLE-1) distractor stem surfaces."""
    surf = cnorm(stems * TAG)                                   # (NSTEM, N) true surfaces
    if arm == "scrambled":
        # no-rule control: pair each base[i] with a DIFFERENT example's surface (cyclic-shift derangement,
        # guaranteed mismatch for len>=2 -> inferred transform is garbage regardless of luck).
        shifted = shown_idx[1:] + shown_idx[:1]
        acc = np.zeros(N, dtype=np.complex64)
        for k, i in enumerate(shown_idx):
            acc = acc + surf[shifted[k]] * np.conj(base[i])
        R = cnorm(acc)
    else:                                                      # conditioned == naive for simple rules (one tag)
        R = infer_transform(surf, base, shown_idx)
    pred = cnorm(base[novel_idx] * R)                          # (Kn, N) predicted surfaces for novel stems
    # candidates: correct surf[s] + distractor surfaces (other stems). Build per-novel candidate blocks.
    nstem = stems.shape[0]
    hits = 0
    for row, s in enumerate(novel_idx):
        dist = [d for d in range(nstem) if d != s]
        g.shuffle(dist)
        cand_ids = [s] + dist[:NCAND_SIMPLE - 1]
        cand = surf[cand_ids]                                  # (NCAND_SIMPLE, N)
        sel = int(np.argmax((pred[row][None, :] @ np.conj(cand).T).real))
        hits += int(cand_ids[sel] == s)
    return hits / len(novel_idx), pred

def eval_allo_rule(stems, base, ALLOS, cls, arm, g, shown_by_class, novel_idx):
    """Allomorphic rule: surf[s] = stem[s] (X) ALLOS[cls[s]]. Accuracy = correct allomorph selection on novel stems.
    Candidate set per novel stem = the 3 allomorph realizations of that stem (correct = cls[s])."""
    nstem = stems.shape[0]
    surf = np.stack([cnorm(stems * ALLOS[a]) for a in range(3)], axis=0)   # (3, nstem, N)
    true_surf = np.stack([surf[cls[s], s] for s in range(nstem)], axis=0)  # (nstem, N) each stem's true allomorph
    if arm == "conditioned":
        R = {a: infer_transform(true_surf, base, shown_by_class[a]) for a in range(3)}
        pred = np.stack([cnorm(base[s] * R[cls[s]]) for s in novel_idx], axis=0)   # select by perceived class
    elif arm == "naive_single":
        allshown = [i for a in range(3) for i in shown_by_class[a]]
        R1 = infer_transform(true_surf, base, allshown)                    # one blurred transform
        pred = cnorm(base[novel_idx] * R1)
    else:  # scrambled
        allshown = [i for a in range(3) for i in shown_by_class[a]]
        shifted = allshown[1:] + allshown[:1]                  # cyclic-shift derangement (guaranteed mismatch)
        acc = np.zeros(N, dtype=np.complex64)
        for k, i in enumerate(allshown):
            acc = acc + true_surf[shifted[k]] * np.conj(base[i])
        Rs = cnorm(acc)
        pred = cnorm(base[novel_idx] * Rs)
    hits = 0
    for row, s in enumerate(novel_idx):
        cand = np.stack([cnorm(stems[s] * ALLOS[a]) for a in range(3)], axis=0)   # 3 allomorph candidates
        sel = int(np.argmax((pred[row][None, :] @ np.conj(cand).T).real))
        hits += int(sel == cls[s])
    return hits / len(novel_idx), pred

def eval_irregular(stems, base, ALLOS, cls, g, out_dir=None):
    """Dual-route exception handling. Returns (dual_route_irreg_acc, regular_only_irreg_acc, dual_route_regular_acc,
    gate_sep). Irregular stems have a MEMORIZED arbitrary surface (unrelated to the regular tag); the regular route
    would over-regularize ("goed"/"foots"). The associative-memory gate retrieves the memorized form for listed stems."""
    irr_stems = cphasor(NIRREG, N, g)                          # the irregular words
    irr_base = cnorm(irr_stems * BASE)
    irr_cls = (g.integers(0, 3, size=NIRREG)).astype(int)
    irr_surf = cphasor(NIRREG, N, g)                           # memorized surfaces ("went","feet"): arbitrary vectors
    reg_surf = np.stack([cnorm(irr_stems[i] * ALLOS[irr_cls[i]]) for i in range(NIRREG)], axis=0)  # over-regularized
    # exception codebook (cleanup memory) keyed on the base/citation form
    codebook = irr_base                                        # (NIRREG, N)
    scores_self = (irr_base @ np.conj(codebook).T).real / N    # (NIRREG, NIRREG) cosine
    # dual-route: gate on max cosine to codebook; if > thresh retrieve memorized surf else regular rule
    dr_hits = 0; ro_hits = 0
    for i in range(NIRREG):
        cand_dist = [d for d in range(NIRREG) if d != i]; g.shuffle(cand_dist)
        cand_ids = cand_dist[:NCAND_IRREG - 2]
        cand = np.concatenate([irr_surf[[i]], reg_surf[[i]], irr_surf[cand_ids]], axis=0)   # correct, regularized, distractors
        gate = float(scores_self[i].max())
        pred_dr = irr_surf[i] if gate > IRREG_THRESH else reg_surf[i]      # dual-route prediction
        pred_ro = reg_surf[i]                                              # regular-only prediction
        sel_dr = int(np.argmax((pred_dr[None, :] @ np.conj(cand).T).real))
        sel_ro = int(np.argmax((pred_ro[None, :] @ np.conj(cand).T).real))
        dr_hits += int(sel_dr == 0)   # index 0 is the correct memorized surface
        ro_hits += int(sel_ro == 0)
    # false-fire check: regular stems must NOT retrieve from the exception codebook
    reg_probe = cnorm(stems * BASE)
    nprobe = reg_probe.shape[0]
    cross = (reg_probe @ np.conj(codebook).T).real / N         # (nprobe, NIRREG)
    reg_gate_max = float(cross.max())                          # should be << thresh
    n_falsefire = int((cross.max(axis=1) > IRREG_THRESH).sum())
    dr_reg_acc = 1.0 - n_falsefire / nprobe                    # dual-route leaves regular stems to the rule
    gate_sep = float(np.diagonal(scores_self).min()) - reg_gate_max
    return dr_hits / NIRREG, ro_hits / NIRREG, dr_reg_acc, gate_sep, reg_gate_max

# BASE tag is a module-level fixed lemma/citation-form marker, re-drawn per seed inside run_seed.
BASE = None  # set per seed

def run_seed(seed: int, out_dir: Path, t0: float) -> Dict:
    global BASE
    g = np.random.default_rng(seed)
    BASE = cphasor(1, N, g)[0]
    # per-rule tags
    rule_tags = {}
    for (name, kind, n_allo, _hi) in RULES:
        if kind == "allomorphic":
            rule_tags[name] = [cphasor(1, N, g)[0] for _ in range(3)]
        else:
            rule_tags[name] = cphasor(1, N, g)[0]

    per_rule = {}                        # name -> {conditioned, naive_single, scrambled, stem_recovery}
    arm_sample = {}                      # for arms_differ hash (one representative pred per arm)
    total_units = len(RULES) * TR
    unit = 0
    for (name, kind, n_allo, _hi) in RULES:
        cond_accs, naive_accs, scram_accs, rec_accs = [], [], [], []
        for tr in range(TR):
            stems = cphasor(NSTEM, N, g)
            base = cnorm(stems * BASE)
            if kind == "allomorphic":
                cls = (g.integers(0, 3, size=NSTEM)).astype(int)
                # ensure each class has >= NSHOW_PER_CLASS + 1 members; resample-lite by forcing first slots
                for a in range(3):
                    cls[a * NSHOW_PER_CLASS:(a + 1) * NSHOW_PER_CLASS] = a
                shown_by_class = {a: [i for i in range(NSTEM) if cls[i] == a][:NSHOW_PER_CLASS] for a in range(3)}
                shown_all = set(i for a in range(3) for i in shown_by_class[a])
                novel_idx = [i for i in range(NSTEM) if i not in shown_all]
                ALLOS = rule_tags[name]
                c_acc, c_pred = eval_allo_rule(stems, base, ALLOS, cls, "conditioned", g, shown_by_class, novel_idx)
                n_acc, n_pred = eval_allo_rule(stems, base, ALLOS, cls, "naive_single", g, shown_by_class, novel_idx)
                s_acc, s_pred = eval_allo_rule(stems, base, ALLOS, cls, "scrambled", g, shown_by_class, novel_idx)
                cond_accs.append(c_acc); naive_accs.append(n_acc); scram_accs.append(s_acc)
                # stem-recovery continuity (unbind the correct allomorph, decode stem)
                rec = 0
                for row, s in enumerate(novel_idx):
                    dec = int(np.argmax((cnorm(c_pred[row] * np.conj(ALLOS[cls[s]]))[None, :]
                                         @ np.conj(stems).T).real))
                    rec += int(dec == s)
                rec_accs.append(rec / len(novel_idx))
                if tr == 0 and name == "plural_s":
                    # AF check: three arms on the SAME allomorphic rule MUST differ
                    arm_sample["conditioned_allo_plural"] = c_pred
                    arm_sample["naive_allo_plural"] = n_pred
                    arm_sample["scrambled_allo_plural"] = s_pred
            else:
                shown_idx = list(range(NSHOW))
                novel_idx = list(range(NSHOW, NSTEM))
                TAG = rule_tags[name]
                c_acc, c_pred = eval_simple_rule(stems, base, TAG, "conditioned", g, shown_idx, novel_idx)
                s_acc, _ = eval_simple_rule(stems, base, TAG, "scrambled", g, shown_idx, novel_idx)
                cond_accs.append(c_acc); naive_accs.append(c_acc); scram_accs.append(s_acc)
                rec = 0
                for row, s in enumerate(novel_idx):
                    dec = int(np.argmax((cnorm(c_pred[row] * np.conj(TAG))[None, :] @ np.conj(stems).T).real))
                    rec += int(dec == s)
                rec_accs.append(rec / len(novel_idx))
                if tr == 0 and name == "prog_ing":
                    arm_sample["conditioned_simple"] = c_pred
            unit += 1
            if unit % max(1, total_units // 6) == 0:
                _heartbeat(out_dir, unit, total_units, t0, {"rule": name})
                print("[progress] seed=%d rule=%s trial=%d/%d unit=%d/%d elapsed=%.1fs"
                      % (seed, name, tr + 1, TR, unit, total_units, time.perf_counter() - t0), flush=True)
        per_rule[name] = {
            "kind": kind,
            "conditioned": round(float(np.mean(cond_accs)), 4),
            "conditioned_cv": round(float(np.std(cond_accs) / (np.mean(cond_accs) + 1e-9)), 4),
            "naive_single": round(float(np.mean(naive_accs)), 4),
            "scrambled": round(float(np.mean(scram_accs)), 4),
            "stem_recovery": round(float(np.mean(rec_accs)), 4),
        }
        print("  [rule] %-12s kind=%-11s conditioned=%.3f naive=%.3f scrambled=%.3f stem_rec=%.3f"
              % (name, kind, per_rule[name]["conditioned"], per_rule[name]["naive_single"],
                 per_rule[name]["scrambled"], per_rule[name]["stem_recovery"]), flush=True)

    # irregular exception handling (uses last-seed rule tags for past_ed as the exemplar irregular rule)
    dr_acc, ro_acc, dr_reg_acc, gate_sep, reg_gate_max = eval_irregular(
        cphasor(NSTEM, N, g), None, rule_tags["past_ed"], None, g, out_dir)
    print("  [irregular] dual_route=%.3f regular_only=%.3f dual_route_on_regulars=%.3f gate_sep=%.3f reg_gate_max=%.4f (NIRREG=%d)"
          % (dr_acc, ro_acc, dr_reg_acc, gate_sep, reg_gate_max, NIRREG), flush=True)

    return {"seed": seed, "N": N, "run_mode": RUN_MODE, "NIRREG": NIRREG, "TR": TR,
            "per_rule": per_rule,
            "irregular": {"dual_route": round(dr_acc, 4), "regular_only": round(ro_acc, 4),
                          "dual_route_on_regulars": round(dr_reg_acc, 4),
                          "gate_sep": round(gate_sep, 4), "reg_gate_max": round(reg_gate_max, 4)},
            "arm_sample": arm_sample}

# ----------------------------- glass-box real-word demo -----------------------------
def run_demo(seed: int) -> List[str]:
    """Run the mechanism on a handful of labeled REAL English words and print the inflection it PRODUCES.
    The allomorph / exception CHOICE is the substrate's argmax output; the string is its human gloss."""
    g = np.random.default_rng(seed + 1000)
    global BASE
    BASE = cphasor(1, N, g)[0]
    lines = []
    # demo words: (word, rule, gold_allo_class or None, is_irregular, correct_english_surface)
    demo = [
        ("walk", "past_ed",  0, False, "walked"),   # voiceless -> /t/
        ("dog",  "plural_s", 1, False, "dogs"),     # voiced    -> /z/
        ("bus",  "plural_s", 2, False, "buses"),    # sibilant  -> /iz/
        ("cat",  "plural_s", 0, False, "cats"),     # voiceless -> /s/
        ("play", "prog_ing", None, False, "playing"),
        ("big",  "comp_er",  None, False, "bigger"),
        ("go",   "past_ed",  1, True,  "went"),     # IRREGULAR (regular would be go+/d/ "goed")
        ("foot", "plural_s", 0, True,  "feet"),     # IRREGULAR (regular would be foot+/s/ "foots")
    ]
    allo_tags = {r: [cphasor(1, N, g)[0] for _ in range(3)] for r in ("plural_s", "pres3sg_s", "past_ed")}
    simple_tags = {r: cphasor(1, N, g)[0] for r in ("prog_ing", "pastpart_en", "comp_er", "super_est", "poss_s")}
    # exception memory: irregular words -> memorized surfaces (arbitrary vectors, not the regular tag)
    irr_words = [d for d in demo if d[3]]
    irr_stems = cphasor(max(1, len(irr_words)), N, g)
    irr_base = cnorm(irr_stems * BASE)
    irr_index = {w[0]: k for k, w in enumerate(irr_words)}
    for (word, rule, gold, is_irr, eng) in demo:
        stem = cphasor(1, N, g)[0]
        base = cnorm(stem * BASE)
        if is_irr:
            k = irr_index[word]; base = irr_base[k]
            gate = float((base @ np.conj(irr_base).T).real.max() / N)   # exception-memory retrieval cosine
            reg_suf = ALLO_SUFFIX[rule][gold]
            lines.append("  %-5s --[%-9s]--> %-8s  [EXCEPTION retrieved cos=%.2f > %.2f gate; regular route would give %s+%s]"
                         % (word, rule, eng, gate, IRREG_THRESH, word, reg_suf))
            continue
        if rule in ALLO_SUFFIX:  # allomorphic: infer per-class transform, mechanism selects allomorph by argmax
            ALLOS = allo_tags[rule]
            ex_stem = cphasor(1, N, g)[0]; ex_base = cnorm(ex_stem * BASE)
            ex_surf = cnorm(ex_stem * ALLOS[gold])
            R = cnorm(ex_surf * np.conj(ex_base))                       # inferred conditioned transform
            pred = cnorm(base * R)
            cand = np.stack([cnorm(stem * ALLOS[a]) for a in range(3)], axis=0)
            sel = int(np.argmax((pred[None, :] @ np.conj(cand).T).real))
            mark = "MATCH" if sel == gold else "MISS"
            lines.append("  %-5s --[%-9s]--> %-8s  substrate selected %s allomorph %s (gold %s) %s"
                         % (word, rule, eng, ALLO_LABELS[sel], ALLO_SUFFIX[rule][sel],
                            ALLO_SUFFIX[rule][gold], mark))
        else:                    # simple rule
            TAG = simple_tags[rule]
            ex_stem = cphasor(1, N, g)[0]; ex_base = cnorm(ex_stem * BASE); ex_surf = cnorm(ex_stem * TAG)
            R = cnorm(ex_surf * np.conj(ex_base))
            pred = cnorm(base * R)
            dec = int(np.argmax((cnorm(pred * np.conj(TAG))[None, :] @ np.conj(np.stack([stem])).T).real))
            lines.append("  %-5s --[%-9s]--> %-8s  (rule applied to novel stem, stem recovered=%s)"
                         % (word, rule, eng, "yes" if dec == 0 else "no"))
    return lines

# ----------------------------- verdict -----------------------------
def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    # aggregate per-rule mean + cv across seeds
    rule_names = [r[0] for r in RULES]
    agg_rule = {}
    for name in rule_names:
        cond = [ps["per_rule"][name]["conditioned"] for ps in per_seed]
        naive = [ps["per_rule"][name]["naive_single"] for ps in per_seed]
        scram = [ps["per_rule"][name]["scrambled"] for ps in per_seed]
        agg_rule[name] = {
            "kind": per_seed[0]["per_rule"][name]["kind"],
            "conditioned_mean": round(float(np.mean(cond)), 4),
            "conditioned_cv": round(float(np.std(cond) / (np.mean(cond) + 1e-9)), 4),
            "naive_mean": round(float(np.mean(naive)), 4),
            "scrambled_mean": round(float(np.mean(scram)), 4),
        }
    dr = float(np.mean([ps["irregular"]["dual_route"] for ps in per_seed]))
    ro = float(np.mean([ps["irregular"]["regular_only"] for ps in per_seed]))
    dr_reg = float(np.mean([ps["irregular"]["dual_route_on_regulars"] for ps in per_seed]))

    # gates
    conditioned_all = {n: agg_rule[n]["conditioned_mean"] for n in rule_names}
    n_rules_pass = sum(1 for v in conditioned_all.values() if v >= HP_RULE_ACC)
    min_rule = min(conditioned_all.values())
    allo_rules = [n for n in rule_names if agg_rule[n]["kind"] == "allomorphic"]
    # discriminator-fires: naive collapses on allomorphic rules; scrambled at chance everywhere; regular_only fails irreg
    naive_fires = all(agg_rule[n]["naive_mean"] <= DISC_FIRE_MAX for n in allo_rules)
    scram_fires = all(agg_rule[n]["scrambled_mean"] <= DISC_FIRE_MAX for n in rule_names)
    irreg_disc_fires = ro <= 0.30 and dr >= HP_IRREG_ACC
    discriminators_fire = naive_fires and scram_fires and irreg_disc_fires

    detail = {"agg_rule": agg_rule, "irregular": {"dual_route": round(dr, 4), "regular_only": round(ro, 4),
              "dual_route_on_regulars": round(dr_reg, 4)},
              "n_rules_conditioned_ge_0.90": n_rules_pass, "min_conditioned_rule_acc": round(min_rule, 4),
              "naive_discriminator_fires": naive_fires, "scrambled_discriminator_fires": scram_fires,
              "irregular_discriminator_fires": irreg_disc_fires}

    s = ("rules(cond>=0.90)=%d/8 min_rule=%.3f dual_route=%.3f regular_only=%.3f disc_fire[naive=%s,scram=%s,irreg=%s]"
         % (n_rules_pass, min_rule, dr, ro, naive_fires, scram_fires, irreg_disc_fires))

    if min_rule < HF_RULE_ACC or dr < HF_IRREG_ACC:
        return ("HARD_FAIL", "HARD_FAIL: a rule or the exception-list did not generalize (min conditioned rule <%.2f OR dual_route <%.2f). "
                "Morphology width-extension failed. %s" % (HF_RULE_ACC, HF_IRREG_ACC, s), detail)
    if not discriminators_fire:
        return ("HARD_FAIL", "HARD_FAIL_DISCRIMINATOR: a control did NOT collapse (naive on allomorphic / scrambled / "
                "regular-only-on-irregular) -- the test is vacuous, cannot attribute the pass to a real rule mechanism. %s" % s, detail)
    if n_rules_pass == 8 and dr >= HP_IRREG_ACC:
        return ("HARD_PASS", "HARD_PASS: substrate inflects word-forms via inspectable algebraic rules -- all 8 core "
                "English inflectional rules generalize to NOVEL stems (>=0.90), allomorphy handled by conditioned "
                "transforms (naive single-transform collapses), and a ~%d-entry irregular exception list overrides the "
                "regular rule (dual-route). STRUCTURED morphology LAYER, not fluent language. %s" % (NIRREG, s), detail)
    if n_rules_pass >= 5 and dr >= HF_IRREG_ACC:
        return ("MIDDLE_BAND", "MIDDLE_BAND: >=5 of 8 rules generalize but not all clear 0.90, or exceptions partial. "
                "Diagnostic of which rule classes need richer transforms. %s" % s, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: partial morphology generalization. %s" % s, detail)

# ----------------------------- selftest + main -----------------------------
def _selftest() -> None:
    """Formula self-test: verify the algebra on a tiny fixed regime BEFORE any full run.
    Asserts: (1) conditioned allomorphic ~ 1.0 and naive ~ chance(0.33); (2) simple conditioned ~1.0, scrambled low;
    (3) dual_route ~1.0 and regular_only ~0 on irregulars; (4) gate separates members from non-members."""
    g = np.random.default_rng(12345)
    global BASE
    BASE = cphasor(1, 4096, g)[0]
    Nsave = globals()["N"]; globals()["N"] = 4096
    try:
        # allomorphic algebra check
        stems = cphasor(30, N, g); base = cnorm(stems * BASE)
        ALLOS = [cphasor(1, N, g)[0] for _ in range(3)]
        cls = (g.integers(0, 3, size=30)).astype(int)
        for a in range(3):
            cls[a * 3:(a + 1) * 3] = a
        sbc = {a: [i for i in range(30) if cls[i] == a][:3] for a in range(3)}
        shown = set(i for a in range(3) for i in sbc[a]); novel = [i for i in range(30) if i not in shown]
        c_acc, _ = eval_allo_rule(stems, base, ALLOS, cls, "conditioned", g, sbc, novel)
        n_acc, _ = eval_allo_rule(stems, base, ALLOS, cls, "naive_single", g, sbc, novel)
        assert c_acc >= 0.95, "selftest FAIL: conditioned allomorphic acc=%.3f (expected ~1.0)" % c_acc
        assert n_acc <= 0.60, "selftest FAIL: naive allomorphic acc=%.3f did not collapse (expected ~0.33)" % n_acc
        # simple algebra check
        TAG = cphasor(1, N, g)[0]
        sc_acc, _ = eval_simple_rule(stems, base, TAG, "conditioned", g, [0, 1, 2], list(range(3, 30)))
        ss_acc, _ = eval_simple_rule(stems, base, TAG, "scrambled", g, [0, 1, 2], list(range(3, 30)))
        assert sc_acc >= 0.95, "selftest FAIL: conditioned simple acc=%.3f" % sc_acc
        assert ss_acc <= 0.40, "selftest FAIL: scrambled simple acc=%.3f did not collapse" % ss_acc
        # irregular check
        globals()["NIRREG"] = 20
        dr, ro, drreg, sep, rgm = eval_irregular(cphasor(30, N, g), None, ALLOS, None, g)
        assert dr >= 0.95, "selftest FAIL: dual_route irregular acc=%.3f" % dr
        assert ro <= 0.10, "selftest FAIL: regular_only irregular acc=%.3f (should over-regularize -> ~0)" % ro
        assert sep > 0.4, "selftest FAIL: exception gate separation=%.3f too small" % sep
        print("[selftest] PASS morph-ruleset: cond_allo=%.3f naive_allo=%.3f cond_simple=%.3f scram_simple=%.3f dual=%.3f reg_only=%.3f gate_sep=%.3f"
              % (c_acc, n_acc, sc_acc, ss_acc, dr, ro, sep), flush=True)
    finally:
        globals()["N"] = Nsave
        globals()["NIRREG"] = (24 if SMOKE else 180)

def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=len(SEEDS) * len(RULES) * TR)
    t0 = time.perf_counter()
    print("[config] anchor=%s mode=%s N=%d NSTEM=%d TR=%d NIRREG=%d seeds=%s"
          % (ANCHOR_NAME, RUN_MODE, N, NSTEM, TR, NIRREG, SEEDS), flush=True)
    per_seed = []
    for seed in SEEDS:
        print("[seed] %d" % seed, flush=True)
        ps = run_seed(seed, out_dir, t0)
        per_seed.append(ps)

    # META_RULE_AF: arms-must-differ on representative predictions
    s0 = per_seed[0]["arm_sample"]
    arms_for_hash = {k: v for k, v in s0.items() if v is not None}
    arms_differ = False
    if len(arms_for_hash) >= 2:
        _arms_must_differ(arms_for_hash); arms_differ = True
    # strip non-serializable ndarray arm samples before persistence (only used for the AF hash above)
    for ps in per_seed:
        ps.pop("arm_sample", None)

    verdict, vmsg, detail = build_verdict(per_seed)

    # smoke discriminator-fires gate: block dispatch if a control did not collapse
    block = None
    if SMOKE:
        if not detail["naive_discriminator_fires"]:
            block = "BLOCK_DISPATCH_META_RULE_K: naive single-transform did NOT collapse on allomorphic rules"
        elif not detail["scrambled_discriminator_fires"]:
            block = "BLOCK_DISPATCH_META_RULE_K: scrambled no-rule control did NOT collapse"
        elif not detail["irregular_discriminator_fires"]:
            block = "BLOCK_DISPATCH_META_RULE_K: regular-only did NOT over-regularize / dual_route below 0.90"

    demo_lines = run_demo(SEEDS[0])
    print("\n[GLASS-BOX DEMO] real-word inflections PRODUCED by the substrate (allomorph/exception choice = argmax output):", flush=True)
    for ln in demo_lines:
        print(ln, flush=True)

    print("\n[VERDICT] " + vmsg, flush=True)
    if block:
        print("[SMOKE-GATE] " + block, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS), "seeds": SEEDS, "N": N, "NSTEM": NSTEM, "TR": TR, "NIRREG": NIRREG,
        "arms_differ_verified": arms_differ,
        "detail": detail, "per_seed": per_seed, "demo": demo_lines,
        "smoke_block": block,
        "elapsed_s": time.perf_counter() - t0,
    }
    # atomic write (META_RULE_AH: tmp + os.replace)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    write_metrics(out_dir, metrics, per_seed)  # inject runner REQUIRED_FIELDS (idempotent re-write)
    print("[metrics] written -> %s" % (out_dir / "metrics.json"), flush=True)

# selftest runs at import (matches predecessor convention); halts on --self-test
_selftest()
if _ARGS.self_test:
    sys.exit(0)

_OUT = get_output_dir(ANCHOR_NAME)
try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as _e:
    _write_crash_metrics(_OUT, _e)
    raise
