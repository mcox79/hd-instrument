# Novel-atom generalization: few-shot concept learning + immediate composition (2026-07-20)

Director synthesis of a 3x parallel novel-atom brain-drill (af3add0d fast/few-shot concept learning, abd7309b novel-filler composition without retraining, a9571d35 feature-derived codes for fixed downstream machinery). Trigger: the compositional-gen VET (atom 29379) proved binding composes SEEN atoms for free (construction-determined) but generalization to a genuinely UNSEEN filler is exactly 0.000 -- the learned front-end only IDs seen atoms. That 0.000 marks the genuine open frontier: NOVEL-ATOM generalization. Deflated; all prior work credited (learn-from/build-on).

## The convergent mechanism (3 scans agree)

- **A novel atom becomes immediately usable when PLACED INTO AN ALREADY-STRUCTURED SPACE built from prior experience** -- cortical feature space, psychological similarity space (prototype/exemplar/GCM), pretrained embedding space (Prototypical Networks = mean of few examples in a fixed metric space), or a primitive-program library (Lake BPL). NOT built from scratch. Even hippocampal fast-mapping largely stores a POINTER (hippocampal indexing) into pre-existing cortical structure; CLS (McClelland) = sparse hippocampal one-shot + slow cortical consolidation, with schema-consistent items assimilated fast.
- **Immediate composition is FREE once the atom is encoded in the shared space.** Across symbolic (Fodor-Pylyshyn typed variables), VSA/TPR/HRR (fixed content-agnostic binding operator), PFC-indirection (Kriete/O'Reilly pointers), and synchrony (LISA/DORA): the binding machinery is fixed and never sees the filler during training; the SOLE requirement on a novel filler is that it be encoded in the SAME representational space as known fillers. This IS our confirmed free-algebra binding.
- **THE NONTRIVIAL PART = ENCODING the novel atom into the right space** (explicitly flagged, load-bearing): the binding step is not where the difficulty lives; producing a usable code for a brand-new item is "itself a nontrivial, separately-solved problem" (the brain uses hippocampal pattern separation). This is exactly where the closed cell failed (0.000: no code for the unseen filler).

## The KEY discriminator (scan 3, reshapes the design)

Necessity of code CONTENT vs FORMAT depends on the DOWNSTREAM OPERATOR:
- **Similarity-based downstream** (embeddings, NN classifiers, our cleanup/retrieval): the novel code needs CONTENT -- genuine feature/context-derived similarity structure relative to seen items. Format alone insufficient; naive derivation (raw averaging) underperforms explicit induction functions (a-la-carte regression, nonce2vec high-risk SGD); **domain-shift + hubness** are the diagnostic failure signatures.
- **Algebraic/role-binding downstream** (VSA bind/unbind): FORMAT (near-orthogonal random vector, right dimensionality) SUFFICES; content-similarity NOT required -- indeed baking similarity in can HURT symbol-binding capacity.
- SCAN/COGS wrinkle: even CORRECT novel-item codes fail without an architecture supporting role/slot generalization. We HAVE that (free-algebra binding). Content-correctness and architecture-correctness are SEPARATE necessary conditions.

## Substrate mapping + the genuine capability

Our pipeline for a novel atom: (1) ENCODE/recognize the novel filler -> a code; (2) BIND to the query role (FREE); (3) unbind + CLEANUP-retrieve (similarity-based). Steps 2 (algebraic, free) and the format requirement are solved. Step 1 (encode a usable code) + step 3 (cleanup needs content-correct code) are the genuine problem. Our CODEBOOK CG learns feature-derived codes that GENERALIZE to held-out items (AUC 0.927) -- it is exactly the "encode into the structured space" mechanism (a-la-carte / DeViSE / Prototypical-Networks analog). So the genuine, can-fail question:

**Does the codebook's held-out feature-generalization SURVIVE composition through binding + cleanup, letting a genuinely-UNSEEN atom compose correctly (>> the 0.000 memorize-prototype baseline), or does codebook imperfection (0.927 not 1.0) + hubness/domain-shift degrade it under composition?** This is an INTEGRATION test (codebook CG + binding), not a re-run of either alone.

## Cell design + construction-determinism guards

Arms on genuinely-UNSEEN atoms (codebook trained on OTHER atoms only; novel atom's code DERIVED from its features/context, never trained on its identity or binding):
- **(a) codebook-feature-derived code** [the genuine arm].
- **(b) HANDED code** [the free-binding CEILING control -- if the novel atom's true code is handed, binding+cleanup should retrieve it; this is the construction-determined ceiling].
- **(c) memorize-prototype front-end** [the 0.000 baseline from 29379].
- **(d) flat end-to-end** [should fail systematically].
- **(e) random-code (format-only, no content)** [tests whether content is needed for cleanup/retrieval -- the scan-3 discriminator].

GUARDS: novel atoms genuinely UNSEEN by the codebook; the win must be the codebook's FEATURE-generalization, NOT a handed code (arm b is the ceiling, not the claim); watch hubness/domain-shift (scan-3 failure signatures); HARD-PASS = codebook-derived (a) >> memorize-prototype (c)=0.000 AND >> flat (d), approaching the handed-code ceiling (b), demonstrating codebook-generalization survives composition. HARD-FAIL = (a) collapses toward 0.000 (codebook imperfection doesn't survive binding+cleanup for novel atoms) OR (a) only matches random-code (e) (no genuine content-generalization). This distinguishes a genuine novel-atom capability from both the free-algebra trick (handed code) and codebook-alone.

## Verdict (one line)
The genuine novel-atom capability = "does the codebook feature-encode a novel atom well enough that binding+cleanup compose it," an integration test of the codebook CG + free binding, design-gated by a handed-code ceiling + a random-code content-control; tractable and non-construction-determined IF the novel atoms are genuinely unseen and the code is feature-derived not handed.
