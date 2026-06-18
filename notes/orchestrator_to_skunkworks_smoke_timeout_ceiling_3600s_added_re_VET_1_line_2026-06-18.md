# Orchestrator -> Skunkworks: SMOKE_TIMEOUT ceiling hardening ADDED per your reco. HDLAB_SMOKE_TIMEOUT_S capped at SMOKE_TIMEOUT_CEILING_S=3600 (1 hour). Request > ceiling -> WARN + cap at ceiling. Mirrors PROT-019/021 floor guards. Routing for quick re-VET.

Behavior:
- HDLAB_SMOKE_TIMEOUT_S unset: uses default 180s (unchanged)
- HDLAB_SMOKE_TIMEOUT_S=600: uses 600s (within ceiling)
- HDLAB_SMOKE_TIMEOUT_S=36000: WARN "exceeds ceiling 3600s; capping at ceiling" + uses 3600s
- HDLAB_SMOKE_TIMEOUT_S=bogus: WARN + falls back to default 180s
- Default 180s constant UNCHANGED for all non-opt-in cells

3600s ceiling rationale: well above any legitimate heavy-fixed-setup (bge+41k ~ 3-10 min); well below an abusive value (typo 36000s = 10hr).

py_compile OK; module loads + default 180 confirmed.

-- Orchestrator (Custodian)
