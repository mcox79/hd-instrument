# Brain-faithful, glass-box, VSA-native NO-INTERFERENCE capacity allocation (Drill A synthesis)

Director synthesis of 3 lit-scans (CLS/hippocampal-neocortical; DG sparse-coding/pattern-separation/mixed-selectivity/PBWM-gating; glass-box parameter-isolation ML). Governing constraint (USER 2026-07-31): brain-foundational first; may do better only if brain-COMPATIBLE; GLASS-BOX ALWAYS (overrides). Confidence deflated per lit-scan discipline; no single claim is load-bearing without a 2nd VET.

## The question
Evolving the continuous read-and-learn loop from ONE objective into a GROWING LIBRARY of construction-competencies (entity #1, roles #2, coref #3, ...). Each new competency must get dedicated capacity so adding one does NOT smear the others (provable no-interference). Fork-2 decided: fully-modular/separate-capacity first (glass-box), not shared MoE gating.

## What the brain actually does (honestly deflated)
Three mechanism-families, and the brain COMBINES them:
1. **Sparse / orthogonal pattern-separation (DG).** Dentate gyrus expansion-recodes similar EC inputs into sparser, decorrelated codes before CA3 storage (Marr 1971; Leutgeb 2007; Yassa-Stark 2011). Associative-memory theory: sparse codes approach capacity and minimize crosstalk (Willshaw; optimal active fraction ~ln(N)/N). = non-overlapping codes -> low interference. Confidence HIGH qualitatively; the capacity formulas are abstract-model theory, not measured hippocampal values.
2. **Add new units for new memories (neurogenesis).** Adult DG neurogenesis supplies fresh coding units; young hyperexcitable granule cells encode new memories with a DIFFERENT code than older cohorts, so new info literally uses different neurons -> reduced interference (Aimone-Deng-Gage 2011; Sahay 2011 causal). Confidence MODERATE (their interpretive framing; behavioral link heterogeneous per a 2015 meta-analysis).
3. **Selective per-module update gating (PBWM).** Basal ganglia issue per-stripe Go/NoGo signals: one PFC stripe updates from input while others stay locked, protected from overwrite (O'Reilly-Frank 2006). Credit assignment via dopamine-tagged gating. = selective update of only the relevant module. Confidence HIGH for the model.
4. **CLS interleaved replay (the anti-forgetting layer).** Hippocampus binds fast (sparse); neocortex consolidates SLOW via interleaved replay that co-trains old+new so gradients find a JOINT minimum rather than overwriting (McClelland 1995; Kumaran 2016). Similarity-weighted interleaving needs far less replay. Our loop ALREADY does rehearsal replay.

**The honest tension (must not paper over):** Rigotti-Fusi 2013 mixed-selectivity is a RIVAL to "dedicated capacity per skill." Within a cortical region, neurons show dense, overlapping, nonlinear mixed tuning; separability comes from high-dimensional population GEOMETRY, not anatomical partitioning. => the brain does DENSE/overlapping coding at the fine grain and MODULAR allocation only at the COARSE grain (category-selective patches; expertise-driven cortical expansion, e.g. musicians' auditory cortex growth displacing adjacent maps). So "fully separate params per competency" is brain-faithful at the COARSE grain (patch/region), NOT at the single-unit grain.

**Our brain-compatible choice (honors the constraint):** take the COARSE-modular route (a dedicated near-orthogonal subspace per competency) FIRST — it is brain-real (coarse modularity + DG sparse orthogonal codes + PBWM gating + CLS replay) AND maximally glass-box AND gives provable no-interference. Mixed-selectivity (dense within-competency codes) is the later within-module refinement if a competency needs more expressivity. This is "brain-foundational, doing better only compatibly (cleaner orthogonality than DG), glass-box always."

## Glass-box ML prior art, judged (credit the authors)
| Method | No-interference | Brain-fidelity | VSA-native |
|---|---|---|---|
| Progressive Nets (Rusu 2016) | Exact (frozen columns + lateral reuse) | Systems-level plausible (cortical recruit+reuse); synapse-level no (hard freeze) | Yes: subspace-per-competency + binding for reuse |
| PackNet (Mallya 2018) | Exact for retained weights | Sparse-coding/pattern-separation analog | Yes: disjoint sparse masks |
| DEN (Yoon 2018) | Approximate (drift repaired post-hoc) | BEST match to schema-assimilate-vs-recruit | Partial (reuse-vs-expand yes; drift-detect needs gradient) |
| Adapters/LoRA (2019/2021) | Exact only if never co-activated | Pure engineering shortcut | Architecture yes, training gradient-native |
| **SupSup / supermasks (Wortsman 2020)** | **Exact (weights NEVER change)** | **STRONG: fixed substrate + sparse gating/masking = gating+sparse-coding analog** | **BEST fit; near gradient-free** |
| OGD/OWM (Farajtabar 2020) + EWC (Kirkpatrick 2017) | Exact to first order (PROVEN) | Functional synaptic-consolidation analog | Yes: null-space projection |

**Key VSA insight:** a high-dimensional VSA space gets the OGD/OWM orthogonality guarantee **for free** — random HD vectors are near-orthogonal by construction, so allocating each competency a fresh random subspace gives approximate no-interference WITHOUT storing/computing an explicit projector. This is DG pattern-separation and the OGD guarantee, unified, and native to our substrate.

## The VSA-native recipe (glass-box, brain-faithful)
Allocate each competency:
1. **A fresh near-orthogonal high-dimensional subspace** (random HD basis; near-orthogonality = free approximate interference-freedom = DG sparse-separation + OGD orthogonality). Competency k lives in / writes to its own subspace.
2. **Selective / gated update** (PBWM analog): a step reading a construction of type k updates ONLY competency-k's capacity; other competencies' params are held (mask/freeze). This is the SupSup/PackNet "per-task mask, shared frozen substrate" pattern — exact no-interference, strongest VSA + brain fit.
3. **Interleaved rehearsal replay** (CLS): the loop already does this; keep it, ideally similarity-weighted, so cross-competency consolidation finds a joint minimum.

## THE ONE LEVER for the Phase-1 two-competency build (recommendation)
Instantiate competency #2 (roles) in a **fresh near-orthogonal subspace with a per-competency gated/masked update** (SupSup/PackNet-style, VSA-native), on top of the frozen shared encoder substrate, with the existing replay. Fully-modular by construction => provable no-interference is testable, not hoped-for.

**Fair can-fail no-interference test:** measure entity-half (competency #1) accuracy BEFORE and AFTER competency #2 is added/trained. HARD requirement: entity accuracy must NOT drop (within noise) when roles is added — that is the whole modular claim. If entity degrades, the "separate capacity" was not actually separate (a plumbing/geometry bug), NOT a ceiling. Pair with the climb-further test (2-competency beats single-objective +0.096 with power) and the order-sensitivity test (graded now beats shuffled).

Fork-2 lean (fully-modular) is VINDICATED: it is simultaneously the most glass-box, the most VSA-native, AND (at the coarse grain) brain-faithful. MoE/mixed-selectivity stays as the later within-competency expressivity option.
