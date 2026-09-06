# Research drill: the forward-coherence WALL, understood (2026-09-06)

Aggressive 4-angle literature drill on WHY glass-box forward-narrative-coherence plateaus at co-occurrence
(~0.55-0.60; humans ~1.0), and the brain-foundational, invariant-compliant (NO inference-LLM) path across it.
Each claim PINNED vs OUR-INVENTION; buildability tagged (a)=glass-box, (b)=online-learnable, (c)=offline static
foundation, (d)=needs a distributed learned net.

## Angle 1 -- knowledge vs mechanism
Kintsch 1988 CI, Graesser/Singer/Trabasso 1994, Bower/Black/Turner 1979, Cain-Oakhill 2001, Recht-Leslie 1988.
CONVERGENCE (PINNED): comprehension = a generic, mechanical SETTLING / SEARCH / SLOT-FILL computation (a/b),
whose success is GATED by the richness+STRUCTURE of the knowledge store (c). Graesser: "a search finds nothing in
an empty store." Bower/Schank scripts: a large class of everyday-narrative inference is SLOT-FILLING over a
stored stereotyped event-schema. Cain-Oakhill: a real integration/search component survives knowledge-control
(it is NOT only knowledge) -- but nothing shows it must be a distributed neural net vs a symbolic search.

## Angle 2 -- mental simulation
Barsalou 1999/2009, Zwaan 2004, Johnson-Laird 1983, Battaglia/Hamrick/Tenenbaum 2013, Gerstenberg CSM,
Schank-Abelson 1977, Meehan TALE-SPIN 1977. The executable precedents for narrative forward-prediction are
SYMBOLIC/PROGRAM-LEVEL and glass-box (a): script execution (Schank), mental-model manipulation (Johnson-Laird),
probabilistic-program rollout / counterfactual simulation (Tenenbaum/Gerstenberg). Embodied sensorimotor
simulation (Barsalou/Bergen) is the (d) piece and is CONTESTED as even necessary (Mahon-Caramazza 2008) -- so
the symbolic/causal-simulation core is a defensible build, not a shortcut. NEGATIVE: Zwaan-Radvansky event-index
is a passive UPDATE index, not a forward GENERATOR; TALE-SPIN plateaus (brittle, hand-crafted).

## Angle 3 -- causal necessity + inverse-planning ToM
Trabasso-Sperry 1985 (necessity: temporal priority + operativity + counterfactual), Baker-Saxe-Tenenbaum 2009
(inverse planning, a glass-box Bayesian program), IPOCL (Riedl-Young 2010), Chandra 2024 (storytelling as inverse
inverse planning). All glass-box (a) as ENGINES; the gap is the state/action/goal EXTRACTION layer from raw text.
LOAD-BEARING NUGGET (Graesser 1994): forecasting inferences are NOT spontaneous -- they are recruited ON-DEMAND
under a forced choice (exactly Story Cloze). So model INSTRUMENTAL, goal-directed graph COMPLETION triggered by
the choice, not during-reading prediction.

## Angle 4 -- SEM decomposition (does human-level need a learned net?)
Franklin/Gershman 2020 SEM = (a) sticky-CRP schema selection + PE-gated segmentation [glass-box, load-bearing,
separable -- Nguyen 2024 SEM-2.0 confirms modularity] + (b) a per-schema LEARNED GRU dynamics. NO ablation
justifies the GRU (Nguyen 2024 calls it "arbitrary"); Kumar et al. 2023 shows a GLASS-BOX Bayesian/KL-surprise
over a FROZEN foundation predicts human event boundaries with NO training at inference. VERDICT: the learned
dynamics is "cheap nonlinear compression," likely ONLINE-fittable (EST: event-models are fast/online; schemata
are slow/offline) -- NOT irreducible. So human-level is NOT gated by a forbidden learned net.

## THE SYNTHESIS (the wall, understood)
The brain's forward-coherence engines -- CI-settling / causal-necessity / inverse-planning -- are ALL glass-box
and buildable (I built + tested CI-settling; see below). Their discriminative power is GATED by a RICH,
STRUCTURED SCRIPT/EVENT-SCHEMA knowledge net. Our available nets (co-occurrence, ConceptNet causal, meaning-
similarity) are the WRONG KIND (associative/taxonomic, not script/event-schema-structured), so every mechanism
over them plateaus. THE GAP IS THE STRUCTURED KNOWLEDGE FOUNDATION, NOT A MISSING MECHANISM.

DIRECT TEST (`exp_forward_event_ci_settling_v1`): Kintsch CI-settling over the co-occurrence net = val 0.5697 /
test 0.5580 -- at the plateau (twin collapses to 0.49, so it USES the context; it just cannot exceed co-occurrence
over an associative net). Confirms: the mechanism is right, the net is the wrong kind.

## THE BRAIN-FOUNDATIONAL PATH ACROSS (buildable, invariant-compliant)
Build the RICH SCRIPT/EVENT-SCHEMA knowledge FOUNDATION (offline static asset (c) = admissible; the project's
north-star clean/typed knowledge foundation, SPECIALIZED to event-schemas): canonical ordered event structures
per situation, causal/goal-typed (Schank scripts + Trabasso causal criteria + Rashkin naive-psychology schema).
THEN run the already-built glass-box engines over it: CI-settling + causal-necessity (Trabasso counterfactual) +
inverse-planning goal (Baker/IPOCL), recruited ON-DEMAND under the forced choice (Graesser). The SEM-style
generative dynamics can be ONLINE-fitted per schema (not a batch-trained GRU). This is a FOUNDATION-scale build
(the north-star), not a mechanism tweak -- which is why the mechanisms I built plateau without it.
