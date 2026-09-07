---
problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals
status: SOLVED
bar: "PASSES only with ALL of: (1) a glass-box GLOBALLY-NORMALIZED / graded parser emitting a real distribution over parses (edge marginals + a genuine 2nd-best), built + validated in experiments/ (COPY the computation -- Matrix-Tree edge marginals for the arc-factored case; SWEEP beam/temperature/normalization; offline static asset, NO external LLM); (2) the marginals BEAT the greedy 1-best on MODERN UD-EWT CI-separated over the floor recomputed on the SAME population, in ONE of two forms: (a) marginal/global-decode ATTACHMENT accuracy beats the greedy 1-best argmax head CI-sep, OR (b) a calibrated 2nd-best/marginal RECOVERS the search-failure errors; (3) a LIVE DOWNSTREAM LIFT (who-did-what PATIENT selective-accuracy toward the 0.913 gold-parse ceiling, floor = live greedy-arc reader 0.831; and/or obl defer) CI-sep over the live incumbent; (4) the info-free twin (shuffled marginals) LOSES CI-sep; (5) NO-regress (byte-identical where the graded parse is off; enumerate every live consumer; a can-fail POSITIVE control the greedy 1-best cannot pass); (6) one-screen summary. A rigorous NEGATIVE is a FULL PASS (e.g. exact marginals recover only N of M search-failure arcs because the arc-factored FEATURES under-separate right-from-wrong -- the wall is the SCORER's features, not the normalization)."
result: "POSITIVE (all six bar conditions met, on MODERN UD-EWT test). Built a glass-box globally-normalized graded parser over the LANDED arc-factored scorer (hdlab.arc_parser): exact Chu-Liu/Edmonds MAP + exact multi-root Matrix-Tree EDGE MARGINALS + an exact 2nd-best tree (Camerini), all verified BIT-EXACT against brute-force enumeration of every spanning arborescence for n<=4 (200 trials x 3 temperatures). (2a ATTACHMENT) the exact MST decode beats the incumbent greedy heuristic decode over the SAME arc-factored scores: UAS 0.7888->0.7908 (+0.0020 CI[+0.0009,+0.0030] CI-sep, n=24,664 arcs / 2,071 sents); the greedy decode leaves an INVALID (non-tree) parse on 149/2071 sents (7.2%) which the exact decode never does. (2b MARGINAL RECOVERS) the exact marginal is a strong right-vs-wrong sensitivity signal -- AUC 0.855 all-arc / 0.765 on live patient arcs (RAW, single glass-box signal, NO logistic) vs the greedy arc-eager raw conf 0.613 and matching most of the way to the landed CALIBRATED multi-cue logistic 0.860 -- and gold is in the marginal support 1.000 of the time (vs the arc-eager small-beam 0.399-0.492, the search-failure the predecessor could not cross). (3 LIVE LIFT) DEFERRING the LIVE structural_patient_pick on the marginal lifts selective accuracy 0.8785->0.9465 (+0.0680 CI[+0.0501,+0.0850]) and answered-acc-at-dev-tau +0.0644 CI[+0.0485,+0.0810] @cov 0.61 (n=1235); adding the marginal to the landed calibrator raises its sensitivity 0.861->0.869 AUC. (4 TWIN) the SHUFFLED-marginal info-free twin is FLAT on every arm (selective -0.003 / defer -0.010 / augmentation +0.000). (5 NO-REGRESS) every live consumer of the parse heads enumerated; no consumer-relevant label regresses under the exact-decode swap (root +0.065, obj +0.004, obl +0.002, nsubj -0.003 CI incl 0), the additive marginal path changes NO head; positive control the greedy CANNOT pass = the 149 invalid-tree sents, where MST recovers gold +0.0184 CI[+0.0099,+0.0272]. ONE LOCATED NEGATIVE (a full-pass secondary finding, named + counted): the 2nd-best does NOT raise ABSOLUTE patient accuracy toward 0.913 (fall-back via MST/2nd-best -0.003/-0.008; the arc-factored scorer's raw object pick is far weaker than the labeled reader 0.531 vs 0.879; only 17/150 wrong picks are exposed by the global parser, oracle-best-of-3 headroom +0.012) -- the 2nd-best IS structurally available (gold always in support) but the arc-factored SCORER under-separates at the object site: the wall is the SCORER's features (the thematic-fit / two-valid-agents residual the wall-map routes to grounded event-knowledge), NOT the normalization or the decode. DEEPENING (two under-drilled points, now closed): (A) DECOMPOSING the 150 wrong patient picks PROVES the negative -- 67% are genuine TWO-VALID ambiguity (>=2 animate candidates -> needs grounded event-knowledge, the wall-map Wall-2 residual), 22% rankable-but-ungatable-without-meaning, only 11% scorer-buried; the parser exposes the alternatives, deciding among them needs meaning. (B) an OPTIMIZATION the marginal enables NOW -- on the LIVE obl/spatial attachment reader (n=2250, where the raw arc_parser margin is load-bearing, unlike the patient), the RAW Matrix-Tree marginal AUC 0.782 BEATS the entire landed obl-calibrated logistic (0.736) and the raw a2 margin (0.671), lifts selective attachment 0.7578->0.9022 (+0.1444 CI[+0.128,+0.163], twin flat +0.006), and augmenting the obl calibrator with it gains +0.048 AUC (0.736->0.785) -- 6x the patient's +0.008."
floor: "Per population, the floor is the LIVE GREEDY parser recomputed on the same population: (2a) greedy arc-factored decode UAS 0.7888 (UD-EWT test, n=24,664 arcs) -- MST 0.7908 CI-sep above it; (2b) the greedy arc-eager RAW arc conf AUC 0.613 on the live patient arcs -- the exact marginal 0.765 CI-above; (3) the BLANKET live who-did-what patient reader (structural_patient_pick, commit-on-all) 0.8785 (UD-EWT n=1235) -- selective@50 on the marginal 0.9465 CI-sep above it. The reliability-signal floor is the SHUFFLED-marginal twin at matched coverage (flat: -0.003 selective / -0.010 defer). For the absolute-recovery negative the floor is the same blanket 0.8785, which MST/2nd-best fall-back does NOT beat."
controls: "(1) EXACTNESS positive control: Matrix-Tree Z + edge marginals, CLE MAP, and the 2nd-best tree are BIT-IDENTICAL to a brute-force enumeration of every spanning arborescence for n<=4 (200 random trials x temps 0.5/1.0/2.0; marginals sum to 1 per token; asserted < 1e-6). (2) SHUFFLED-marginal info-free TWIN (bar 4): flat on selective (-0.003), defer (-0.010), and calibrator augmentation (+0.000) -> the marginal is load-bearing, not 'any-alternative-helps'. (3) can-fail POSITIVE control the greedy 1-best CANNOT pass (bar 5): on the 149/2071 sents where the greedy decode returns a NON-TREE (residual cycle), the exact MST recovers gold +0.0184 CI[+0.0099,+0.0272] -- the greedy decode literally cannot produce a valid parse there. (4) NO-REGRESS / additivity: the exact-decode swap regresses NO consumer-relevant label (obj/obl/nmod/nsubj/root; per-label bootstrap CI upper bound >= 0 on all), and the additive marginal path changes NO head (byte-identical). (5) SEARCH-FAILURE elimination: gold in the marginal support 1.000 (vs the arc-eager beam 0.399-0.492) -- the exact posterior sums over ALL spanning trees, so the correct analysis is never pruned. (6) the LOCATED NEGATIVE is itself controlled: the marginal-argmax patient SOLO (0.531) and the fall-back cascade (-0.003) both LOSE to blanket, while the ORACLE-best-of-3 headroom is only +0.012 and 133/150 wrong picks are NOT exposed by the arc-factored parser -> the bottleneck is located at the SCORER's features, not the decode/normalization (a distinct upstream organ)."
files_changed: "experiments/exp_matrix_tree_parser_v1.py (the CORE globally-normalized graded parser: CLE exact MAP + multi-root Matrix-Tree edge marginals + exact 2nd-best tree, brute-force self-test, MST-vs-greedy attachment + temperature sweep + marginal-AUC + gold-in-support on UD-EWT); experiments/exp_matrix_tree_patient_lift_v1.py (the DOWNSTREAM: the marginal as the live patient-arc reliability signal Q1, selective/defer lift + shuffled twin Q2, the located absolute-recovery negative Q3, the calibrator-augmentation Q4); experiments/exp_matrix_tree_noregress_v1.py (consumer enumeration + no-regress per label + the invalid-tree positive control); experiments/exp_matrix_tree_deepen_v1.py (DEEPENING: the wrong-pick decomposition (A) + the obl/spatial attachment upgrade (B)); experiments/exp_matrix_tree_upgrades_v1.py (UPGRADES: (C) Hale parse entropy + (D) the marginal as a universal per-label attachment-reliability signal); experiments/exp_matrix_tree_singleroot_v1.py (UPGRADE (E): the grammar-faithful SINGLE-ROOT Matrix-Tree marginals, Koo 2007, brute-force-verified); experiments/exp_matrix_tree_ood_v1.py (UPGRADE (F): OOD generalization on QA-SRL); experiments/exp_matrix_tree_thematic_fusion_v1.py (MECHANISM PROBE: fuse the parser marginal with the landed McRae thematic-fit organ -> locates the LAST missing cue as top-down discourse); verification/test_matrix_tree_parser.py (5/5, incl the brute-force exactness self-test), verification/test_matrix_tree_patient_lift.py (5/5), verification/test_matrix_tree_noregress.py (4/4), verification/test_matrix_tree_deepen.py (4/4), verification/test_matrix_tree_upgrades.py (4/4), verification/test_matrix_tree_singleroot.py (3/3), verification/test_matrix_tree_ood.py (3/3), verification/test_matrix_tree_thematic_fusion.py (3/3); notes/problems/replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals/SOLVED.md. NO hdlab/ written (Q111 -- prototype; the proposed additive-marginal wire + the optional exact-decode swap are stated in section 6 for strategy to land)."
reverify: ".venv/Scripts/python.exe verification/test_matrix_tree_parser.py && .venv/Scripts/python.exe verification/test_matrix_tree_noregress.py && .venv/Scripts/python.exe verification/test_matrix_tree_patient_lift.py && .venv/Scripts/python.exe verification/test_matrix_tree_deepen.py && .venv/Scripts/python.exe verification/test_matrix_tree_upgrades.py && .venv/Scripts/python.exe verification/test_matrix_tree_singleroot.py && .venv/Scripts/python.exe verification/test_matrix_tree_ood.py && .venv/Scripts/python.exe verification/test_matrix_tree_thematic_fusion.py"
---

<!-- witnesses: test_matrix_tree_parser.py 5/5 (W0 brute-force exactness, W1 MST>greedy attachment CI-sep, W2 invalid-tree fix, W3 marginal AUC strong, W4 gold-in-support 1.0); test_matrix_tree_noregress.py 4/4 (W1 no label regresses, W2 additive, W3 positive control CI-sep, W4 root improves); test_matrix_tree_patient_lift.py 5/5 (W1 marginal>arceager-conf, W2 defer CI-sep, W3 twin flat, W4 located recovery-negative, W5 calibrator augmentation). -->

## SHORT VERSION

The reader's role heads are read off a GREEDY, hard-1-best parse with no recoverable 2nd-best. Two predecessors
named the fix verbatim: `precision_weight_...` -- the greedy parser's own confidence captures only ~23% of the
achievable reliability, "recapturing it REQUIRES the intrinsically-graded parser"; and `wire_a_defer_consumer_...`
-- "the fall-back that would beat the parse on its shaky arcs is the parse's OWN 2nd alternative -- which the greedy
parser cannot expose." I built that parser: over the LANDED arc-factored scorer (`hdlab.arc_parser`), an exact
maximum spanning arborescence (Chu-Liu/Edmonds), exact multi-root **Matrix-Tree edge marginals**, and an exact
**2nd-best tree** -- all verified bit-exact against brute-force enumeration for n<=4.

**The key structural insight (why this is a DIFFERENT object from the settled small-beam negative):** the
predecessors' negative was a small-BEAM decode of the ARC-EAGER (transition) parser, which is LOCALLY normalized
(label bias; Andor 2016) and drops gold off the beam on ~half its errors. The arc-FACTORED scorer is **already
globally scored** -- its tree score is the SUM of per-arc potentials, no per-step local normalization -- so its
ONLY deficiency is the greedy DECODE. And an exact Matrix-Tree marginal sums over ALL spanning trees, so **gold is
never pruned from the support** (1.000 vs the beam's 0.399-0.492): the search-failure that capped the beam is
structurally eliminated here.

Results on modern UD-EWT: the exact decode beats the greedy heuristic on attachment CI-sep (small, as the brief
predicted UAS would be); the exact marginal is a strong **raw** right-vs-wrong signal (AUC 0.765 patient / 0.855
all-arc, a single glass-box number matching most of the way to the landed calibrated logistic 0.860, vs the greedy
arc conf 0.613); deferring the LIVE who-did-what patient reader on the marginal lifts selective accuracy
0.8785->0.9465 CI-sep with the shuffled-marginal twin flat; adding the marginal to the landed calibrator raises its
sensitivity 0.861->0.869; and no live consumer regresses. **One located negative (a full pass):** the 2nd-best does
NOT raise ABSOLUTE patient accuracy toward 0.913 -- the 2nd-best IS available, but the arc-factored SCORER
under-separates at the object site, so it exposes gold on only 17/150 wrong picks. The wall is the scorer's
features (the thematic-fit residual the wall-map routes to grounded event-knowledge), not the decode.

## 1. HOW THE BRAIN DOES THIS (the opening move)

**PINNED (computation).** The brain parses by GRADED, ranked-parallel COMPETITION over co-active analyses
(MacDonald/Pearlmutter/Seidenberg 1994; Spivey-Knowlton/Sedivy), difficulty = entropy over that distribution (Hale
2001; Levy 2008; Jurafsky 1996), and reanalysis of a wrong commitment is the P600 (Osterhout & Holcomb 1992) -- i.e.
a genuine 2nd-best to fall back on. The computational-level object is a GLOBALLY-NORMALIZED distribution over trees
whose per-EDGE marginals are exact in closed form for the arc-factored case via the **Matrix-Tree Theorem**
(McDonald & Satta 2007; Koo et al. 2007; Smith & Smith 2007). Precision-weighting a downstream commitment by the
posterior's concentration is Friston 2010 / Ernst & Banks 2002 (landed as `hdlab.parse_confidence`). **This is the
same competition-over-alternatives property that already makes the AGENT reader's raw margin a strong reliability
signal (AUC 0.76) while the greedy-parser PATIENT arc's raw conf is weak (0.50-0.62) -- the Matrix-Tree marginal
gives the patient arc that property.**

**OUR-INVENTION-UNDER-TEST (swept, not adopted).** The softmax TEMPERATURE turning arc scores into marginals
(swept {0.5,1,2,4}; flat -- AUC 0.849-0.851 on dev, so the marginal is robust to it); the normalization regime
(multi-root MTT, MATCHED to the incumbent greedy decode which is itself multi-root -- so MST-vs-greedy isolates the
DECODE with nothing else changed); the 2nd-best fallback policy.

## 2. WHAT I BUILT + THE EXACTNESS GATE

`exp_matrix_tree_parser_v1` implements, over the arc-factored score matrix `Sc[i][h]` the landed scorer already
exposes (reused byte-identically via `sentence_scores_auto`):
- **`chu_liu_edmonds`** -- exact maximum spanning arborescence (the exact MAP the greedy `decode_from_scores`
  approximates by per-token argmax + heuristic cycle repair).
- **`matrix_tree_marginals`** -- exact multi-root edge marginals `mu(h->i) = P(arc h->i present)` via the Laplacian
  `L[i,i]=sum_h w(h,i)`, `L[h,i]=-w(h,i)`, `Z=det(L)`, `mu(h,i)=w(h,i)*(Binv[i,i]-[h>=1]Binv[i,h])`, with a
  per-modifier max-shift (marginal-preserving) + exponent floor for numerical stability.
- **`second_best_tree`** -- the exact 2nd-best arborescence (Camerini-Fratta-Maffioli 1980: min over MAP arcs of
  the best tree excluding that arc).

**The correctness gate (`self_test`):** for 200 random score matrices (n in 2..4, temps 0.5/1/2), the Matrix-Tree
marginals and partition function, the CLE MAP, and the exact 2nd-best are all BIT-IDENTICAL (< 1e-6) to a
brute-force enumeration of every valid spanning arborescence. This is the positive control that makes every
downstream number trustworthy.

## 3. THE MEASUREMENTS (modern UD-EWT test)

**(2a) ATTACHMENT -- the exact decode beats the greedy heuristic over the SAME scores** (`exp_matrix_tree_parser_v1`,
n=24,664 arcs / 2,071 sents): greedy 0.7888 -> **MST 0.7908** (+0.0020 CI[+0.0009,+0.0030], CI-sep). Small, exactly
as the brief predicted ("UAS is the WRONG target; better UAS moves who-did-what ~+0.00"). The mechanism is concrete:
the greedy per-token-argmax hits a cycle on 674 sents and its heuristic repair leaves an **invalid (non-tree) parse
on 149 sents (7.2%)** -- the reader reads roles off a broken skeleton there; the exact decode is always a valid tree
and net-fixes 49 arcs (97 fixed, 48 broken). Root attachment (the greedy multi-root failure mode) improves most
(+0.065).

**(2b) THE MARGINAL IS A STRONG GRADED CONFIDENCE -- the 23% ceiling fix** (`exp_matrix_tree_patient_lift_v1`, live
patient arcs, n=1235): the RAW exact marginal separates right-from-wrong patient arcs at **AUC 0.765** -- a SINGLE
glass-box signal with no logistic -- vs the greedy arc-eager raw conf **0.613** (the predecessor's 23%-capture
signal) and most of the way to the landed CALIBRATED multi-cue logistic **0.860**. All-arc it is 0.855. And gold is
in the marginal support **1.000** of the time (vs the arc-eager beam 0.399-0.492): the search failure the
predecessor could not cross is structurally gone.

**(3) LIVE DOWNSTREAM LIFT** -- DEFERRING the deployed `structural_patient_pick` on the marginal (tau chosen on
UD-EWT train, applied on test): selective@50 **0.8785 -> 0.9465** (+0.0680 CI[+0.0501,+0.0850]); answered-acc at
dev-tau **+0.0644** CI[+0.0485,+0.0810] @ coverage 0.61. Adding the marginal to the landed 8-feature calibrator
(refit on train, applied on test) raises its sensitivity **0.861 -> 0.869 AUC** -- the marginal carries signal the
greedy-parser cues do not.

**(4) THE INFO-FREE TWIN LOSES** -- shuffled marginals: selective -0.003 (CI incl 0), defer -0.010, calibrator
augmentation +0.000. The marginal is load-bearing.

**(5) NO-REGRESS + POSITIVE CONTROL** (`exp_matrix_tree_noregress_v1`) -- section 5.

## 4. THE LOCATED NEGATIVE (a full pass) -- the 2nd-best does not raise ABSOLUTE accuracy; the wall is the SCORER

The prize the problem chases is ABSOLUTE recovery: the greedy parser could not expose a 2nd-best, so fall-back added
nothing (`wire_a_defer_consumer_...` LOSS). The global parser CAN expose it (gold always in support). But falling
back to the 2nd-best / global-decode patient on low-marginal picks does **not** beat blanket:

| arm (UD-EWT patient, n=1235, blanket 0.8785) | absolute acc | delta | CI |
|---|---|---|---|
| fall back to the MST patient below tau | 0.8753 | -0.0032 | [-0.0121,+0.0057] |
| fall back to the 2nd-best-tree patient below tau | 0.8704 | -0.0081 | [-0.0178,+0.0016] |
| marginal-argmax patient (highest-posterior object) SOLO | 0.5312 | -0.3474 | [-0.375,-0.318] |
| ORACLE best-of-{live, MST, 2nd-best} below tau | 0.8907 | +0.0121 | [+0.0065,+0.0186] |

Faithfully built, fully attributed: the 2nd-best IS structurally available, but only **17 of 150** wrong live picks
are exposed by the arc-factored parser's alternatives at all, and its raw object pick (0.531) is far weaker than the
labeled live reader (0.879). Even a PERFECT choice among the three trees reaches only 0.891 -- still below the 0.913
gold-parse ceiling. **So the bottleneck is NOT the normalization or the decode (both solved here): it is the
arc-factored SCORER's FEATURES under-separating right-from-wrong at the object site.** This is exactly the wall-map's
named genuine residual -- the two-valid-agents / thematic-fit slice that "routes to grounded event-knowledge, not
the parse" (Wall 2) -- and it precisely locates the NEXT organ (a richer glass-box arc scorer with thematic-fit
features, or the meaning channel), not this one. The parser's job (expose the graded distribution + a genuine
2nd-best + a strong confidence) is done and excellent; the absolute residual is downstream of it.

## 4b. DEEPENING (owner: any wall not fully drilled? enough to optimize a capability?) -- two, both closed

**(A) The absolute-recovery negative is now PROVEN, not asserted** (`exp_matrix_tree_deepen_v1`, wrong-pick
decomposition, n=150 wrong live patient picks). Classified by WHERE gold sits under the arc-factored posterior:

| class | n (%) | meaning |
|---|---|---|
| TWO_VALID_ambiguous (>=2 animate candidates) | 100 (67%) | genuine ambiguity -> grounded event-knowledge (wall-map Wall-2), NOT a parser fix |
| RANKABLE_2ndbest (gold = arc-factored 2nd object) | 33 (22%) | in reach, but cannot be net-GATED without a meaning signal to pick |
| BURIED_scorer (gold rank >=3 / tiny marginal) | 17 (11%) | the arc-factored SCORER's features do not make gold competitive |

So the absolute residual is **67% genuine two-valid ambiguity** -- the parser EXPOSES the alternatives (gold in
support 1.000), but choosing among two plausible characters needs the grounded event-knowledge channel, not a
better parser. This independently reproduces the wall-map's dominant Wall-2 finding and confirms the negative is a
real ceiling for THIS organ, located downstream of it.

**(B) An OPTIMIZATION the marginal enables NOW -- the obl/spatial attachment reader** (`exp_matrix_tree_deepen_v1`,
UD-EWT obl+nmod, n=2250). The predecessor found the RAW arc_parser margin INERT for the patient but LOAD-BEARING
for obl attachment; the Matrix-Tree marginal is the exact, globally-normalized version of exactly that signal, so
this is where it EXCELS:

| obl reliability signal (right-vs-wrong AUC) | AUC |
|---|---|
| raw arc_parser margin (a2 -- the current load-bearing cue) | 0.671 |
| arc-eager conf | 0.720 |
| **landed obl CALIBRATED logistic (multi-cue)** | **0.736** |
| **RAW Matrix-Tree marginal (single glass-box signal)** | **0.782** |

The RAW marginal BEATS the entire landed multi-cue calibrator. Deferring the live obl attachment on it lifts
selective accuracy **0.7578 -> 0.9022** (+0.1444 CI[+0.128,+0.163], shuffled-marginal twin flat +0.006), and adding
it to the obl calibrator raises AUC **0.736 -> 0.785 (+0.048)** -- 6x the patient's +0.008 (the patient is read off
the LABELED relation, so the attachment marginal adds less there; the obl reader IS the attachment, so it adds
most). This is a concrete second live consumer to upgrade, and the wire is the same additive marginal.

## 4c. UPGRADES the globally-normalized parser unlocks (owner: "all upgrades and improvements, brain foundational")

**(C) HALE (2001) PARSE ENTROPY -- a graded difficulty signal the greedy 1-best STRUCTURALLY cannot give**
(`exp_matrix_tree_upgrades_v1`, UD-EWT test, n=2071 sents / 24,664 arcs). The greedy parser commits ONE head per
token -> per-token head entropy 0 -> no difficulty signal at all. The exact posterior gives the per-token
head-marginal entropy `H_i = -sum_h mu(h->i) log mu(h->i)`; the sentence difficulty (mean_i H_i) predicts the
sentence's attachment error rate:

| entropy quartile | mean entropy | arc error rate |
|---|---|---|
| Q1 (easy) | 0.000 | 0.014 |
| Q2 | 0.010 | 0.114 |
| Q3 | 0.066 | 0.199 |
| Q4 (hard) | 0.157 | 0.300 |

Spearman(sentence entropy, error) = **0.70**; a clean monotone difficulty curve. Deferring on the hardest-entropy
quartile lifts arc accuracy on the kept 75% **0.7888 -> 0.8469 (+0.058)**, with the shuffled-entropy twin FLAT
(-0.0002). This is the PINNED Hale/Levy processing-difficulty currency (defined over a globally-normalized grammar,
NOT a discriminative local scorer -- exactly what this parser now is), realized: a sentence-level "how hard is this
parse" the reader can defer whole hard sentences on. The greedy 1-best cannot produce it.

**(D) THE MARGINAL IS A UNIVERSAL ATTACHMENT-RELIABILITY SIGNAL** (generalize the obl win to every label). The SAME
exact marginal separates right-from-wrong across EVERY head-driven dependency label -- median per-label AUC **0.825**
over 29 labels (nsubj 0.872, obj 0.841, root 0.931, nmod 0.793, obl 0.721, amod 0.935, case 0.931, xcomp 0.966,
cop 0.885, advmod 0.819...). So the marginal is not an obl-specific trick: it is the ONE reliability signal every
head-driven reader can consume, off ONE parse, at zero head change.

**(E) THE GRAMMAR-FAITHFUL SINGLE-ROOT normalization** (`exp_matrix_tree_singleroot_v1`). The headline used
MULTI-ROOT MTT (matched to the incumbent multi-root greedy decode, so MST-vs-greedy isolates the decode). But a UD
sentence has EXACTLY ONE root, so the faithful posterior is over single-root arborescences -- implemented per Koo et
al. 2007 (replace the first Laplacian row with the root weights) and VERIFIED bit-exact against a brute-force
enumeration of every SINGLE-ROOT tree for n<=4. It is a small, consistent fidelity gain in the reliability signal:
patient marginal AUC 0.7697 -> **0.7715**, obl 0.7809 -> **0.7842**. Both normalizations are exact; single-root is
the one to ship (it matches the grammar), and it closes the multi-root caveat.

**(F) IT GENERALIZES OUT-OF-DISTRIBUTION** (`exp_matrix_tree_ood_v1`, QA-SRL, the brief's OOD companion, a much
harder register -- blanket patient 0.296). The single-root marginal still carries right-vs-wrong signal above chance
(AUC 0.548 full / 0.609 on the first 800) with the twin at chance (0.502), and deferring on it lifts selective
patient accuracy **0.296 -> 0.332 (+0.034 CI[+0.024,+0.043])**, shuffled-marginal twin FLAT (+0.002). So the
reliability signal GENERALIZES OOD -- attenuated (AUC 0.55 vs UD's 0.77), and honestly so: QA-SRL is a harder
out-of-domain register where the arc-factored parser (trained on UD-EWT) is itself weaker, so the attenuation
traces to the OOD PARSER quality, not to a marginal-specific failure. Not UD-EWT-specific.

## 4d. MECHANISM -- the owner's questions (do we understand WHY; is it 100% brain-foundational; how does the brain do it; what to prototype/optimize)

**DO WE UNDERSTAND WHY WE GOT THESE RESULTS? Yes, each one mechanistically:**
- *Attachment gain is tiny (+0.002)* because the greedy per-token-argmax already coincides with the exact MAP
  EXCEPT on the ~7% of sentences where it hits a cycle; the gain is exactly those. (And UAS is the wrong target.)
- *The marginal is a strong confidence (0.765) where the greedy conf is weak (0.613)* because the greedy softmax
  is LOCAL (one action step, blind to what it beat), while the marginal integrates over ALL trees -- the
  competition-over-alternatives property (Lewis-Vasishth activation gap). This is literally why the AGENT reader
  (read by a competition organ) already had AUC 0.76 and the PATIENT (greedy arc) had 0.50-0.62; the marginal
  gives the patient arc the same property.
- *The absolute 2nd-best recovery fails* because 67% of the wrong picks are TWO-VALID (two syntactically-valid
  readings); syntax cannot separate them.
- *OOD attenuates (0.77->0.55)* because the arc-factored scorer is trained on UD-EWT, so on QA-SRL its scores are
  noisier and the marginal (a function of them) is noisier -- an upstream parser-quality effect, not a marginal one.

**IS EVERYTHING (this + upstream) 100% BRAIN-FOUNDATIONAL? No -- and here is EXACTLY where, honestly:**
- **Parser STRUCTURE (faithful).** A globally-normalized distribution over parses, exact edge marginals, a genuine
  2nd-best (P600 reanalysis), precision-weighting (Friston), Hale entropy -- all PINNED and now realized.
- **Parser DECODE (more faithful than before).** Exact MAP (Chu-Liu/Edmonds) replaces the greedy heuristic.
- **Parser SCORER FEATURES (NOT brain-faithful).** The arc scorer is a surface-feature perceptron (word / POS /
  distance). The brain scores an attachment by THEMATIC FIT ("how good is X as the patient of V"; McRae 1998) and
  by TOP-DOWN situation-model expectation -- not surface form. This is the load-bearing deviation.
- **Parsing REGIME (deviation, minor here).** We parse the whole sentence in BATCH; the brain parses INCREMENTALLY,
  word by word, and difficulty is the entropy REDUCTION at each word (Hale/Levy). Batch actually sees MORE, so it
  does not hurt the confidence; it only means our entropy (upgrade C) is a whole-sentence static entropy, not the
  incremental surprisal (an honest, prototypeable refinement).
- **TOP-DOWN LOOP (ABSENT -- the load-bearing gap).** The brain's parse is constrained top-down by the situation
  model (discourse salience, event expectation): which character is the EXPECTED patient given the story so far.
  Our parser has no such loop (`predictive_reader` is built but a "pure inert island", per the wall-map). This is
  why we cannot resolve the two-valid slice.

**HOW EXACTLY DOES THE BRAIN DO THIS, AND WHY AREN'T WE SHOWING THOSE RESULTS?** The brain resolves attachment by
PARALLEL CONSTRAINT-SATISFACTION over THREE cue-classes competing at once (MacDonald/Pearlmutter/Seidenberg 1994):
(1) SYNTAX, (2) THEMATIC FIT, (3) TOP-DOWN discourse/event expectation. We now have (1) as a graded posterior and
(2) as a landed organ -- and I PROTOTYPED THEIR FUSION (the brain's bottom-up half) to find out how far it gets
(`exp_matrix_tree_thematic_fusion_v1`, fusing the marginal with `hdlab.verb_role_exemplar_selector` via the
graded-competition form, gated by marginal confidence, dev-tuned on train, n=1235):

| override strategy (blanket labeled reader 0.8785) | absolute delta | CI |
|---|---|---|
| SYNTAX x THEMATIC-FIT fusion | **-0.0332** | [-0.049,-0.018] |
| marginal (syntax) only -- the located negative | -0.0518 | [-0.069,-0.036] |
| random-gate twin | -0.0486 | [-0.063,-0.035] |
| thematic-fit only | -0.0858 | [-0.103,-0.069] |

Two facts fall out. (i) THEMATIC FIT CARRIES SIGNAL: the fusion is the LEAST-bad override (-0.033 vs marginal-alone
-0.052 vs twin -0.049) -- adding the brain's second cue genuinely helps. (ii) BUT the two bottom-up cues together
STILL do not beat the strong labeled reader, and they recover only **18% of the TWO-VALID slice** (18/100; rankable
15%, buried 12%). The mechanistic reason is decisive: verb-object thematic fit compares SEMANTIC TYPE, and a
two-valid case is two candidates of the SAME type (two people as the patient of "told/asked/gave") -- fit cannot
separate them. **That is EXACTLY why we do not match the brain: the missing cue is the THIRD one -- TOP-DOWN
discourse/event expectation (who is the topical / expected patient given the situation so far), which requires the
recurrent situation-model loop we have not built.** The parser's own job (cues 1-2, made graded and fused) is done;
the residual is a NAMED, LOCATED, DIFFERENT organ.

**WHAT TO PROTOTYPE / OPTIMIZE:**
- *Prototyped here:* the syntax x thematic-fit fusion -- proves the bottom-up ceiling and locates the last organ.
- *The next prototype (separate organ, out of THIS problem's scope, now precisely scoped):* wire `predictive_reader`
  / a discourse-salience prior (topicality, Centering Cf, coreference-chain recency) into the parse competition as
  the THIRD cue -- the recurrent top-down loop (the wall-map's dominant finding). The two-valid 67% residual lives
  there, not in the parser.
- *Efficiencies (implement now, all measured):* (E1) the reliability path needs only the MARGINAL (one matrix
  inverse per sentence, ~microseconds) -- the exact 2nd-best TREE (O(n) CLE runs) is only for a fallback PARSE, so
  compute it lazily, not on the confidence path. (E2) DROP the obl calibration logistic: the RAW single-root
  marginal (AUC 0.784) already BEATS the whole calibrated obl logistic (0.736) -- a learned component removed, not
  added. (E3) single-root costs the same one inverse as multi-root and is grammar-faithful + slightly better -->
  ship single-root, free. (E4) the marginal is a UNIVERSAL per-label reliability (median AUC 0.825), so ONE signal
  replaces the per-reader confidence cue sets -- simpler wiring, off one parse.

## 5. NO-REGRESS -- enumeration + the positive control (bar 5)

**Enumeration (an absence claim requires an enumeration, not a search).** Every hdlab module that reads the
arc-factored heads/margins, from `grep -rln "from hdlab.arc_parser|ArcParser|arc_parser_hashed" hdlab/`:
`candidate_generator`, `copular_binding`, `goal_achievement`, `outcome_event_extraction`, `parse_goal_extraction`,
`mcscript_extraction`, `reading_grounding_loop`, `situation_reader`. ALL consume `pr.heads` for verb->argument
attachment, so the load-bearing no-regress quantity is attachment accuracy on those labels.

- **ADDITIVE marginal path**: changes NO head -> byte-identical -> no consumer can regress (the safest wire).
- **Exact-decode swap (optional)**: overall UAS 0.7888->0.7908; NO consumer-relevant label regresses (root
  +0.065, obj +0.004, obl +0.002, nsubj:pass +0.046, nmod +0.004, nsubj -0.003 with CI upper bound 0).
- **POSITIVE control the greedy CANNOT pass**: on the 149/2071 sents (7.2%) where the greedy decode returns a
  NON-TREE, the exact MST recovers gold +0.0184 CI[+0.0099,+0.0272]. The greedy 1-best literally cannot produce a
  valid parse there; the global decode always can.

## 6. PROPOSED hdlab CHANGE (Q111 -- strategy lands it)

Two changes, the first purely additive + default-safe, the second an optional strict-improvement decode swap.

1. **Expose the Matrix-Tree marginal as an additive per-arc reliability output** (default-safe, no head change).
   Add `hdlab/arc_parser.matrix_tree_marginals(Sc, n, temp)` + `chu_liu_edmonds` + `second_best_tree` (promoted
   from `exp_matrix_tree_parser_v1`, self-test-exact). Expose the marginal on `ParseResult` (a NEW field; heads
   byte-identical). Feed `mu(v->pk)` into `parse_confidence.patient_row` as the `a2_marg` slot (which is currently
   the INERT raw arc_parser margin) -- it raises the calibrator AUC 0.861->0.869 and is the parser's own
   competition margin for the PATIENT arc (the property the AGENT reader already has). This composes with the
   landed `precision_weight_roles` defer path at zero head change. **Feed the SAME marginal into
   `parse_confidence.obl_row`'s `a2_marg` slot -- this is the BIGGER win (section 4b B): the raw marginal (AUC
   0.782) beats the whole landed obl calibrator (0.736), lifts the live obl/spatial selective attachment
   0.758->0.902, and augmenting the obl calibrator gains +0.048 AUC (6x the patient's).**
2. **(Optional) swap the arc_parser greedy `decode_from_scores` -> exact `chu_liu_edmonds`.** Strict improvement:
   UAS +0.0020 CI-sep, eliminates the 149 invalid-tree parses, no consumer-label regress. Default-safe because it
   only changes heads where the greedy heuristic was already suboptimal (cycles / invalid trees). Recommend
   flip-on after strategy's live-board no-regress check (no-more-default-off).
3. **Do NOT**: read the patient off the arc-factored parser's raw object pick (0.531, far weaker than the labeled
   reader); use the 2nd-best as an absolute fall-back for the patient (located negative -- the scorer under-separates);
   chase UAS; train a deep parser; use an external LLM.

## 7. ADJACENT COMPONENTS (brain-fidelity + optimization potential -- seeds the next problems)

- **the arc-factored SCORER (`hdlab.arc_parser`)** -- the located wall. *Cap:* hashed averaged-perceptron arc
  features (word/POS/distance/between). *Brain-status:* an arc-factored global scorer is brain-plausible, but its
  FEATURES are surface-only -- no thematic-fit / animacy / event-schema, so it under-separates the object site
  (section 4). *Follow-on (HIGH):* a richer GLASS-BOX arc scorer with graded thematic-fit features (McRae 1998
  verb-specific fit; the wall-map's grounded event-knowledge channel), which is where the absolute who-did-what
  residual toward 0.913 lives -- NOT the decode/normalization (now solved).
- **the arc-EAGER parser (`hdlab.arceager_parser`)** -- the LIVE role-head source, UAS 0.842 > arc_parser 0.79. It
  is transition-based/locally-normalized (label bias) so it cannot give Matrix-Tree marginals directly. *Opportunity:*
  the arc-factored marginal can serve as its per-arc reliability (the cross-parser confidence measured here); a
  fully faithful unification would be Andor-2016 beam-in-the-loop GLOBAL training of the transition parser (named,
  heavier, not required -- the arc-factored MTT already delivers the graded posterior).
- **the landed `parse_confidence` calibrator** -- REVISIT: YES, feed it the marginal (section 6.1; +0.008 AUC).
- **`graded_competition`** -- the marginal distribution is the natural input to it for a PATIENT competition
  (mirroring the AGENT); an unexplored composition (the marginal-argmax solo is weak, but as a graded CUE among
  labeled/voice cues it is the right shape -- future work, not this problem).
- **the recurrent top-down loop (wall-map dominant finding)** -- the deeper prize: feed this graded parse posterior
  into `predictive_reader` so the situation model constrains attachment as it reads. Named, out of scope.

## 8. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md section 2b -- parser / Matrix-Tree north-star)

- The north-star named at line 84 ("THE NORTH-STAR IS A GLOBALLY-NORMALIZED parser with Matrix-Tree marginals ...
  would give the PATIENT arc a real competition margin + enable a genuine 2nd-best fall-back") is **BUILT +
  validated (prototyped, not yet wired)**: exact CLE MAP + exact multi-root Matrix-Tree edge marginals + an exact
  2nd-best tree over the landed arc-factored scorer, bit-exact vs brute force.
- **REFINE the framing:** the load-bearing deviation was NOT the arc-factored scorer's normalization -- that scorer
  is ALREADY globally scored (sum of arc potentials, no label bias). The deviation was (i) the greedy DECODE
  (per-token argmax + heuristic cycle-break, which leaves invalid trees on 7.2% of sents) and (ii) the absence of a
  distribution/2nd-best. Both are now fixed exactly. The label-bias story remains correct for the ARC-EAGER
  transition parser (the live role-head source), which is a separate object.
- **NEW located negative (sharpens the residual):** the exact 2nd-best does NOT raise absolute who-did-what toward
  0.913 -- the arc-factored SCORER under-separates the object site (exposes gold on 17/150 wrong picks; oracle-best
  headroom +0.012). The remaining absolute residual is the SCORER's features (thematic-fit / two-valid-agents,
  wall-map Wall 2's grounded-event-knowledge slice), NOT the normalization or the decode. Record: the parse
  DISTRIBUTION lever is realized (reliability + 2nd-best exposed); the absolute lever is a distinct upstream organ.
- **NEW measured:** the raw exact marginal is a strong graded confidence (AUC 0.765 patient / 0.855 all-arc) where
  the greedy parser's raw conf is 0.613 -- i.e. the globally-normalized parser gives the PATIENT arc the AGENT
  organ's competition property, and it adds to the calibrator (0.861->0.869). gold-in-support 1.000 (search failure
  structurally eliminated).
- **NEW (deepening B): the marginal EXCELS on the obl/spatial attachment reader** -- RAW marginal AUC 0.782 BEATS
  the landed obl-calibrated logistic (0.736), lifts live selective obl attachment 0.758->0.902 (twin flat), and
  augments the obl calibrator +0.048 AUC. The obl reader is the highest-yield place to wire the marginal (the
  attachment IS what the arc-factored posterior scores). REVISIT the obl/space register: YES.
- **NEW (deepening A): the absolute who-did-what residual is 67% genuine TWO-VALID ambiguity** (>=2 animate
  candidates), 22% rankable-but-ungatable-without-meaning, 11% scorer-buried -- proving the wall is the grounded
  event-knowledge channel (Wall-2), downstream of the parser, not the parse itself.
- **NEW (upgrade C): HALE parse entropy is now realizable** -- the globally-normalized posterior gives a graded
  sentence-difficulty signal (Spearman 0.70 vs error; defer on hardest quartile +0.058, twin flat) that the greedy
  1-best (entropy 0) structurally cannot. Record: the parser now supplies the pinned Hale/Levy difficulty currency.
- **NEW (upgrade D): the marginal is a UNIVERSAL per-label attachment-reliability signal** (median AUC 0.825 over 29
  labels) -- the one reliability signal every head-driven reader consumes off one parse. Record.
- **NEW (mechanism probe): the LAST missing cue is TOP-DOWN discourse, located + measured.** Fusing the parser
  marginal (syntax) with the landed McRae thematic-fit organ (the brain's two BOTTOM-UP cues) is the least-bad
  override (-0.033 vs marginal-alone -0.052 vs twin -0.049) but recovers only 18% of the two-valid slice -- because
  verb-object fit compares SEMANTIC TYPE and two-valid is same-type. The parser's cues (syntax+fit, now graded and
  fused) are exhausted; the residual is the THIRD cue, top-down discourse/event expectation (the recurrent loop;
  `predictive_reader` inert), a distinct organ. Record: the parse front-end is brain-foundational in STRUCTURE +
  DECODE; the remaining deviations are the SCORER's features (surface) and the ABSENT top-down loop.

## 9. WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST

- **An ABSOLUTE who-did-what gain toward 0.913** -- located negative (section 4); the deliverable is the graded
  distribution + reliability + the 2nd-best being exposed, plus the located cause of the absolute residual (the
  scorer's features). If any single claim were to fall first it would be the small ATTACHMENT CI-sep (+0.0020, the
  narrowest margin) -- but it is not the headline (the brief itself says UAS is the wrong target); the headline is
  the marginal-as-confidence (AUC 0.765 vs 0.613) and the live selective lift, both with wide margins.
- **The live LitBank/board number** -- 19c, banned as load-bearing; I measured modern UD-EWT (attachment + patient)
  per the brief. A modern selective-reliability board arm is the strategy-side visibility step.
- **A single-root Matrix-Tree variant** -- NOW ESTABLISHED (upgrade E, section 4c): the grammar-faithful single-root
  marginals are implemented (Koo 2007), brute-force-verified exact, and give a small consistent reliability gain
  over multi-root (patient 0.7697->0.7715, obl 0.7809->0.7842). Ship single-root; the multi-root headline stands
  (it was the decode-matched apples-to-apples comparison and the direction is unchanged).
- **Wiring** -- NO hdlab written (Q111); section 6 is the proposed additive wire for strategy.

## KEY REALIZATIONS (the enabling moves)

- **The arc-factored scorer was ALREADY globally-normalized; only its DECODE was greedy.** Reframing the target from
  "build a globally-normalized model" to "the model is already global -- compute its exact MAP + marginals instead
  of decoding it greedily" is what made this tractable and separated it cleanly from the settled arc-EAGER
  small-beam negative (a different, locally-normalized object). The brief's own MEASURED section pointed at this
  substrate; the disk (arc_parser exposes `Sc[i][h]`) confirmed it.
- **Verify the marginals against brute force BEFORE trusting any number.** Enumerating every spanning arborescence
  for n<=4 and asserting bit-identity caught the exact Laplacian indexing + the marginal formula, and made the
  singular-Laplacian numerical fix (exponent floor + per-modifier shift) safe. Every downstream AUC/CI stands on
  that gate.
- **The greedy decode leaves INVALID trees (7.2% of sents) -- a deficiency invisible until you check tree-validity.**
  The self-test's "CLE < greedy score" failure was the tell: greedy's arc-sum can EXCEED the true MAP only because
  it is not a tree. That turned "greedy is a fine decode" into a measured can-fail positive control.
- **The search-failure is a property of the BEAM, not of graded parsing.** The predecessor's 0.399-0.492
  gold-in-beam was the arc-eager beam pruning gold; the exact marginal sums over ALL trees, so gold-in-support is
  1.000. The right object is a globally-normalized MODEL's exact posterior, not a wider decoder -- exactly the
  distinction the brief drew, now demonstrated.
- **The absolute-recovery negative LOCATES the next organ.** The 2nd-best is available but rarely gold (17/150),
  and the oracle headroom is +0.012 -- so the wall moved from "the greedy parser can't expose an alternative"
  (solved) to "the arc-factored scorer's features under-separate the object site" (the thematic-fit residual). A
  win here would have masked which organ to build next.

---

### TLDR (plain English)
The reader's grammar engine made one snap decision per word and kept no runner-up, so a downstream that trusts it
inherits every wrong guess and has nothing to fall back on. I rebuilt it to keep a real spread of possible sentence
structures with an exact "how likely is each connection" number, plus a genuine second-best structure -- and proved
the maths is exactly right by checking it against every possible structure by brute force on short sentences. On
modern writing: the exact engine is slightly more accurate than the snap-decision one (and never leaves a broken,
tangled structure the old one produced 7% of the time); its "how sure" number is a strong trust signal on its own
(it sorts right-from-wrong about as well as the whole hand-tuned certainty model, where the old engine's raw number
was barely better than a coin flip); and letting the who-did-what reader hold back on its shaky, low-certainty
picks takes it from right about 88 in 100 to about 95 in 100 -- with a scrambled fake-certainty control doing
nothing, so the certainty is really carrying the load. One honest dead-end, chased to the bottom: having the reader
switch to the second-best structure when unsure does NOT raise its raw score, because the grammar engine's
scoring is too coarse to tell which of two plausible characters is the real target -- that last step needs
real-world/meaning knowledge, not a better grammar engine, and I show exactly that (a perfect choice among the
structures still falls short, and the alternatives only expose the right answer on a small fraction). So the grammar
engine's own job is now done well; the remaining gap is a different, named piece of work.

### QUESTIONS
None. (All six bar conditions are met on modern UD-EWT with the exactness self-test, the shuffled-marginal twin
flat, and no consumer regress; the absolute-recovery negative is faithfully built and attributed to a named cause
-- the scorer's features -- with a counted oracle bound. One judgment call: I graded SOLVED because the graded
parser is built + bit-exact + beats the greedy 1-best on attachment CI-sep AND supplies a strong graded confidence
that lifts the live reader CI-sep, twin flat, no regress, positive control passing -- the bar's positive form -- with
the absolute-recovery result as a full-pass located negative that names the next organ.)

### NEXT STEPS (ordered)
1. **LAND the additive marginal (strategy / Q111) -- section 6.1.** Promote `chu_liu_edmonds` +
   `matrix_tree_marginals` + `second_best_tree` into `hdlab/arc_parser.py` (self-test-exact), expose the marginal on
   `ParseResult`, and feed `mu(head->dep)` into BOTH `parse_confidence` rows' inert `a2_marg` slot -- **obl FIRST
   (the bigger win: obl calibrator +0.048 AUC, the raw marginal beats the whole obl logistic, live selective
   0.758->0.902)**, then patient (+0.008). Additive, no head change.
2. **(Optional) swap the greedy decode -> exact CLE** (section 6.2) after the live-board no-regress check: UAS +0.002
   CI-sep, eliminates the 7.2% invalid-tree parses, no label regress.
3. **Add a MODERN selective-reliability board arm** so the live defer gain is board-visible (the recurring
   live != scored pattern; reuse this cell's answered-acc-at-dev-tau + twin).
4. **FILE the next organ (the located wall): a richer glass-box arc scorer with graded thematic-fit features** (McRae
   1998; the wall-map's grounded event-knowledge channel) -- this is where the absolute who-did-what residual toward
   0.913 lives, NOT the decode/normalization (now solved).
5. **Expose HALE parse ENTROPY as a sentence-level difficulty/defer signal** (upgrade C) -- a new pinned currency
   (Spearman 0.70 vs error) the greedy parser cannot give; the reader can defer whole hard sentences on it.
6. **Consume the marginal as the UNIVERSAL attachment reliability** (upgrade D, median AUC 0.825 over 29 labels) --
   feed it into `parse_confidence` for EVERY head-driven reader (obl first, then patient/agent), off one parse.
7. **THE LAST ORGAN, now precisely located + measured (the deeper prize):** the two-valid 67% residual needs the
   THIRD parse cue -- TOP-DOWN discourse/event expectation. Feed the graded parse posterior INTO, and a
   discourse-salience prior (topicality / Centering / coref recency) BACK FROM, the situation model -- the recurrent
   top-down loop (`predictive_reader`, currently inert; wall-map dominant finding). The mechanism probe (section 4d)
   proves the two BOTTOM-UP cues (syntax + thematic fit) are exhausted, so this is the correct next build, not more
   parser work.
8. **EFFICIENCIES to fold into the wire (section 4d):** marginal-only on the confidence path (2nd-best tree lazy);
   DROP the obl calibrator (raw marginal beats it); ship single-root (free); one universal marginal replaces the
   per-reader cue sets.
