# The archive already predicted today's write-gate negative. We ran it anyway.

**2026-08-19. Answers the owner's standing question: *"I want to know how you missed that surprise
experimental data - I thought we had this all consolidated and known at this point? What else are we
missing?"***

Today's `exp_predictive_write_gate_v1` pre-committed reading (C) -- *"GATED ties or loses to
ACCUMULATE at every threshold -> the residual gate does not help"* -- and (C) fired. Mining the
RESULTS archive (not the code archive) afterwards turned up two landed cells from 2026-07-16 that
between them predicted that outcome a month in advance.

## What was already on disk, disk-verified from metrics.json (not from docstrings)

**`exp_ingest_gate_deconfound_within_relation_derivability_v1`**
verdict `MEASURED_BOUND_relation_identity_artifact`

    DECONF_AUC   0.545      <- flat raw surprise, chance = 0.500
    CONF_AUC     0.990      <- confound control reproduces
    POSCTRL_AUC  0.999      <- positive control fires
    RANDLABEL    0.486      <- random-label control at chance

Read plainly: **once you control for which relation a fact belongs to, raw surprise cannot tell a
fact the system could have worked out from one it could not.** Surprise detected whole-relation
presence -- an encoding-status signal -- not within-schema novelty. The controls are clean, so this
is a real bound and not a broken harness.

**`exp_ingest_gate_combination_rule_race_v1`**
verdict `SCHEMAFIT_CARRIES_the_fix`

    arm            DECONF_AUC (test)
    flat            0.542    raw prediction error alone -- CHANCE
    schemafit       0.836    the structural signal alone
    brain           0.530    raw_PE * (1 - schema_fit), Friston form, fixed weights -- CHANCE
    hybrid          0.602    same form, calibrated weights
    learned         0.628    free features, weights learned

## The three things this actually establishes, at three different strengths

**DURABLE -- flat raw surprise sits at chance.** Measured twice, in two cells, with clean controls:
0.545 and 0.542. Today's residual gate is the same quantity under a different name, applied to a
different task, and it did the same nothing. **Reading (C) was predictable from the archive before a
line of it was written.**

**LEAD ONLY, AND I AM NOT GOING TO OVERSTATE IT -- "schemafit carries the fix".** The verdict string
says it; the per-seed numbers do not support leaning on it. Three seeds, `min_class=3`, `bal=0.38`,
and the schemafit arm reads **0.642 / 1.000 / 0.867** across them. A 1.000 on a class of three is a
width, not an effect. This is a lead worth testing at power, not a result to build on. Logging it
this way deliberately: *reading an underpowered null as a capability statement* is the error that has
cost this project the most, and reading an underpowered WIN the same way is the same error wearing
better clothes.

**NOTABLE AND AWKWARD -- the brain-form arm was ALSO at chance (0.530).** `raw_PE * (1 - schema_fit)`
is the Friston precision-weighted decomposition, and it did no better than flat. The cell's own
docstring was honest about why that is allowed to happen: *"the Friston fast/slow decomposition is
DIRECTOR/DRILL SYNTHESIS -- no paper states it, P<=0.50."* So the archive does **not** hand us a
brain-faithful fix for the write gate. It hands us a prediction of the failure and one underpowered
lead.

## Why I missed it, stated exactly

The prior-work check I ran covered the **code** archive -- the capability registry and `hdlab/` --
and confirmed nothing there implemented a residual write gate. That was true. It was also the wrong
question. **The results archive holds the finding, and EXISTS-IN-CODE and HAS-BEEN-MEASURED are
different questions with different indexes.** Non-negotiable 5 names only the registry, which is why
the check felt complete when it was half done.

The rule earned from this is already in CLAUDE.md as **TWO ARCHIVES, TWO QUESTIONS**. This note is
the worked instance behind it.

## What it costs

One experiment that could have been skipped, and more importantly a wrong prior: I went into today
treating "does prediction error gate writes usefully" as open when it had a measured chance-level
answer. The instrument was fine. **The retrieval was the failure, twice now** -- the same shape as
the 2026-08-18 incident that produced `tools/experiment_index.py` in the first place.
