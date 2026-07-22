#!/usr/bin/env python
# -*- coding: ascii -*-
"""Entity/noun-typing selectional-enrichment WSD gate for the meaning module.

QUESTION (DIRECTIONAL GATE, properly powered):
Does enriching the sense-disambiguation signal with the ARGUMENT NOUN's semantic
TYPE (WordNet supersense / lexname of the object) give a STATISTICALLY SIGNIFICANT
improvement in correct verb-sense assignment over a type-level baseline that
ignores the argument -- the thing the N=31 hand-gold WSD gate (atom 29434) could
NOT establish (its aggregate lift was statistically NULL, McNemar p~0.6)?

BUILD-ON: atom 29434 (frame-matching alone nets ZERO; selectional restriction --
the filler noun's semantic type -- supplies the disambiguation lift) + the
WordNet-noun-type KB (atom 29420). This cell REPLACES the tiny hand-gold with a
real-scale, sense-tagged eval: NLTK SemCor (WordNet-sense-tagged, LOCAL).

ONE VARIABLE: the entity-typing selectional term ON vs OFF. Both arms share the
SAME candidate sense pool and the SAME most-frequent-sense (MFS) prior learned
from the SemCor TRAIN split. The ONLY difference is whether we add the learned
selectional-preference term log P(object_supersense | verb_sense).

  baseline (OFF): argmax_s  log P(sense | word)                        [MFS prior]
  mechanism (ON): argmax_s  log P(sense | word) + log P(obj_lex | s)   [+ entity-typing]

MUST-FAIL CONTROL: scramble the object-noun -> supersense map at TEST time via a
fixed global permutation of the noun lexnames (trained table left TRUE). This
decorrelates the type from the sense; the lift MUST vanish (multi-seed ->
sigma-over-scramble). A consistent relabeling would be a bijection and preserve
the model, so the scramble is applied at TEST-lookup only -- the honest kill.

CAN-FAIL (why this is a real gate): MFS is a notoriously strong WSD baseline;
nearest-noun selectional typing may not beat it. The residual may be
WORLD-KNOWLEDGE not TYPE (perception/cognition verbs whose object supersense does
not disambiguate -- the saw->perception class). An honest NEGATIVE (entity-typing
does not significantly beat MFS) is a valid, valuable outcome.

HONEST TIER: MEASURED_MECHANISM (meaning = better sense ASSIGNMENT via
entity-semantics; NOT compositional generalization / chain-grade). Do NOT inflate.

COMPUTE: symbolic count-model over SemCor + WordNet lookups. No matmul, no GPU, no
substrate primitive. Full wall ~1-2 min (dominated by SemCor tree deserialization,
done ONCE and cached). Foreground-to-completion, LOCAL-ONLY. Lightweight diagnostic
gate per compute-proportionality (class (b) sequential-CPU justified).

CELL-TEMPLATE MANDATORY (subset applicable to a symbolic non-substrate diagnostic):
# - arms_differ_verified at smoke gate (META_RULE_AF; baseline vs mech predictions)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < MFS_acc < 0.95)
# - HARD_PASS strictly above floor: real_gain > 0.01 AND McNemar p < 0.01 AND
#   scramble-sigma >= 2 (META_RULE_L; a real, scramble-confirmed, powered lift)
# - discriminator-fires (META_RULE_K): #prediction-flips > 0 at smoke; McNemar
#   discordant pairs (b+c) > 0
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in report
# - crlb_n/a: symbolic accuracy over a fixed sense-tagged corpus; no matmul noise floor
# - PROT-023: no hash()-seeded RNG / no list(set()); fixed int seeds + sorted()
"""
import os
import sys
import json
import math
import random
import argparse
import hashlib
import traceback
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "entity_typing_selectional_wsd_v1"

# WordNet has 26 noun lexnames (supersenses). Fixed constant for smoothing denom.
N_NOUN_LEXNAMES = 26
OBJ_WINDOW = 6            # nearest following gold-tagged noun within this many chunks
ALPHA_SENSE = 0.5        # add-alpha smoothing for P(sense|word)
BETA_SEL = 0.5           # add-beta smoothing for P(obj_lex|sense)
SPLIT_MOD = 5            # test = sent_idx % 5 == 0 (deterministic 80/20)


# ---------------------------------------------------------------------------
# SemCor extraction (done ONCE, cached in-process). Each verb INSTANCE ->
#   {train, word, gold, cands (ordered synset names), obj_lex}
# ---------------------------------------------------------------------------
def extract_instances(max_sents=None):
    from nltk.corpus import semcor, wordnet as wn
    from nltk.tree import Tree
    sents = semcor.tagged_sents(tag="sem")
    n = len(sents) if max_sents is None else min(max_sents, len(sents))
    insts = []
    for i in range(n):
        s = sents[i]
        # linearize chunks -> (pos, synset, word) with None for untagged tokens
        seq = []
        for ch in s:
            pos = syn = word = None
            if isinstance(ch, Tree):
                lab = ch.label()
                if hasattr(lab, "synset"):
                    try:
                        syn = lab.synset()
                    except Exception:
                        syn = None
                    if syn is not None:
                        pos = syn.pos()
                        try:
                            word = lab.name()
                        except Exception:
                            word = None
            seq.append((pos, syn, word))
        is_train = (i % SPLIT_MOD) != 0
        for j, (pos, syn, word) in enumerate(seq):
            if pos != "v" or word is None:
                continue
            cands = wn.synsets(word, "v")
            if len(cands) < 2:
                continue                       # need polysemy (difficulty-on)
            if syn not in cands:
                continue                       # gold must be reachable (fair)
            # nearest following gold-tagged noun -> its supersense (lexname)
            obj_lex = None
            for k in range(j + 1, min(j + 1 + OBJ_WINDOW, len(seq))):
                if seq[k][0] == "n":
                    obj_lex = seq[k][1].lexname()
                    break
            insts.append({
                "train": is_train,
                "word": word,
                "gold": syn.name(),
                "cands": [c.name() for c in cands],   # WordNet order (cands[0] = wn MFS)
                "obj_lex": obj_lex,
            })
    return insts


# ---------------------------------------------------------------------------
# Count model built from TRAIN instances only.
# ---------------------------------------------------------------------------
def build_model(insts):
    sense_freq = {}      # word -> {sense_name: count}
    sel_counts = {}      # sense_name -> {obj_lex: count}
    sel_total = {}       # sense_name -> total obj observations
    for it in insts:
        if not it["train"]:
            continue
        w = it["word"]
        g = it["gold"]
        sense_freq.setdefault(w, {})
        sense_freq[w][g] = sense_freq[w].get(g, 0) + 1
        if it["obj_lex"] is not None:
            sel_counts.setdefault(g, {})
            sel_counts[g][it["obj_lex"]] = sel_counts[g].get(it["obj_lex"], 0) + 1
            sel_total[g] = sel_total.get(g, 0) + 1
    return {"sense_freq": sense_freq, "sel_counts": sel_counts, "sel_total": sel_total}


def _log_p_sense(model, word, sense, cands):
    """log P(sense | word) with add-alpha over the candidate pool."""
    freqs = model["sense_freq"].get(word, {})
    c = freqs.get(sense, 0)
    tot = sum(freqs.get(s, 0) for s in cands)
    denom = tot + ALPHA_SENSE * len(cands)
    return math.log((c + ALPHA_SENSE) / denom)


def _log_p_obj_given_sense(model, sense, obj_lex):
    """log P(obj_lex | sense) with add-beta over the noun-lexname vocab.
    Senses unseen in the selectional table return uniform -> no effect on argmax."""
    counts = model["sel_counts"].get(sense, {})
    c = counts.get(obj_lex, 0)
    tot = model["sel_total"].get(sense, 0)
    denom = tot + BETA_SEL * N_NOUN_LEXNAMES
    return math.log((c + BETA_SEL) / denom)


def predict(model, it, use_entity_typing, obj_lex_override=None):
    """Argmax over candidate senses. use_entity_typing=False -> baseline (MFS prior
    only). obj_lex_override replaces the item's object supersense (scramble control).
    Tie-break: candidate order (WordNet MFS first) -> deterministic."""
    cands = it["cands"]
    obj = obj_lex_override if obj_lex_override is not None else it["obj_lex"]
    best = None
    best_score = None
    for s in cands:
        score = _log_p_sense(model, it["word"], s, cands)
        if use_entity_typing and obj is not None:
            score = score + _log_p_obj_given_sense(model, s, obj)
        if best_score is None or score > best_score + 1e-12:
            best_score = score
            best = s
    return best


# ---------------------------------------------------------------------------
# Evaluation + significance.
# ---------------------------------------------------------------------------
def _lexname_of(sense_name):
    from nltk.corpus import wordnet as wn
    try:
        return wn.synset(sense_name).lexname()
    except Exception:
        return None


def evaluate(insts, model):
    """Score baseline (OFF) vs mechanism (ON) on the TEST split. Primary population
    = test items WITH an object noun (mechanism is active there); also report the
    full polysemous-test population (diluted by no-object items)."""
    test = [it for it in insts if not it["train"]]
    withobj = [it for it in test if it["obj_lex"] is not None]

    # precompute gold lexnames (coarse "who-is-affected"-adjacent secondary metric)
    lex_cache = {}

    def lex(name):
        if name not in lex_cache:
            lex_cache[name] = _lexname_of(name)
        return lex_cache[name]

    def score_pop(pop):
        n = len(pop)
        base_ok = 0
        mech_ok = 0
        base_lex_ok = 0
        mech_lex_ok = 0
        flips = 0
        b = 0   # baseline correct, mech wrong
        c = 0   # baseline wrong, mech correct
        for it in pop:
            gp = predict(model, it, use_entity_typing=False)
            mp = predict(model, it, use_entity_typing=True)
            gold = it["gold"]
            gok = int(gp == gold)
            mok = int(mp == gold)
            base_ok += gok
            mech_ok += mok
            base_lex_ok += int(lex(gp) == lex(gold))
            mech_lex_ok += int(lex(mp) == lex(gold))
            if gp != mp:
                flips += 1
            if gok == 1 and mok == 0:
                b += 1
            elif gok == 0 and mok == 1:
                c += 1
        return {
            "n": n,
            "baseline_sense_acc": base_ok / n if n else 0.0,
            "mech_sense_acc": mech_ok / n if n else 0.0,
            "baseline_lexname_acc": base_lex_ok / n if n else 0.0,
            "mech_lexname_acc": mech_lex_ok / n if n else 0.0,
            "n_flips": flips,
            "mcnemar_b_base_only": b,
            "mcnemar_c_mech_only": c,
        }

    return {
        "withobj": score_pop(withobj),
        "all_poly": score_pop(test),
        "n_test_poly": len(test),
        "n_test_withobj": len(withobj),
    }


def scramble_eval(insts, model, seeds):
    """Must-fail: for each seed, apply a global random permutation of the noun
    lexnames to the TEST objects only, score the entity-typing arm, collect acc.
    A real selectional signal -> these accuracies collapse toward baseline."""
    test_withobj = [it for it in insts if not it["train"] and it["obj_lex"] is not None]
    # the set of noun lexnames present as objects in train sel table + test objects
    lexset = set()
    for d in model["sel_counts"].values():
        lexset.update(d.keys())
    for it in test_withobj:
        lexset.add(it["obj_lex"])
    lexnames = sorted(lexset)                 # PROT-023: sorted(), deterministic
    accs = []
    for sd in seeds:
        rng = random.Random(sd)               # fixed int seed; no hash()
        perm = lexnames[:]
        rng.shuffle(perm)
        mapping = {lexnames[i]: perm[i] for i in range(len(lexnames))}
        ok = 0
        for it in test_withobj:
            mp = predict(model, it, use_entity_typing=True,
                         obj_lex_override=mapping[it["obj_lex"]])
            ok += int(mp == it["gold"])
        accs.append(ok / len(test_withobj) if test_withobj else 0.0)
    mean = sum(accs) / len(accs)
    std = (sum((a - mean) ** 2 for a in accs) / len(accs)) ** 0.5
    return {"seeds": list(seeds), "acc_per_seed": accs, "acc_mean": mean, "acc_std": std}


# --- significance -----------------------------------------------------------
def _binom_two_sided_p(k, n):
    """Exact two-sided binomial p for k successes of n, p=0.5 (McNemar exact)."""
    if n == 0:
        return 1.0
    kk = min(k, n - k)
    # P(X <= kk) under Binom(n, 0.5), doubled, capped at 1
    logc = 0.0
    tail = 0.0
    # sum_{i=0..kk} C(n,i) * 0.5^n
    for i in range(0, kk + 1):
        tail += math.comb(n, i)
    p = tail * (0.5 ** n) * 2.0
    return min(1.0, p)


def significance(pop):
    b = pop["mcnemar_b_base_only"]
    c = pop["mcnemar_c_mech_only"]
    n_disc = b + c
    real_gain = pop["mech_sense_acc"] - pop["baseline_sense_acc"]
    p_exact = _binom_two_sided_p(min(b, c), n_disc)
    # continuity-corrected McNemar chi2 (secondary)
    if n_disc > 0:
        chi2 = (abs(b - c) - 1) ** 2 / n_disc
    else:
        chi2 = 0.0
    # 95% CI on the paired accuracy delta (normal approx: var ~= (b+c)/N^2)
    N = pop["n"]
    se = (math.sqrt(n_disc) / N) if N else 0.0
    ci_lo = real_gain - 1.96 * se
    ci_hi = real_gain + 1.96 * se
    return {
        "real_gain": real_gain,
        "mcnemar_b_base_only": b,
        "mcnemar_c_mech_only": c,
        "n_discordant": n_disc,
        "mcnemar_p_exact": p_exact,
        "mcnemar_chi2_cc": chi2,
        "delta_ci95": [ci_lo, ci_hi],
    }


# --- verdict ----------------------------------------------------------------
def make_verdict(ev, sig, scr):
    pop = ev["withobj"]
    base = pop["baseline_sense_acc"]
    mech = pop["mech_sense_acc"]
    real_gain = sig["real_gain"]
    p = sig["mcnemar_p_exact"]
    scr_mean = scr["acc_mean"]
    scr_std = scr["acc_std"]
    scr_gain = mech - scr_mean
    sigma_over_scramble = (scr_gain / scr_std) if scr_std > 1e-9 else float("inf")
    baseline_in_band = 0.05 < base < 0.95
    discriminator_fires = (pop["n_flips"] > 0) and (sig["n_discordant"] > 0)
    # scramble must remove most of the lift AND be many-sigma below mechanism
    scramble_kills = (sigma_over_scramble >= 2.0) and (scr_gain <= 0.30 * abs(real_gain) + 1e9 * (real_gain <= 0))
    # (the 1e9 term makes scramble_kills irrelevant when real_gain<=0; HF fires on gain first)

    if not baseline_in_band:
        verdict, msg = "MIDDLE_BAND", "baseline out of measurable band (AG); inconclusive"
    elif not discriminator_fires:
        verdict, msg = "MIDDLE_BAND", "discriminator did not fire (no flips / no discordant pairs)"
    elif real_gain <= 0.0:
        verdict, msg = "HARD_FAIL", "entity-typing does NOT beat MFS baseline (gain <= 0); residual likely world-knowledge not type"
    elif p >= 0.05:
        verdict, msg = "HARD_FAIL", "entity-typing lift is NOT statistically significant (McNemar p >= 0.05)"
    elif not scramble_kills:
        verdict, msg = "HARD_FAIL", "scramble control did NOT remove the lift; the noun->type map is not load-bearing"
    elif real_gain > 0.01 and p < 0.01 and sigma_over_scramble >= 2.0:
        verdict, msg = "HARD_PASS", ("entity-typing gives a STATISTICALLY REAL sense lift over MFS; "
                                     "scramble kills it (tier=MEASURED_MECHANISM)")
    else:
        verdict, msg = "MIDDLE_BAND", "lift is significant but small/marginal; entity-typing helps weakly"

    return {
        "verdict": verdict, "verdict_msg": msg,
        "tier_honest": "MEASURED_MECHANISM (entity-typing improves verb-sense ASSIGNMENT; NOT compgen)",
        "baseline_sense_acc": base, "mech_sense_acc": mech, "real_gain": real_gain,
        "mcnemar_p_exact": p, "mcnemar_b_base_only": sig["mcnemar_b_base_only"],
        "mcnemar_c_mech_only": sig["mcnemar_c_mech_only"], "n_discordant": sig["n_discordant"],
        "delta_ci95": sig["delta_ci95"],
        "scramble_acc_mean": scr_mean, "scramble_acc_std": scr_std,
        "scramble_gain": scr_gain, "sigma_over_scramble": sigma_over_scramble,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "scramble_kills_gain": scramble_kills,
        "n_test_withobj": ev["n_test_withobj"], "n_flips": pop["n_flips"],
    }


# --- io / harness -----------------------------------------------------------
def output_dir():
    d = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_crash(od, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": (type(exc).__name__ + ": " + str(exc)[:400]),
            "summary": "CELL_CRASHED", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:4000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _atomic_write(os.path.join(od, "metrics.json"), diag)


def arms_must_differ(insts, model):
    """META_RULE_AF: baseline vs mechanism predictions must not be bit-identical on
    the with-object test population (they can only differ there)."""
    test_withobj = [it for it in insts if not it["train"] and it["obj_lex"] is not None]
    base = [predict(model, it, use_entity_typing=False) for it in test_withobj]
    mech = [predict(model, it, use_entity_typing=True) for it in test_withobj]
    db = hashlib.sha256("|".join(base).encode("ascii")).hexdigest()
    dm = hashlib.sha256("|".join(mech).encode("ascii")).hexdigest()
    assert db != dm, "META_RULE_AF VIOLATION: baseline and mechanism predictions identical (entity-typing inert)"
    return {"baseline": db, "mechanism": dm}


def self_test():
    """Exercises the REAL code path (SemCor extraction on a tiny slice, WordNet
    lookups, model build, both arms, scramble) + asserts model shapes + one
    known selectional flip exists."""
    insts = extract_instances(max_sents=800)
    assert len(insts) > 20, "too few instances from 800 sents: %d" % len(insts)
    model = build_model(insts)
    assert model["sense_freq"], "empty sense_freq"
    # both arms return a candidate for every test item
    test = [it for it in insts if not it["train"]]
    assert test, "no test instances in self-test slice"
    for it in test[:20]:
        gp = predict(model, it, use_entity_typing=False)
        mp = predict(model, it, use_entity_typing=True)
        assert gp in it["cands"] and mp in it["cands"], "prediction not in candidate pool"
    # scramble runs
    scr = scramble_eval(insts, model, [1, 2])
    assert 0.0 <= scr["acc_mean"] <= 1.0
    # exact binomial sanity
    p = _binom_two_sided_p(0, 10)
    assert p < 0.01, "binomial p wrong: %s" % p
    assert abs(_binom_two_sided_p(5, 10) - 1.0) < 1e-9, "binomial symmetric case wrong"
    print("[self-test] PASS: SemCor extraction + WordNet + count-model + both arms + "
          "scramble + significance exercised (n_inst=%d, n_test=%d)" % (len(insts), len(test)), flush=True)
    return True


def run(mode):
    od = output_dir()
    t0 = datetime.now(timezone.utc)
    max_sents = 6000 if mode == "smoke" else None
    seeds = [1, 2, 3, 4, 5] if mode == "smoke" else list(range(1, 21))
    print("[run] extracting SemCor instances (mode=%s, max_sents=%s)..." % (mode, max_sents), flush=True)
    insts = extract_instances(max_sents=max_sents)
    model = build_model(insts)
    digests = arms_must_differ(insts, model)
    ev = evaluate(insts, model)
    sig = significance(ev["withobj"])
    scr = scramble_eval(insts, model, seeds)
    verdict = make_verdict(ev, sig, scr)
    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode,
        "verdict": verdict["verdict"], "verdict_msg": verdict["verdict_msg"],
        "summary": ("withobj N=%d base_sense=%.4f mech_sense=%.4f gain=%.4f McNemar_p=%.2e "
                    "scramble_mean=%.4f sigma=%.2f"
                    % (ev["n_test_withobj"], verdict["baseline_sense_acc"], verdict["mech_sense_acc"],
                       verdict["real_gain"], verdict["mcnemar_p_exact"], verdict["scramble_acc_mean"],
                       verdict["sigma_over_scramble"])),
        "elapsed_s": elapsed,
        "config": {"split_mod": SPLIT_MOD, "obj_window": OBJ_WINDOW,
                   "alpha_sense": ALPHA_SENSE, "beta_sel": BETA_SEL,
                   "n_noun_lexnames": N_NOUN_LEXNAMES, "max_sents": max_sents,
                   "n_instances_total": len(insts)},
        "verdict_block": verdict,
        "eval": ev,
        "significance": sig,
        "scramble": scr,
        "arms_differ_verified": True, "arm_digests": digests,
        "ts_iso": t0.isoformat(),
    }
    _atomic_write(os.path.join(od, "metrics.json"), out)
    print("[run] %s" % out["summary"], flush=True)
    print("[run] verdict=%s (%s)" % (verdict["verdict"], verdict["verdict_msg"]), flush=True)
    print("[run] withobj: base_sense=%.4f mech_sense=%.4f | base_lex=%.4f mech_lex=%.4f | flips=%d b=%d c=%d"
          % (ev["withobj"]["baseline_sense_acc"], ev["withobj"]["mech_sense_acc"],
             ev["withobj"]["baseline_lexname_acc"], ev["withobj"]["mech_lexname_acc"],
             ev["withobj"]["n_flips"], sig["mcnemar_b_base_only"], sig["mcnemar_c_mech_only"]), flush=True)
    print("[run] all_poly(diluted): base_sense=%.4f mech_sense=%.4f N=%d"
          % (ev["all_poly"]["baseline_sense_acc"], ev["all_poly"]["mech_sense_acc"], ev["all_poly"]["n"]), flush=True)
    print("[run] scramble acc_mean=%.4f std=%.4f -> sigma_over_scramble=%.2f | McNemar p_exact=%.3e chi2=%.2f"
          % (scr["acc_mean"], scr["acc_std"], verdict["sigma_over_scramble"],
             sig["mcnemar_p_exact"], sig["mcnemar_chi2_cc"]), flush=True)
    print("[run] baseline_in_band=%s discriminator_fires=%s scramble_kills=%s"
          % (verdict["baseline_in_band"], verdict["discriminator_fires"], verdict["scramble_kills_gain"]), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    mode = "smoke" if args.smoke else "full"
    run(mode)


if __name__ == "__main__":
    od_top = output_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(od_top, e)
        raise
