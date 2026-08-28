# Brain analysis + design -- content-addressable retrieval over a separated store (p3)

**Opened by the solver, 2026-08-26.** The re-located binding deviation: the bind OPERATOR is validated
(`the_core_binding_operator_may_not_be_brain_faithful` SOLVED/EXCELLENT); the deviation is one level up,
in the flat-superposition RETRIEVAL. This doc pins the brain mechanism, the arms, and what would falsify.

## 1. HOW THE BRAIN DOES THIS (the opening move, before any tool)

**Which structure, and are we replicating or substituting?**

- **Cue-based content-addressable retrieval (PINNED).** Declarative/working memory is not indexed by an
  exact address; a (possibly partial) CUE is matched in parallel against stored items and the best match
  is retrieved, with similarity-based interference between items sharing cue features (Lewis & Vasishth
  2005 ACT-R cue-based retrieval; McElree direct-access retrieval). Audit E3 already PINS this for
  coreference ("who is 'he'" = match the pronoun's partial cue against the discourse entities).
- **Hippocampal implementation is a matched pair (PINNED).** Dentate-gyrus PATTERN SEPARATION
  orthogonalises overlapping memories (Leutgeb 2007; McHugh 2007 DG-NMDAR KO fails separation while CA3
  completion stays intact -- a double dissociation), and CA3 PATTERN COMPLETION settles a partial cue
  onto the stored attractor (Marr 1971; Treves & Rolls 1994). **CA3's defining behaviour is PARTIAL-cue
  robustness** (Nakazawa 2002: CA3-NMDAR knockouts retrieve normally from FULL cues and fail
  SELECTIVELY from PARTIAL ones). This is the exact axis the win must live on.
- **The brain SEPARATES then MATCHES; it does not superpose-and-unmix, and it does not look up by an
  exact key.** Our `situation_model_multibank` does the opposite: `stable_bank_id(hash(event_idx))`, an
  exact-key hash whose own docstring says "routing accuracy 1.0 by construction" -- there is no graceful
  path for a partial cue.

**OUR-INVENTION-UNDER-TEST (labelled):** representing "separated slots" as M explicit vectors and doing
the parallel match with `iterative_attractor` (modern-Hopfield / Kanerva SDM, the standard comp-neuro
proxy the organ itself cites: Krotov-Hopfield 2016, Ramsauer 2021, Kanerva 2010). We copy the
COMPUTATION (separate + content-addressable match-and-complete); we SWEEP the parameters (CA3 temp,
steps, alpha; DG expand, sparsity).

## 2. THE DECOMPOSITION (why the win is two levers, each separately controlled)

Storage: item i = `bind(key_i, val_i)`, `key_i = bind(entity_i, event_i)`, `val_i = bind(role_i,
filler_i)`. Retrieval recovers `filler_i` (argmax over |V|), given the role and a PARTIAL key cue.

The brain fix is TWO things and the controls isolate each:
1. **Content-addressing (a partial cue recovers the right slot identity by matching).** Without it, a
   degraded key used to unbind directly gives garbage. Control: `FLAT_CLEANKEY` cleans the cue by
   matching against the key codebook FIRST -- available to a flat store too.
2. **Separation (the recovered value is crosstalk-free).** `FLAT_CLEANKEY` still reads a SUPERPOSED
   bundle, so its value carries crosstalk from the other M-1 items. `SEP_CA` reads a clean separated
   slot. `SEP_CA - FLAT_CLEANKEY` = the value-separation lever, isolated.

Load-bearing NEGATIVE (from the binding SOLVED, re-measured here): `CA3_ON_FLAT` settles the FLAT
readback via the real attractor -- it MUST tie argmax cleanup. You cannot clean your way out of
superposition; the fix is architecture, not terminal cleanup.

## 3. ARMS (each excludes something specific)

| arm | what it is | excludes |
|---|---|---|
| FLAT | one hdlab bundle; unbind by the degraded cue directly | -- (the thing to beat; the naive superpose-and-unmix) |
| HASH_BANK | MultiBankAccumulateRegister-style hash routing on the address | the current LIVE default; partial address -> wrong bank |
| FLAT_CLEANKEY | content-address the KEY then unbind the FLAT bundle | "cleaning the cue is enough without separating values" |
| SEP_ARGMAX | separated slots + 1-step argmax match (no recurrence) | isolates whether the CA3 RECURRENCE adds anything |
| SEP_CA | separated slots + iterative CA3 attractor match | the brain fix |
| SEP_CA_DG | + DG pattern separation on the keys | the DG->CA3 matched pair, for OVERLAPPING cues |
| CA3_ON_FLAT | CA3 settle on the FLAT readback | "clean up harder" -- must TIE argmax |
| FLAT_MATCHED | FLAT at d_big so total reals ~ the separated store's | "SEP just has more memory" |
| SHUFFLED_KEYS (twin) | key->slot correspondence destroyed | "the match works regardless of key->content map" |
| RANDOM_ROUTE (twin) | pick a random slot | "any separated store + any pick wins" |
| NO_ADDRESS (twin) | all keys identical -> cue cannot discriminate | "separation without a content address does the work" |

## 4. THE PARTIAL CUE (the brain's, not a convenient one)

- **fragment (DEFAULT, Nakazawa/CA3):** keep a (1-p) fraction of key components at the true phase; the
  rest are RANDOM phases (a fragment of the pattern, the rest absent/noise). `cos(cue, true) ~ (1-p)`,
  ~0 with every other key -> a genuine partial cue whose nearest stored pattern is still the target if
  (1-p) clears the inter-key noise floor. p is the DEGRADED fraction; p=0 is the full cue.
- **interference (drill, the fan effect):** dropped components carry a coherent DONOR item's phase (a
  competing memory). Conflates partial-recall with similarity interference; this is the regime the
  DG->CA3 pair exists for. Reported separately at rho=0.5.
- **REJECTED an early model:** donor-fill at every p made the cue MORE similar to the donor than the
  target at high p (cos 0.7 donor vs 0.3 target) -- not a partial cue, an impossible one. Diagnosed in
  self-test and replaced with random-phase fragments. (Kept as the `interference` axis, honestly named.)

## 5. WHY NOT REAL McGUFFEY TEXT (disk outranks the brief)

The brief names E2's `LOCALIZED_WALL` cell as the natural harness. On disk that cell's wall is the
FRONT-END frozen encoder (role attribution ~0.5); its `SituationWM` loop SATURATES at 1.000 with clean
inputs, and its retrieval is exact-address -- it is NOT a partial-cue retrieval test. The real reader
(`situation_reader.read()`) has event-extraction recall ~0.32 (tagger-capped, its own docstring), which
would swamp the retrieval-architecture signal with extraction noise. So we hold inputs CLEAN and vary
ONLY the retrieval under a partial cue (one variable), exactly as LOCALIZED_WALL holds the loop constant
and varies the front-end. This is an ISOLATION result and is labelled as such (isolation win != capability).

## 6. THE BAR + WHAT WOULD FALSIFY

BAR (from PROBLEM.md): on the live-register retrieval task under a partial cue, floor recomputed on its
population, content-addressable retrieval over the SEPARATED store beats the exact-key HASH route
CI-separated over the strongest floor's UPPER bound, info-free twin LOSING CI-separated, CI half-width +
null p95 reported; sweep the matching/completion parameters.

Falsifiers I actively look for:
- At the FULL cue (p=0) the arms TIE -> then the flat/hash store is adequate for a non-partial regime,
  and the finding is "cues are never partial in the current live regime" (a real, decisive-either-way PASS).
- SEP_ARGMAX == SEP_CA everywhere -> the CA3 RECURRENCE buys nothing; the mechanism is content-addressing,
  not attractor completion (honest, and I say so).
- DG never helps even at rho>0 -> the DG->CA3 pairing is not realised here (honest negative).
- A twin does NOT collapse -> the DV leaks; no treatment number may be read.

## 7. GUARDS (code, not prose)

- FLAT bundle asserted bit-equal to `hdlab.bundling.bundle`; single-item unbind exact -> the baseline IS
  the live op.
- FHRR similarity `Re(conj(a)*b)` asserted equal to the real dot of the `[Re;Im]` stack fed to
  `iterative_attractor` -> the CA input is faithful FHRR, not a re-derivation.
- ORACLE p=0 positive control (SEP_CA and HASH near ceiling) -> the DV is valid.
- Twins asserted to collapse in the self-test.
