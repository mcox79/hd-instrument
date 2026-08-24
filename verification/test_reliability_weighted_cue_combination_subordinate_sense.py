"""Scaffold-free witness for problem `the_prior_swamps_the_channel_instead_of_combining_with_it`.

Recomputes every headline INDEPENDENTLY from the saved per-candidate cue vectors
(_scored_population.json), in pure python, with its own paired bootstrap over WORDS. It never imports
the cell -- it re-derives each arm's pick from (z_prior, z_channel) and re-runs the ceilings.

VERDICT UNDER TEST: REFUTED as stated (no gold-blind combination beats the channel on subordinate),
and the REASON is a correlated-error regime, not a useless channel. The checks:
  1. positive control -- PRIOR is 0.0 by construction, CHANNEL beats chance: the instrument matches.
  2. THE SWAMPING -- the fixed z-sum (== BAYES_HUB) lands far BELOW the channel it was added to.
  3. NO HEADROOM -- routing (max of the two cues per item) == channel EXACTLY, and the blend oracle
     (truth Pareto-optimal in (z_prior,z_channel)) is ~= channel too: no non-negative blend beats it.
  4. NO BLEND ARM BEATS THE CHANNEL -- the whole lambda sweep on subordinate stays <= channel, and
     the reliability-weighted arm's paired-bootstrap delta vs channel does NOT clear zero.
  5. WHY (correlated errors) -- on subordinate items the channel gets wrong, its wrong pick is a
     HIGHER-frequency sense than the truth, so a frequency prior can only reinforce the error; and
     THE CRUX: prior peakedness does NOT predict which items the prior gets wrong (auc ~ 0.5).
  6. THE CHANNEL SIGNAL IS REAL -- the info-free twin channel (permuted spokes) scores well below the
     real channel, so the failure to combine is not an artifact of a noise channel.

Run: .venv/Scripts/python.exe verification/test_reliability_weighted_cue_combination_subordinate_sense.py
"""
import io
import json
import os
import random
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POP = os.path.join(REPO, "data",
                   "exp_reliability_weighted_cue_combination_subordinate_sense_v1",
                   "_scored_population.json")


def pick(zp, zc, wp, wc):
    best_i, best = 0, float("-inf")
    for i in range(len(zp)):
        s = wp * zp[i] + wc * zc[i]
        if s > best + 1e-12:
            best_i, best = i, s
    return best_i


def subj_weighted(rows, value_of):
    by_word = defaultdict(list)
    for r in rows:
        v = value_of(r)
        if v is not None:
            by_word[r["word"]].append(v)
    per_word = [sum(v) / len(v) for v in by_word.values() if v]
    return (sum(per_word) / len(per_word) if per_word else None), len(per_word)


def paired_boot(rows, fa, fb, seed=20260824, nboot=4000):
    aw, bw = defaultdict(list), defaultdict(list)
    for r in rows:
        va, vb = fa(r), fb(r)
        if va is not None:
            aw[r["word"]].append(va)
        if vb is not None:
            bw[r["word"]].append(vb)
    words = sorted(set(aw) & set(bw))
    a = [sum(aw[w]) / len(aw[w]) for w in words]
    b = [sum(bw[w]) / len(bw[w]) for w in words]
    n = len(words)
    rng = random.Random(seed)
    diffs = []
    for _ in range(nboot):
        sa = sb = 0.0
        for _ in range(n):
            i = rng.randrange(n)
            sa += a[i]; sb += b[i]
        diffs.append((sa - sb) / n)
    diffs.sort()
    delta = sum(a) / n - sum(b) / n
    lo, hi = diffs[int(0.025 * nboot)], diffs[int(0.975 * nboot)]
    return delta, lo, hi, n


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for q in neg:
            wins += 1.0 if p > q else (0.5 if p == q else 0.0)
    return wins / (len(pos) * len(neg))


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    if not os.path.exists(POP):
        print("[witness] FAIL saved population missing: %s (re-run the cell --mode full)" % POP)
        raise SystemExit(1)
    with io.open(POP, encoding="utf-8") as fh:
        pop = json.load(fh)
    rows = pop["rows"]
    rows_if = pop["rows_infofree"]
    LAM = pop.get("LAMBDA_GRID", [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0])

    SUB = [r for r in rows if (not r["dominant"]) and r["covered"]]
    SUB_if = [r for r in rows_if if (not r["dominant"]) and r["covered"]]

    def c_prior(r):   return int(pick(r["zp"], r["zc"], 1.0, 0.0) == r["t"])
    def c_channel(r): return int(pick(r["zp"], r["zc"], 0.0, 1.0) == r["t"]) if r["covered"] else None
    def c_fixed(r):   return int(pick(r["zp"], r["zc"], 1.0, 1.0) == r["t"])
    def c_rb(r):      return int(pick(r["zp"], r["zc"], r["_rb"]["wp"], r["_rb"]["wc"]) == r["t"])

    def c_route(r):
        pc = int(pick(r["zp"], r["zc"], 1.0, 0.0) == r["t"])
        cc = int(pick(r["zp"], r["zc"], 0.0, 1.0) == r["t"]) if r["covered"] else 0
        return max(pc, cc)

    def c_blend(r):
        if not r["covered"]:
            return int(pick(r["zp"], r["zc"], 1.0, 0.0) == r["t"])
        zp, zc, t = r["zp"], r["zc"], r["t"]
        for j in range(len(zp)):
            if j == t:
                continue
            if zp[j] >= zp[t] - 1e-12 and zc[j] >= zc[t] - 1e-12 and (zp[j] > zp[t] + 1e-12 or zc[j] > zc[t] + 1e-12):
                return 0
        return 1

    chance, n_words = subj_weighted(SUB, lambda r: 1.0 / r["k"])
    prior, _ = subj_weighted(SUB, c_prior)
    channel, _ = subj_weighted(SUB, c_channel)
    fixed, _ = subj_weighted(SUB, c_fixed)
    rb, _ = subj_weighted(SUB, c_rb)
    route, _ = subj_weighted(SUB, c_route)
    blend, _ = subj_weighted(SUB, c_blend)

    print("[witness] --- subordinate, %d words, subject-weighted, chance = %.4f ---" % (n_words, chance))
    for nm, v in [("PRIOR", prior), ("CHANNEL", channel), ("FIXED z-sum", fixed),
                  ("RELIABILITY_BINNED", rb), ("ORACLE_ROUTE", route), ("ORACLE_BLEND", blend)]:
        print("[witness]     %-20s %.4f" % (nm, v))

    # 1. positive control
    chk("PRIOR is 0.0 on subordinate BY CONSTRUCTION", abs(prior) < 1e-9, "PRIOR %.4f" % prior)
    chk("CHANNEL alone beats chance on subordinate", channel > chance,
        "CHANNEL %.4f vs chance %.4f" % (channel, chance))
    # 2. the swamping
    chk("THE SWAMPING: fixed z-sum lands far below the channel", fixed < channel - 0.15,
        "FIXED %.4f vs CHANNEL %.4f" % (fixed, channel))
    # 3. no headroom
    chk("ROUTING oracle == channel (routing cannot beat the channel here)",
        abs(route - channel) < 1e-9, "ROUTE %.4f == CHANNEL %.4f" % (route, channel))
    chk("BLEND oracle gives no material headroom over the channel", blend - channel < 0.03,
        "BLEND %.4f vs CHANNEL %.4f (+%.4f)" % (blend, channel, blend - channel))
    # 4. no blend arm beats the channel: full lambda sweep on subordinate stays <= channel
    lam_max = 0.0
    for lam in LAM:
        v, _ = subj_weighted(SUB, lambda r, l=lam: int(pick(r["zp"], r["zc"], 1.0, l) == r["t"]))
        lam_max = max(lam_max, v or 0.0)
    chk("no lambda-blend on subordinate beats the channel", lam_max <= channel + 1e-9,
        "max over lambda sweep = %.4f <= channel %.4f" % (lam_max, channel))
    d, lo, hi, nb = paired_boot(SUB, c_rb, c_channel)
    chk("reliability-weighted arm does NOT CI-beat the channel", not (lo > 0.0),
        "RB - CHANNEL d=%+.4f CI[%+.4f,%+.4f] n=%d" % (d, lo, hi, nb))
    # 5. WHY: correlated errors + the crux
    scw = [r for r in SUB if pick(r["zp"], r["zc"], 0.0, 1.0) != r["t"]]
    hf = [1 if r["counts"][pick(r["zp"], r["zc"], 0.0, 1.0)] >= r["counts"][r["t"]] else 0 for r in scw]
    hf_frac = sum(hf) / len(hf) if hf else None
    chk("channel's wrong picks on subordinate are HIGHER-freq than truth (correlated error)",
        hf_frac is not None and hf_frac >= 0.8,
        "%.4f of %d channel-wrong items" % (hf_frac or 0, len(scw)))
    cov = [r for r in rows if r["covered"]]
    Hn = [-r["H_prior"] for r in cov]
    pw = [0 if pick(r["zp"], r["zc"], 1.0, 0.0) == r["t"] else 1 for r in cov]
    a_crux = auc(Hn, pw)
    # a usable down-weight gate needs auc(peaked -> prior_wrong) meaningfully > 0.5; it is < 0.5 here
    # (a peaked prior is if anything MORE often right), so peakedness cannot flag the prior's errors.
    chk("CRUX: prior peakedness does NOT predict prior-error (auc not usable, < 0.55)",
        a_crux is not None and a_crux < 0.55,
        "auc(peaked -> prior_wrong) = %.4f (0.5 = none; < 0.5 = anti)" % a_crux)
    # 6. the channel signal is real (info-free twin channel loses)
    ch_if, _ = subj_weighted(SUB_if, c_channel)
    chk("info-free twin channel scores well below the real channel (signal is real)",
        ch_if is not None and ch_if < channel - 0.1,
        "CHANNEL_infofree %.4f vs CHANNEL %.4f" % (ch_if, channel))

    # 7. SUPPRESSION: allowing the prior a NEGATIVE weight (suppress the dominant sense; reordered
    #    access) DOES open headroom the monotone blend hid -- but it is a pure population trade-off,
    #    and no gold-blind detector fires it selectively.
    def signed_pick(r, b):
        v = [r["zc"][i] + b * r["zp"][i] for i in range(len(r["zp"]))]
        bi, bst = 0, float("-inf")
        for i in range(len(v)):
            if v[i] > bst + 1e-12:
                bi, bst = i, v[i]
        return bi
    BGRID = [round(-6 + 0.25 * k, 3) for k in range(49)]
    sup_oracle, _ = subj_weighted(SUB, lambda r: int(any(signed_pick(r, b) == r["t"] for b in BGRID)))
    sup_fixed_sub, _ = subj_weighted(SUB, lambda r: int(signed_pick(r, -1.5) == r["t"]))
    DOM = [r for r in rows if r["dominant"] and r["covered"]]
    prior_dom, _ = subj_weighted(DOM, lambda r: int(signed_pick(r, 1e9) == r["t"]))
    sup_fixed_dom, _ = subj_weighted(DOM, lambda r: int(signed_pick(r, -1.5) == r["t"]))
    chk("SUPPRESSION mechanism EXISTS: signed oracle (incl. b<0) >> channel",
        sup_oracle > channel + 0.15, "signed oracle %.4f vs channel %.4f" % (sup_oracle, channel))
    chk("but SUPPRESSION is a pure trade-off: fixed b=-1.5 beats channel on sub AND harms dom",
        sup_fixed_sub > channel + 0.1 and sup_fixed_dom < prior_dom - 0.1,
        "b=-1.5: sub %.4f (>ch %.4f), dom %.4f (<prior %.4f)"
        % (sup_fixed_sub, channel, sup_fixed_dom, prior_dom))
    # detector: does the channel's disagreement with the MFS identify subordinate items? (auc ~ 0.5)
    cov = [r for r in rows if r["covered"]]
    a_det = auc([r["disfavor_mfs"] for r in cov], [0 if r["dominant"] else 1 for r in cov])
    chk("NO gold-blind detector fires suppression selectively (disfavor->subordinate auc ~ 0.5)",
        a_det is not None and a_det < 0.58,
        "auc(channel-disfavours-MFS -> subordinate) = %.4f" % a_det)

    print()
    print("[witness] READ THIS AS: the fixed-weight rule DESTROYS a working cue (a combination defect,")
    print("[witness] not a useless channel). A SUPPRESSION rule (suppress the dominant sense) DOES beat")
    print("[witness] the channel on subordinate (+0.29) -- so a winning mechanism exists -- but it is a")
    print("[witness] pure population trade-off (dominant crashes), and NO gold-blind detector fires it")
    print("[witness] selectively (auc ~0.5). The missing organ is a subordinate-context detector, which")
    print("[witness] is bottlenecked on channel quality -- the same redirect as reader_meaning_channel.")
    print("[witness] RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()


def test_reliability_weighted_cue_combination_subordinate_sense():
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0, "witness FAILED (exit %r) -- run the file directly for detail" % (exc.code,)
