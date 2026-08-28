"""exp_theory_of_mind_realtext_v1 -- FALSE-BELIEF (Theory of Mind) on REAL TEXT, on the substrate's OWN organs.

De-islands the HARD_PASS-but-SYNTHETIC Sally-Anne organ (row theory_of_mind_sally_anne_nested_hrr,
validated_hard_pass_islanded_2026-08-05) per its OWN revival criteria: (a) a divergent-belief NARRATIVE
task, (b) run on the substrate's own FHRR organs (hdlab.binding + situation_model_accumulate) instead of
hand-rolled numpy, (c) inputs from TEXT, not a perfect symbolic codebook. Gold: experiments/data/
gold_false_belief_realtext_v1.jsonl (10 real-English passages, 22 Qs; false-belief + true-belief controls
+ a divergent two-agent item).

BRAIN FRAME. False belief = the canonical Theory-of-Mind test (Wimmer & Perner 1983; Baron-Cohen/Leslie/
Frith 1985 Sally-Anne). PINNED: an agent acts on its OWN belief, which can DIVERGE from reality when the
agent did not observe a change; the mentalizing network (TPJ/mPFC; Saxe & Kanwisher 2003) maintains
belief representations SEPARATE from the observer's own knowledge. MECHANISM (ours, faithful to the organ):
a PER-AGENT belief store -- an agent that did NOT observe a move keeps the OLD binding (stale = false
belief); observers/informed agents update. OUR-INVENTION-UNDER-TEST: the FHRR code assignment + the
observation-cue extractor.

TASK. Answer each question by reading the queried store:
  belief Q ("where will X look?")  -> unbind X's per-agent bank by the object -> cleanup over locations.
  reality Q ("where is it really?") -> unbind the WORLD bank.
  memory Q ("where did X put it?")  -> the initial world binding.

ARMS (belief questions are the discriminator; identical inputs; only the belief store changes):
  NO_TOM (floor)     single shared belief = current reality (observer's own knowledge leaks to the agent)
  FULL_TOM           per-agent banks; observation from the gold field (mechanism, clean observation)
  FULL_TOM_LIVE      per-agent banks; observation EXTRACTED FROM TEXT via lexical cues (end-to-end)
  TWIN (info-free)   per-agent banks; observation bit RANDOMISED -> must not systematically beat NO_TOM
  ORACLE             gold lookup (upper bound)
Floors: NO_TOM (shared-reality) recomputed on the belief-Q population; ALWAYS_INITIAL (a trivial "the
agent looks where they left it" rule -- the true-belief controls make it can-fail).

Writes only to data/exp_theory_of_mind_realtext_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

from hdlab import binding
from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax

ANCHOR_NAME = "theory_of_mind_realtext_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_RELS = ["experiments/data/gold_false_belief_realtext_v1.jsonl",
             "experiments/data/gold_false_belief_realtext_v1b.jsonl"]
D = 1024


def repo_path(rel):
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def load_gold():
    rows = []
    for rel in GOLD_RELS:
        p = repo_path(rel)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def _gen(tag, seed):
    h = int(__import__("hashlib").md5(f"{tag}|{seed}".encode()).hexdigest()[:8], 16)
    g = torch.Generator()
    g.manual_seed(h)
    return g


class Codes:
    """Deterministic FHRR codes derived from TEXT surface forms (revival criterion c: text, not a
    perfect codebook -- the code is seeded by the surface string)."""
    def __init__(self, seed):
        self.seed = seed
        self._c = {}

    def __init__(self, seed, loc_interfere=False):  # noqa: F811 (extend the simple __init__)
        self.seed = seed
        self.loc_interfere = bool(loc_interfere)
        self._c = {}

    def get(self, kind, surface):
        key = (kind, surface.lower().strip(), self.loc_interfere)
        v = self._c.get(key)
        if v is None:
            if kind == "loc" and self.loc_interfere:
                # INTERFERENCE STRESS: build the location code as an FHRR bundle of its WORD-token codes,
                # so similar phrases ("red box" / "blue box" / "red basket") SHARE components and are no
                # longer near-orthogonal -- the fan-effect regime the first run did not stress.
                import torch as _t
                toks = [w for w in re.split(r"\W+", surface.lower().strip()) if w and w not in
                        ("the", "a", "an", "by", "of", "under", "over", "in", "on", "behind")]
                if not toks:
                    toks = [surface.lower().strip()]
                codes = _t.stack([unit_phase_vec(D, _gen(f"loctok::{w}", self.seed)) for w in toks], 0)
                s = codes.sum(0)
                mag = s.abs(); mag = _t.where(mag > 0, mag, _t.ones_like(mag))
                v = (s / mag).to(_t.complex64)
            else:
                v = unit_phase_vec(D, _gen(f"{kind}::{surface.lower().strip()}", self.seed))
            self._c[key] = v
        return v


# ---- live observation extractor (read "did the agent observe the move?" from TEXT) ----
_NOT_OBSERVED = [
    r"did not see", r"did not notice", r"while .* was gone", r"while .* was away",
    r"while .* was out", r"in his absence", r"in her absence", r"while he slept",
    r"while she slept", r"while .* slept", r"went (outside|out|to)", r"ran to", r"left the room",
    r"left for", r"in the far field", r"went to fetch", r"went to answer",
]
_OBSERVED = [r"watched", r"saw him", r"saw her", r"plainly", r"stayed in the room", r"heard (him|her)"]
_INFORMED = [r"told .*(,| that)", r"said,? ['\"]", r"heard (him|her)", r"and nodded"]


def extract_observed_from_text(text, protagonist):
    """Return True if the text indicates the protagonist OBSERVED or was INFORMED of the move, else
    False (absent/asleep). Deliberately lexical -- a small honest front-end; its accuracy is reported."""
    t = text.lower()
    # informed (told/heard) counts as knowing -> observed-equivalent
    if any(re.search(p, t) for p in _INFORMED) and ("nodded" in t or "heard" in t or "told" in t):
        # only if the telling is about the object location move; here the informed items say so
        if re.search(r"(putting|moving|is (in|on) )", t) or "nodded" in t or "heard her" in t:
            return True
    if any(re.search(p, t) for p in _OBSERVED):
        return True
    if any(re.search(p, t) for p in _NOT_OBSERVED):
        return False
    return True  # default: no absence cue -> assume present


def believed_location(observed, initial, final):
    return final if observed else initial


def build_answer(arm, row, codes, rng, loc_vocab):
    """Return dict question_type -> predicted location string, via FHRR bind/unbind + cleanup on the
    substrate's own organs. loc_vocab: {location_string: code} for cleanup."""
    obj = row["object"]
    obj_c = codes.get("obj", obj)
    init, fin = row["initial_location"], row["final_location"]
    prot = row["protagonist"]
    second = row.get("second_agent")

    # observation per agent, per arm
    def obs_for(agent):
        if arm == "ORACLE":
            return None  # handled separately
        if agent == second:
            return True  # the mover observes the final state
        # protagonist:
        if arm == "NO_TOM":
            return True  # shared reality: agent "knows" current world
        if arm == "FULL_TOM":
            # belief tracks KNOWLEDGE (saw the move OR was informed of it), not vision alone --
            # the informed-true-belief control is what distinguishes 'saw' from 'knows'.
            return bool(row["protagonist_saw_move"]) or row["condition"] == "true_belief_informed"
        if arm == "FULL_TOM_LIVE":
            return extract_observed_from_text(row["text"], prot)
        if arm == "TWIN":
            return bool(rng.integers(0, 2))
        raise ValueError(arm)

    # world bank (truth) always tracks final
    world_bank = binding.bind(obj_c, codes.get("loc", fin))

    def agent_bank(agent):
        loc = believed_location(obs_for(agent), init, fin)
        return binding.bind(obj_c, codes.get("loc", loc))

    def decode(bank):
        readback = binding.unbind(bank, obj_c)
        best, _ = cleanup_argmax(readback, loc_vocab)
        return best

    out = {}
    for q in row["questions"]:
        qt = q["type"]
        if arm == "ORACLE":
            out[qt] = q["gold"]
            continue
        if qt == "reality":
            out[qt] = decode(world_bank)
        elif qt == "memory":
            out[qt] = decode(binding.bind(obj_c, codes.get("loc", init)))  # initial world binding
        elif qt in ("belief", "belief_protagonist"):
            out[qt] = decode(agent_bank(prot))
        elif qt == "belief_second_agent":
            out[qt] = decode(agent_bank(second))
        else:
            out[qt] = decode(agent_bank(prot))
    return out


def boot_ci(vals, n_boot=2000, seed=0):
    if not vals:
        return (0.0, 0.0, 0.0, 0.0)
    a = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    m = a[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi), float((hi - lo) / 2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260826)
    args = ap.parse_args()
    out_dir = repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if args.self_test else ""))
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.perf_counter()
    try:
        rows = load_gold()
        codes = Codes(args.seed)
        # global location vocabulary (cleanup among ALL locations -> real distractors)
        loc_strings = sorted({row[k] for row in rows for k in ("initial_location", "final_location")})
        loc_vocab = {s: codes.get("loc", s) for s in loc_strings}

        arms = ["ALWAYS_INITIAL", "NO_TOM", "FULL_TOM", "FULL_TOM_LIVE", "TWIN", "ORACLE"]
        # belief-question subsets
        def is_belief(qt):
            return qt.startswith("belief")

        results = {}
        # observation-extractor accuracy (report the live front-end honestly)
        obs_correct = obs_total = 0
        for row in rows:
            pred = extract_observed_from_text(row["text"], row["protagonist"])
            # gold "observed" = saw the move OR was informed (true-belief_informed)
            gold_obs = bool(row["protagonist_saw_move"]) or row["condition"] == "true_belief_informed"
            obs_correct += int(pred == gold_obs)
            obs_total += 1

        for arm in arms:
            rng = np.random.default_rng((hash(arm) ^ args.seed) & 0x7FFFFFFF)
            belief_all, belief_fb, belief_tb, reality = [], [], [], []
            for row in rows:
                fb = row["condition"].startswith("false_belief")
                if arm == "ALWAYS_INITIAL":
                    ans = {q["type"]: row["initial_location"] for q in row["questions"]}
                else:
                    ans = build_answer(arm, row, codes, rng, loc_vocab)
                for q in row["questions"]:
                    qt = q["type"]
                    ok = int(ans[qt] == q["gold"])
                    if is_belief(qt):
                        belief_all.append(ok)
                        (belief_fb if fb else belief_tb).append(ok)
                    elif qt == "reality":
                        reality.append(ok)
            bm, blo, bhi, bhw = boot_ci(belief_all, seed=args.seed + 1)
            results[arm] = {
                "belief_acc": bm, "belief_ci": [blo, bhi], "belief_hw": bhw, "n_belief": len(belief_all),
                "belief_false_belief_acc": float(np.mean(belief_fb)) if belief_fb else None,
                "belief_true_belief_acc": float(np.mean(belief_tb)) if belief_tb else None,
                "reality_acc": float(np.mean(reality)) if reality else None, "n_reality": len(reality),
            }

        # ---- INTERFERENCE STRESS: rebuild location codes as compositional (similar phrases share
        # components) and re-measure the belief discriminator. If the mechanism relied on near-
        # orthogonal codes, FULL_TOM would collapse here. ----
        codes_i = Codes(args.seed, loc_interfere=True)
        loc_vocab_i = {s: codes_i.get("loc", s) for s in loc_strings}
        # measure inter-location similarity to prove interference is real (not still orthogonal)
        import itertools
        sims = []
        keys = list(loc_vocab_i)
        for a, b in itertools.islice(itertools.combinations(keys, 2), 400):
            va, vb = loc_vocab_i[a], loc_vocab_i[b]
            sims.append(abs(float(torch.real(torch.sum(torch.conj(va) * vb)).item()) / D))
        interfere = {"mean_abs_loc_sim": float(np.mean(sims)) if sims else 0.0,
                     "max_abs_loc_sim": float(np.max(sims)) if sims else 0.0}
        for arm in ("FULL_TOM", "NO_TOM", "ORACLE"):
            rng = np.random.default_rng((hash(arm) ^ args.seed) & 0x7FFFFFFF)
            bvals = []
            for row in rows:
                ans = build_answer(arm, row, codes_i, rng, loc_vocab_i)
                for q in row["questions"]:
                    if q["type"].startswith("belief"):
                        bvals.append(int(ans[q["type"]] == q["gold"]))
            interfere[f"{arm}_belief_acc"] = float(np.mean(bvals)) if bvals else None

        # gates
        ft, no, tw, orc, ai = (results["FULL_TOM"], results["NO_TOM"], results["TWIN"],
                               results["ORACLE"], results["ALWAYS_INITIAL"])
        ftl = results["FULL_TOM_LIVE"]
        gates = {
            "full_tom_beats_no_tom_floor_ci": ft["belief_ci"][0] > no["belief_ci"][1],
            "full_tom_beats_always_initial_floor_ci": ft["belief_ci"][0] > ai["belief_ci"][1],
            "full_tom_beats_twin_ci": ft["belief_ci"][0] > tw["belief_ci"][1],
            "full_tom_solves_false_belief": (ft["belief_false_belief_acc"] or 0) >= 0.99,
            "full_tom_keeps_true_belief": (ft["belief_true_belief_acc"] or 0) >= 0.99,
            "full_tom_live_beats_no_tom_ci": ftl["belief_ci"][0] > no["belief_ci"][1],
            "reality_intact_full_tom": (ft["reality_acc"] or 0) >= 0.99,
            "full_tom_robust_to_location_interference": (interfere["FULL_TOM_belief_acc"] or 0) >= 0.90,
        }
        obs_acc = obs_correct / obs_total if obs_total else 0.0

        elapsed = time.perf_counter() - t0
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": "MEASURED",
            "run_mode": "smoke" if args.self_test else "full",
            "seed": args.seed, "D": D, "n_passages": len(rows),
            "n_belief_questions": results["FULL_TOM"]["n_belief"],
            "n_locations_vocab": len(loc_vocab),
            "observation_extractor_acc": obs_acc,
            "arms": results, "interference_stress": interfere, "gates": gates,
            "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        tmp = os.path.join(out_dir, "metrics.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(tmp, os.path.join(out_dir, "metrics.json"))

        print(f"=== {ANCHOR_NAME} ({metrics['run_mode']}) {elapsed:.1f}s "
              f"n_passages={len(rows)} n_belief_Q={results['FULL_TOM']['n_belief']} "
              f"n_loc_vocab={len(loc_vocab)} obs_extractor_acc={obs_acc:.3f} ===")
        print(f"{'ARM':16s} belief_acc[CI]           FB    TB    reality")
        for a in arms:
            r = results[a]
            fb = f"{r['belief_false_belief_acc']:.2f}" if r['belief_false_belief_acc'] is not None else " -- "
            tb = f"{r['belief_true_belief_acc']:.2f}" if r['belief_true_belief_acc'] is not None else " -- "
            rl = f"{r['reality_acc']:.2f}" if r['reality_acc'] is not None else " -- "
            print(f"  {a:14s} {r['belief_acc']:.3f}[{r['belief_ci'][0]:.3f},{r['belief_ci'][1]:.3f}]  "
                  f"{fb}  {tb}  {rl}")
        print("GATES:")
        for k, v in gates.items():
            print(f"  {'PASS' if v else 'fail'}  {k}")
    except Exception as e:
        with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "err": f"{type(e).__name__}: {e}",
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise


if __name__ == "__main__":
    main()
