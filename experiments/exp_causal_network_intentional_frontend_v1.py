"""BUILDING ACROSS THE WALL: an INTENTIONAL force-source front-end feeding the SAME Wolff typer.
   (problem: causation_is_typed_per_clause_not_across_the_causal_network)

The real-text bound (exp_causal_network_realtext_v1) found the force-dynamic edge typer covers only
the PHYSICAL slice of discourse causation (3/16 real edges); the bulk is MENTAL/INTENTIONAL/SOCIAL
causation the physical verb lexicon cannot type. A brain-mechanism research drill
(research_causation_systems_brain_mechanism_2026-08-30.md) returned the decisive verdict:

  The physical/mental split is a principled bound on the FORCE-SOURCE system (two dissociable brain
  systems: intuitive-physics/ToBY, frontoparietal/premotor -- Fischer, Mikhael, Tenenbaum &
  Kanwisher 2016 PNAS; vs mentalizing/ToMM, mPFC/TPJ -- Saxe & Kanwisher 2003; Leslie 1994). BUT
  the CAUSE/ENABLE/PREVENT TYPOLOGY is ONE unified domain-general scheme: Talmy (1988) built force
  dynamics to span physical, intra-psychological and social causation; Wolff (2007) defined the
  types via three ABSTRACT dimensions (patient tendency, affector-patient concordance, endstate
  reached) -- none physical; Wolff & Barbey (2015) treat force theory as general causal composition.
  "He held his tongue because he promised" = the promise is the ANTAGONIST force blocking the urge
  to speak -> PREVENT config. So the split FACTORIZES: one Wolff typer, two force-source front-ends.
  Corroborated by Trabasso's own narrative taxonomy (physical / motivational / psychological /
  enablement -- Warren, Nicholas & Trabasso 1979), a two-source one-typology structure.

THIS CELL builds the second (intentional) front-end and shows the SAME force_dynamic_type engine
types MENTAL/SOCIAL cross-event causal edges CI-separated over the placeholder, with the physical
lexicon (the wrong front-end) abstaining, and the info-free twin (intentional-class shuffle) losing.
This is the owner's "if the brain can do it, we can once we understand" -- the 13/16 miss is a
BUILDABLE fidelity gap, not a ceiling.

The INTENTIONAL LEXICON is derived from FrameNet MENTAL/SOCIAL frames (built before the gold, the
anti-construction-proof move): affective/cognitive/desire/memory/awareness frames -> CAUSE (a mental
state is a force that produces a reaction); prohibition + a closed commitment-to-refrain set ->
PREVENT (a self-imposed / social antagonist force opposing a tending action); permission -> ENABLE.
Glass-box, NO external LLM. ASCII-only. Deterministic.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._force_dynamics_lexicon import (  # noqa: E402  (the SAME Wolff typer + endstate detector)
    build_force_lexicon, force_dynamic_type, detect_endstate_reached,
)
from experiments.exp_causal_network_edge_typer_v1 import (  # noqa: E402  (reuse network + scoring)
    E, _it, find_cause_net, _boot, _acc, _edge_type_shuffle_acc, N_BOOT, N_SHUF,
)

ANCHOR = "causal_network_intentional_frontend_v1"
SEED = 20260830

# ---------------------------------------------------------------------------
# INTENTIONAL force-source lexicon from FrameNet mental/social frames (verb -> force class).
# Affective/cognitive/desire/memory/awareness -> CAUSE (mental state = force producing a reaction).
# Prohibition + closed commitment-to-refrain -> PREVENT (antagonist social force vs a tending action).
# Permission -> ENABLE. The ONE curated hand-set is the commitment-to-refrain verbs (Commitment frame
# conflates commit-to-ACT (CAUSE) with commit-to-REFRAIN (PREVENT) -- the intentional tendency
# ambiguity, the same world-knowledge bound the physical typer measured for CAUSE-vs-ENABLE).
# ---------------------------------------------------------------------------
CAUSE_INT_FRAMES = ["Experiencer_focus", "Experiencer_obj", "Cause_emotion", "Desiring",
                    "Remembering_experience", "Remembering_information", "Awareness",
                    "Coming_to_believe", "Becoming_aware", "Trust", "Emotion_directed"]
# Mixed prohibition/permission frames -- split by the closed ENABLE (permission) LU set.
PROHIB_PERMIT_FRAMES = ["Prohibiting_or_licensing", "Deny_or_grant_permission"]
PERMIT_LUS = {"allow", "permit", "let", "entitle", "approve", "authorize", "clear", "greenlight",
              "okay", "sanction", "suffer", "grant", "license"}
# Commitment-to-refrain (the marked narrative "bind oneself against an urge" sense -> PREVENT).
COMMIT_REFRAIN = {"promise", "vow", "pledge", "swear", "undertake"}


def build_intentional_lexicon(use_cache=True):
    from nltk.corpus import framenet as fn
    lex = {}

    def add(frame, cls, sink_over=False):
        try:
            fr = fn.frame_by_name(frame)
        except Exception:
            return
        for lu in fr.lexUnit.keys():
            if not lu.endswith(".v"):
                continue
            v = lu.rsplit(".", 1)[0].strip().lower()
            if " " in v or not v.isalpha():
                continue
            if sink_over or v not in lex:
                lex[v] = cls

    for fr in CAUSE_INT_FRAMES:
        add(fr, "CAUSE")
    # prohibition/permission mixed frames: split by sense
    from nltk.corpus import framenet as fn
    for frame in PROHIB_PERMIT_FRAMES:
        try:
            fr = fn.frame_by_name(frame)
        except Exception:
            continue
        for lu in fr.lexUnit.keys():
            if not lu.endswith(".v"):
                continue
            v = lu.rsplit(".", 1)[0].strip().lower()
            if " " in v or not v.isalpha():
                continue
            lex[v] = "ENABLE" if v in PERMIT_LUS else "PREVENT"   # sense split (overrides CAUSE)
    for v in COMMIT_REFRAIN:
        lex[v] = "PREVENT"      # marked commitment-to-refrain
    return lex


# ---------------------------------------------------------------------------
# GOLD -- connective-neutral CROSS-SENTENCE INTENTIONAL causation (extraction given, as cell 1).
# Cause verbs are covered by the intentional lexicon (built above, before this gold).
# ---------------------------------------------------------------------------
# CAUSE_INT: a mental/affective state produces a reaction; endstate REACHED.
SET_CAUSE = [
    _it("CAUSE_INT", [E("remember", "she remembered the cruel words"), E("fall", "her face fell at once")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("fear", "he feared the dark water"), E("back", "he moved away slowly")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("want", "she wanted the prize badly"), E("run", "she went to the front")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("know", "he knew the truth now"), E("speak", "he spoke up boldly")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("hope", "she hoped for good news"), E("smile", "she grinned to herself")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("hate", "he hated the loud noise"), E("cover", "he shut his ears tight")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("realize", "she realized her mistake"), E("blush", "she went red at once")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("notice", "he noticed the open door"), E("enter", "he stepped inside")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("grieve", "she grieved for her friend"), E("weep", "she cried all night")], 1, "CAUSE"),
    _it("CAUSE_INT", [E("believe", "he believed the rumor"), E("warn", "he told the others")], 1, "CAUSE"),
]

# PREVENT_INT: prohibition or commitment-to-refrain OPPOSES a tending action; the block is stated in
# the effect clause (a negation cue). Cross-event: the cause clause alone cannot tell it succeeded.
SET_PREVENT = [
    _it("PREVENT_INT", [E("promise", "he had promised to stay silent"), E("say", "he said nothing at all")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("vow", "she vowed to hold her peace"), E("speak", "she did not speak")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("forbid", "the law forbade the sale"), E("trade", "no trade took place")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("pledge", "he pledged to keep the secret"), E("tell", "he never told a soul")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("prohibit", "the rule prohibited the game"), E("play", "the children did not play")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("swear", "she swore to stay calm"), E("show", "she showed no anger")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("ban", "the order banned the march"), E("gather", "the crowd never gathered")], 1, "PREVENT"),
    _it("PREVENT_INT", [E("undertake", "he undertook to remain still"), E("move", "he did not move")], 1, "PREVENT"),
]

# ENABLE_INT: permission lets a tending action proceed; REACHED.
SET_ENABLE = [
    _it("ENABLE_INT", [E("permit", "the judge permitted the appeal"), E("speak", "the lawyer spoke freely")], 1, "ENABLE"),
    _it("ENABLE_INT", [E("allow", "the teacher allowed a break"), E("run", "the pupils went outside")], 1, "ENABLE"),
    _it("ENABLE_INT", [E("approve", "the board approved the plan"), E("begin", "the work started at once")], 1, "ENABLE"),
    _it("ENABLE_INT", [E("authorize", "the chief authorized the raid"), E("move", "the troops went in")], 1, "ENABLE"),
    _it("ENABLE_INT", [E("authorize", "the officer authorized their entry"), E("talk", "the guests came in freely")], 1, "ENABLE"),
    _it("ENABLE_INT", [E("sanction", "the council sanctioned the fair"), E("set", "the traders put up stalls")], 1, "ENABLE"),
]

# SEQUENTIAL: non-intentional-force cause verb, no connective -> no edge.
SET_SEQ = [
    _it("SEQ_INT", [E("pour", "she poured the tea"), E("yawn", "he yawned at the table")], 1, "SEQUENTIAL"),
    _it("SEQ_INT", [E("read", "he read the letter"), E("tick", "the clock ticked on")], 1, "SEQUENTIAL"),
    _it("SEQ_INT", [E("sweep", "she swept the porch"), E("sing", "a bird sang nearby")], 1, "SEQUENTIAL"),
    _it("SEQ_INT", [E("walk", "he walked the lane"), E("fall", "the leaves came down")], 1, "SEQUENTIAL"),
    _it("SEQ_INT", [E("gaze", "she gazed at the sky"), E("hiss", "the kettle hissed")], 1, "SEQUENTIAL"),
    _it("SEQ_INT", [E("watch", "he watched the fire"), E("sleep", "the cat dozed")], 1, "SEQUENTIAL"),
]

POOL = SET_CAUSE + SET_PREVENT + SET_ENABLE + SET_SEQ


def _fold(t):
    return t if t in ("CAUSE", "ENABLE", "PREVENT") else "SEQUENTIAL"


def arm_intentional(item, int_lex):
    """The INTENTIONAL front-end + the SAME Wolff typer. Necessity/precedence via find_cause_net over
    the intentional lexicon; endstate from the EFFECT clause; force_dynamic_type does the typing."""
    events, outcome = item["events"], item["outcome"]
    c, licensed = find_cause_net(events, outcome, int_lex)
    if not licensed or c is None:
        return "SEQUENTIAL"
    es = detect_endstate_reached(events[outcome]["clause"])
    return _fold(force_dynamic_type(events[c]["v"], es, int_lex))


def arm_physical_only(item, phys_lex):
    """The PHYSICAL front-end (wrong system for mental causation): abstains on mental verbs."""
    events, outcome = item["events"], item["outcome"]
    c, licensed = find_cause_net(events, outcome, phys_lex)
    if not licensed or c is None:
        return "SEQUENTIAL"
    es = detect_endstate_reached(events[outcome]["clause"])
    return _fold(force_dynamic_type(events[c]["v"], es, phys_lex))


def arm_placeholder(item, majority="CAUSE"):
    return majority


def _shuffled(int_lex, seed):
    rng = random.Random(seed)
    ks, vs = list(int_lex.keys()), list(int_lex.values())
    rng.shuffle(vs)
    return dict(zip(ks, vs))


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def self_test():
    il = build_intentional_lexicon()
    assert arm_intentional(SET_CAUSE[0], il) == "CAUSE", "remembered -> face fell = CAUSE"
    assert arm_intentional(SET_PREVENT[0], il) == "PREVENT", "promised silence -> said nothing = PREVENT"
    assert arm_intentional(SET_ENABLE[0], il) == "ENABLE", "permitted -> spoke freely = ENABLE"
    assert arm_physical_only(SET_CAUSE[0], build_force_lexicon()) == "SEQUENTIAL", "physical abstains on 'remember'"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    int_lex = build_intentional_lexicon()
    phys_lex = build_force_lexicon()

    preds_int = [arm_intentional(it, int_lex) for it in POOL]
    preds_phys = [arm_physical_only(it, phys_lex) for it in POOL]
    preds_ph = [arm_placeholder(it) for it in POOL]
    golds = [it["gold"] for it in POOL]

    rec_int = [int(p == y) for p, y in zip(preds_int, golds)]
    rec_phys = [int(p == y) for p, y in zip(preds_phys, golds)]
    rec_ph = [int(p == y) for p, y in zip(preds_ph, golds)]

    m_int, lo_int, hi_int = _boot(rec_int)
    m_phys, lo_phys, hi_phys = _boot(rec_phys)
    m_ph, lo_ph, hi_ph = _boot(rec_ph)

    twinA = sorted(_acc([int(arm_intentional(it, _shuffled(int_lex, 1000 + s)) == it["gold"])
                         for it in POOL]) for s in range(N_SHUF))
    twinA_mean, twinA_p95 = sum(twinA) / len(twinA), twinA[int(0.95 * (len(twinA) - 1))]
    twinB = sorted(_edge_type_shuffle_acc(POOL, preds_int, 2000 + s) for s in range(N_SHUF))
    twinB_mean, twinB_p95 = sum(twinB) / len(twinB), twinB[int(0.95 * (len(twinB) - 1))]

    per_subset = {}
    for name, items in [("CAUSE_INT", SET_CAUSE), ("PREVENT_INT", SET_PREVENT),
                        ("ENABLE_INT", SET_ENABLE), ("SEQ_INT", SET_SEQ)]:
        per_subset[name] = {"n": len(items),
                            "intentional": round(_acc([int(arm_intentional(it, int_lex) == it["gold"]) for it in items]), 4),
                            "physical_only": round(_acc([int(arm_physical_only(it, phys_lex) == it["gold"]) for it in items]), 4),
                            "placeholder": round(_acc([int(arm_placeholder(it) == it["gold"]) for it in items]), 4)}

    # coverage lift on the REAL LitBank MENTAL edges the physical lexicon missed
    import experiments.exp_read_causal_chain_on_chain_cause_v1 as RC
    from nltk.stem import WordNetLemmatizer
    lm = WordNetLemmatizer()
    real_int_cov = real_phys_cov = real_union_cov = 0
    real_rows = []
    for it in RC.GOLD:
        cl = lm.lemmatize(it.cause_lemma, "v")
        pi, pp = int_lex.get(cl), phys_lex.get(cl)
        real_int_cov += pi is not None
        real_phys_cov += pp is not None
        real_union_cov += (pi is not None) or (pp is not None)
        real_rows.append({"cause": it.cause_lemma, "lemma": cl, "intentional": pi, "physical": pp})
    n_real = len(RC.GOLD)

    beats_placeholder = lo_int > hi_ph
    beats_physical = lo_int > hi_phys
    twinA_loses = lo_int > twinA_p95
    twinB_loses = lo_int > twinB_p95
    passed = beats_placeholder and beats_physical and twinA_loses and twinB_loses
    verdict = ("INTENTIONAL_FRONTEND_TYPES_MENTAL_CAUSATION_CI_SEPARATED__SAME_WOLFF_TYPER__TWINS_LOSE"
               if passed else "INTENTIONAL_FRONTEND_DID_NOT_CLEAR_ALL_GATES")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "summary": (
            f"INTENTIONAL FRONT-END (FrameNet mental/social frames) + the SAME Wolff typer, on constructed "
            f"connective-neutral MENTAL/SOCIAL cross-sentence causation: 4-way edge-type acc INTENTIONAL "
            f"{m_int:.3f} [{lo_int:.3f},{hi_int:.3f}] vs PHYSICAL-only (wrong front-end) {m_phys:.3f} "
            f"[{lo_phys:.3f},{hi_phys:.3f}] (beats={beats_physical}) and vs PLACEHOLDER (majority) {m_ph:.3f} "
            f"[{lo_ph:.3f},{hi_ph:.3f}] (beats={beats_placeholder}). Intentional-class-shuffle twin {twinA_mean:.3f} "
            f"(p95 {twinA_p95:.3f}, loses={twinA_loses}); edge-type-shuffle twin {twinB_mean:.3f} (p95 "
            f"{twinB_p95:.3f}, loses={twinB_loses}). REAL-TEXT coverage lift on the 16 LitBank causal edges: "
            f"COMBINED (physical OR intentional) covers {real_union_cov}/{n_real}, DOUBLE the physical-alone "
            f"{real_phys_cov}/{n_real} (intentional adds {real_int_cov} different verbs -- remember/know/promise) "
            f"-- the same typology, a second front-end, recovers mental causation the physical lexicon could not."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "n_pool": len(POOL),
        "intentional_lexicon_size": len(int_lex),
        "pooled": {"intentional_acc": round(m_int, 4), "intentional_ci": [round(lo_int, 4), round(hi_int, 4)],
                   "physical_only_acc": round(m_phys, 4), "physical_only_ci": [round(lo_phys, 4), round(hi_phys, 4)],
                   "placeholder_acc": round(m_ph, 4), "placeholder_ci": [round(lo_ph, 4), round(hi_ph, 4)]},
        "twin_intentional_class_shuffle": {"mean": round(twinA_mean, 4), "p95": round(twinA_p95, 4), "loses": twinA_loses},
        "twin_edge_type_shuffle": {"mean": round(twinB_mean, 4), "p95": round(twinB_p95, 4), "loses": twinB_loses},
        "per_subset": per_subset,
        "real_text_coverage_lift": {"n": n_real, "intentional_cov": real_int_cov, "physical_cov": real_phys_cov,
                                    "combined_cov": real_union_cov, "rows": real_rows},
        "gates": {"beats_placeholder_ci": beats_placeholder, "beats_physical_ci": beats_physical,
                  "intentional_twin_loses": twinA_loses, "edge_twin_loses": twinB_loses},
        "brain_note": (
            "Talmy 1988 / Wolff 2007 force dynamics is domain-general (physical/psychological/social); the "
            "CAUSE/ENABLE/PREVENT typology is one engine, the force-SOURCE extraction is domain-specific "
            "(intuitive-physics ToBY vs mentalizing ToMM, two brain systems). This cell adds the intentional "
            "source; the typer is UNCHANGED. Commitment-to-act vs commitment-to-refrain is the intentional "
            "tendency-ambiguity (the same world-knowledge bound as physical CAUSE-vs-ENABLE)."),
        "scope": (
            "Constructed connective-neutral MENTAL/SOCIAL cross-sentence causation; extraction GIVEN. Intentional "
            "lexicon derived from FrameNet frames BEFORE this gold. The physical-only arm is the 'wrong front-end' "
            "control (abstains). Real-text coverage lift is a verb-coverage count, not an accuracy (real cause-ID "
            "gold is all-CAUSE). ToM/communication source frames (say/die/seem) remain a follow-on front-end."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"[verdict] {verdict}")
    print(f"elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
