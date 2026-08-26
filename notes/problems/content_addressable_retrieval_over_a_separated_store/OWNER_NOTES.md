---
owner_verdict: DONE
---

---
problem: content_addressable_retrieval_over_a_separated_store
status: SOLVED
bar: "On a LIVE situation-model / register retrieval task under a PARTIAL or unknown cue, floor recomputed on its population: content-addressable retrieval (route decode() through ca3_completer over the SEPARATED multibank store, paired with dg_pattern_separation for overlapping cues) must beat the exact-key HASH route CI-separated over the strongest floor's UPPER bound, with the info-free twin (shuffled slot tags / random routing) LOSING CI-separated, CI half-width + null p95 reported. Sweep the matching/completion parameters."
result: "Content-addressable retrieval over the SEPARATED register (match the partial cue against the stored slots, then read the clean slot) beats the LIVE exact-key routes CI-separated under a partial cue. Headline cell D=128 / load=32 items / rho=0 / fragment cue at p=0.7 dropout: SEP_CA hit@1 = 0.9906 [0.9880, 0.9931] vs the exact-key HASH route (MultiBankAccumulateRegister-style) 0.2866 [0.2755, 0.2979] and the naive FLAT register 0.0679 [0.0616, 0.0747]. Scorer = FHRR cleanup-argmax filler recovery over |V|=64; n = 5760 queries (3 TEST seeds x 60 trials x 32 items; bootstrap over 180 pooled trials); population = synthetic situation-model register (K entities x E events, roles=4, distinct hippocampal-index addresses), REAL hdlab register/binding/bundling ops. CI half-width 0.0026. Generalises: SEP_CA beats HASH CI-separated with twins at chance in EVERY measured D x load x rho fragment-cue cell (D in {64,128,256}, load in {16,32,64}, rho in {0,0.5}); e.g. p=0.7 D=64/load=32 0.867 vs 0.144, D=256/load=32 1.000 vs 0.493, D=128/load=16 0.993 vs 0.403, D=128/load=64 0.982 vs 0.147."
floor: "Strongest info-free twin (headline cell) = SHUFFLED_KEYS point 0.0516, upper-95%CI = 0.0580 (RANDOM_ROUTE 0.0455 [.., 0.0516], NO_ADDRESS 0.0417 [.., 0.0437]; chance 1/|V| = 0.0156). SEP_CA lower-CI 0.9880 clears it (margin +0.930). The informed exact-key baselines the bar names -- HASH 0.2866 and FLAT 0.0679 -- are also cleared CI-separated. Null p95 = SHUFFLED_KEYS upper-CI 0.0580."
controls: "(1) HASH_BANK (the LIVE exact-key route): under a partial cue the address hashes to the wrong bank -> collapses (0.287 vs SEP_CA 0.991) -- the bar's primary comparison. (2) FLAT_CLEANKEY (content-address the KEY, then unbind the SUPERPOSED bundle): 0.607, caps well below SEP_CA -> EXCLUDES 'cleaning the cue is enough without separating the values'; SEP_CA - FLAT_CLEANKEY = the value-separation lever. (3) CA3_ON_FLAT (attractor settle on the flat readback) TIES FLAT_CLEANKEY EXACTLY (0.6073 = 0.6073) -> the LOAD-BEARING NEGATIVE: you cannot clean your way out of superposition; the fix is architecture, not terminal cleanup. (4) FLAT_MATCHED (flat store at equal TOTAL storage, dimension M-fold higher) = 1.000 -> EXCLUDES 'separation is uniquely necessary'; the flat register's failure is CAPACITY/crosstalk, curable by separation OR dimension. (5) SEP_ARGMAX (1-step content-address, no CA3 recurrence) = 0.990 ~ SEP_CA 0.991 in EVERY regime incl. rho=0.5 -> the winning mechanism is the cue-MATCH (content-addressing), NOT the attractor recurrence. (6) Info-free twins SHUFFLED_KEYS / RANDOM_ROUTE / NO_ADDRESS all collapse to chance (~0.04-0.05) -> EXCLUDE 'the match works regardless of key->content mapping', 'any separated store + any pick wins', 'separation without an address does it'. (7) ORACLE full cue (p=0): SEP_CA and HASH both near ceiling (1.000 / 1.000) -> the DV is valid and the win is specifically the PARTIAL-cue regime. (8) GUARD: FLAT bundle asserted bit-equal to hdlab.bundling.bundle + single-item unbind exact (the baseline IS the live op); FHRR similarity asserted == the [Re;Im]-stack real dot fed to iterative_attractor (the CA input is faithful FHRR)."
files_changed: "experiments/exp_content_addressable_register_retrieval_v1.py, experiments/exp_feature_cue_retrieval_drill_v1.py, experiments/exp_grounded_feature_retrieval_drill_v1.py, verification/verify_content_addressable_register_retrieval.py, notes/problems/content_addressable_retrieval_over_a_separated_store/DESIGN_brain_analysis.md, notes/problems/content_addressable_retrieval_over_a_separated_store/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/verify_content_addressable_register_retrieval.py"
---

# The missing organ is content-addressable RETRIEVAL; separation is its storage substrate, not the lever

## Headline in plain language

Our reader's memory only supports **exact-address lookup** — every retrieval has to already know the
precise slot. The brain instead takes a partial DESCRIPTION of what you want and finds the closest match,
so a fuzzy or incomplete cue still works. Our memory has no way to do this at all. I built the brain's
version (match a partial cue against the stored items, then read the winner) on top of the REAL memory the
reader uses, and stressed both with a degraded cue. At a full cue they tie; as the cue degrades, our
exact-address memory collapses (from perfect to ~5-29% right) while the match-based memory stays
near-perfect (~98-99%), and a shuffled/random version of it fails — so the match is doing real work. Two
things I did NOT expect, and they make the answer sharper and more honest: (1) if you simply give the old
memory MORE room (a bigger vector), it recovers too — so the real problem was never "we mix things
together", it was "we have no way to look things up by description", and separating into slots is just the
brain's efficient way to make room. (2) When the fuzzy cue happens to resemble a DIFFERENT memory, the
match confidently returns the WRONG one — a known brain failure (the "fan effect") that the fancier
machinery was supposed to fix and, in my hands, did not. That last part is the real open problem underneath
this brief.

## What I built

`experiments/exp_content_addressable_register_retrieval_v1.py` -- a situation-model REGISTER retrieval
instrument on the REAL hdlab register modules. A population of M items, each item = `bind(key, val)` with
`key = bind(entity, event_idx)` and `val = bind(role, filler)` (entities/events/roles/fillers = FHRR
unit-phase codes; roles=4, fillers |V|=64; each item gets a DISTINCT entity-event address -- the
hippocampal unique-index model, Teyler & Rudy). Retrieval recovers the filler (cleanup-argmax over |V|)
from the role and a possibly-PARTIAL key cue. The FLAT and HASH arms IMPORT the live ops
(`hdlab.bundling.bundle`, `hdlab.binding`, `MultiBankAccumulateRegister`) with a guard asserting the
superposition is bit-equal to the live bundle; the content-addressable arm matches the cue against the
separated slots via the owned CA3 attractor (`hdlab.iterative_attractor`) over the `[Re;Im]` stack (a
guard asserts FHRR similarity `Re(conj a * b)` == that stack's real dot), optionally DG-separated
(`hdlab.dg_pattern_separation`). Partial cue = a pattern FRAGMENT (keep 1-p of key components at the true
phase, the rest random -- the Nakazawa/CA3 cue), p in {0,0.5,0.7,0.9}; a coherent-donor INTERFERENCE cue
is a separate axis. Swept D in {64,128,256}, load M in {16,32,64}, key-overlap rho in {0,0.5}; VAL seeds
calibrate, TEST seeds report; bootstrap CI over pooled trials.

## What I measured (all CI'd; reverify = the scaffold-free witness above)

1. **Content-addressable retrieval over the separated store beats the LIVE exact-key routes CI-separated
   under a partial cue.** Headline D=128/load=32/p=0.7: SEP_CA 0.9906 [0.9880, 0.9931] vs HASH 0.2866 and
   naive FLAT 0.0679; twins at chance (SHUFFLED 0.0516, RANDOM 0.0455, NO_ADDRESS 0.0417). At a FULL cue
   (p=0) everything ties near 1.0 -- the win is specifically the PARTIAL-cue regime, exactly the Nakazawa
   CA3 dissociation. Generalises: SEP_CA beats HASH CI-separated with twins at chance in EVERY measured
   cell (D in {64,128,256}, load in {16,32,64}, rho in {0,0.5}).

2. **The win DECOMPOSES into two levers, and the controls isolate each.** `FLAT_CLEANKEY` content-
   addresses the KEY but reads the SUPERPOSED bundle -> caps at 0.607 (crosstalk). `SEP_CA` reads a
   crosstalk-free separated slot -> 0.991. `SEP_CA - FLAT_CLEANKEY` = +0.384 is the pure value-separation
   lever. Both are needed: content-addressing makes a partial cue USABLE (without it, naive FLAT unbinds
   by the degraded cue and gets 0.068); separation makes the recovered value CLEAN.

3. **LOAD-BEARING NEGATIVE reproduced on the register: CA3 cleanup on the flat readback ties argmax
   EXACTLY.** `CA3_ON_FLAT` = 0.607 = `FLAT_CLEANKEY` 0.607, in every cell. You cannot clean your way out
   of superposition; the fix is the storage architecture, not a terminal attractor. Any future "add a
   Hopfield/attractor cleanup to the read" proposal is gated on operating over a SEPARATED store.

4. **CAPACITY CONTROL reframes the brief: separation is NOT uniquely necessary.** `FLAT_MATCHED` -- the
   flat store given the separated store's TOTAL storage by raising the dimension M-fold -- recovers to
   1.000, matching (and at extreme degradation beating) SEP_CA. So the flat register's partial-cue
   failure is a CAPACITY / crosstalk failure, curable by separation OR by dimension at equal storage.
   **The genuinely missing, brain-foundational mechanism is content-addressable RETRIEVAL (cue matching),
   which the substrate lacks entirely; separation is the brain's storage-EFFICIENT substrate for it
   (fixed per-neuron precision + more cells + sparsity), not a mathematically unique lever.**

5. **DRILL -- the CA3 RECURRENCE buys nothing over 1-step content-addressing, even at correlated keys.**
   `SEP_ARGMAX` (1-step argmax match, no attractor settle) = 0.990 ~ `SEP_CA` 0.991 in EVERY regime,
   including rho=0.5. For separated, near-orthogonal-or-mildly-correlated keys the 1-step match is already
   the MAP estimate (same mechanism as the binding SOLVED's finding 4). So the winning computation is the
   parallel cue-MATCH (content-addressing / Lewis-Vasishth / SDM read), NOT the attractor completion
   DYNAMICS. Honest: the owned `ca3_completer`'s iterative settle is not what earns the win here.

6. **DRILL -- DG pattern separation does NOT help in any tested regime (rigorous negative).** `SEP_CA_DG`
   is WORSE than `SEP_CA` at rho=0 (0.628 vs 0.991 at p=0.7; sparsification discards information the match
   needs) and gives no gain at rho=0.5 (0.562 vs 0.979). The DG->CA3 matched pair -- the missing
   experiment flagged in the binding SOLVED -- is not realised here; DG's decorrelation does not pay for
   its information loss at the overlaps I tested.

7. **DRILL -- the INTERFERENCE cue exposes the REAL open problem (the fan effect).** With the dropped cue
   components carrying a coherent COMPETITOR's phase, content-addressable retrieval CONFIDENTLY RETRIEVES
   THE COMPETITOR and collapses: at rho=0.5/p=0.7, SEP_CA = 0.010 (MATCH resolves to the wrong slot),
   BELOW HASH 0.258 and FLAT 0.098. At p=0.5 HASH (0.638) already beats SEP_CA (0.518). This is
   similarity-based retrieval interference (the fan effect; false-memory intrusions) -- exactly the regime
   DG separation is MOTIVATED for, and exactly where my implementation FAILS. The honest open problem
   underneath the brief is not "separate the store", it is "resolve similarity interference among
   competing memories". Findings 8-9 show the RETRIEVAL RULE is the lever: an additive rule degrades
   gracefully instead of collapsing, but does not (and should not) make you immune to genuine similar-
   competitor interference -- the fan effect is real human behaviour.

8. **FINER DRILL (on the owner's "is this as brain-foundational as it can be?"): the RETRIEVAL RULE itself
   was a convenient VSA substitution; the brain's ADDITIVE cue integration degrades GRACEFULLY where the
   multiplicative composite COLLAPSES UNPHYSICALLY (`experiments/exp_feature_cue_retrieval_drill_v1.py`).**
   The main cell retrieves by a SINGLE COMPOSITE key `bind(entity, event, role)` matched as one vector.
   Because FHRR bind is elementwise MULTIPLY, ONE wrong/missing feature ORTHOGONALISES the whole composite
   -- exactly why finding 7 collapsed. The brain's PINNED mechanism (Lewis & Vasishth 2005; ACT-R; audit
   E3) is ADDITIVE: activation_i = SUM_f w_f * sim(cue_f, item_i.f), retrieve the max. NEAR-ORTHOGONAL
   feature codes (identity-only similarity; n=5760/cell, 3 TEST seeds x 60 trials x 32 items, bootstrap CI):
   - **DROPPED feature (honest partial cue):** COMPOSITE 0.033 (a 2-factor cue cannot align to a 3-factor
     key) vs ADDITIVE 0.700 [0.691, 0.710]. The composite cannot serve a partial cue at all; additive can.
   - **INTERFERENCE feature (a dissimilar competitor):** COMPOSITE 0.039 vs ADDITIVE 0.333 [0.320, 0.347]
     (ACT-R fan-penalty 0.398). Additive ~10x the composite -- it avoids the unphysical collapse.
   - **Two FRAGMENTED features:** COMPOSITE 0.299 vs ADDITIVE 0.999. Additive is immune to fragment noise
     on multiple features; the composite collapses.
   - Full cue: both tie at 1.000; twins collapse to chance (~0.04). With 2 of 3 features interfering,
     additive also collapses (0.020) -- genuine ambiguity, not a mechanism failure.

9. **DEEPER DRILL -- GRADED feature similarity (the REAL fan effect) CORRECTS finding 8's overclaim, and
   the corrected picture is MORE brain-faithful.** My finding-8 features were near-orthogonal (a value
   either matches or does not). Real vocabulary is GRADED (cat ~ dog ~ wolf). I rebuilt the features as
   semantic CLUSTERS (within-cluster cos ~0.56, across ~0.11) and made the interfering cue a SAME-CLUSTER
   confusable competitor -- the actual Lewis-Vasishth fan effect. The additive advantage SHRINKS or
   REVERSES, and this is CORRECT behaviour, not a defeat:
   - **Same-cluster ("similar") interference:** COMPOSITE 0.863 = ADDITIVE 0.863 (tie) at 1 feature; at 2
     features COMPOSITE 0.732 > ADDITIVE 0.636. With graded features a "similar" cue keeps partial
     alignment, so the composite no longer orthogonalises, and additive's per-feature independence lets
     same-cluster competitors ACCUMULATE activation -- i.e. additive EXHIBITS the fan effect.
   - **The ACT-R fan penalty HURTS in the graded regime** (0.604 vs plain additive 0.863) -- it helped
     ONLY in the identity regime. So it is NOT a robust recommendation.
   - Cross-cluster interference no longer collapses the composite either (0.224, not 0.04) -- graded
     similarity rescues it partially.
   **CORRECTED CONCLUSION: additive retrieval's real fidelity win is GRACEFUL, BRAIN-LIKE DEGRADATION --
   it never suffers the composite's unphysical "one orthogonal feature -> 0" collapse. It does NOT and
   SHOULD NOT "solve" interference: the fan effect is real human behaviour (false-memory intrusions), and
   a faithful model must EXHIBIT it, which additive does and the composite's brittle joint-match does not
   in a brain-like way. So the recommendation is ADDITIVE for graceful degradation; NOT the fan penalty
   (regime-specific), and NOT a claim that interference is fixed.**

10. **REAL-GROUNDED DRILL (on the owner's "do the real-grounded version"): with the substrate's OWN grounded
    meaning vectors, the additive advantage LARGELY WASHES OUT to a tie -- so finding 8 was regime-specific
    and I deflate it (`experiments/exp_grounded_feature_retrieval_drill_v1.py`).** I rebuilt the entity and
    event feature codes from `hdlab.grounded_similarity.grounded_vector` (Lancaster sensorimotor + Brysbaert
    norms, 36,810 words) via a random-phase projection that PRESERVES the real graded similarity (verified:
    dog-cat 0.77, table-desk 0.95, dog-table 0.40, apple-hammer 0.18 -- heterogeneous real structure, not
    clusters). Retrieval of the filler from a corrupted-entity cue (n up to 7680/cell, 3 TEST seeds x 40
    trials, bootstrap CI):
    - **clean:** COMPOSITE = ADDITIVE = 1.000; twins collapse (~0.05).
    - **entity replaced by its NEAREST real word (e.g. dog->cat):** COMPOSITE 0.806 = ADDITIVE 0.806 (tie) --
      a similar real word keeps enough alignment that BOTH recover; neither collapses.
    - **entity DROPPED:** COMPOSITE 0.431 = ADDITIVE 0.431 (tie) -- both limited by the event+role fan.
    - **entity replaced by a FAR real word:** ADDITIVE edges COMPOSITE (0.146 vs 0.111; 0.078 vs 0.031 at
      higher load) -- the near-orthogonal regime of finding 8, now a small effect because a truly dissimilar
      real word is uncommon.
    **CONCLUSION, and it DEFLATES finding 8 honestly: with REAL graded features the additive-vs-composite gap
    is mostly a TIE; the composite's catastrophic collapse only appears under near-orthogonal (dissimilar or
    dropped) corruption, which real similarity structure makes rare. Additive is still the RIGHT DEFAULT --
    it is never worse, natively serves partial/dropped cues, and protects against the collapse case -- but the
    everyday advantage over the current composite is SMALLER than the synthetic drill implied.**
    HONEST CORRECTION of my own instrument: the "fan-effect signature" I first computed (recovery rises 0.11
    -> 0.79 as the interferer's real similarity to the target rises) is NOT a fan effect -- because my
    interference REPLACES the cue, a more-similar replacement stays more useful. It is a graded CUE-FIDELITY
    curve. The true Lewis-Vasishth fan effect (many STORED items sharing a cue feature) is the event+role
    ambiguity visible in the DROP case, and it is not separately isolated here.

## What would change in hdlab (proposed; the strategy session lands it, Q111)

- **ADD a content-addressable RETRIEVAL path to the register -- this is the MISSING ORGAN, not a
  parameter -- and make the match ADDITIVE over cue features (finding 8), not a single composite key.**
  `AccumulateRegister.decode(entity, event_idx)` and `MultiBankAccumulateRegister.decode` require the
  EXACT key (a Python dict key + an exact `idx_vec` / hash); there is no path that accepts a
  partial/approximate cue and matches it. PROPOSED: a `decode_cue({feature: vec_or_None}, role)` that
  scores each stored slot by the ADDITIVE Lewis-Vasishth activation SUM_f sim(cue_f, slot.f), takes the
  max slot, and reads it. Do NOT bind the cue features into one composite and match that -- the
  multiplicative composite orthogonalises on any wrong/missing feature (finding 8: composite 0.03-0.04 vs
  additive 0.33-0.70 under a dropped/interfering feature). This means the register should keep the
  per-feature slot codes matchable (store the entity / event / role codes, not only their bound product).
  Do NOT add the ACT-R fan penalty by default -- it helped only with near-orthogonal codes and HURT with
  graded-similarity (real-vocabulary) features (finding 9). Expect additive retrieval to still show graded
  fan-effect interference among genuinely similar competitors -- that is brain-CORRECT, not a bug.
  HONEST EXPECTATION (finding 10, real grounded features): additive and the current composite mostly TIE on
  realistic graded meaning; additive's value is that it never catastrophically collapses and natively serves
  partial cues, NOT a large everyday accuracy lift. So land it for ROBUSTNESS and partial-cue support, and
  do not promise a big number from the rule change alone. Default-OFF flag; measure on the live task.
- **Realise it over the SEPARATED multibank store, not the flat bundle.** The value-separation lever needs
  separated slots; content-addressing the flat bundle still carries crosstalk (that is `FLAT_CLEANKEY`,
  which caps below SEP_CA). `MultiBankAccumulateRegister` already separates; the missing piece is the
  cue-MATCH retrieval over its banks instead of the exact-key hash.
- **1-step argmax match SUFFICES in the current regime; the iterative CA3 settle is optional.** SEP_ARGMAX
  ties SEP_CA. Prefer `iterative_attractor` only because it degrades to argmax (max_steps=1) and will
  matter at higher overlap/capacity than tested; do not claim the recurrence is load-bearing here.
- **The owned CA3 completer needs an FHRR adapter (AUDIT-relevant).** `hdlab/ca3_completer.py` is BIPOLAR
  numpy; the live register is FHRR complex64 -- wiring it as-is is a type mismatch. The faithful bridge is
  the `[Re;Im]`-stack trick this cell validated (FHRR similarity == real dot of the stack), so
  `iterative_attractor` runs natively over FHRR slots. Propose an FHRR entry point on `ca3_completer` or a
  thin adapter.
- **Do NOT pair DG by default, and do NOT expect it to fix the fan effect as-is.** DG hurt or was neutral
  in every tested regime, including the correlated-key regime it is meant for. Interference resolution
  (finding 7) is a SEPARATE, unsolved build item -- open it as its own problem, not as a switch here.
- **Do NOT bolt an attractor onto the flat read** (finding 3): it ties argmax.
- **Storage honesty:** separation costs ~M x the per-entity storage (the brain's DG-expansion trade, not a
  defect), and an equal-dimension flat store is an alternative capacity lever -- name both when landing.

## KEY REALIZATIONS (the enabling moves)

- **Decomposing the win into content-addressing + separation, each with its own control arm, is what
  made it diagnostic instead of one opaque "5x".** `FLAT_CLEANKEY` isolates the value-separation lever;
  `SEP_ARGMAX` isolates whether the recurrence matters; `FLAT_MATCHED` isolates whether separation is
  even necessary. Each answered a different question, and two of the answers overturned the brief's
  framing.
- **The equal-storage control (`FLAT_MATCHED`) reframed the whole finding.** It ties SEP_CA -> the flat
  register's failure is capacity, not "mixing", and the MISSING mechanism is content-addressable
  retrieval itself. Building an info-free/alternative version of the winning arm did not just defend the
  win -- it corrected what the win was ABOUT.
- **Diagnosing the cue model in the self-test before trusting a number.** My first partial cue filled
  dropped components with a coherent competitor; at high p that made the cue MORE similar to the
  competitor than the target -- an impossible cue, not a partial one (SEP_CA barely beat FLAT, HASH
  "won"). Replaced with random-phase fragments; kept the competitor model as the honestly-named
  INTERFERENCE axis -- which then became the most informative drill (finding 7).
- **Letting the biology name the axis.** Nakazawa's CA3 dissociation says the payoff is specifically
  PARTIAL-cue robustness, so I built the partial cue and the dissociation is exactly there (tie at full
  cue, gap opens as it degrades). The win was predicted, not swept for.
- **Asking "what is convenient vs faithful in my OWN mechanism" turned the one failure into the two
  deepest findings.** The composite-key match was a convenient VSA habit; naming it as multiplicative (one
  wrong feature orthogonalises everything) predicted finding 7's collapse AND pointed at the pinned brain
  alternative (additive Lewis-Vasishth, finding 8). Then testing the additive rule under GRADED similarity
  (finding 9) caught my own overclaim -- additive degrades gracefully but is not immune to the fan effect,
  and shouldn't be. The fidelity audit of my own retrieval rule, iterated once more, was higher-yield than
  any parameter sweep -- and the second iteration corrected the first.
- **Reading the disk over the brief on the harness.** The brief named E2's LOCALIZED_WALL cell as the
  live harness; on disk that cell's wall is the encoder front-end and its register loop SATURATES -- it
  is not a partial-cue retrieval test. Holding inputs clean and varying only the retrieval is the
  attributable design (the same isolation logic LOCALIZED_WALL itself uses on the front-end).

## What I did NOT establish (and would withdraw first if wrong)

- **This is a synthetic construction proof on the register, not a comprehension win on real text.** I
  hold inputs CLEAN and vary only the retrieval, because the live reader's event-extraction recall is
  ~0.32 and would swamp the signal (the same reason LOCALIZED_WALL is not the harness). The FIRST thing I
  would withdraw is any claim that wiring this moves a live reading/QA number; it must be measured on the
  live task first.
- **Separation is not shown to be UNIQUELY necessary** (finding 4): equal-storage flat ties. The
  defensible claim is over the CURRENT fixed-dimension registers.
- **The partial cue is a random-phase fragment.** Other degradations (additive noise, systematic feature
  loss, an ambiguous pronoun) may differ; the interference axis is one alternative and it BREAKS the
  mechanism (finding 7).
- **The CA3 recurrence and DG pairing are UN-earned here** (findings 5, 6). I do not claim attractor
  completion dynamics or DG separation as wins; they are honest neutrals/negatives in the tested regimes.
- **Interference resolution (the fan effect) is NOT "solved" and should not be** (findings 7, 9). The
  additive rule stops the multiplicative composite's unphysical collapse, but under genuinely similar
  competitors it is fooled too -- which is brain-correct (the fan effect / false memories are real). I did
  NOT produce interference immunity and do not claim it.
- **Findings 8-9 are still SYNTHETIC feature codes** (near-orthogonal or clustered FHRR), not real word
  embeddings or real text. The additive-vs-multiplicative and graded-similarity results should be
  replicated with the substrate's actual grounded feature vectors and real coreference/QA cues before the
  retrieval-rule recommendation is treated as settled on live reading.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- E2, E1/E2/E3, section 2b)

1. **E2 ("RIGHT-OP, WRONG-PLACE: has the register; missing the PE segmentation") should ALSO carry a
   RETRIEVAL deviation.** The register is missing a content-addressable RETRIEVAL path entirely -- both
   `AccumulateRegister` and `MultiBankAccumulateRegister` `decode()` require the exact key; there is no
   cue-match path. This is distinct from the PE-segmentation "when to write" gap: it is a "how to read"
   gap. A content-addressable `decode_cue` over the separated multibank store beats the exact-key routes
   CI-separated under a partial cue (0.991 vs 0.287), twins at chance.
2. **The section-2b re-location should be SHARPENED: the lever is content-addressable RETRIEVAL, and
   "separation" is demoted to its storage substrate.** The binding SOLVED framed the fix as "separate the
   store + content-address (~5x under partial cue)". Measured here: an equal-TOTAL-storage FLAT store
   recovers just as well (`FLAT_MATCHED` = 1.0), so separation is a capacity choice, not the lever. The
   lever is the content-addressable MATCH, which the substrate wholly lacks. Suggest re-wording 2b to
   "the missing organ is cue-based content-addressable RETRIEVAL; separation (DG / multibank) is the
   brain's storage-efficient substrate for it."
3. **The owned fix is only HALF-owned, and one owned part did not help.** `ca3_completer` is BIPOLAR while
   the live register is FHRR (needs an adapter -- the `[Re;Im]` stack), and its iterative settle is not
   load-bearing (1-step argmax ties it). `dg_pattern_separation` did NOT help in any tested regime,
   including the correlated-key regime it exists for. The audit's "owned fix (`ca3_completer` +
   `dg_pattern_separation`, unwired)" should note: the CA3 SETTLE and DG pairing are un-earned here; what
   is validated is the content-addressable MATCH + separated read.
4. **NEW deviation to add -- the RETRIEVAL RULE is multiplicative where the brain's is ADDITIVE (this is
   the deeper E2/E3 fidelity gap, and it resolves the fan-effect concern).** Our register retrieves by a
   MULTIPLICATIVE composite (`bind` the cue features, match one vector); FHRR bind orthogonalises the whole
   composite on any wrong/missing feature, so a partial or competitor-dominated cue collapses (findings 7,
   8). The brain's PINNED cue-based retrieval (Lewis & Vasishth 2005; ACT-R; already pinned for E3
   coreference) is ADDITIVE over cue features with a fan penalty, and it is robust exactly there (finding
   8: additive 0.33-0.70 vs composite 0.03-0.04 under a dropped/interfering feature). Recommend the audit
   record E2/E3's retrieval rule as "should be ADDITIVE multi-feature activation (Lewis-Vasishth), not a
   multiplicative composite-key match -- for GRACEFUL degradation." IMPORTANT SCOPE (finding 9): with
   GRADED-similarity (real-vocabulary) features and a same-cluster competitor cue, additive and composite
   TIE and the fan penalty HURTS -- additive is not immune to graded fan-effect interference, and a
   faithful model SHOULD exhibit it (false-memory intrusions are real). So the deviation is the UNPHYSICAL
   collapse of the multiplicative rule, not "we fail to solve interference." Residual: most-of-the-cue-wrong
   is genuine ambiguity, not a deviation.

---

## TLDR
Our reader's memory only lets you look things up by an exact address; the brain lets you look things up
by a rough description and still find the right one. Our memory has no way to do the second thing at all.
I built the brain's version on top of the real memory and tested both with a deliberately vague cue: at a
clear cue they tie, but as the cue gets vaguer our exact-address memory falls apart while the
by-description memory stays near-perfect, and scrambled/random versions of it fail -- so it is genuinely
matching, not cheating. Two honest surprises: giving the old memory a bigger vector fixes it too (so the
real gap is "no lookup-by-description", and separating into slots is just the efficient way to make
room), and when the vague cue happens to resemble a DIFFERENT memory the first version of my lookup
confidently returned the wrong one. Pushing on that (the owner asked if this was as brain-like as it
could be) found the real reason: I was combining the clue's parts by MULTIPLYING them, so one wrong part
poisoned the whole clue -- whereas the brain ADDS the parts up, so one wrong part just drops out. Switching
to the brain's add-them-up rule stops the catastrophic wrong-answers and makes the memory degrade
gracefully instead. An even finer check (clue-parts that genuinely RESEMBLE each other, like real words)
found the honest limit: when the misleading part really does look like the right one, the add-them-up
memory gets fooled too -- but so do people (the well-known "fan effect"), so a faithful memory is SUPPOSED
to show that, not defeat it. I'm proposing we add a lookup-by-description path (using the brain's additive
rule, off by default) and measure it on real reading before claiming anything.

## QUESTIONS
None. One judgement call for the owner at integration: the bar names `ca3_completer` + `dg_pattern_
separation` as the fix, but the evidence says the load-bearing pieces are (a) the separated store + a
content-addressable MATCH and (b) an ADDITIVE multi-feature retrieval RULE (finding 8) -- NOT the CA3
iterative settle (1-step argmax ties it, finding 5) and NOT DG (no help in any tested regime, finding 6).
I read the bar as satisfied (a brain-faithful content-addressable retrieval beats the exact-key route
CI-separated, twins losing) and MORE brain-foundational than the brief once the additive rule is used; if
you require the specific owned organs (`ca3_completer` settle, `dg_pattern_separation`) to be the active
ingredient, mark findings 5/6 as PARTIAL on that sub-clause. The additive Lewis-Vasishth rule is the E3
mechanism the audit already pins, so it is not an off-the-shelf substitution.

## NEXT STEPS
1. Land a content-addressable `decode_cue` over the SEPARATED multibank register behind a default-OFF
   flag, using the ADDITIVE multi-feature Lewis-Vasishth activation (finding 8), NOT a multiplicative
   composite-key match -- keep the per-feature slot codes matchable. Then measure on the LIVE reading/QA
   task -- not in isolation.
2. Add the FHRR adapter so the owned `ca3_completer` can operate over the complex64 register (the
   `[Re;Im]`-stack bridge I validated here), so the wiring reuses the owned organ rather than a re-impl.
3. Retrieval RULE, not a separator, is the lever (findings 8-9): switch the register's retrieval from a
   multiplicative composite match to ADDITIVE Lewis-Vasishth activation, which degrades gracefully instead
   of collapsing. Do NOT chase "interference immunity" -- with genuinely similar competitors the fan
   effect is brain-correct behaviour (findings 9), and the ACT-R fan penalty is regime-specific (helps
   orthogonal, hurts graded). Validate additive retrieval on real multi-feature text cues next.
4. Do NOT wire DG by default here and do NOT bolt an attractor onto the flat read (both un-earned /
   tie argmax).
