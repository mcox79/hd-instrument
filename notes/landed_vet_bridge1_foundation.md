# Landed-VET (AUDIT-ONLY) — BRIDGE-1 / C-AB foundation before C-C

Auditor: Skunkworks (independent, AUDIT-ONLY). Date 2026-08-05. Branch dataprep/mcguffey-graded-corpus.
Method: READ-THE-CODE + independent .venv recompute off disk (not report-trust). Recompute script
reproduced every load-bearing metrics.json number bit-for-bit at seed 0 (Bopen 1.000/0.500/0.250,
theta witness BLOCK_HIGH=+0.6118769 / BLOCK_LOW=-0.2923 / random-theta≈-0.0014, subset-A no-regression
1.000). LOCAL-only; no push.

Cells: 96e8e8404 (governor grounding), 761211bf6 (confirmation), b226cfad6 (two-stage v2 SHAPE),
c555bdb34/9ce85a298 (open-vocab). Frozen valuation = exp_grounded_appraisal_sim_earned_v1 theta.

## Per-axis verdict (MEASURED = independently recomputed; else REPORTED)

### AXIS 1 — Leakage / construction-determination:  CLEAN (MEASURED)
- Bopen target nouns `{canoe,colt,contract,drummer,essay,fence,ledger,nephew,sailor,statue,tenant,
  toddler}` and Bgap `{ankle,elbow,knee,lever,vase,wire}` are EMPTY-intersection with every closed
  lexicon (GOAL_OBJECT/ADVERSARIAL/ANIMATE_HARMABLE whitelists + BODY_PART_SUPPLEMENT), with subset A,
  and with v2/conf items. The noun axis is GENUINELY open-vocab.
- REAL_ANIMACY_MAP ∩ subset-A vocab = ∅ (scope-of-application holds; subset A structurally unreachable
  by the event stage → its 0.962 is unchanged, recomputed subset-A two_stage=governor=1.000 seed0).
- Independent WordNet lookup (no supplement) reproduces the exact animacy of all 12 Bopen objects: 6
  inanimate (object/abstract), 6 animate (person/animal). Gold is semantically correct per item.
- No item sneaks into a covered set. Bopen is truly open on the patient-category axis.

### AXIS 2 — Control soundness:  REAL DISCRIMINATORS (MEASURED)
- Bopen governor-only = 0.500 (recomputed): UNK governor → perceptron emits RECIPROCITY (sign −1) for
  all 12, correct on the 6 NEUTRAL, wrong on the 6 BLOCK_HIGH. Chance by construction, not tuned.
- Scrambled-animacy collapses the lift: recomputed seed0 = 0.250 (mean 0.400), i.e. BELOW chance —
  permuting the animacy values systematically INVERTS the within-pair decision, proving the correct
  animacy signal (not merely "an extra feature") carries it. lift_Bopen = +0.600.
- BOW control = 0.500 (disjoint train/test vocab → informative tokens OOV). Real discriminator.
- These are not trivially-passable: the governor and BOW arms genuinely cannot see the object identity.

### AXIS 3 — SHAPE vs CAPABILITY:  Director's line HOLDS, with ONE framing tightening
- v2 (closed hand-lexicon OBJECT_EVENT_CLASS) = construction-bounded SHAPE proof. Correct label.
- Open-vocab Bopen=1.000 IS a real capability BUT ONLY on the PATIENT-ANIMACY axis. Verified: within
  every Bopen pair the governor is held fixed and is force+UNK for both members, so the ONLY thing that
  separates the pair is the object's WordNet animacy → the real organ genuinely produces the split.
- ⚠️ TIGHTENING (not an error, but must not be over-read): the animate→BLOCK_HIGH branch is a CONJUNCTION
  `animacy==animate AND gov_verb ∈ FORCE_CLASS_HARM_REAL AND gov UNK`. FORCE_CLASS_HARM_REAL is a
  HAND-AUTHORED closed set that was extended to include EXACTLY the 6 Bopen verbs
  (batter/clobber/wallop/pummel/maul/claw) — recomputed: all 6 present, all 6 UNK to the governor. So
  the VERB/force axis is NOT open-vocab; it is test-fitted. This does not manufacture the within-pair
  distinction (verb is constant within a pair) so the animacy-capability claim stands, but the overall
  "event-assembly" is open on ONE axis (patient category) and CLOSED on the other (force-verb identity).
- The `inanimate→NEUTRAL` rule is UNCONDITIONAL. It only survives because subset A (which contains
  abstract HARM nouns insult/curse/threat/penalty that WordNet also calls inanimate) is SCOPED OUT. The
  organ cannot tell an abstract-harm-noun from an abstract-goal-noun; applied universally it would
  regress subset A. Real boundary, honestly documented, but load-bearing for the certified statement.
- theta genuinely drives the valuation (see Axis 4) — the capability is not carried by a valence table.

### AXIS 4 — theta WITNESS:  GENUINE (MEASURED)
- Recomputed: valence(BLOCK_HIGH)=+0.612, BLOCK_LOW=−0.292, RECIPROCITY=−0.995, NEUTRAL=−0.366;
  random-theta valence(BLOCK_HIGH)=−0.001 (≈0). The earned/frozen sim theta separates harm-congruent
  from all else; a random theta does not. CONG/COPE only supply the (congruence,coping) DIMS (the
  supplied innate appraisal schema); the VALUE is a theta forward pass over FHRR-encoded dims, not a
  congruence→stored-valence lookup. Witness is real.

### AXIS 5 — The gaps:  BOTH REAL + CORRECTLY SCOPED; no hidden 3rd bug-gap
- Body-part WordNet gap: recomputed ankle/elbow/knee → inanimate → Bgap two_stage=0.500 (= governor,
  no lift). Genuine raw-organ miss, honestly quantified, supplement deliberately NOT extended to cover
  the test words. Real.
- Social-relational ≠ animacy: recomputed B_two_stage_real=0.833 (10/12) and Bgen=0.750 (6/8) — the
  shortfall is EXACTLY the adversarial items (aided/comforted enemy; helped rival; comforted thief),
  where both patients are `person`(animate) so animacy cannot flip the sign and the HELP governor wins.
  Correctly routed out to a relational/social-appraisal lexicon. Real.
- Third item worth surfacing (NOT a bug, a framing limit): the force-verb lexicon is closed/test-fitted
  (Axis 3) and the STAGE-2b situation/discourse port (THREAT/BENIGN words, subset C) was NEVER
  open-vocab-tested — it remains closed-lexicon SHAPE only. C-C must not treat any discourse/situation
  grounding as a measured capability.

### AXIS 6 — Promote/wire readiness
- READY to promote as a NARROW, HONESTLY-BOUNDED piece: (governor sense-select stage-1) +
  (animacy-axis event override on concrete artifact-vs-animate patients, real WordNet). This is the
  first genuinely open-vocab brick and is scramble/BOW/governor-controlled and no-regression on A.
- NOT ready to promote as: general "event-assembly", force-verb identification, abstract-patient
  handling, or any discourse/situation grounding — those are closed-lexicon shape or out of scope.

## CERTIFIED capability statement (what C-C may build on)
REAL / open-vocab (chain-grade on its axis):
  "Given a validly-extracted direct-object patient and a force-capable governing verb, BRIDGE-1's
   event stage flips harm↔neutral by the patient's WordNet ANIMACY on OPEN vocabulary (Bopen=1.000,
   5 seeds; scramble→0.400; BOW/governor=0.500; no subset-A regression). The frozen appraisal-sim
   theta genuinely values the resulting event type (random-theta≈0)."
SHAPE-ONLY / closed-lexicon (do NOT build on as capability):
  force-verb identification (hand list, test-fitted); goal-object/adversarial object classes;
  the STAGE-2b discourse/situation-bias port (subset C).
PROVEN GAPS (bounded, with revival routes):
  (1) body-part patients (WordNet routes to body-part hypernyms → inanimate; revive via a body-part
      ontology branch or animacy-of-possessor); (2) social-relational valence (adversary vs
      sympathetic person; both animate → needs a relational/social-appraisal signal, not animacy);
  (3) abstract-harm vs abstract-goal nouns (animacy alone conflates them; only avoided by scoping A out).

## Over-reads to correct (symmetric anti-negativity — no inflation either way)
- The plan/commit phrase "open-vocab capability" is TRUE but must be qualified to "open-vocab on the
  PATIENT-ANIMACY axis"; the harm/force-verb axis is still a closed test-fitted lexicon. Recommend the
  certified statement above replace any unqualified "event-assembly works open-vocab" wording.
- No downward correction needed on the SHAPE-vs-capability call itself — the Director's self-catch was
  correct and the open-vocab cell's PARTIAL_WITH_BODYPART_GAP verdict is accurate and not inflated.

Disposition: chain-grade on the animacy axis (bounded); proven-gap x3; shape-only for force-verb +
discourse. AUDIT-ONLY: no atoms authored here beyond this VET record; promotion is Director's call.
