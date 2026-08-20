"""Build the anomaly set the F5 evaluation needs -- with the confound killed BY CONSTRUCTION.

THE TASK IT SERVES. F5 (the coherence monitor / N400 generator) computes how much an incoming word
forces the running discourse state to change. **The read-out is: does the error peak at an anomalous
word?** That is what the N400 literature measures.

*** THE CONFOUND THAT WOULD RUIN IT, AND WHY THIS SCRIPT EXISTS. ***
**ANOMALOUS WORDS ARE USUALLY RARE WORDS.** A detector that merely flags low-frequency tokens would
score brilliantly while understanding nothing -- **vocabulary statistics wearing a comprehension
costume.** That is exactly the failure that invalidated my context-diversity test (an outcome that
rewarded topical narrowness) and that inflated the sensorimotor floor (an uncontrolled covariate the
matching missed).

**SO THE INTRUDER IS MATCHED TO THE WORD IT REPLACES ON FREQUENCY, LENGTH AND PART OF SPEECH**, and
the achieved balance is REPORTED as a standardized mean difference -- **and as a DISTRIBUTION, not
only a mean, because two groups can share a mean and still be trivially separable.**

WHAT MAKES AN INTRUDER ANOMALOUS RATHER THAN MERELY DIFFERENT: it is topically DISJOINT -- it must
not co-occur with any content word of the host sentence anywhere in the scanned sample.

*** V1 PRODUCED A PERFECT BALANCE TABLE AND UNUSABLE ITEMS. THIS IS V2. ***
**V1's matching was flawless -- log-frequency smd +0.0126, length smd -0.0085, quartiles aligned --
and reading twelve items showed the set was broken.** Three defects, all invisible to the balance
table, and *all three would have made the anomaly detectable WITHOUT COMPREHENSION*, which is the
exact confound the matching exists to remove:

1. **WORDNET NOUN-HOOD IS NOT A PART-OF-SPEECH CHECK.** `begin`, `past`, `independent`, `inside` and
   `middle` all carry a rare noun sense, so all passed. Substituting them produced **ungrammatical**
   sentences (*"the only month to both carbon and end"*) -- **detectable on SYNTAX.**
2. **PROPER NOUNS ARRIVED LOWERCASED BY LEMMATISATION** -- `december`, `january`, `pierre` used as
   common nouns (*"Several december species"*).
3. **TABLE AND LIST DEBRIS IS NOT PROSE** (*"Kandahar 1,127,000 54,022 Pashto, Dari 16 districts"*).

**➡️ THE FIX: an IN-CONTEXT UPOS tag from the owned perceptron, a case-based proper-noun filter, and
a prose filter.** *The lesson generalises past this script: **A BALANCE TABLE MEASURES THE MATCHING,
NEVER THE ITEM.** Only reading the items measures the item -- and v1's balance was good enough to
have been reported as success.*

**WHAT THIS SCRIPT STILL DOES NOT DO: claim the items are good.** Item quality is a HUMAN judgement
and the sample is printed for exactly that.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

N_SENT = int(os.environ.get("DIAG_N_SENT", "8000"))
N_ITEMS = int(os.environ.get("DIAG_N_ITEMS", "120"))
CORPUS = os.environ.get("DIAG_CORPUS", "simplewiki")
SEED = int(os.environ.get("DIAG_SEED", "20260821"))
POS_CKPT = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")

# a token is a usable COMMON NOUN only if the tagger calls it NOUN this often across the corpus,
# and it appears lowercase this often (the proper-noun filter -- v1 shipped "december", "pierre")
NOUN_SHARE = 0.80
LOWER_SHARE = 0.90


def ascii_(s):
    return s.encode("ascii", "replace").decode("ascii")


def word(tok):
    return "".join(ch for ch in tok if ch.isalpha() or ch == "-")


def is_prose(s):
    """Reject table/list debris AND fragments. V1 emitted 'Kandahar 1,127,000 54,022 Pashto, Dari
    16 districts'; V5 still emitted the fragments 'Note that this does not apply for X (i' and
    'makes his "I Have a Dream" X for Civil Rights', plus a source with an unbalanced paren."""
    toks = s.split()
    if not (6 <= len(toks) <= 45):
        return False
    if sum(1 for t in toks if word(t) and word(t) == t.strip(".,;:()\"'")) / len(toks) < 0.80:
        return False
    if sum(1 for t in toks if any(c.isdigit() for c in t)) > 2:
        return False
    if s.count("(") != s.count(")"):
        return False                      # V5 item 26: "(Earth's money are well known"
    if not s[:1].isupper():
        return False                      # V5 item 51: "makes his ... " -- a mid-sentence fragment
    if len(toks[-1].strip(".,;:()\"'")) <= 1:
        return False                      # V6: "eaten in the U" -- split mid-abbreviation
    # RUN-TOGETHER TOKENS: the corpus concatenates across missing whitespace, e.g.
    # "EasterPentecostPinseThe", "BededagA", "DayJuledagThe". A lowercase letter immediately
    # followed by an uppercase one inside a token is the tell. Costs the odd legitimate CamelCase.
    for t in toks:
        w = word(t)
        if any(w[k].islower() and w[k + 1].isupper() for k in range(len(w) - 1)):
            return False
    return True


# --------------------------------------------------------------------- grammatical number
# **`lemma_word` ALONE IS NOT A NUMBER TEST, AND TRUSTING IT COST A WHOLE BUILD.** It is documented
# to return a REAL ENGLISH WORD rather than a stripped stem -- which is why it is right for concept
# identity -- but that same guarantee makes it leave `laws -> laws` and `values -> values`
# UNCHANGED, so both read SINGULAR. V3 therefore shipped *"Many countries have thing based on this
# idea"* and *"The values members who sit on the left"* while its own check reported **120 of 120
# agreeing, 0 violations** -- because the CHECK CALLED THE SAME FUNCTION THE BUILDER DID.
#
# *That is standing discipline 3 -- a checker sharing a flaw with what it checks hides it -- and it
# was found by READING THE ITEMS, not by any statistic. Third time in this one script that a clean
# number sat on top of broken items.*
#
# So: three independent signals, and a `--self-test` over hand-labelled traps in BOTH directions
# (irregular plurals that do not end in s; singulars that do).
_SG_ENDING_IN_S = {
    "glass", "grass", "class", "gas", "bus", "news", "species", "series", "means", "lens",
    "physics", "mathematics", "politics", "economics", "ethics", "process", "analysis", "basis",
    "crisis", "thesis", "axis", "campus", "virus", "status", "focus", "bonus", "census", "atlas",
    "canvas", "chaos", "cosmos", "surplus", "consensus", "apparatus", "octopus", "hypothesis",
    "diagnosis", "emphasis", "illness", "business", "witness", "address", "press", "success",
    "access", "loss", "cross", "dress", "mass", "pass", "miss", "boss", "kiss", "guess",
}


def grammatical_number(w):
    """SG/PL for a lowercase surface form.

    **DELIBERATELY TAKES NO VOCABULARY.** An earlier version confirmed a singular existed in a
    corpus vocabulary before calling a trailing-s word plural -- and the builder passed its
    FILTERED common-noun set, which omits `law`, so `laws` read SINGULAR and 10 violations shipped.
    The exception list plus the `ss` rule already carry the hard cases, so the vocabulary bought
    nothing and cost a build. *Removing a parameter removes the class of bug where a caller passes
    the wrong one.*"""
    from hdlab.reading_grounding_loop import normalize_lemma
    if w in _SG_ENDING_IN_S or w.endswith("ss"):
        return "SG"
    if normalize_lemma(w) != w:
        return "PL"                      # lemmatiser changed it -> inflected
    return "PL" if (w.endswith("s") and len(w) > 3) else "SG"


def _selftest_number():
    """Positive AND negative controls. An absence check ('no violations') inherits the detector's
    blind spots; a labelled trap list does not."""
    pl = ["laws", "values", "buildings", "creditors", "children", "mice", "feet", "dishes",
          "scales", "cultures", "churches", "events", "cities", "leaves", "types", "crops"]
    sg = ["thing", "choir", "glass", "species", "news", "half", "analysis", "series", "bus",
          "process", "crisis", "lens", "physics", "status", "focus", "business", "law", "value"]
    # Exercise BOTH call signatures -- bare, and WITH a vocab, which is what the builder uses.
    # A vocab that omits the singular must not silently flip a plural to singular.
    bad = [(w, "PL", grammatical_number(w)) for w in pl if grammatical_number(w) != "PL"]
    bad += [(w, "SG", grammatical_number(w)) for w in sg if grammatical_number(w) != "SG"]
    # THE EXACT REGRESSION that shipped v4, as a permanent case: these three read SG under the old
    # vocabulary-gated version and put "Many countries have thing" / "Usually the days is used"
    # into a 120-item evaluation set.
    bad += [(w, "PL(v4 regression)", grammatical_number(w))
            for w in ("laws", "values", "days") if grammatical_number(w) != "PL"]
    if bad:
        print("NUMBER SELF-TEST FAILED (%d):" % len(bad))
        for w, want, got in bad:
            print("   %-12s want %s got %s" % (w, want, got))
        return 1
    print("number self-test PASS: %d plurals + %d singulars, including the traps lemma_word alone "
          "gets wrong (laws, values) and the traps a trailing-s rule gets wrong (glass, species, "
          "news, analysis)" % (len(pl), len(sg)))
    return 0


def smd(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a) / max(1, len(a) - 1)
    vb = sum((x - mb) ** 2 for x in b) / max(1, len(b) - 1)
    return (ma - mb) / math.sqrt(max(1e-12, (va + vb) / 2))


def q(v, f):
    v = sorted(v)
    return v[min(len(v) - 1, int(f * len(v)))]


def main():
    from nltk.corpus import wordnet as wn

    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.pos_tagger import PosTagger
    from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma

    # ------------------------------------------------------------------ TWO FILTERS FROM THE READ
    # **1. THE INTRUDER MUST NOT BE A NEAR-SYNONYM OF THE TARGET -- THE WORST DEFECT FOUND, BECAUSE
    # IT MAKES THE ITEM UNANSWERABLE RATHER THAN EASY.** V5 shipped laws->rules ("Many countries
    # have RULES based on this idea of fairness"), types->ideas, ways->tools and
    # particles->molecules. **Every one of those sentences is still TRUE, so there is no anomaly to
    # find and a PERFECT detector must fail on them.** Topical disjointness was supposed to prevent
    # this and cannot: it asks whether two words co-occur in an 8,000-sentence sample, and `law`
    # and `rule` simply never did. *Co-occurrence is not relatedness -- synonyms are precisely the
    # words that SUBSTITUTE for each other instead of appearing together, so the disjointness rule
    # was actively SELECTING for them.*
    def relatedness_blocked(a, b):
        sa, sb = wn.synsets(a, pos="n"), wn.synsets(b, pos="n")
        if not sa or not sb:
            return True                   # unknown to WordNet -> cannot verify -> refuse
        if {x.name() for x in sa} & {x.name() for x in sb}:
            return True                   # share a sense
        close = set()
        for x in sa:
            close |= {h.name() for h in x.hypernyms()} | {h.name() for h in x.hyponyms()}
            for h in x.hypernyms():
                close |= {g.name() for g in h.hyponyms()}      # siblings (co-hyponyms)
        return bool(close & {x.name() for x in sb})

    # **2. BOTH WORDS MUST BE REAL ENGLISH.** V5 shipped the corpus's own misspellings and debris as
    # intruders -- `countrys` (twice), `todays`, `cetera` (from "et cetera"). A misspelled intruder
    # is detectable on ORTHOGRAPHY, which is one of the mandatory floors: the item would be scored
    # by the very baseline it is meant to beat.
    def real_word(w):
        return bool(wn.synsets(w, pos="n"))

    reg = CorpusRegistry()
    h = reg.handles.get(CORPUS)
    if h is None or not h.available or h.remaining() <= 0:
        print("corpus %r unavailable" % CORPUS)
        return 1
    raw = list(h.take(N_SENT))
    sents = [s for s in raw if is_prose(s)]
    print("corpus %s: %d sentences, %d prose (%.0f%% rejected as table/list debris)"
          % (CORPUS, len(raw), len(sents), 100.0 * (1 - len(sents) / max(1, len(raw)))))

    if not os.path.exists(POS_CKPT):
        print("POS checkpoint missing: %s" % POS_CKPT)
        return 1
    tagger = PosTagger.load(POS_CKPT)

    # ---- tag every prose sentence ONCE; everything downstream reads these tags
    tags_by_sent, tagcount, casecount, docfreq = [], collections.defaultdict(collections.Counter), \
        collections.Counter(), collections.Counter()
    lem_by_sent = []
    for i, s in enumerate(sents):
        toks = s.split()
        tags = tagger.tag(toks)
        tags_by_sent.append(tags)
        lem_by_sent.append(content_lemmas(s))
        seen = set()
        for t, g in zip(toks, tags):
            w = word(t)
            if not w:
                continue
            lw = w.lower()
            tagcount[lw][g] += 1
            if w[0].islower():
                casecount[lw] += 1
            if lw not in seen:
                seen.add(lw)
                docfreq[lw] += 1
        if (i + 1) % 1000 == 0:
            print("  tagged %d/%d" % (i + 1, len(sents)), flush=True)
    total = sum(docfreq.values()) or 1

    def is_common_noun(lw):
        c = tagcount[lw]
        n = sum(c.values())
        if n < 3 or len(lw) < 3:
            return False
        if c["NOUN"] / n < NOUN_SHARE:
            return False
        return casecount[lw] / n >= LOWER_SHARE

    vocab = [w for w in docfreq if is_common_noun(w) and real_word(w)]
    print("common-noun vocabulary (UPOS NOUN >=%.0f%%, lowercase >=%.0f%%, n>=3): %d"
          % (100 * NOUN_SHARE, 100 * LOWER_SHARE, len(vocab)))
    if len(vocab) < 200:
        print("vocabulary too small to match within -- UNDERPOWERED, not writing")
        return 1

    # ** PASS THE FULL CORPUS TOKEN SET, NOT `vocab`. ** `vocab` is the heavily FILTERED
    # common-noun set (UPOS NOUN >=80%, lowercase >=90%), and `law` is not in it -- so `laws` failed
    # the "does a singular exist" test and read SINGULAR. That let 10 violations through, including
    # *"Many countries have thing"* and *"Usually the days is used"*.
    # **AND THE SELF-TEST PASSED THROUGHOUT, BECAUSE IT CALLS gn(w) WITH THE DEFAULT vocab=None --
    # IT NEVER EXERCISED THE CALL THE BUILDER MAKES.** A self-test that does not use the production
    # call signature is a self-test of a different function.
    number = grammatical_number

    by_bin = collections.defaultdict(list)
    for w in vocab:
        by_bin[(round(math.log(docfreq[w] / total), 1), len(w))].append(w)

    cooc = collections.defaultdict(set)
    for ls in lem_by_sent:
        u = set(ls)
        for w in u:
            cooc[w] |= u

    rng = random.Random(SEED)
    used_pairs, used_target = set(), collections.Counter()
    items, order = [], list(range(len(sents)))
    rng.shuffle(order)
    for i in order:
        if len(items) >= N_ITEMS:
            break
        s, tags, ls = sents[i], tags_by_sent[i], lem_by_sent[i]
        toks = s.split()
        # the target must be a COMMON NOUN **IN THIS SENTENCE**, lowercase here, and not the
        # first token (sentence-initial case is uninformative about proper-noun status)
        cand_pos = [j for j in range(1, len(toks))
                    if tags[j] == "NOUN" and word(toks[j])
                    and word(toks[j])[0].islower() and word(toks[j]).lower() in vocab
                    and word(toks[j]) == toks[j].strip(".,;:()\"'")]
        if not cand_pos:
            continue
        pos = rng.choice(cand_pos)
        target = word(toks[pos]).lower()
        lf, L = math.log(docfreq[target] / total), len(target)
        pool = []
        for dl in (0.0, 0.1, -0.1, 0.2, -0.2):
            for dL in (0, 1, -1):
                pool += by_bin.get((round(lf + dl, 1), L + dL), [])
        host = set(ls)
        tnum = number(target)
        prev = word(toks[pos - 1]).lower() if pos > 0 else ""
        pool = [w for w in pool if w != target and not (cooc[w] & host) and number(w) == tnum
                and not relatedness_blocked(normalize_lemma(w), normalize_lemma(target))]
        if prev in ("a", "an"):
            # "a"/"an" is fixed by the FOLLOWING word's initial sound. Swapping a vowel-initial
            # target for a consonant-initial intruder yields "an cost" -- an agreement cue, the
            # same defect as number. REJECTING is preferable to rewriting the article, because
            # rewriting would change a SECOND token and put a spurious change one slot before the
            # position the error is read at.
            want = prev == "an"
            pool = [w for w in pool if (w[0] in "aeiou") == want]
        if not pool:
            continue
        # ** ITEM INDEPENDENCE. ** V6 used `cities -> changes` FOUR times and `ways -> types` three
        # times: 111 distinct pairs across 120 items, with one target reused 6 times. Repeated pairs
        # are not independent items -- they share the same lexical decision, so a detector that
        # happens to handle `changes` well collects four correlated wins and n is overstated.
        # Cap each (target, intruder) pair at ONE use and each target at two.
        pool = [w for w in pool if (target, w) not in used_pairs]
        if not pool or used_target[target] >= 2:
            continue
        intruder = rng.choice(pool)
        used_pairs.add((target, intruder))
        used_target[target] += 1
        anom = list(toks)
        # **PRESERVE THE TOKEN'S PUNCTUATION.** Writing `anom[pos] = intruder` replaces the WHOLE
        # token, so `fire)` -> `music` DESTROYED a closing parenthesis and left V7 item 12 reading
        # "the 4 classical elements (water, air, earth and music". Same for a closing quote
        # (`site"`). An unbalanced bracket is a visible corruption at exactly the position being
        # scored -- the anomaly becomes findable by punctuation. Splice the alphabetic core only.
        core = word(toks[pos])
        at = toks[pos].find(core)
        anom[pos] = toks[pos][:at] + intruder + toks[pos][at + len(core):]
        items.append({
            "sentence_original": s, "sentence_anomalous": " ".join(anom),
            "target": target, "intruder": intruder, "anomaly_token_index": pos,
            "log_docfreq_target": round(lf, 4),
            "log_docfreq_intruder": round(math.log(docfreq[intruder] / total), 4),
            "len_target": L, "len_intruder": len(intruder),
            "noun_share_target": round(tagcount[target]["NOUN"] / sum(tagcount[target].values()), 3),
            "noun_share_intruder": round(
                tagcount[intruder]["NOUN"] / sum(tagcount[intruder].values()), 3),
            "number": tnum, "preceding_token": prev,
            "rel_position": round(pos / max(1, len(toks) - 1), 3),
        })

    if len(items) < 20:
        print("only %d items built -- UNDERPOWERED, not writing" % len(items))
        return 1

    lf_t = [it["log_docfreq_target"] for it in items]
    lf_i = [it["log_docfreq_intruder"] for it in items]
    ln_t = [it["len_target"] for it in items]
    ln_i = [it["len_intruder"] for it in items]

    print("\n" + "=" * 84)
    print("BALANCE -- necessary, NOT sufficient. V1 passed this and its items were unusable.")
    print("=" * 84)
    print("  log DOCUMENT frequency  smd = %+.4f  (%.3f vs %.3f)"
          % (smd(lf_t, lf_i), sum(lf_t) / len(lf_t), sum(lf_i) / len(lf_i)))
    print("  word length             smd = %+.4f  (%.2f vs %.2f)"
          % (smd(ln_t, ln_i), sum(ln_t) / len(ln_t), sum(ln_i) / len(ln_i)))
    print("  distributions, because a shared mean is not balance:")
    print("     target   min %.2f p25 %.2f p75 %.2f max %.2f"
          % (min(lf_t), q(lf_t, .25), q(lf_t, .75), max(lf_t)))
    print("     intruder min %.2f p25 %.2f p75 %.2f max %.2f"
          % (min(lf_i), q(lf_i, .25), q(lf_i, .75), max(lf_i)))
    print("  POS: mean NOUN share  target %.3f  intruder %.3f  (min intruder %.3f)"
          % (sum(it["noun_share_target"] for it in items) / len(items),
             sum(it["noun_share_intruder"] for it in items) / len(items),
             min(it["noun_share_intruder"] for it in items)))
    # POSITIVE CONTROL on the number guard rather than an absence check: assert agreement holds on
    # every item, and print the count so "0 violations" is distinguishable from "0 items checked".
    bad = [it for it in items if number(it["target"]) != number(it["intruder"])]
    print("  NUMBER agreement: %d of %d items agree, %d violations (%d PL / %d SG items)"
          % (len(items) - len(bad), len(items), len(bad),
             sum(1 for it in items if it["number"] == "PL"),
             sum(1 for it in items if it["number"] == "SG")))
    if bad:
        print("  GUARD FAILED -- not writing"); return 1

    out = os.path.join(_REPO, "data", "anomaly_set_frequency_matched_v8.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"corpus": CORPUS, "n_sentences_scanned": len(raw), "n_prose": len(sents),
                   "seed": SEED, "pos_checkpoint": os.path.relpath(POS_CKPT, _REPO),
                   "construction": "intruder matched on log document-frequency and length; both "
                                   "target and intruder are UPOS NOUN in >=%.0f%% of corpus "
                                   "occurrences and lowercase in >=%.0f%%; target is tagged NOUN "
                                   "IN ITS OWN SENTENCE and is not sentence-initial; host passes a "
                                   "prose filter; intruder never co-occurs with any host content "
                                   "word in the scanned sample" % (100 * NOUN_SHARE,
                                                                   100 * LOWER_SHARE),
                   "balance_smd": {"log_docfreq": smd(lf_t, lf_i), "length": smd(ln_t, ln_i)},
                   "items": items}, fh, indent=1)
    print("\nwrote %d items -> %s" % (len(items), out))

    print("\n" + "=" * 84)
    print("SAMPLE FOR HUMAN JUDGEMENT -- the only thing that measures ITEM quality.")
    print("Read for: is it ungrammatical (bad -- syntax cue) or merely odd (good -- meaning cue)?")
    print("=" * 84)
    for it in items[:14]:
        print("\n  %s -> %s  (logdf %.2f vs %.2f, len %d vs %d, nounshare %.2f vs %.2f)"
              % (it["target"], it["intruder"], it["log_docfreq_target"],
                 it["log_docfreq_intruder"], it["len_target"], it["len_intruder"],
                 it["noun_share_target"], it["noun_share_intruder"]))
        print("     %s" % ascii_(it["sentence_anomalous"])[:160])
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_selftest_number())
    if _selftest_number():
        raise SystemExit("number self-test failed -- refusing to build")
    raise SystemExit(main())
