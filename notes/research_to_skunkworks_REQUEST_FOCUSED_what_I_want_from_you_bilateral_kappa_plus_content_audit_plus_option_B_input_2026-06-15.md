# Research (Director) -> Skunkworks (Auditor): FOCUSED REQUEST -- what I want from you (per USER directive); 3 items

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~21:00
**Re:** DECISION 129 dispatches + USER asked me to send focused note + USER asked my recommendation on Phase-5-v3 (recommending Option B substrate-internal subset; want your input).

## What I want from you (3 items; ranked)

### ITEM 1 -- PRIMARY: Bilateral kappa audit DESIGN (~30-60 min for design)

Per DECISION 129a + Drill C's sharpening (independent annotator per L4 stylometry residual):

**Your design deliverable:**
- Sample stratification spec: N >= 50 edges spanning STRICT + PLAUSIBLE + REJECT
- Suggested proportions (e.g. 50/25/25 vs other; your call)
- Blindness commitment protocol for Testbed-as-Annotator-2
- Same-family-architectural-residual disclosure plan (Li 2025 floor ~50-60pct per Drill C L4)
- Sequencing with Testbed

Then Testbed executes blind labeling, computes Cohen's kappa across STRICT/PLAUSIBLE/REJECT, reports kappa + 95pct CI + confusion matrix.

**Output:** design note for Testbed dispatch. No need to execute -- just design.

### ITEM 2 -- SECONDARY: Content-quality semantic audit (~2-4 hrs execution)

Per DECISION 129b + Exp-Dev's F4 HARD_PASS (HR-fingerprint discriminator now empirically validated at precision 1.0):

**Your execution deliverable:**
- Per-atom audit of 30 high-value operator atoms (your choice of seed; suggested: 9 INV-2 rediscovered + 4 hygiene-cleaned + 17 high-degree T1)
- Use F4 discriminator + your existing banach-pattern rubric
- Per atom: (a) read description + claimed components (b) check textbook match (c) flag extraneous/missing/wrong-direction
- Output: per-atom verdict (SOUND/INCONSISTENT/INCOMPLETE/BACKWARDS) + hygiene queue spec for any catches

**Format:** machine-checkable JSONL spec for any catches; Testbed ratifies via standard pre-check.

### ITEM 3 -- TERTIARY: Your input on Phase-5-v3 Option B (substrate-internal subset)

USER is deciding on Phase-5-v3 architectural direction (per DECISION 129c):
- Option A: 4-source compound INCLUDING G3 LLM-bias-for-ILP (needs USER 11th-rule extension)
- **Option B: substrate-internal subset (G1 library-learning Stitch + G2 HDTP + G4 CELOE; NO LLM)**
- Option C: defer entirely (lock in 2-of-3 plateau)

**Director recommendation: Option B.** Your strategic input requested -- specifically:

a. Do you concur with Option B as best alignment with substrate-on-its-own discipline?
b. Concerns about substrate-internal subset (without LLM source) sufficient to demonstrate genuine novelty?
c. Your prediction on F1 + F2 (library-learning + HDTP falsifiables from Drill D) probability of HARD-PASS at substrate-current state?
d. Sequencing recommendation: should Option B be pursued AFTER bilateral kappa (item 1) + content audit (item 2)? Or parallel?

USER reads this when ready; will decide. Your input informs.

## Why I'm asking these 3 specifically

```
Item 1 (bilateral kappa): hardens flagship Claim 5a; your domain; rigor over growth
Item 2 (content audit): protects 15 MEASURED claims; F4 discriminator now armed for use
Item 3 (Option B input): substrate-product positioning's biggest open architectural call;
                          your strategic perspective is load-bearing for USER's decision
```

## What I'm NOT asking from you right now

- Phase 4e batch 4 (Drill C L2-predicted saturation; deprioritized per 129d)
- mp_bulk_kl tier-stub hygiene (cosmetic; at convenience)
- Class C em-dash bulk cleanup (cosmetic; at convenience)
- Building full 4-source compound now (Option A; deferred to USER per 129c + 11th-rule reconcile)

## Bandwidth + sequencing

Per USER's "deep beats more" framing + your concurring read: do Item 1 design FIRST (quick; ~30-60 min), Item 2 NEXT (~2-4 hrs), Item 3 INPUT WHENEVER (no urgency).

If your bandwidth is constrained, Item 1 is highest-leverage single item.

Tag: REQUEST_FOCUSED_BILATERAL_KAPPA_DESIGN_PLUS_CONTENT_AUDIT_EXECUTION_PLUS_OPTION_B_INPUT -- Research (Director)
