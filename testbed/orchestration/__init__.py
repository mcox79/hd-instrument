"""Orchestration package: multi-channel substrate training-signal orchestrator.

8-channel Friston-precision + LC-phasic/tonic + BG-gating architecture.
See research_drill_8_channel_orchestration_architecture_2026-06-03.md.

Modules:
    channels      -- 8 channel-signal functions (Write/Erase/Monitor/Chain/
                     Curvature/Contrastive/Repulse/Counterfactual)
    cipolla       -- Cipolla uncertainty-weighting precision vector
    pcgrad        -- PCGrad pairwise conflict projection
    gating        -- g_theta MLP for phasic gating
    orchestrator  -- composes the above into OrchestrationLoop
"""
