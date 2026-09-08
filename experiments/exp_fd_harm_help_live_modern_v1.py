"""LIVE-READER validation of the force-dynamics harm/help rebuild (companion to
exp_force_dynamics_harm_help_v1.py). Two things the constructed-pop measurement did not cover:

PART A -- LIVE-READER NO-REGRESS. Monkeypatch stage-2 (experiments.exp_bridge1_event_assembly_open_vocab
_v1.event_type_for_item_real) with the force-dynamics decision, run the FULL hdlab.situation_reader.read()
on a MODERN sample, and confirm end-to-end: (a) no crash; (b) EVERY non-affect SituationModel dimension is
BYTE-IDENTICAL to the current reader (dim_signatures) -- the only field that changes is EventRecord.affect
(additive metadata, per situation_reader.py L1990-91); (c) the downstream consumers of the affect
dimension are unchanged -- sm.infer_emotion (OCC appraisal, reads sm.affect_register + sm.goal_register,
NOT e.affect) and the emotion register sm.feels/valence_of; (d) the newly-surfaced HELP events are
sensible on spot-check. NOTE (verified): HELP surfaces with NO change to _assign_affect -- when stage-2
returns RECIPROCITY, result["stage"]=="event" so it passes the existing gate; to_ternary(RECIPROCITY)=HELP.

PART B -- SCORED MODERN HARM/HELP ARM. The modern board OMITS affect ("needs a modern emotion gold"). Build
a can-fail modern harm/help gold the HONEST way and score current-closed-list vs force-dynamics through the
LIVE reader, floors + bootstrap CI + info-free twin.

  GOLD CONSTRUCTION (declared, mirrors occ_appraisal_gold's self-authored-but-transparent method; NOT tuned
  to either arm): 36 self-authored CONTEMPORARY one-sentence SVO scenes, balanced 12 HARM / 12 HELP / 12
  NEUTRAL. The label is the plain reading of whether the animate patient ends up WORSE off (HARM),
  PROTECTED / BETTER off (HELP), or valence-unchanged (NEUTRAL). The verb inventory is deliberately
  ADVERSARIAL to force dynamics: it MIXES verbs FrameNet covers (stab/beat/attack; rescue/shield/defend)
  with verbs FrameNet MISSES (mug/evict/bully/fire social-harm; comfort/console CAUSE-emotion) so the gold
  is NOT cherry-picked to the model's strengths -- FD's own coverage gaps are IN the gold and count against
  it. HONEST CAVEAT: the author has seen both lexicons, so this is DIRECTIONAL live-path evidence; the
  load-bearing evidence remains the constructed-pop (P2/P3), the modern coverage probe (P5), and the
  structural no-regress. NOT a corpus gold -- no harm/help-labeled modern corpus exists on disk.

Glass-box. ASCII. Deterministic. NO external LLM at inference.
"""
from __future__ import annotations

import glob
import os
import random
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.situation_reader as SR  # noqa: E402
import experiments.exp_bridge1_event_assembly_open_vocab_v1 as ea  # noqa: E402
import experiments.exp_assembled_reader_all_flags_on_v1 as H  # noqa: E402 (dim_signatures)
import experiments.exp_force_dynamics_harm_help_v1 as FD  # noqa: E402 (LEX_AUG, HARM_VERBS, harm_help)

SEED = 20260908
N_BOOT = 2000
SCRATCH = os.path.join(REPO, "data", "exp_fd_harm_help_live_modern_v1")

_ORIG_EVENT_TYPE = ea.event_type_for_item_real


# --------------------------------------------------------------------------- the proposed stage-2 (FD)
def fd_event_type_for_item(it, animacy_map, force_class, gov_class_dict):
    """DROP-IN replacement for ea.event_type_for_item_real: SAME structural gate (nearest governing verb +
    valid direct object + WordNet animacy), force-dynamics decision instead of the closed FORCE_CLASS_HARM
    _REAL list. Returns BLOCK_HIGH (->HARM) / RECIPROCITY (->HELP) / NEUTRAL (->NA) / None (abstain). The
    governor perceptron / closed list are not consulted. This is the exact behaviour the hdlab diff lands."""
    gi = ea.bridge1.nearest_verb_idx(it["tokens"], it["pos"], it["target_idx"])
    if not ea.v2.valid_direct_object(it["pos"], gi, it["target_idx"]):
        return None, None, None
    gov_word = ea.bridge1.lemma_verb(it["tokens"][gi])
    obj_word = it["target_word"].lower()
    a = animacy_map.get(obj_word)
    if a is None:
        return None, None, gov_word
    hh = FD.harm_help(gov_word, a["animacy"], FD.LEX_AUG, FD.HARM_VERBS, mode="refined")
    mapped = {"NA": "NEUTRAL", "HARM": "BLOCK_HIGH", "HELP": "RECIPROCITY"}.get(hh)
    return (mapped, a["category"], gov_word) if mapped else (None, a["category"], gov_word)


def patch():
    ea.event_type_for_item_real = fd_event_type_for_item


def unpatch():
    ea.event_type_for_item_real = _ORIG_EVENT_TYPE


# --------------------------------------------------------------------------- conll helper
def make_conll(docid, sents):
    lines = [f"#begin document ({docid}); part 0"]
    for si, toks in enumerate(sents):
        for ti, w in enumerate(toks):
            lines.append("\t".join([docid, str(si), str(ti), w] + ["_"] * 8))
        lines.append("")
    lines.append("#end document")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- modern harm/help gold (declared)
# (subject, verb_surface, patient_noun, gold)  -- one contemporary SVO scene each. Determiner filled below.
GOLD = [
    # ---- HARM (12): patient ends up worse off. mix of FrameNet-covered + social-harm FrameNet misses ----
    ("mugger", "attacked", "tourist", "HARM"),
    ("soldier", "stabbed", "captive", "HARM"),
    ("bully", "punched", "student", "HARM"),
    ("driver", "struck", "cyclist", "HARM"),
    ("guard", "beat", "prisoner", "HARM"),
    ("attacker", "wounded", "officer", "HARM"),
    ("thug", "kicked", "vendor", "HARM"),
    ("robber", "mugged", "pedestrian", "HARM"),       # 'mug'->Robbery frame -- FrameNet MISS (adversarial)
    ("landlord", "evicted", "tenant", "HARM"),         # 'evict'->Removing -- FrameNet MISS (adversarial)
    ("manager", "fired", "clerk", "HARM"),             # social/economic harm -- FrameNet MISS (adversarial)
    ("coworker", "bullied", "intern", "HARM"),         # FrameNet MISS (adversarial)
    ("dog", "scratched", "toddler", "HARM"),
    # ---- HELP (12): patient protected / better off. PREVENT/ENABLE + some misses ----
    ("firefighter", "rescued", "child", "HELP"),
    ("bodyguard", "protected", "senator", "HELP"),
    ("lifeguard", "saved", "swimmer", "HELP"),
    ("knight", "defended", "villager", "HELP"),
    ("officer", "shielded", "witness", "HELP"),
    ("volunteer", "sheltered", "refugee", "HELP"),
    ("judge", "spared", "defendant", "HELP"),
    ("activist", "freed", "hostage", "HELP"),          # ENABLE
    ("captain", "guarded", "passenger", "HELP"),
    ("nurse", "comforted", "patient", "HELP"),         # 'comfort'->Cause_emotion -- FD abstains (adversarial)
    ("teacher", "consoled", "pupil", "HELP"),          # FD abstains (adversarial)
    ("stranger", "helped", "widow", "HELP"),           # 'help' generic -- FD abstains (adversarial)
    # ---- NEUTRAL (12): animate patient, no valence change (perception/communication) + inanimate ----
    ("reporter", "watched", "mayor", "NEUTRAL"),
    ("tourist", "photographed", "dancer", "NEUTRAL"),
    ("clerk", "greeted", "customer", "NEUTRAL"),
    ("agent", "phoned", "client", "NEUTRAL"),
    ("author", "described", "hero", "NEUTRAL"),
    ("student", "emailed", "professor", "NEUTRAL"),
    ("boy", "kicked", "ball", "NEUTRAL"),              # inanimate patient -> NA
    ("mechanic", "fixed", "engine", "NEUTRAL"),        # inanimate patient -> NA
    ("chef", "chopped", "onion", "NEUTRAL"),           # inanimate patient -> NA
    ("worker", "painted", "fence", "NEUTRAL"),         # inanimate patient -> NA
    ("child", "watched", "cartoon", "NEUTRAL"),        # inanimate patient -> NA
    ("woman", "read", "letter", "NEUTRAL"),            # inanimate patient -> NA
]


def gold_sentence(subj, verb, pat):
    a_subj = "An" if subj[0] in "aeiou" else "A"
    return [a_subj, subj, verb, "the", pat, "."]


# --------------------------------------------------------------------------- affect via the LIVE reader
def read_affects(reader, path, patient_head):
    """read() the doc; return the affect the reader assigned to the event whose patient head matches
    (case-insensitive), or '__ABSTAIN__' if the reader produced no such event/affect."""
    sm = reader.read(path)
    for e in sm.events:
        if e.patient and str(e.patient).lower().strip(".,") == patient_head.lower():
            return e.affect if e.affect is not None else "__ABSTAIN__"
    return "__NO_EVENT__"


def to_gold3(affect_label):
    """map the reader's affect to the gold 3-way {HARM,HELP,NEUTRAL}; abstain/NA -> NEUTRAL (the organ's
    conservative default -- an abstain on a harm/help item counts as a MISS, on a neutral item as a HIT)."""
    if affect_label in ("HARM", "HELP"):
        return affect_label
    return "NEUTRAL"  # 'NA', '__ABSTAIN__', '__NO_EVENT__'


# --------------------------------------------------------------------------- bootstrap CI
def boot_ci(corr, n_boot=N_BOOT, seed=SEED):
    if not corr:
        return 0.0, 0.0
    rng = random.Random(seed)
    n = len(corr)
    ms = []
    for _ in range(n_boot):
        ms.append(sum(corr[rng.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return sum(corr) / n, (ms[int(0.975 * n_boot)] - ms[int(0.025 * n_boot)]) / 2.0


# --------------------------------------------------------------------------- PART A: no-regress
def part_A_noregress():
    os.makedirs(SCRATCH, exist_ok=True)
    # modern docs: the synthetic contemporary scenes already in reader-conll format + the gold sentences.
    scene_docs = sorted(glob.glob(os.path.join(REPO, "data", "tmp_mid", "*.conll")) +
                        glob.glob(os.path.join(REPO, "data", "tmp_cons", "*.conll")) +
                        glob.glob(os.path.join(REPO, "data", "tmp_gbtrace", "*.conll")))
    gold_paths = []
    for i, (subj, verb, pat, _g) in enumerate(GOLD):
        p = os.path.join(SCRATCH, f"gold_{i:02d}.conll")
        open(p, "w", encoding="utf-8").write(make_conll(f"gold{i}", [gold_sentence(subj, verb, pat)]))
        gold_paths.append(p)
    docs = scene_docs + gold_paths

    reader = SR.SituationReader()
    dim_mismatches = []
    emotion_mismatches = []
    affect_changed = 0
    help_events = []
    crashes = []
    n_ok = 0

    for path in docs:
        try:
            unpatch()
            sm0 = reader.read(path)
            sig0 = H.dim_signatures(sm0)
            aff0 = [(e.sent_idx, e.predicate, e.patient, e.affect) for e in sm0.events]
            emo0 = _emotion_readouts(sm0)

            patch()
            sm1 = reader.read(path)
            sig1 = H.dim_signatures(sm1)
            aff1 = [(e.sent_idx, e.predicate, e.patient, e.affect) for e in sm1.events]
            emo1 = _emotion_readouts(sm1)
            unpatch()
            n_ok += 1
        except Exception as e:  # noqa: BLE001
            crashes.append((os.path.basename(path), f"{type(e).__name__}: {str(e)[:200]}"))
            unpatch()
            continue

        for k in sig0:
            if sig0[k] != sig1[k]:
                dim_mismatches.append((os.path.basename(path), k, sig0[k], sig1[k]))
        if emo0 != emo1:
            emotion_mismatches.append(os.path.basename(path))
        for (a0, a1) in zip(aff0, aff1):
            if a0[3] != a1[3]:
                affect_changed += 1
                if a1[3] == "HELP":
                    help_events.append((os.path.basename(path), a1[1], a1[2]))
    return {"n_docs": len(docs), "n_ok": n_ok, "crashes": crashes,
            "dim_mismatches": dim_mismatches, "emotion_mismatches": emotion_mismatches,
            "n_affect_changed": affect_changed, "help_events": help_events}


def _emotion_readouts(sm):
    """The downstream affect consumers: OCC appraisal (sm.infer_emotion) + the emotion register
    (sm.feels/valence_of). Returns a comparable tuple over every tracked entity head."""
    out = []
    heads = []
    for ent in (sm.entities or []):
        if getattr(ent, "heads", None):
            heads.append(ent.heads[0])
    for h in sorted(set(heads)):
        rec = {"h": h}
        for fn_name in ("infer_emotion", "feels", "valence_of"):
            fn = getattr(sm, fn_name, None)
            if callable(fn):
                try:
                    rec[fn_name] = repr(fn(h))
                except Exception as e:  # noqa: BLE001
                    rec[fn_name] = f"ERR:{type(e).__name__}"
        out.append(tuple(sorted(rec.items())))
    return out


# --------------------------------------------------------------------------- PART B: scored modern gold
def part_B_scored_gold():
    os.makedirs(SCRATCH, exist_ok=True)
    paths = []
    for i, (subj, verb, pat, g) in enumerate(GOLD):
        p = os.path.join(SCRATCH, f"gold_{i:02d}.conll")
        open(p, "w", encoding="utf-8").write(make_conll(f"gold{i}", [gold_sentence(subj, verb, pat)]))
        paths.append((p, pat, g, verb))

    reader = SR.SituationReader()

    def score_arm(patched, twin=False):
        if twin:
            # info-free twin: scrambled force lexicon + scrambled harm-verb membership through the SAME
            # live path (patch stage-2 to use the scrambled maps).
            scr_lex = FD.scramble_lexicon(FD.LEX_AUG, SEED + 1)
            all_v = set(FD.LEX_AUG) | FD.HARM_VERBS
            scr_harm = FD.scramble_set_membership(FD.HARM_VERBS, all_v, SEED + 2)

            def twin_event_type(it, amap, fc, gc):
                gi = ea.bridge1.nearest_verb_idx(it["tokens"], it["pos"], it["target_idx"])
                if not ea.v2.valid_direct_object(it["pos"], gi, it["target_idx"]):
                    return None, None, None
                gw = ea.bridge1.lemma_verb(it["tokens"][gi])
                a = amap.get(it["target_word"].lower())
                if a is None:
                    return None, None, gw
                hh = FD.harm_help(gw, a["animacy"], scr_lex, scr_harm, mode="refined")
                m = {"NA": "NEUTRAL", "HARM": "BLOCK_HIGH", "HELP": "RECIPROCITY"}.get(hh)
                return (m, a["category"], gw) if m else (None, a["category"], gw)
            ea.event_type_for_item_real = twin_event_type
        elif patched:
            patch()
        else:
            unpatch()
        corr, preds, abstain = [], [], 0
        for p, pat, g, verb in paths:
            aff = read_affects(reader, p, pat)
            if aff in ("__ABSTAIN__", "__NO_EVENT__", "NA"):
                abstain += 1
            pred = to_gold3(aff)
            preds.append((verb, pat, g, aff, pred))
            corr.append(1 if pred == g else 0)
        unpatch()
        m, h = boot_ci(corr)
        return {"acc": round(m, 4), "ci_half": round(h, 4), "abstain": abstain, "preds": preds}

    # majority-class floor (all-NEUTRAL) = 12/36
    maj = round(sum(1 for _p, _pat, g, _v in paths if g == "NEUTRAL") / len(paths), 4)
    res = {"n": len(paths), "majority_floor_allNEUTRAL": maj,
           "closed_list": score_arm(patched=False),
           "force_dynamics": score_arm(patched=True),
           "twin_scrambled": score_arm(patched=False, twin=True)}
    # per-class accuracy for force_dynamics + closed
    for arm in ("closed_list", "force_dynamics"):
        by = {"HARM": [0, 0], "HELP": [0, 0], "NEUTRAL": [0, 0]}
        for (verb, pat, g, aff, pred) in res[arm]["preds"]:
            by[g][1] += 1
            by[g][0] += int(pred == g)
        res[arm]["by_class"] = {k: f"{v[0]}/{v[1]}" for k, v in by.items()}
    return res


if __name__ == "__main__":
    import pprint
    print("=" * 78, "\nPART A -- LIVE-READER NO-REGRESS (modern docs)\n", "=" * 78)
    A = part_A_noregress()
    print(f"docs read: {A['n_ok']}/{A['n_docs']}  crashes: {A['crashes']}")
    print(f"NON-AFFECT dim mismatches (must be []): {A['dim_mismatches']}")
    print(f"emotion/appraisal readout mismatches (must be []): {A['emotion_mismatches']}")
    print(f"events whose .affect changed: {A['n_affect_changed']}")
    print(f"newly-surfaced HELP events (spot-check): {A['help_events']}")
    print("\n", "=" * 78, "\nPART B -- SCORED MODERN HARM/HELP GOLD (live reader)\n", "=" * 78)
    B = part_B_scored_gold()
    print(f"n={B['n']}  majority(all-NEUTRAL) floor={B['majority_floor_allNEUTRAL']}")
    for arm in ("closed_list", "force_dynamics", "twin_scrambled"):
        r = B[arm]
        extra = f"  by_class={r.get('by_class')}" if "by_class" in r else ""
        print(f"  {arm:16s} acc={r['acc']:.3f} +/-{r['ci_half']:.3f}  abstain={r['abstain']}/{B['n']}{extra}")
    print("\n  force_dynamics per-item (verb, patient, gold, live_affect, pred):")
    for row in B["force_dynamics"]["preds"]:
        flag = "" if row[2] == row[4] else "   <-- MISS"
        print(f"    {row[0]:12s} {row[1]:10s} gold={row[2]:8s} live={str(row[3]):12s} pred={row[4]:8s}{flag}")
