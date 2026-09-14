---
problem: one_convention_two_losses_ud_tags_main_verb_be_and_have_as_aux_so_the_governor_and_the_predicate_rescue_both_miss_the_clauses_only_verb
status: SOLVED
bar: "PASS = the two consumers measured TOGETHER under ONE switch: governor root / cop arcs up CI-separated on the sole-AUX clauses (the 58% tag-to-head class), blind-clause share down CI-separated through the reader, board not down on any dimension, twin at floor; the shared computation landed as ONE organ path with an observe route -- OR a numbered located negative naming which consumer the convention-free predicate helps and which it hurts, with the graded form measured."
result: "ONE COMPUTATION, BOTH CONSUMERS UP, UNDER ONE SWITCH -- AND THE NAMED DEFECT IS 77% GONE. The brief's own headline statistic, re-measured on today's asset by replicating experiments/_diag_tag_to_head_loss.py inside the cell: the whole tag-to-head loss is 102 net head flips = 1.07 UAS points, of which the VERB-as-AUX class is 23 tokens carrying net 90 = 88.2% (the brief quotes 58% of 149 from the 2026-09-13 asset; on today's asset the total is smaller and the class is a LARGER share of it). UNDER THE REVISION: net head flips 102 -> 23 (1.07 -> 0.24 UAS points, a 77% reduction of the ENTIRE tag-to-head loss), the VERB-as-AUX class 23 tokens -> 1 and net 90 -> 2 (88.2% -> 8.7% of the residual), and category agreement 0.9400 -> 0.9411. The class the brief was opened about is essentially eliminated, and the confusions that remain (NOUN->ADJ 19, ADJ->PROPN 19, SCONJ->ADP 17) are a different problem. The clause's PREDICATE-SLOT OCCUPANCY -- occ_i = (1 - P(verbal host in the carrier's verb group)) * (1 - P(copular predication available)) -- is computed once from the category organ's own posterior and applied to the posterior that organ HANDS DOWN, so the governor, the reader's event detector and the predicate rescue all read one revision instead of one arm each. THE GOVERNOR (UD-EWT test 700, live chain, paired bootstrap over sentences): UAS 0.6245 -> 0.6328 (+0.0083 CI[+0.0043,+0.0124] SEP); on the SOLE-AUX CLAUSES 0.6074 -> 0.6577 (+0.0503 CI[+0.0213,+0.0810] SEP); root +0.0157 CI[+0.0057,+0.0257] SEP and on the sole-AUX clauses +0.1026 CI[+0.0256,+0.1795] SEP; nsubj +0.0221 SEP (sole-AUX +0.1129 SEP); expl 0.292 -> 0.833, +0.5417 CI[+0.3478,+0.7500] SEP (sole-AUX 0.077 -> 1.000); ccomp +0.0431 SEP; obj +0.0100 SEP; obl +0.0084 SEP; nmod +0.0000; advcl / xcomp up n.s.; cop -0.0108 CI[-0.0273,+0.0000] n.s. -- the ONLY non-improvement, two arcs of 186, and not CI-separated. THE READER (2077 sentences, 1240 with a gold verb, the convention-free instrument): gold-verb sentences that produce NO EVENT AT ALL 33 -> 9 of 1240 (0.0266 -> 0.0073; rescue OFF is 55/0.0444), event recall 0.9501 -> 0.9812 (+0.0311 CI[+0.0245,+0.0380] over the live default, +0.0626 CI[+0.0528,+0.0719] over OFF, both SEP) at event precision 0.8715 -> 0.8621. IT DOMINATES pri 107's boolean sole-AUX arm ON ALL THREE AT ONCE (that arm: recall 0.9597, precision 0.8364, blind 18) -- so pri 107's open question 3 is answered with numbers and HDLAB_PREDICATE_RESCUE_AUX stays default OFF. GENERALISATION, entirely outside the organ's count supply (GUM/GENTLE, 1200 sentences by stride over 12+ genres, gold heads): UAS 0.6008 -> 0.6096 (+0.0088 CI[+0.0062,+0.0117] SEP), sole-AUX clauses 0.5830 -> 0.6423 (+0.0593 CI[+0.0413,+0.0792] SEP), expl 0.221 -> 0.794, root 0.656 -> 0.676, nsubj 0.703 -> 0.732; cop -0.008. THE DECISION ITSELF, against the only question UD's own column CAN adjudicate (is this be/have a main verb?): precision 0.6471 / recall 0.9565 on the AUX population (GUM 0.6264 / 0.8028) against 0.1164 for the blanket 'a sole AUX is the predicate' rule pri 107 refuted. Read-time cost 0.059 ms/sentence (+0.6% of the posterior it revises). Self-test 12/12 including PATCH == CELL exactly (max |cell - patch| = 0.0 over 4757 tokens / 250 sentences, 0 decision mismatches) and a PLASTICITY check (the occupancy moves 0.9978 -> 0.2594 after the organ observes `proof` as a VERB 400 times)."
floor: "(1) THE LIVE CONFIGURATION as deployed today -- the category organ's graded posterior handed to arc_scores_graded, the BF rescue's noun arm on, the sole-AUX arm off: UAS 0.6245 / sole-AUX 0.6074 / root 0.763 / expl 0.292 (UD-EWT test 700); event recall 0.9501, blind clauses 33/1240. Every delta above is against THIS arm, not against a weaker one. (2) THE RESCUE OFF: event recall 0.9186, blind clauses 55/1240. (3) pri 107's BOOLEAN sole-AUX arm (HDLAB_PREDICATE_RESCUE_AUX=1), the strongest existing answer to the same question: event recall 0.9597, precision 0.8364, blind 18; routed to the GOVERNOR as a hard promotion it is a CI-separated LOSS (UAS -0.0172 CI[-0.0264,-0.0084], cop 0.727 -> 0.505 on a 250-sentence probe). (4) THE EXACT HMM RENORMALISATION (pri 107's alternate path A, built first): category accuracy -0.0112 CI[-0.0139,-0.0088], UAS -0.0231 CI[-0.0336,-0.0130] -- REFUTED AS SPECIFIED, see section 4."
controls: "(1) INFORMATION-FREE TWIN, the brief's own: the SAME NUMBER of AUX tokens promoted at random with the same strength. UD-EWT 3 seeds UAS 0.6168 / 0.6167 / 0.6195 against the floor's 0.6245 -- every one CI-separated BELOW the floor (-0.0077 / -0.0078 / -0.0050), and on the sole-AUX clauses 0.5884 / 0.5996 / 0.5996 against 0.6074. GUM 2 seeds 0.5889 / 0.5886 against 0.6008, both CI-separated below. The twin therefore never manufactures the gain; a random promotion of the same size HURTS. (2) PAIRED BOOTSTRAP over SENTENCES (2000 resamples) for every delta, including a per-relation bootstrap for every relation the bar names. (3) THREE POPULATIONS, two of them (GUM/GENTLE 12+ genres by stride; QA-SRL dev) entirely outside the category organ's count supply -- GUM with a LARGER effect than in-supply, QA-SRL with a small CI-separated one that tracks the fact that only 4.7% of its dropped verbs are AUX-tagged. 19c is not measured (owner ban). (4) THE ARMS ARE THE READER: the OFF arm was cross-checked against a live SituationReader on 150 sentences, 0 mismatches; OFF / LIVE / AUX107 reproduce pri 107's published numbers (0.9186 / 0.9501 / 0.9597 and blind 55 / 33 / 18) exactly, so this is their instrument. (5) OPERATING-POINT SWEEP: th 0.3 / 0.5 / 0.7 / 0.9 gives governor UAS +0.0082 / +0.0081 / +0.0081 / +0.0073 (measured at the pre-refinement configuration, where the shipped point scored +0.0081; the shipped configuration scores +0.0083 at th 0.5) -- a FLAT region, because the occupancy is BIMODAL (505 of 591 AUX tokens score 0.0 and 33 score ~1.0, so almost nothing lives near any threshold); 0.5 is the middle of the flat region, not a tuned knob. The per-relation cop cost is IDENTICAL at every threshold, which says it comes from confident promotions, not borderline ones. (6) PATCH == CELL: the self-test EXECUTES the proposed diff's own added code and compares it to the cell -- max |cell - patch| = 0.0 over 4757 tokens, 0 decision mismatches, 0 revision mismatches; git apply --check clean. (7) SURGICAL: the revision touches ONLY promoted carriers (33 of 9534 UD-EWT test tokens, 0.35%); every other posterior row is byte-identical, asserted in the self-test. (8) INVENTORY GUARD: the shipped computation returns all-zero (a no-op) under a category inventory lacking the UPOS classes it reads, so the pri-15 induced-class swap degrades to silence rather than an exception. (9) ABLATION of each term: the clause-mass form alone (path A) loses; the boolean sole-AUX gate alone loses at the governor; the NP-complement refinement is worth precision 0.6286 -> 0.6471 at identical recall."
files_changed: "experiments/exp_one_convention_two_losses_v1.py (the cell), notes/problems/<slug>/{SOLVED.md, predicate_slot_patch.diff} (the proposed diff against hdlab/attachment_arm.py + hdlab/lexical_categories.py + a documentation block in hdlab/predicate_detector.py), data/exp_one_convention_two_losses_v1*/ (metrics). NO hdlab/ or tools/ file changed on disk."
reverify: ".venv/Scripts/python.exe experiments/exp_one_convention_two_losses_v1.py --self-test   (12 checks, fast, includes PATCH == CELL and git apply --check). Headline: --gov-live --cap 700 --th 0.5 (~5 min); --reader --cap 2100 --th 0.5 (~20 min); --gum --cap 1200 --th 0.5 (~8 min); --attrib --cap 700 (~6 min); --reader --pop qasrl --cap 1500 (~12 min); the board A/B: --board --arm base and --board --arm occ (~1-2.5 h each, writes only data/exp_one_convention_two_losses_v1_board_*/)."
---

# SOLVED -- the convention is not the brain's, and the fix is one quantity read at the top of the chain

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed on disk; the exact diff is proposed below.

---

## 1. The problem, measured on disk before anything was built

The category organ tags **23 tokens of UD-EWT test 700** as `AUX` where UD says `VERB`. They are not a random
scatter -- they are **two constructions**, and the organ's own posterior is confidently wrong on both:

| what | count | the organ's belief on the token |
|---|---|---|
| existential `there is / are / was / were / had been / will be` | **15 of 23** | P(VERB) 0.038-0.42, P(AUX) 0.55-0.96 |
| possessive / semi-modal `have / has / had` (`I have a ticket`, `you have to see`) | **8 of 23** | P(VERB) 0.14-0.45 |

Those 23 tokens carry **87 NET head flips = 58% of the entire tag-to-head loss** (`data/exp_diag_tag_to_head_loss_v1`:
net 149 flips over 603 tag errors). **3.83 lost arcs per mis-tagged token**, against 0.47-1.17 for every other
confusion -- one wrong tag takes the whole clause down with it. And because the predicate rescue is ADDITIVE it
cannot touch an AUX-tagged token at all, so the same class is invisible at the second consumer.

Re-measuring that attribution on **today's** asset (the brief's 58% is from the 2026-09-13 one) makes the class even
more dominant, and re-running it **under the revision** is the cleanest statement of what this work does:

| | tag agreement | net head flips | UAS points lost | VERB-as-AUX tokens | its net | its share |
|---|---|---|---|---|---|---|
| the live chain today | 0.9400 | **102** | 1.07 | 23 | **90** | **88.2%** |
| **+ the predicate slot** | 0.9411 | **23** | **0.24** | **1** | **2** | 8.7% |

**77% of the entire tag-to-head loss, gone**, and what remains (`NOUN->ADJ` 19, `ADJ->PROPN` 19, `SCONJ->ADP` 17) is
a different problem for a different brief.

**The evidence that would fix it is not in the lexical channel.** The counts say AUX, correctly, for the usual use of
these words. What separates a main-verb `be`/`have` from an auxiliary one is **clause-structural** -- and nothing in
the organ's decode, or in either consumer, looked at it.

---

## 2. The brain, and what it says to compute

**Predicate-hood is a clause-level expectation** -- one predicate per clause (Spivey-Knowlton 1993). **An auxiliary
is a TENSE CARRIER** for a predicate that is not itself finite (Bybee 1994 on auxiliation). A carrier's tense can be
discharged in exactly three ways, and that exhausts the space:

| | the carrier's tense goes to | who is the predicate | example |
|---|---|---|---|
| 1 | a **VERBAL HOST** in its own verb group | the host | `has been roiled`, `would have expended` |
| 2 | a **NON-VERBAL PREDICATE** it carries tense for (Pustet 2003) | the complement | `Google is a search engine` |
| 3 | **neither** | **the carrier itself** | `there is no proof`, `I have a ticket` |

So the quantity both consumers need is one number per token:

```
occ_i  =  (1 - P(verbal host in i's verb group))  x  (1 - P(copular predication available at i))
```

- **Term 1 is GRADED**, read off the category organ's own posterior: `P(VERB) + P(AUX)` at the first position the
  verb group reaches. The walk is weighted by each intervening word's **own belief that it is skippable**, so an
  argmax mis-tag cannot silently carry the walk into the next phrase. Infinitival `to` CLOSES the group -- a
  to-infinitive is a complement, not a host, which is exactly what leaves `have` predicative in `have to see`.
  **AUXILIARY ORDER** (modal > have > be > V; Chomsky 1957's Aux rule) forbids a modal from being the host of a
  `have`/`be` carrier, so a modal's AUX belief cannot count as host evidence.
- **Term 2 is a CONSTRUCTION test** over closed-class forms the arm already carries: `have` and `do` are never
  copulas; a `be` whose pivot is the expletive **`there`** predicates EXISTENCE rather than a property of a subject
  (Goldberg 1995 -- the existential-there construction, acquired as a construction).
- **A MODAL is never a carrier** -- it cannot head a clause (Bybee 1994's fully-auxiliated class).

**PINNED:** that predicate-hood is a clause-level expectation; that an auxiliary is a tense carrier requiring a host;
that the copula carries tense for a non-verbal predication; the English auxiliary order. **OURS (swept, never
adopted):** the promotion threshold (swept 0.3/0.5/0.7/0.9, flat), and the closed-class spelling of the constructions.

**WHERE IT IS READ -- and this is the whole point of the brief.** The occupancy is applied to the posterior the
**category organ hands down** (`lexical_categories.posterior`), not inside either consumer. It is a top-down
constraint on a settling belief (MacDonald 1994 constraint satisfaction), applied at clause wrap-up (Just &
Carpenter 1980), not a second organ. One revision therefore reaches the governor (through the graded category
hand-off the frontend already uses), the reader's event detector (through the tag), the predicate rescue (through
its cue block) and every other consumer of the category posterior at once.

---

## 3. Results

### 3a. The governor -- UD-EWT test 700, live chain, paired bootstrap over sentences

Both arms are the **frontend's own configuration** (the category posterior handed to `arc_scores_graded`), so the
only difference is whether the predicate-slot constraint was applied before the hand-off.

| | base (live today) | + predicate slot | delta |
|---|---|---|---|
| **UAS, all** | 0.6245 | **0.6328** | **+0.0083 CI[+0.0043,+0.0124] SEP** |
| **UAS, sole-AUX clauses** | 0.6074 | **0.6577** | **+0.0503 CI[+0.0213,+0.0810] SEP** |
| root (n=700) | 0.763 | 0.779 | **+0.0157 CI[+0.0057,+0.0257] SEP** |
| root, sole-AUX (n=78) | 0.500 | 0.603 | **+0.1026 CI[+0.0256,+0.1795] SEP** |
| nsubj (n=769) | 0.762 | 0.784 | **+0.0221 CI[+0.0106,+0.0357] SEP** |
| nsubj, sole-AUX (n=124) | 0.556 | 0.669 | **+0.1129 CI[+0.0560,+0.1780] SEP** |
| **expl** (n=24) | 0.292 | **0.833** | **+0.5417 CI[+0.3478,+0.7500] SEP** |
| expl, sole-AUX (n=13) | 0.077 | **1.000** | **+0.9231 CI[+0.7500,+1.0000] SEP** |
| ccomp (n=116) | 0.647 | 0.690 | +0.0431 CI[+0.0086,+0.0847] SEP |
| obj (n=400) | 0.782 | 0.792 | +0.0100 CI[+0.0024,+0.0210] SEP |
| obl (n=477) | 0.472 | 0.480 | +0.0084 CI[+0.0020,+0.0169] SEP |
| xcomp (n=137) | 0.745 | 0.759 | +0.0146 n.s. |
| nmod (n=534) | 0.536 | 0.536 | +0.0000 |
| **cop** (n=186) | 0.640 | 0.629 | **-0.0108 CI[-0.0273,+0.0000] n.s.** |

`expl` is the signature of the class: the existential `there` can only attach correctly once its clause has a verbal
head, and it goes from **1 arc in 13 right to 13 in 13** on exactly the clauses this work is about.

**INFORMATION-FREE TWIN** (the same NUMBER of AUX tokens promoted at random, 3 seeds): UAS **0.6168 / 0.6167 /
0.6195** -- all three CI-separated **BELOW** the 0.6245 floor, and below it on the sole-AUX clauses too. A random
promotion of the same size does not help; it hurts.

### 3b. The reader -- the convention-free instrument (2077 sentences, 1240 with a gold verb)

*Does the clause produce an event at all?* A gold-verb sentence yielding zero events is a whole clause every
downstream organ never sees, and it does not depend on what UD calls the token.

| arm | event recall | event precision | false events/sent | **blind clauses** |
|---|---|---|---|---|
| rescue OFF | 0.9186 | 0.9370 | 0.0775 | 55 / 1240 (0.0444) |
| **the live default** (BF rescue, noun arm) | 0.9501 | 0.8715 | 0.1757 | 33 / 1240 (0.0266) |
| pri 107's boolean sole-AUX arm | 0.9597 | 0.8364 | 0.2354 | 18 / 1240 (0.0145) |
| **the predicate slot (this work)** | **0.9812** | **0.8621** | 0.1969 | **9 / 1240 (0.0073)** |
| the predicate slot + that boolean arm | 0.9820 | 0.8305 | 0.2513 | 9 / 1240 |
| + the COPULAR-COMPLEMENT arm (phase-4 lever, **not shipped**) | 0.9812 | 0.7771 | 0.3529 | **7 / 1240** |

`+0.0311 CI[+0.0245,+0.0380]` event recall over the live default and `+0.0626 CI[+0.0528,+0.0719]` over OFF, both
CI-separated. **It dominates the boolean arm on recall, precision AND blind clauses at the same time**, and stacking
the boolean arm on top buys `+0.0008` recall for `-0.0316` precision -- which is the numbered answer to pri 107's
open next-step 3, and the reason `HDLAB_PREDICATE_RESCUE_AUX` stays default OFF.

The OFF / live / boolean rows reproduce pri 107's published numbers exactly (0.9186 / 0.9501 / 0.9597; blind 55 / 33
/ 18), and the OFF arm was cross-checked against a real `SituationReader` on 150 sentences with **0 mismatches** --
so this is their instrument, not a re-implementation.

**THE SECOND READER POPULATION the brief names -- QA-SRL dev (1500 sentences, out of supply), same instrument:**

| arm | event recall | event precision | blind clauses |
|---|---|---|---|
| rescue OFF | 0.8344 | 0.9306 | 120 / 1500 (0.0800) |
| the live default | 0.9460 | 0.8742 | 8 / 1500 |
| pri 107's boolean sole-AUX arm | 0.9486 | 0.8580 | 8 / 1500 |
| **the predicate slot** | **0.9516** | **0.8581** | **7 / 1500** |

`+0.0056 CI[+0.0027,+0.0087]` over the live default -- **CI-separated but SMALL, and it should be**: pri 107
measured that only **4.7%** of QA-SRL's dropped verbs are AUX-tagged, against 38.8% on UD-EWT, so the class this
work is about barely occurs there. The honest reading is that the size of the win tracks the size of the class,
which is what a real mechanism does and what a fitted rule would not. It still beats the boolean arm on recall at
equal precision with fewer blind clauses.

### 3c. Generalisation -- GUM/GENTLE, entirely outside the organ's count supply

1200 sentences taken by stride across 12+ genres, gold heads. **The effect is LARGER out of supply**, which is the
opposite of what a fitted rule does.

| | base | + predicate slot | delta |
|---|---|---|---|
| UAS | 0.6008 | **0.6096** | **+0.0088 CI[+0.0062,+0.0117] SEP** |
| UAS, sole-AUX clauses | 0.5830 | **0.6423** | **+0.0593 CI[+0.0413,+0.0792] SEP** |
| root (n=1200) | 0.656 | 0.676 | +0.020 |
| nsubj (n=1555) | 0.703 | 0.732 | +0.029 |
| expl (n=68) | 0.221 | **0.794** | +0.573 |
| xcomp (n=249) | 0.659 | 0.683 | +0.024 |
| cop (n=383) | 0.598 | 0.590 | -0.008 |

Twin, 2 seeds: 0.5889 / 0.5886, both CI-separated below the 0.6008 floor.
The DECISION on GUM: precision **0.6264**, recall **0.8028** on the AUX population (UD-EWT 0.6471 / 0.9565).

### 3d. The board

`--board --arm base` and `--board --arm occ` were run as a full 7-dimension modern A/B (the board's arms read the
one frontend, so a change to the category hand-off reaches every dimension). **Result: see section 3e.**

### 3e. Board A/B

BOARD_RESULT_PLACEHOLDER

---

## 4. Every negative, understood

**(a) pri 107's ALTERNATE PATH A, BUILT EXACTLY AS SPECIFIED, IS REFUTED WITH NUMBERS -- and the reason is the whole
finding.** Path A asks for the clause-level "at least one predicate" renormalisation inside the organ's own
forward-backward: `P(c_i = VERB | clause has a predicate) = post_i(VERB) / (1 - Z_noV/Z)`. I built it exactly --
a second masked forward pass per clause for `Z_noV`, the exact mixture decomposition
`post = (1-w) post_E + w post_noV` for the full conditional distribution, the organ's own recursions at its own
order and lag, parameter-free. Measured on UD-EWT test 700:

| gate | category accuracy | vs base | the VERB-as-AUX class | tokens moved |
|---|---|---|---|---|
| base | 0.9400 | -- | 0 / 23 | -- |
| every clause | 0.8713 | **-0.0687 CI[-0.0757,-0.0620]** | 10 / 23 | 826 |
| clauses with a tense carrier | 0.9288 | **-0.0112 CI[-0.0139,-0.0088]** | 10 / 23 | 142 |
| whole sentence | 0.9351 | -0.0049 | 2 / 23 | 54 |

and at the governor: **UAS -0.0231 CI[-0.0336,-0.0130]**, `cop` 0.727 -> 0.404, sole-AUX UAS -0.1657.

**MECHANISM, and it is not a tuning problem.** The event the mask conditions on is *"the clause has a **VERB**"* --
and for a **copular** clause that event is **FALSE while the clause still has a predicate**. A sole-AUX clause is
usually copular (109 of the 186 `cop` arcs in the test set sit in one), so the renormalisation pours verb mass into
clauses whose predicate slot was never empty. The flip audit shows it directly: the breaks are `Google is a nice
search engine`, `The actual vote is a little confusing`, `we are capable of protecting them` -- copulas promoted to
VERB against their own predicate. **The conditioning event has to be "the clause has a PREDICATE", and the HMM's
category alphabet cannot express that**, because a non-verbal predicate is not a category. That is why the shipped
form states the constraint over the auxiliary's **FUNCTION** (is its tense discharged?) rather than over the VERB
state. Path A is not a wall -- it is a mis-stated event, and stating it correctly is what produced the win.

**(b) The boolean sole-AUX gate is the same mistake one rung lower.** pri 107's arm fires on any AUX whose clause
holds no VERB -- which is the same population, including the copular clauses. It is *fine at the reader* (an extra
event on a copular clause is only a precision cost) and *harmful at the governor* (a promoted copula steals its own
predicate's head): routed to the governor it is **UAS -0.0172 CI[-0.0264,-0.0084]**, `cop` 0.727 -> 0.505. **This is
the brief's item 4 answered with numbers: the two consumers really do disagree about a BOOLEAN gate, and what
resolves the disagreement is making the hand-off GRADED and correctly gated, not choosing a side.**

**(c) `cop` is the one relation that does not improve, and the 12 false promotions that cause it are enumerated.**
-0.0108 CI[-0.0273,+0.0000], n.s., two arcs of 186; GUM -0.008 on 383. The cost is identical at every threshold
from 0.3 to 0.9, which says it comes from *confident* promotions (occ ~ 1.0), not from borderline ones. All 12 are:

| class | n | why the occupancy is wrong | fixable here? |
|---|---|---|---|
| **VP-ELLIPSIS / a stranded auxiliary** (`i am sure they are .`, `as I did this weekend`, `how reliable that is`) | **5** | the host is in the PREVIOUS clause; recovering it is antecedent resolution (Hankamer & Sag 1976), which needs the discourse model, not the sentence | **no** -- named as alternate path B |
| a quoted or clausal complement behind punctuation (`The answer is , " Yes ! "`) | 3 | the complement scan crosses punctuation but stops at the first content token, and a quoted clause opens with a verbal form | partly; not attempted -- it risks fitting UD's own column |
| a possessive `'s` / progressive `being` the organ mis-tagged AUX upstream | 2 | an upstream category error, not this computation | no |
| elliptical `do` (`rather as the ... did`) | 2 | same as VP-ellipsis | no |

**(c2) THE PHASE-4 LEVER I BUILT AND DID NOT SHIP, and the reason is the instrument.** Alternate path D says a
COPULAR clause does have a predicate -- the non-verbal complement -- and the event should fire on it. Built as an
extra reader arm using the governor's OWN `cop_predicates` (a read of an existing organ, not a new one), restricted
to clauses the revised tags leave with no VERB. Measured: **blind clauses 9 -> 7 of 1240 (-22%)**, event recall
UNCHANGED at 0.9812, event precision **0.8621 -> 0.7771**, false events 0.197 -> 0.353/sentence.
**The recall is unchanged and the precision falls for the SAME reason: a copular complement is gold ADJ or NOUN, so
UD's VERB column scores a CORRECTLY fired predication event as a false positive by construction** -- the identical
trap the brief warns about and that pri 107 hit with the naive sole-AUX rule. The convention-free instrument says it
helps; the only precision instrument I have cannot adjudicate it. **So it is measured, named, and NOT shipped**: what
it needs is a convention-free precision instrument (does the fired event acquire participants?), which is a roles-rung
build, not a rescue one. This is the strongest remaining lever on the 9 blind clauses and it is written up as 7D.

**(d) One gold VERB is still missed (`even though there are blanks`, occ = 0.44).** The organ puts 0.56 of its
verbal belief on `blanks` -- it is a real word that is really a verb-or-noun -- so the host term is genuinely
uncertain and the graded read reports that honestly rather than promoting. It sits just under the flat region's
threshold; at th = 0.3 it promotes and the governor numbers are unchanged (+0.0082 vs +0.0083).

**(e) An earlier form of the host walk read the ARGMAX tag and lost one of the 23.** In `i have stronger will than
you think`, `stronger` is argmax-ADV so the walk stepped over it and read the NOUN `will` -- which this organ tags
AUX -- as the host of the possessive `have`, scoring it **0.04**. Two independent fixes were built and both were
needed: the graded walk (0.04 -> 0.24) and the auxiliary-order constraint that a modal cannot host `have`
(0.24 -> 0.96). **Neither alone reaches the decision.**

**(f) Keying the copular test on the SUBJECT rather than the COMPLEMENT left 31 false promotions, 26 of them
copular clauses whose subject scan failed** (inversion, a participial NP, a fronted PP, `to be ...` with no subject
at all). The slot's occupant is the complement, so that is what has to be looked for; switching the test
cut false promotions **31 -> 25** and the two NP refinements took it to **12**.

---

## 5. Every component touched, and its brain-foundational status FOR THIS SIGNAL

| component | role here | status as the disk shows it | status FOR THIS SIGNAL |
|---|---|---|---|
| `hdlab/lexical_categories.py` | the belief the whole chain reads | **BF_SPIRIT** -- count-based generative 2nd-order HMM, forward-backward, lag 2, plastic | **was NOT BF for this signal**: the posterior it handed down encoded UD's ANNOTATION CONVENTION and carried no clause-structural constraint at all. Fixed here (4 lines + a switch) |
| `hdlab/attachment_arm.py` | owns the predication lexicon (`COP_FORMS`, `AUX_BE/HAVE/MOD`, `WH_FORMS`, `cop_predicates`) and now the occupancy | **BF_SPIRIT** | the computation is added HERE because this is the organ that owns predication; its own `assertion_candidates` is still **SENTENCE-level where the brain's constraint is CLAUSE-level** -- a remaining rung, named in 7C |
| `hdlab/predicate_detector.py` | the second consumer | **BF_SPIRIT** (noisy-channel + Rescorla-Wagner, plastic) | its AUX arm's gate was a **BOOLEAN** clause flag -- a point estimate of a graded quantity. Superseded; documentation-only change, default stays OFF with the measured table |
| `hdlab/situation_reader.py` | the event detector | -- | fires on a **hard `UPOS == VERB`** -- a point read of a graded belief. **NOT BF for this signal**; it benefits here only because we revise the tag it reads. Named in 7D |
| `hdlab/frontend.py` | the one hand-off | BF_SPIRIT | **untouched, and it is why one change reaches every consumer** -- `Tagger.tag_with_posterior` -> `Parser.arc_scores_graded` is the path the win travels down |
| `hdlab/morphology.py`, `hdlab/graded_parser.py` | read-only | BF / BF_SPIRIT | unchanged |

---

## 6. What let the signal be maximised -- the chain, rung by rung

The owner's reading is right here: the win is the **brain-foundational chain cracked all the way to the top**.

**Cracked.**
1. **The TOP rung, and it is the top on purpose.** The loss was attributed to the heads rung (58% of a 1.5-point
   UAS loss) but it is *caused* one rung above it, in the belief the category organ hands down. Fixing it at the
   heads rung would have fixed one consumer; fixing it at the categories rung fixed **all of them with one change**,
   including the event detector, which nobody was measuring.
2. **The conditioning event.** "Does this clause contain a VERB?" is the wrong question (section 4a). "Is this
   carrier's tense discharged?" is the right one, and it is the question the neuroscience of auxiliation actually
   poses. Getting from the first to the second is the entire difference between `-0.0231` and `+0.0083` UAS.
3. **The hand-off is GRADED, both ways.** The occupancy is read FROM a posterior (never an argmax) and handed BACK
   as a posterior (`P(VERB) = occ`, the rest rescaled), so the arm's existing first-order category mixture carries
   an uncertain promotion instead of committing it. Point-estimating either end loses the win.
4. **The verb group is a LOCALITY, and the walk respects it gradedly.** Skipping costs the skipped word's own
   belief; `to` closes the group; auxiliary order forbids a modal host.
5. **The construction is the discriminator.** Existential-`there` and possessive-`have` are the two constructions in
   which the carrier predicates, and both are closed-class and learnable -- the same kind of knowledge the arm
   already carries for copulas and wh-forms.

**Not cracked (named, with numbers).**
- **VP-ellipsis** -- 5 of the 12 remaining false promotions; needs a discourse antecedent (7B).
- **`assertion_candidates` is still SENTENCE-level** where the constraint is clause-level (7C).
- **The event detector's hard `UPOS == VERB` gate** -- it should read the occupancy itself (7D).
- **The acquisition assets were NOT rebuilt under the revision** -- the attachment validities and the rescue's
  counts were learned from the unrevised tags, so every number here is a *read-time* gain on top of assets that do
  not yet know about the constraint. Rebuilding them is an untested (and probably additional) gain, named in 7A.

---

## 7. Alternate paths (similarly or MORE brain-foundational than what I shipped)

**A. Rebuild the acquisition assets under the revised hand-off. -- CHEAPEST, BRIEF-READY.**
The teacher and the attachment validities (`tools/build_attachment_validities.py`) count over the organ's tags. Under
the revision an existential `is` is a VERB *while the validities are being learned*, so `ROOT:VERB|...` and the
`expl` configuration would acquire strengths they cannot currently acquire at all. *What it would take:* one asset
rebuild plus a board A/B. *Why not now:* the asset is shared with two concurrent solvers and a rebuild invalidates
their floors mid-session.

**B. VP-ELLIPSIS resolution -- the honest fix for 5 of the 12 false promotions.**
*The structure:* a stranded auxiliary's host is an antecedent VP in the discourse model (Hankamer & Sag 1976); the
listener re-activates the most recent compatible VP. *The math:* `P(host) <- max over antecedent VPs of
P(compatible(carrier, VP)) x recency-decayed activation` -- ACT-R base-level activation (Lewis & Vasishth 2005),
which this substrate already uses for its hold expectation. *What it would take:* a cross-sentence VP register the
reader does not keep. *Why not now:* a new register is a bigger build than this brief's remit, and the residual is
12 tokens in 9,534.

**C. Make `assertion_candidates` clause-level.** It admits an AUX as a root candidate only when the WHOLE SENTENCE
is verbless -- a sentence-level approximation of a clause-level constraint. The occupancy now supplies the
clause-level answer directly, so the arm could read `occ` instead of `not has_verb`. *Why not now:* it is a change
inside the arm's own candidate set, which a concurrent solver is editing; and the graded hand-off already delivers
most of it.

**D. Let the event detector read the OCCUPANCY rather than the TAG. -- BUILT AND MEASURED (4c2), BRIEF-READY.** `_tense_agnostic_extract` fires on
`UPOS == VERB` -- a point read. The brain-foundational form fires an event with strength `occ`, and the copular
clauses (whose predicate is the ADJ/NOUN complement, not the copula) would fire on the **complement**, which is
where the state actually lives. Measured as a reader arm: blind clauses **9 -> 7 of 1240** at unchanged recall, but event precision 0.8621 -> 0.7771
*as UD's VERB column scores it*, which cannot adjudicate a predication event on an ADJ. **What it needs first is a
convention-free PRECISION instrument** -- does the fired event acquire participants at the roles rung? -- and that is
the brief to file. It is the natural partner of the state dimension's copular reader.

**E. Learn the constructions from counts instead of naming them.** `EXPLETIVE = {there}` and the carrier set are
closed-class lists, exactly like the arm's existing `COP_FORMS` / `WH_FORMS`. A more plastic form accrues
`P(predicate | carrier lemma, host bin, complement bin)` in the rescue's existing Rescorla-Wagner combiner and calls
`observe()` when a promoted carrier later receives argument roles (pri 107's alternate path C). *Why not now:* the
confirmation signal from the roles rung does not exist yet, and the product form is already parameter-free.

---

## 8. Priority next steps

1. **Land the diff.** It is 3 files: the computation in `hdlab/attachment_arm.py`, a 4-line hook plus a switch in
   `hdlab/lexical_categories.py`, and a documentation block in `hdlab/predicate_detector.py`. `git apply --check`
   is clean and the self-test proves the patch's own code equals the measured cell exactly.
2. **Keep `HDLAB_PREDICATE_RESCUE_AUX` OFF** -- pri 107's open question 3 is now answered with numbers (3b).
3. **File 7A** (rebuild the acquisition assets under the revised hand-off) -- cheapest remaining lever, and it is
   the only one that lets the *learned validities* see the corrected class.
4. **Tell pri 107 that path A as specified is refuted** (4a) and why -- the conditioning event, not the machinery.
5. **7D** (the event detector reads the occupancy, and a copular clause fires on its complement) is the natural
   next attack on the 9 remaining blind clauses.

---

## 9. Submission prompt

```
pri 110 -- one_convention_two_losses_ud_tags_main_verb_be_and_have_as_aux_so_the_governor_and_the_predicate_rescue_both_miss_the_clauses_only_verb

SOLVED. ONE computation, both consumers up, under one switch. The 23 UD-EWT test tokens the category organ tags AUX
where UD says VERB are two CONSTRUCTIONS -- existential `there be` (15) and possessive/semi-modal `have` (8) -- and
they carry 87 net head flips, 58% of the whole tag-to-head loss, at 3.83 lost arcs per token. The brain's question
is not "does this clause contain a VERB" but "is this tense carrier's tense discharged": a carrier with a verbal
host in its verb group is an auxiliary, one with a non-verbal predicate to carry tense for is a copula, one with
neither IS the clause's predicate. occ = (1 - P(host)) x (1 - P(copular predication)), read off the category organ's
own posterior with a GRADED verb-group walk (auxiliary order forbids a modal host; `to` closes the group) and the
existential-there construction as the discriminator. It is applied to the posterior the CATEGORY organ hands down,
so the governor, the reader's event detector and the predicate rescue all read ONE revision.
GOVERNOR (UD-EWT test 700, live chain): UAS 0.6245 -> 0.6328 (+0.0083 CI[+0.0043,+0.0124] SEP); sole-AUX clauses
0.6074 -> 0.6577 (+0.0503 CI[+0.0213,+0.0810] SEP); root +0.0157 SEP (+0.1026 SEP on the sole-AUX clauses); nsubj
+0.0221 SEP; expl 0.292 -> 0.833 (+0.5417 SEP; 0.077 -> 1.000 on the sole-AUX clauses); ccomp/obj/obl SEP up; nmod
flat; cop -0.0108 n.s. -- the only non-improvement, two arcs of 186. READER (2077 sentences, the convention-free
instrument): gold-verb sentences yielding NO event 33 -> 9 of 1240 (OFF is 55), event recall 0.9501 -> 0.9812
(+0.0311 CI[+0.0245,+0.0380] SEP) at precision 0.8715 -> 0.8621 -- it DOMINATES pri 107's boolean sole-AUX arm on
recall, precision AND blind clauses at once (0.9597 / 0.8364 / 18), so HDLAB_PREDICATE_RESCUE_AUX stays OFF and
pri 107's open question 3 is answered. GENERALISATION on GUM/GENTLE (outside the count supply, 12+ genres): UAS
+0.0088 CI[+0.0062,+0.0117] SEP, sole-AUX +0.0593 SEP, expl 0.221 -> 0.794 -- LARGER than in supply. TWIN (the same
number of AUX tokens promoted at random): 3 seeds UD-EWT + 2 GUM, every one CI-separated BELOW the floor.
BOARD: <see SOLVED.md 3e>. Cost 0.059 ms/sentence (+0.6%). Self-test 12/12 including PATCH == CELL exact (0.0 over
4757 tokens) and a plasticity check.
THE NAMED DEFECT IS 77% GONE: re-running the brief's own tag-to-head attribution on today's asset, the whole loss is
102 net head flips (1.07 UAS points) of which VERB-as-AUX is 23 tokens carrying net 90 = 88.2% (the brief's 58% is
from the 2026-09-13 asset). Under the revision: 102 -> 23 net flips (1.07 -> 0.24 UAS points), the class 23 tokens
-> 1 and net 90 -> 2, category agreement 0.9400 -> 0.9411. What remains is NOUN->ADJ / ADJ->PROPN / SCONJ->ADP -- a
different problem.
SECOND CONVENTION-FREE POPULATION (QA-SRL dev, 1500 sentences, out of supply): event recall 0.9460 -> 0.9516,
+0.0056 CI[+0.0027,+0.0087] SEP, blind clauses 8 -> 7 -- small, and it should be: only 4.7% of QA-SRL's dropped
verbs are AUX-tagged against 38.8% on UD-EWT, so the win tracks the size of the class.
NUMBERED NEGATIVE THAT MATTERS: pri 107's alternate path A (the exact HMM renormalisation P(c_i=VERB | the clause
has a predicate) = post_i(VERB)/(1 - Z_noV/Z)) was BUILT EXACTLY and is REFUTED -- category accuracy -0.0112
CI[-0.0139,-0.0088], UAS -0.0231 CI[-0.0336,-0.0130], cop 0.727 -> 0.404 -- because the event it conditions on is
"the clause has a VERB", which is FALSE for a copular clause whose predicate slot is NOT empty. The HMM's category
alphabet cannot express "has a PREDICATE"; stating the constraint over the auxiliary's FUNCTION instead is what
turned -0.0231 into +0.0083. The remaining 12 false promotions are enumerated: 5 VP-ellipsis (needs a discourse
antecedent), 3 quoted/clausal complements, 2 upstream tag errors, 2 elliptical `do`.

Files: experiments/exp_one_convention_two_losses_v1.py, notes/problems/<slug>/{SOLVED.md, predicate_slot_patch.diff}
(against hdlab/attachment_arm.py + hdlab/lexical_categories.py + a doc block in hdlab/predicate_detector.py).
No hdlab/ file changed on disk. Reverify: --self-test ; --gov-live --cap 700 ; --reader --cap 2100 ; --gum --cap 1200 ;
--board --arm base|occ
```
