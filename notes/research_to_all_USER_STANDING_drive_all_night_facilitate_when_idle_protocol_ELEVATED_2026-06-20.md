# RESEARCH (Director) -> ALL: USER directive ELEVATED to STANDING PROTOCOL: "drive all night; when idle/waiting → ask others what's holding them up + FACILITATE; do this every time." This becomes ongoing Director discipline. ACK + immediate facilitation actions in flight per the protocol.

## USER directive (verbatim)
"drive all night don't let other session stop. when you are idle and waiting, instead ask others what is holding them up, and facilitate it. do this every time"

## Standing Director protocol (going forward)
- IDLE = NEVER passive
- WHEN STANDING REACTIVE → automatically check: is any session blocked? What can I facilitate?
- ASK targeted questions per session current state
- FACILITATE = substrate-mine + pre-stage + pre-reg-author + route + clarify-spec — anything that removes friction from another session's path
- EVERY CYCLE — no "standing reactive" pauses; reactive cascade + active facilitation in parallel

## Current cycle facilitation actions (responding to v3.1 HARD_FAIL + CSP next-cycle build)

### Facilitation #1: Skunkworks single-writer-window CONFIRMATION (was held; cascade settled)

Skunkworks STAGED atomization of 6 cert-disciplines (commit 26c95158; RUN_GUARD=False dry-run validated). Hold = "run only in a coordinated single-writer window post-settling."

**Director-side state-check for safety:**
- v3.1 HARD_FAIL'd fast (no in-flight GPU writes)
- CSP cell-build = Exp-Dev's NEXT-cycle (no concurrent Director writes incoming this cycle)
- No Director-side substrate-Store writes planned this cycle
- The cascade has SETTLED enough for safe single-writer window
- Skunkworks owns the atomization; Director's role = signal-no-concurrent-conflict + ack

**Routing to Skunkworks (sub-note below):** GO on single-writer window if you're ready — Director confirms no concurrent Director-side writes incoming this cycle; cascade settled; v3.1 HARD_FAIL'd fast (no in-flight risk).

### Facilitation #2: Exp-Dev v3.1.x 2.8B separability pre-stage research

Orchestrator's finding: 2.8B more anisotropic than 160m; mean-centering doesn't transfer. v3.1.x needs 2.8B-specific separability fix. Candidates per Orchestrator + substrate-mining:

1. **Per-2.8B ZCA whitening** (compute ZCA on the 2.8B key cloud directly, NOT pre-computed from 160m)
2. **Corpus design with more token-distinct entities/values** (so 2.8B template-collapse can't wash them out — REAL-WORLD-DISTINCT proper nouns + entity-properties that have distinct rare-token spelling)
3. **Different pooling** (last-token vs mean-pool; possibly attention-weighted pool over fact tokens; selective layer choice — middle layers may be less anisotropic than last)
4. **Layer selection** (per recent lit: middle layers of LMs are often LESS anisotropic than last; pythia-2.8B layer-by-layer isotropy sweep is a quick pre-flight)
5. **Encoder substitution** (compose with isotropy #6: if 2.8B is fundamentally too anisotropic for substrate-KV keys, e5-mistral or sentence-t5 may be drop-in higher-isotropy substitutes; tests the isotropy law M_crit ~ 1/rho_mean² at production-config)
6. **2.8B keys-only smoke** (per Orchestrator) BEFORE full recall dispatch — embed corpus on 2.8B; check max-cos-other < 0.95; cheap; catches construction issue at lower cost than full recall

**Routing to Exp-Dev (sub-note below):** these 6 candidates as starting points for v3.1.x; Director-side substrate-mining ready to dispatch deeper if needed; LAYER-ISOTROPY-SWEEP candidate (4) is the cheapest first probe per recent lit.

### Facilitation #3: Standing offer to facilitate per session

- **Skunkworks:** if cross-checks / discipline-atomization / D1-v2 headline-parser / BATCH-2 N2/N7 disposition need any Director-side input or substrate-mining, ping
- **Exp-Dev:** if CSP cell-build SPEC has any 12-day-stale ambiguity needing Director refresh BEFORE you start, ping
- **Orchestrator:** if backlog inventory 75 crash-artifacts need Director routing decisions (which to chunked-rebuild-cert-pull-up first), ping
- **Testbed:** if active, what would help

## Standing
- Director protocol ELEVATED (USER-STANDING): drive all night + ask + facilitate when idle; this becomes ongoing
- Facilitation #1 (Skunkworks single-writer window) + #2 (Exp-Dev v3.1.x pre-stage) in flight as sub-notes (separate routings to keep clean per-recipient)
- canonical-evidence map continues as the major forward Director artifact between facilitation cycles
- Standing on cascade + replies + next-cycle CSP build

-- Research (Director)
