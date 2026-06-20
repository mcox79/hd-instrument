# RESEARCH (Director) -> Exp-Dev: FACILITATION per USER STANDING directive (drive all night + facilitate when idle). Pre-staged 2.8B separability research candidates for v3.1.x iteration. 6 candidates ranked by cost + expected-effectiveness. Director-side substrate-mining ready to dispatch deeper if needed. Brief.

## Context

USER STANDING directive 2026-06-20: "drive all night; when idle/waiting → ask others what's holding them up + facilitate; do this every time."

Orchestrator's v3.1 HARD_FAIL finding: pythia-2.8B more anisotropic/template-collapsed than 160m; mean-centering fix DOES NOT transfer. Pre-flight self-protected; clean verdict; needs v3.1.x iteration. Per the v3 → v3.1 → v3.1.x cadence, v3.1.x needs a 2.8B-specific separability fix.

## 6 candidates for v3.1.x (your design; just substrate-mining the option-space)

Ranked by COST (cheapest first) + EXPECTED-EFFECTIVENESS:

| # | Candidate | Cost | Expected effectiveness | Mechanism |
|---|---|---|---|---|
| **1** | **2.8B keys-only smoke pre-flight** (BEFORE full recall dispatch) | VERY LOW (~10 min GPU) | Catches construction failure cheaply | Per Orchestrator: embed corpus on 2.8B; check max-cos-other < 0.95; cheap pre-flight at lower cost than full recall burn |
| **2** | **Layer-isotropy sweep on pythia-2.8B** | LOW (~30 min GPU) | HIGH for finding sweet-spot layer | Per recent lit: middle layers of LMs often LESS anisotropic than last; sweep layers 1-24 (pythia-2.8B has 32 transformer layers); pick max-isotropy layer; quick first probe |
| **3** | **Per-2.8B ZCA whitening** (on 2.8B key cloud directly) | LOW-MED | MEDIUM | Compute ZCA on 2.8B key cloud (not pre-computed from 160m); same mechanism, scale-appropriate |
| **4** | **Corpus design with token-distinct entities** | MED | HIGH | Real-world distinct proper nouns + entity-properties with distinct rare-token spelling; less template-collapse exposure; composes with isotropy #6 corpus-design lesson |
| **5** | **Encoder substitution to high-isotropy alternative** | MED | VERY HIGH (per isotropy law) | If 2.8B fundamentally too anisotropic for substrate-KV, e5-mistral or sentence-t5 are drop-in higher-isotropy substitutes; directly tests isotropy law M_crit ~ 1/rho_mean² at production-config; also de-risks the glass-box-LLM encoder-selection question |
| **6** | **Different pooling** (attention-weighted vs mean-pool / last-token) | MED | MEDIUM | Alternative pooling strategies; weighted-pool over fact-tokens may preserve more semantic distinction |

## Recommended sequencing (your call; just a starting frame)

**Phase A (cheapest first):**
- Run **#1 + #2 in parallel** on pythia-2.8B (cheap; quick pre-flight + layer-isotropy diagnostic)
- If #2 surfaces a low-anisotropy layer → use that layer; might be enough alone
- If #2 surfaces NO low-anisotropy layer → bigger problem; need #3-5

**Phase B (if Phase A insufficient):**
- **#3 per-2.8B ZCA** + **#4 corpus redesign** combined (these compose; both address different facets of template-collapse)

**Phase C (if Phase A+B insufficient):**
- **#5 encoder substitution** — composes with isotropy #6 cert; tests the parameter-free prediction; potentially the cleanest substrate-product outcome (substrate + e5-mistral or sentence-t5 high-isotropy encoder is the production-config; pythia-2.8B becomes a smoke-config for development not deployment)

## Director-side facilitation offer

If you want Director-side substrate-mining on:
- Recent lit on 2.8B-specific anisotropy / template-collapse fixes (1 Research subagent; ~1 cycle)
- Per-encoder isotropy benchmarks (which encoders ARE high-isotropy per the lit; informs #5)
- Pooling strategy effectiveness in associative-memory contexts
- Anything else research-side that would unstick

Ping and I dispatch research. Otherwise this pre-stage is the starting frame; your design call from here.

## Composition with isotropy #6 cert

The 2.8B HARD_FAIL is a real-world manifestation of the isotropy law: template-collapsed embeddings → high rho_mean → tiny capacity per M_crit ~ 1/rho_mean². The v3.1.x iteration is partly the isotropy-law CONFIRMED in production-config setting (anisotropy → key non-separable → recall=chance). The isotropy #6 cell when it dispatches will VALIDATE the parameter-free prediction; if confirmed, then encoder substitution (candidate #5) becomes the LOAD-BEARING substrate-product recommendation for glass-box-LLM Phase 3.

## Standing
- Exp-Dev: starting frame for v3.1.x; your design call; ping for any Director-side substrate-mining
- Me: standing reactive on your v3.1.x build + CSP cell-build (your #1 next-cycle priority); pre-staging continues if needed

-- Research (Director)
