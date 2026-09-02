# Brain-fidelity wall-drill + adjacent-component evaluation

Solver deliverable for `the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold`, answering the
owner's two questions: **"how does the brain do it EXACTLY, where do we differ PRECISELY?"** and **"understand the
capabilities/limitations/opportunities/brain-foundational status of adjacent components to plan the next problems."**
Every claim is either measured on disk (this problem's cells) or cited from the two research drills
(`BRAIN_MECHANISM_DRILL_composition_prediction.md`), which verified all load-bearing citations live.

---

## PART 1 -- THE WALLS, DRILLED (brain mechanism EXACTLY; where WE differ PRECISELY)

### WALL 1 -- Linear position dominates who-did-what SELECTION on canonical direct objects (0.918)
- **How the brain does it, exactly:** Competition Model (MacWhinney & Bates; MacWhinney, Bates & Kliegl 1984).
  Who-did-what is GRADED, PARALLEL cue integration with LEARNED VALIDITIES; in English, word ORDER has the highest
  validity -- when order conflicts with animacy, English speakers follow ORDER (case-marking languages follow
  morphology). Thematic fit is a LOW-validity cue that surfaces only when order is ambiguous/marked.
- **Where we differ: WE DON'T -- this is a MATCH, not a gap.** Our position dominance and the live
  `hdlab/graded_role_assigner` (order-dominant + marked-cue override, validities fit by logistic regression) are
  faithful to the cue hierarchy. The "wall" was a mis-framed test (selection accuracy on the regime where order is
  the correct cue), not an implementation deficit.

### WALL 2 -- Agent x verb composition ties its twin as a SELECTOR, but is real as PREDICTION
- **How the brain does it, exactly:** the Bicknell 2010 / Chersoni agent x verb effect is measured as reading-time /
  N400 (forward PREDICTION / pre-activation -- Altmann & Kamide 1999 fire anticipatory looks to the plausible object
  ~200ms before it is read), on items where SYNTAX ALREADY FIXES the object. Thematic fit changes the SELECTION/parse
  only at points of SYNTACTIC AMBIGUITY (McRae, Spivey-Knowlton & Tanenhaus 1998, reduced relatives).
- **Where we differ: instrument, not mechanism.** We measured composition as which-noun SELECTION on 100%-active
  canonical DOs (no ambiguity), where the brain uses order, not fit. On the brain's ACTUAL instrument (held-out
  forward prediction, MRR) composition IS real: +0.0322 over marginal CI-sep, +0.0403 over agent-shuffle CI-sep
  (`exp_19c_composition_as_prediction_v1`, n=4000). No mechanism gap; it was graded on the wrong test.

### WALL 3 -- Composition ties its twin in the 12-d grounded space, works in the 100-d PPMI space
- **How the brain does it, exactly (TWO dimensionalities -- the key precision):**
  1. **Binding ALGEBRA** (role (X) filler conjunction). The brain encodes who-did-what via conjunctive role-filler
     coding in left mid-superior temporal cortex (Frankland & Greene 2015, PNAS -- distinct agent/patient subregion
     patterns). This is HIGH-D and is NOT the bottleneck; our FHRR/VSA binding is already high-D and faithful.
  2. **Filler CONTENT** (the vector for "mechanic" vs "journalist"). Fine conceptual individuation lives in the
     high-D transmodal ATL HUB, NOT the low-D sensorimotor SPOKES (Controlled Semantic Cognition; Lambon Ralph 2017,
     Nat Rev Neurosci). In a spoke, "mechanic" and "journalist" are near-collinear (both animate human agents), so
     conditioning on the agent adds no information.
- **Where we differ, PRECISELY:** our forward-prediction organ (`hdlab/predictive_reader`) computes thematic fit over
  a 12-d sensorimotor SPOKE (Lancaster 11-d: 6 perceptual + 5 action). That is the wrong basis for the agent x verb
  CONJUNCTION -- too coarse to carry agent identity. Measured: in the 12-d grounded space composition ties its
  agent-shuffle twin (+0.0022 ns) and even HURTS vs exemplar-marginal (-0.036); in a 100-d register-native PPMI-SVD
  space (a HUB proxy -- the distributional stream carries the relational structure grounding lacks, Andrews/Vigliocco
  complementarity) composition is real (+0.0395 vs agent-shuffle CI-sep) and the composed-exemplar beats the organ's
  centroid-marginal +0.0140 CI-sep (`exp_predictive_reader_composition_upgrade_v1`, n=4000). **The differ is
  REPRESENTATIONAL (spoke used where a hub is required), NOT algebraic. Remedy: feed hub-grade high-D fillers into the
  conjunction; KEEP FHRR.** (Exemplar>centroid in low-D but centroid~=exemplar in high-D is also brain-consistent: a
  centroid collapses a role's multimodal filler clusters catastrophically only in low-D -- Erk 2010; near-orthogonality
  in high-D lets the centroid retain structure; composed-exemplar-best = instance-based conjunctive conditioning, CLS.)

### WALL 4 -- The canonical-DO residual is 89% structural (NP-head), not semantic
- **How the brain does it, exactly:** NP head-finding (compound Right-hand Head Rule, Williams 1981; genitive
  DP-head) is a SYNTACTIC operation that PRECEDES thematic role assignment -- a different computation at a different
  level. A thematic-fit store cannot repair a head-selection error.
- **Where we differ:** our positional selector picks the nearest post-verbal noun = the FIRST token of the NP
  ("a trade delivery VAN" -> `trade`; "the undertaker's SHOP" -> `undertaker`). The brain picks the HEAD. Measured:
  an NP-head-aware selector beats nearest +0.0433 CI-sep, reaching 0.9611 (`exp_19c_whodidwhat_residual_taxonomy_v1`).
  Gap = no NP-head chunker (compound + genitive). Buildable, structural, brain-independent.

### WALL 5 -- Morphological CASE is a high-validity cue we do NOT use (the missed lever, 19c-matched)
- **How the brain does it, exactly:** morphological case (nominative/accusative pronouns he/him, she/her, they/them;
  and who/whom) is the HIGHEST-validity Competition-Model cue WHERE IT EXISTS -- morphology OVERRIDES word order.
  It resolves position-ambiguous who-did-what (fronted / relative-clause patients) WITHOUT needing thematic fit.
- **Where we differ:** verified on disk -- `hdlab/graded_role_assigner` cue set is
  `[order, adjacency, passive_strong, passive_weak, gap, unacc, byagent, animacy]` -- **no case cue.** And 19c prose
  PRESERVES "whom"/pronoun case far better than modern text, so this cue is MORE available in the target register
  than anywhere else. Cheap surface cue, NOT in the organ's named residual. **This is the strongest fundable
  who-did-what SELECTION lever the sweep found.**

### WALL 6 -- Non-canonical (passive / reduced-relative) who-did-what
- **How the brain does it, exactly:** the same graded cue integration; voice morphology and filler-gap override order
  on marked constructions; reduced relatives need verb subcategorization frames + incremental clause segmentation.
- **Where we differ: mostly covered.** `hdlab/graded_role_assigner` already does the marked-construction override
  (validated: non-canonical slice 0.60 vs 0.5758 +0.024 CI-sep). Its residual is UPSTREAM, and the organ names it:
  verb-subcategorization SUPPLY (from WordNet frames), the incremental clause structure-builder, and an unwired coref
  organ. (This is why a 19c passive build would DUPLICATE existing work -- confirmed, and dropped.)

**No large uncovered who-did-what comprehension lever exists** (both drills swept it): Construction Grammar (Goldberg)
is a reframing of the syntactic cue; discourse/referential event-model (Altmann-Kamide, Metusalem) lives in the same
forward-prediction pathway; cue-based retrieval interference (Lewis & Vasishth 2005, ACT-R) is a real DISTINCT error
mechanism for long/embedded 19c sentences but is mechanism-heavy -- log it, don't fund near-term.

---

## PART 2 -- ADJACENT COMPONENTS (capability / limitation / brain-fidelity / opportunity -> next problems)

| organ | brain frame + fidelity | limitation (measured/named) | opportunity -> candidate next problem |
|---|---|---|---|
| **`predictive_reader`** (forward prediction, landed EXCELLENT) | PINNED-faithful in FORM (Altmann-Kamide pre-activation; Levy/Hale surprisal = -log P). | Predicts from the **marginal, role-specific CENTROID over a 12-d sensorimotor SPOKE** -- no agent-composition; filler content too coarse for the conjunction (WALL 3). | **Upgrade to agent-COMPOSED EXEMPLAR over HUB-grade (register-native, high-D) fillers.** Measured gain +0.0140 MRR CI-sep over the organ's method; keep FHRR. This is the brain-faithful HOME of composition. |
| **`graded_role_assigner`** (Competition-Model role assignment, landed EXCELLENT) | PINNED-faithful (MacWhinney-Bates graded cue integration; order-dominant + marked override). HIGH fidelity. | Cue set has **no morphological CASE cue** (WALL 5); reduced-relative residual is upstream (subcat/segmentation/coref). | **Add the morphological-case cue** (he/him, who/whom) -- highest-validity, surface-cheap, MORE available in 19c. Cleanest fundable selection lever. |
| **`verb_role_exemplar_selector`** (the exemplar store, p3/p5, landed) | PINNED-faithful (McRae exemplar / instance distribution). | DOMAIN-BOUND to modern prose (ties its twin on 19c/OOD, its own finding); as a STANDALONE selector it is dominated by position on canonical DOs (this problem). | Its value is (a) as a graded PREDICTION store (via `predictive_reader`, WALL 3) and (b) on the non-canonical slice via `graded_role_assigner`; **NP-head chunking upstream** would stop it mis-picking compound modifiers. |
| **`n400_coherence_monitor`** (event segmentation, ORGAN F5, landed EXCELLENT) | PINNED-faithful (Event Segmentation Theory; N400 = graded coherence error vs running situation gist). | Backward-looking EVENT level; consumes a forward-prediction surprisal that is currently coarse (marginal centroid). | Indirect: a better forward predictor (composed-exemplar, hub-grade fillers) yields a sharper surprisal -> better N400 boundary confidence. |
| **NP-head chunker** (does not exist) | Compound Right-hand Head Rule (Williams 1981) + genitive DP-head -- syntactic, precedes role assignment. | 89% of the clean-DO who-did-what residual; no organ finds NP heads. | **Build an NP-head selector** (compound + genitive head). Measured +0.0433 CI-sep -> 0.9611; helps every downstream selector. |

### Candidate next problems, ranked by leverage x cheapness x brain-fidelity
1. **Morphological-case cue in `graded_role_assigner`** -- cheap, highest-validity, register-matched (19c preserves
   whom/case). The best sweep find; verified absent on disk.
2. **NP-head chunker** (compound + genitive head selection) -- structural, +0.043 CI-sep, helps all selectors, and
   is THE lever for clean 19c who-did-what selection (89% of the residual).
3. **Hub-grade filler representation + agent-composed exemplar for `predictive_reader`** -- the brain-faithful home
   of composition (+0.014 CI-sep measured), a REPRESENTATION swap (spoke->hub proxy), keep FHRR.
4. **(log, do not fund near-term)** cue-based retrieval interference (Lewis-Vasishth ACT-R) for long/embedded 19c
   sentences; verb-subcategorization SUPPLY from WordNet frames (already named by `graded_role_assigner`).

---

## PART 3 -- OPTIMIZATION HEADROOM (measured; `exp_composition_representation_optimization_v1`)

The brain-fidelity finding ("composition is representation-bounded -- spoke fails, hub works") makes a falsifiable
optimization prediction: the composition margin should GROW with representational capacity. It does -- a clean
dose-response (held-out prediction MRR; agent-shuffle margin; n=4000):

| filler representation | MRR | COMPOSED - AGENT-SHUFFLE |
|---|---|---|
| 12-d grounded sensorimotor (SPOKE -- the organ's current basis) | 0.0594 | +0.0022 **ns (dead)** |
| PPMI-SVD dim 25 | 0.1062 | +0.0224 CI-sep |
| PPMI-SVD dim 50 | 0.1377 | +0.0339 CI-sep |
| PPMI-SVD dim 100 | 0.1590 | +0.0403 CI-sep |
| **PPMI-SVD dim 200** | **0.1638** | +0.0442 CI-sep |
| PPMI-SVD dim 300 | 0.1623 | +0.0456 CI-sep |

**Optimizations, with numbers:**
1. **Swap the 12-d sensorimotor SPOKE for a ~200-d register-native distributional HUB proxy.** This is the big
   lever: MRR 0.059 -> 0.164 (2.8x) and the composition margin 0.002 (dead) -> 0.044 (CI-sep). The margin doubles
   from dim-25 to dim-300 and MRR peaks at ~200 then plateaus -- so ~200 dims is the efficient operating point
   (300 adds noise dims, MRR dips to 0.162). This CONFIRMS "representation is the bottleneck, not the mechanism."
2. **gamma (agent-weight sharpness) ~3.0**, not the default 2.0: margin +0.0483 vs +0.0456. Small, free.
3. **Do NOT naively concatenate spoke+hub.** Measured: HUBSPOKE_concat MRR 0.1167 < HUB-alone 0.1540 -- the coarse
   near-collinear spoke dims DILUTE the hub. Brain-faithful reading: the ATL hub is a DEEP transmodal integration of
   the spokes (Lambon Ralph 2017), not a vector concatenation; use the hub-grade distributional representation, do
   not bolt the raw sensorimotor spoke onto it. (An honest negative that sharpens the "hub, not concat" recommendation.)

**Net for the `predictive_reader` upgrade next-problem:** agent-composed EXEMPLAR over a ~200-d register-native
distributional (hub-proxy) filler representation, gamma~3, no raw-spoke concat -- a REPRESENTATION swap, KEEP FHRR.
Quantified headroom: MRR 0.059 -> ~0.16 on held-out patient prediction; the mechanism only switches on once the
representation is hub-grade.

### One-line reconciliation with the audit
The register/selection story is now fully brain-scoped: **English who-did-what SELECTION is word-order-dominant
(we match the brain); thematic-fit/composition is a forward-PREDICTION mechanism that is REPRESENTATION-bounded (spoke
vs hub), not a selection lever; the cheap missing selection cue is morphological CASE; the canonical residual is
NP-head chunking.** Nothing here needs a new binding algebra -- FHRR stays.
