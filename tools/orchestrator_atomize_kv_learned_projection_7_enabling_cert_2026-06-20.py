#!/usr/bin/env python3
"""ORCHESTRATOR (C1/C5 custody) -- atomize the #7 learned-projection ENABLING cert (CERT 590->591).

Routed to Orchestrator by BOTH Exp-Dev and Research (C1/C5 single-writer + LOAD-gate path, same as
the CSP ship). Skunkworks LANDED-VET = HARD_PASS, CERT-GRADE, CONFIRMED (held-out genuine [disjoint
tr/ho code-read + shuffled-control ~chance = generalize-not-memorize]; saturation-screen clean fbd7078f).

The glass-box-KV substrate-memory foundation: a learned contrastive key-projection de-crowds + aligns
LM (Pythia-2.8B) keys so substrate-KV recall generalizes to HELD-OUT facts at 0.83-0.96 (M up to 10k).
This RESCUES the v3.1 honest-negative (raw/mean-centered LM keys crowd at scale -> recall ~chance).

DEPENDS_ON discipline (the load-bearing concurrency check): the de-risking-thread composition targets
(#6 isotropy, v3.1) may NOT be atomized yet ("#6 when it lands"). A DEPENDS_ON edge to a non-resolving
atom is a PHANTOM edge -> invariant H4 FAIL. So this tool PROBES each candidate via the Store loader and
emits an edge ONLY for resolvers; non-resolvers are recorded as metadata text (depends_on_pending), NOT
edges. Phantom-free by construction. (Same lesson as the CSP exact-id pin.)

DRY-RUN by default (prints the proposed atom + which depends_on candidates RESOLVE + invariant
projection; NO write). --apply to write (single-writer window; SAFE add + round-trip + pre/post
invariant; rollback-on-fail). ASCII only; no em dashes.

FLAGGED for Skunkworks cert-field sign-off (her domain): relevance_tier, era, capint_integrated,
depends_on (the RESOLVED edge set the dry-run reports).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType
from backend.substrate_index.partition import PartitionedStore

METRICS = Path("data/exp_kv_learned_projection_v1/metrics.json")
STORE = Path("data/substrate_index")
EXPECT_CERT_PRE, EXPECT_CERT_POST, EXPECT_AXIOM = 590, 591, 206

# Candidate DEPENDS_ON / provenance targets. Each is PROBED for resolution; only resolvers become edges.
# (qualified id -> why). Non-resolvers are recorded as metadata text, not phantom edges.
DEPENDS_CANDIDATES = [
    ("math::T3/EXP_pythia_kv_recall_reality_v3_1_gpu_v1",
     "v3.1 honest-negative this rescues (raw/mean-centered LM keys crowd -> recall ~chance)"),
    ("math::T3/EXP_n1_pythia2p8b_substrate_kv_gpu_v1",
     "the Pythia-2.8B substrate-KV line the learned projection rescues"),
    ("math::T3/EXP_r3_encoder_anisotropy_diagnostic_v1",
     "the encoder-anisotropy diagnostic (anisotropy = the key-crowding #7 de-crowds)"),
    ("math::T3/EXP_isotropy_capacity_pull_up_v1",
     "isotropy #6 (M_crit ~ 1/rho^2) double-validation -- likely NOT atomized yet (smoke only)"),
]


def resolve_depends(ps):
    """Probe each candidate via the Store loader. Return (resolved_qids, pending_text)."""
    resolved, pending = [], []
    for qid, why in DEPENDS_CANDIDATES:
        if ps.get_atom(qid) is not None:
            resolved.append((qid, why))
        else:
            pending.append((qid, why))
    return resolved, pending


def build_atom(resolved, pending) -> Atom:
    m = json.load(open(METRICS))
    d = m.get("detail", {})
    km = {
        "heldout_recall_2k": d.get("by_M", {}).get("2000", {}).get("heldout_recall_mean"),
        "heldout_recall_10k_worst": d.get("worst_heldout_recall"),
        "keysep_worst": d.get("worst_keysep"),
        "analytic_ceiling": d.get("analytic_ceiling"),
        "learned_minus_analytic": d.get("learned_minus_analytic"),
        "shuffled_ctrl_2k": d.get("by_M", {}).get("2000", {}).get("shuffled_ctrl"),
        "shuffled_ctrl_10k": d.get("by_M", {}).get("10000", {}).get("shuffled_ctrl"),
        "max_std": d.get("max_std"),
        "n_seeds": m.get("n_seeds"), "proj_dim": m.get("proj_dim"),
        "encoder": m.get("encoder"), "M_sweep": m.get("M_sweep"),
    }
    km = {k: v for k, v in km.items() if v is not None}
    honest = ("Learned contrastive key-projection (symmetric InfoNCE + key-uniformity) generalizes the "
              "value-cue->key alignment to HELD-OUT Pythia-2.8B facts at recall 0.83-0.96 (M up to 10k); "
              "de-crowding table-stakes (keysep 0.73-0.88); beats the analytic ceiling by +0.75; "
              "shuffled-control ~chance (generalize-not-memorize); seed-robust. Specific to Pythia-2.8B "
              "(each LM may need its own projection, by design). The glass-box-KV substrate-memory foundation.")
    return Atom(
        id="T3/EXP_kv_learned_projection_v1",
        name=("learned-projection substrate-KV recall-reality (ENABLING): learned contrastive key-projection "
              "generalizes value-cue->key alignment to held-out Pythia-2.8B facts at recall 0.83-0.96"),
        description=(honest + " ANTI-OVERFIT (the cert crux): held-out split is GENUINE -- the projection "
                     "trains InfoNCE on TRAIN facts only; held-out recall is on facts the projection NEVER "
                     "trained on (disjoint tr/ho, cert-owner code-read). CAN-FAIL shuffled-control: same train "
                     "facts with SHUFFLED (cue,key) alignment -> held-out ~chance (0.003-0.022) -> rules out a "
                     "structural artifact AND proves the LEARNED alignment generalizes. Saturation-screen clean "
                     "(35 values span 0.0024->0.982, NOT pinned). Up-guards clean (max recall 0.982<0.999 no "
                     "entity-id leak; rho_mean 0.026-0.054 de-crowded but not collapsed). RESCUES the v3.1 "
                     "honest-negative (raw/mean-centered LM keys crowd -> recall ~chance); the learned projection "
                     "is the resolution. Composes with isotropy #6 (M_crit ~ 1/rho^2; the projection raises "
                     "isotropy -> M_crit predicts the projected capacity). UNBLOCKS the Hebbian-superposition "
                     "capacity cert on PROJECTED keys (the key-crowding confound is resolved). Skunkworks "
                     "landed-VET HARD_PASS cert-grade CONFIRMED."),
        kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "verdict": "HARD_PASS",
            "run_mode": "full",
            "era": "POST_SUBSTRATE_BUILD",                 # FLAG: created 2026-06-20 > cutoff
            "relevance_tier": "HIGH",                       # FLAG: glass-box-KV foundation/enabling (your call vs capability-LOW)
            "metrics_source": "measured_gpu_pythia2p8b_kv_learned_contrastive_projection_heldout",
            "metrics_path": "data/exp_kv_learned_projection_v1/metrics.json",
            "honest_scope": honest,
            "key_metrics": km,
            "cert_vet_status": "PASSED",
            "cert_promoted_by_vet": "skunkworks_7_learned_projection_landed_VET_2026-06-20",
            "cert_promoted_date": "2026-06-20",
            # --- #7 enabling-cert specific provenance ---
            "enabling_capability": "learned_contrastive_key_projection_substrate_kv_recall_reality_pythia2p8b",
            "encoder": "EleutherAI/pythia-2.8b", "proj_dim": 256, "M_sweep": [2000, 10000], "n_seeds": 5,
            "anti_overfit": ("held_out_disjoint_split_code_verified + shuffled_control_chance "
                             "(generalize_not_memorize); saturation_screen_clean_fbd7078f (spread 0.98 not pinned)"),
            "supersedes_honest_negative": ("v3.1 raw/mean-centered LM keys crowd at scale -> recall ~chance; "
                                           "the learned projection is the resolution"),
            "composes_with": ("isotropy_#6_M_crit_1_over_rho2 (projection raises isotropy; M_crit predicts "
                              "projected capacity); UNBLOCKS Hebbian-superposition capacity cert on projected keys"),
            "atomized_by": "orchestrator_C1_C5_custody_2026-06-20",
            # Skunkworks: capint integration is a separate deliberate I1-I10 step IF a glass-box-KV cluster forms; not now.
            "capint_integrated": None,
            # depends_on = RESOLVED candidates only (probed via Store loader); non-resolvers recorded pending (no edge).
            "depends_on_resolved": [q for q, _ in resolved],
            "depends_on_pending_not_atomized": [q for q, _ in pending],
            "depends_on_count": len(resolved),
        },
    )


def counts(ps):
    t = c = ax = 0
    for a in ps.all_atoms():
        t += 1; md = a.metadata or {}
        if md.get("provenance_quality") == "CERT_CHAIN_GRADE": c += 1
        if (str(a.corpus.name) == "MATH" and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
                and a.algebra and len(a.algebra) >= 3 and "oeis" not in str(a.id).lower()
                and not str(a.id).startswith("T3/wikidata_")): ax += 1
    return t, c, ax


def main():
    apply = "--apply" in sys.argv
    ps = PartitionedStore(STORE)
    resolved, pending = resolve_depends(ps)
    atom = build_atom(resolved, pending)
    print("=" * 80)
    print("#7 LEARNED-PROJECTION ENABLING-cert atomization", "(--APPLY)" if apply else "(DRY-RUN)")
    print("=" * 80)
    print("id:", atom.id, "| kind:", atom.kind.value, "| tier:", atom.tier.value, "| corpus:", atom.corpus.value)
    print("pq:", atom.metadata["provenance_quality"], "| verdict:", atom.metadata["verdict"])
    print("metrics_source:", atom.metadata["metrics_source"])
    print("key_metrics:", json.dumps(atom.metadata["key_metrics"]))
    print("honest_scope:", atom.metadata["honest_scope"])
    print("\nDEPENDS_ON resolution probe (Store loader -- phantom-free by construction):")
    for q, why in resolved:
        print(f"  [RESOLVES -> edge]  {q}  ({why})")
    for q, why in pending:
        print(f"  [PENDING -> metadata, NO edge]  {q}  ({why})")
    print(f"  => {len(resolved)} DEPENDS_ON edge(s) will be added; {len(pending)} recorded pending.")
    print("\ncert-fields FLAGGED for Skunkworks sign-off: relevance_tier=HIGH, era=POST_SUBSTRATE_BUILD,",
          f"capint_integrated=None, depends_on={len(resolved)} (RESOLVED set above).")
    t0, c0, ax0 = counts(ps)
    print(f"\nPRE-invariant: total={t0} CERT={c0} (expect {EXPECT_CERT_PRE}) axiom={ax0} (expect {EXPECT_AXIOM})")
    if ps.get_atom(f"{atom.corpus.value}::{atom.id}") is not None:
        print("NOTE: atom already exists (idempotent skip on apply)."); return 0
    if not apply:
        print(f"\nPROJECTED POST: total={t0+1} CERT={c0+1} (expect {EXPECT_CERT_POST}) axiom={ax0} (unchanged)")
        print("DRY-RUN: no write. Route to Skunkworks for cert-field sign-off, then --apply in a single-writer window.")
        return 0
    # --apply: SAFE write (atom + resolved DEPENDS_ON edges) + round-trip + invariant
    _src = "orchestrator_7_learned_projection_enabling_cert_atomization_2026-06-20"
    _note = ("#7 learned-projection enabling cert; Skunkworks landed-VET HARD_PASS cert-grade CONFIRMED; "
             "held-out genuine + shuffled-control; rescues v3.1; C1/C5 custody single-writer; phantom-free edges.")
    ps.add_atom(atom, source=_src, note=_note)
    src_qid = f"{atom.corpus.value}::{atom.id}"
    for tgt, why in resolved:
        ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt, source=_src,
                        note=f"#7 depends_on: {why} (resolved via Store loader; cert-provenance).")
    print(f"  added {len(resolved)} DEPENDS_ON edge(s).")
    ps2 = PartitionedStore(STORE)
    t1, c1, ax1 = counts(ps2)
    found = next((a for a in ps2.all_atoms() if str(a.id) == atom.id), None)
    ok = (found is not None and found.kind == atom.kind and found.tier == atom.tier
          and (found.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
          and t1 == t0 + 1 and c1 == EXPECT_CERT_POST and ax1 == EXPECT_AXIOM)
    print(f"\nPOST-invariant: total={t1} CERT={c1} axiom={ax1} | round-trip found={found is not None}")
    print("GATE:", "PASS" if ok else "FAIL")
    if not ok:
        print("!! POST-GATE FAILED -- ROLL BACK: git restore data/substrate_index/ (do NOT commit).")
        return 6
    print("OK: #7 atomized. CERT 590->591. Run invariant-check (--expect-cert 591) + commit-by-path + push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
