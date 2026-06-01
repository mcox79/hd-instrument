# Research: atom-registry design review v1 (PP-3 / PP-12 converged design)

Date: 2026-06-01
Origin: `notes/strategy_request_to_research_atom_registry_design_review_2026-06-01.md` (orchestrator-forwarded from testbed; HIGH severity; gating ~5-7 days PP-3 Phase 2 engineering)
Method: 1 Sonnet drill (~2.5 min, design-pattern + cross-system-precedent lit-scan, generic compliance terms only); main-thread synthesis + calibration

## HEADLINE

**Converged atom-registry design satisfies BOTH PP-3 rotation + PP-12 compositionality verifier-replay with ~8-12 weeks greenfield eng (6-9 weeks if refactoring V2 linear chain). Net novel synthesis ~3-4 weeks; remainder is integration on established primitives (Cert Transparency RFC 9162, Sigstore Rekor, IPFS Merkle-DAG, S/MIME archival, content-addressed storage).**

## Strategic recommendation for testbed PP-3 Phase 2

The 6 design questions converge to a single design:

1. **Atom identity**: content-addressed `atom_id = BLAKE3(data || salt || nonce)`; separate `subject_atom_index` table maps subject_id → {atom_id, ...} for GDPR-deletion lookup
2. **Audit-chain shape**: **DAG with daily Merkle epoch checkpoints**; checkpoint roots signed and submitted to Sigstore Rekor (external transparency log); per-link cost ~347 bytes (315 cert-chain + 32 DAG pointer)
3. **Deletion cascade**: tombstone-in-place (Option b) as primary; zk-SNARK proof as fallback for deep composition trees
4. **Long-lived compositions**: hardening — inline atom data as encrypted snapshot at composition-creation when lifetime > 30 days; standalone atom rotates normally
5. **Tombstone formal shape**: `{atom_id, deletion_timestamp, deletion_reason_code, hash_of_deleted_data, deletion_authority_sig (Ed25519), cert_chain_link_ref, merkle_proof_at_deletion}`; **~760 bytes minimum** for GDPR Art 17 defense
6. **External compliance**: GDPR Art 17 → `deletion_authority_sig` is the erasure certificate; HIPAA §164.312(b) → epoch checkpoint roots are the audit controls trail; SOC 2 CC7.2/7.3 → Rekor checkpoint submission is the cryptographic trail; EU AI Act Art 50/Annex IV → composition cert + atom provenance chain is the technical documentation

Total: 8-12 weeks greenfield / 6-9 weeks refactor from V2 linear chain. Phasing: (1) atom identity + tombstone model, 3 weeks; (2) DAG refactor + Merkle checkpointing, 4 weeks; (3) hardening + verifier API, 3 weeks; (4) Rekor integration + compliance documentation, 2 weeks.

## Q1. Atom identity schema — content-addressed + separate subject index

| Schema | Deletion-ergonomics | Forensic-audit-ergonomics | Storage-efficiency | API-simplicity |
|---|---|---|---|---|
| Subject-keyed `hash(subject_id, data, salt)` | 5 — prefix scan deletes all subject atoms | 2 — subject linkage exposed in ID space | 4 | 3 — verifier must know subject_id |
| Composition-keyed (atom_id derived from composition) | 2 — must walk composition graph per subject | 5 — provenance directly encoded | 3 — duplicates if atom in multiple compositions | 2 — multiple IDs for same logical atom |
| Dual-keyed (subject internal ID + composition audit alias) | 4 | 4 | 2 — two ID spaces | 3 |
| **Content-addressed `hash(data, salt)`, subject linkage in separate index** | **3** — needs subject_atom_index lookup | **4** — content-stable audit alias | **5** | **4** |

**Recommendation: content-addressed**. Atom_id = BLAKE3(data || salt || nonce). Separate `subject_atom_index` maps subject_id → {atom_id, ...}. Deletion: index lookup, collect atom_ids, write tombstones, purge index entries. Audit: verifier uses atom_id directly.

**Precedent**: AWS S3 Object Lock (content-hash ETag + bucket policy separation); IPFS CIDs (CID + pin metadata separation); Certificate Transparency RFC 9162 (leaf hash identity + cert-owner identity separation).

**Eng cost**: 1-2 weeks. Complexity: index is second write path; index purge must be atomic with tombstone write (two-phase commit or WAL).

## Q2. Deletion cascade semantics — tombstone-in-place primary

| Option | Compliance | Forensic-audit survives | Storage cost | Verifier-replay still works |
|---|---|---|---|---|
| (a) Re-cert composition without atom | 4 | 3 — provenance altered | 3 | 4 |
| **(b) Redact atom in place; tombstone keeps cert valid** | **5** | **5** — chain unbroken | **4** — ~760 byte tombstone | **5** |
| (c) Archive to cold storage | 1 — data still exists; Art 17 NON-compliant | 5 | 2 | 5 |
| (d) Block reads from composition | 2 — data still exists; not deletion | 5 | 5 | 1 |
| (e) zk-proof of prior atom existence | 5 | 5 | 3 — costly upfront | 5 |

**Primary recommendation: Option (b) tombstone-in-place**. The `deletion_authority_sig` (Ed25519 signed by deletion-authority key) is the "erasure certificate" regulator-defensible under GDPR Art 17. The `hash_of_deleted_data` proves correct-record deletion without re-exposing data. Original cert-chain link is NOT removed — annotated with pointer to tombstone. Composition cert remains valid (references atom_id + cert-chain link, not atom data).

**Fallback (Option e) for edge cases**: When compositions hashed atom CONTENT (not just atom_id), tombstone alone is insufficient. zk-SNARK proof of prior atom existence lets verifier confirm "atom existed with these properties" without re-exposing data.

**Precedent**: AWS CloudTrail key-rotation annotation pattern; Sigstore Rekor revocation entries (Merkle path intact); CT RFC 9162 §8.1 expired-certificate handling; ICO/CNIL guidance on cryptographic erasure certificates.

**Eng cost**: 2-3 weeks. Complexity: tombstone-write atomicity with data-deletion (write tombstone → zero data → confirm; rollback path).

## Q3. Audit-chain shape — DAG with Merkle checkpointing

**Linear cert-chain (current V2)**: rotation-tolerant (deletion of atom data doesn't break chain). Verifier-replay O(n) sequential scan. Partial verification expensive.

**Merkle tree**: O(log n) inclusion proof. Deletion-tolerant via tombstone leaf at same position. Designed for fixed-epoch batch commits, not streaming.

**DAG**: composition nodes have explicit back-pointers to constituent atom nodes. Verifier-replay O(k) subgraph walk where k = atoms in composition. Partial verification native. Deletion = atom node content → tombstone; back-pointers still resolve.

**Recommendation: DAG with Merkle epoch checkpointing**. Atom + composition nodes are DAG vertices; "composition-used-atom" edges. Daily Merkle checkpoint over all DAG nodes; checkpoint root signed and submitted to Sigstore Rekor as transparency log. Per-link cost ~347 bytes (315 cert-chain + 32 DAG pointer SHA-256).

**Verifier-replay complexity**: O(k + log n) where k = atoms in composition, n = total DAG size. 10-atom composition at n=10^6 → proof bundle ~10 KB. Verifier-transmissible.

**Precedent**: Git object DAG (blobs/trees/commits = atoms/compositions/epochs); IPFS Merkle-DAG (IPLD) for arbitrary sub-DAG verification; CT for Merkle inclusion proofs.

**Eng cost**: 3-5 weeks for V2 linear-chain → DAG refactor + Merkle checkpointing.

## Q4. 30-day retention window vs long-lived compositions — hardening

Three mechanisms evaluated:

- **Refresh (expiry clock resets on reference)**: NOT VIABLE — creates Art 17 window-extension without re-consent (regulator audit would flag)
- **Re-cert on atom rotation**: compliant (re-cert documents rotation) but creates audit artifact complexity
- **Hardening (inline atom data into long-lived composition at creation)**: cleanest

**Recommendation: Hardening with retention-class tagging.**

Atoms have `retention_class` ∈ {SHORT (30-day default), LONG (extended retention; requires re-consent record), SNAPSHOT (inlined into composition; not independently retained)}.

When composition created with `lifetime > 30 days`:
1. Inline atom data into composition cert as encrypted snapshot (KMS-managed composition-specific key)
2. Write atom standalone copy as SHORT-class; rotates normally
3. Composition cert stands independently; verifiable without standalone atom

**GDPR Art 17 interaction**: if subject revokes post-composition-creation, snapshot inside composition cert IS the deletion target. Composition cert re-issued with snapshot → tombstone.

**Precedent**: S/MIME email archiving (cert is composition; key is atom; key expiry doesn't invalidate archived certs); CloudTrail key-rotation handling for retained log entries.

**Eng cost**: 2-3 weeks (retention-class tagging + hardening + KMS integration).

## Q5. Forensic-audit gap — tombstone formal shape

**Tombstone minimum viable shape**:
```
Tombstone_X = {
  atom_id:               BLAKE3(data || salt || nonce)
  deletion_timestamp:    ISO-8601 UTC
  deletion_reason_code:  "GDPR_ART17" | "RETENTION_EXPIRY" | ...
  hash_of_deleted_data:  BLAKE3(original_atom_data)
  deletion_authority_sig: Ed25519(deletion_authority_key,
                           hash(atom_id || deletion_timestamp || hash_of_deleted_data))
  cert_chain_link_ref:   link_id of original atom-write cert-chain entry
  merkle_proof_at_deletion: Merkle path atom→epoch-checkpoint-root
}
```

**Verifier checks**:
1. cert_chain_link_ref resolves to valid cert-chain entry (atom written + cert'd)
2. hash_of_deleted_data matches cert-chain entry's recorded write-time hash
3. deletion_authority_sig valid under known deletion-authority public key
4. merkle_proof_at_deletion validates against signed epoch-checkpoint root
5. For composition C: each referenced atom_id has valid cert_chain_link OR valid tombstone

**Minimum size (GDPR Art 17 defense)**: 32 (hash) + 8 (timestamp) + 64 (Ed25519 sig) + 16 (link UUID) + 640 (Merkle proof at n=10^6, 20-level × 32 bytes) = **~760 bytes**.

**Verification cost**: 1 Ed25519 verify + 1 Merkle path check + 1 cert-chain link lookup = **<50ms per tombstone with warm index**.

**Precedent**: Sigstore Rekor revocation records (exact same shape); CT RFC 9162 §4.4 signed tree head verification.

**Eng cost**: 1-2 weeks (assumes DAG + Merkle checkpointing from Q3).

## Q6. Cross-system primitives — ranked

### Tier 1 (direct load-bearing precedent)

**Certificate Transparency RFC 9162**: append-only Merkle log with signed tree heads + inclusion proofs. Adapting requires: deletion-event record type + tombstone semantics + DAG back-pointers. Append-only-only model too strict for GDPR Art 17. Eng: 4-6 weeks to build CT-analog (fork Trillian/Sunlight as starting point).

**Sigstore Rekor transparency log**: append-only Merkle log with REST API + Trillian backend. Revocations map well to tombstones (Q5). Adapting requires: subject-rights revocation as first-class record + subject-consent DB integration + DAG composition-back-pointers. **MOST PRACTICAL STARTING POINT**. Eng: 3-5 weeks building on Rekor REST API.

**Vector commitments (Tas-Boneh 2020)**: cross-updatable position-indexed commitment; O(1) deletion updates. Requires trusted setup + BLS12-381/BN256 curve ops (~100× more expensive than SHA-256). Verifier-replay = O(k) pairings. Eng: 8-12 weeks; novel synthesis area; no off-the-shelf production system.

### Tier 2 (partial precedent; significant adaptation)

- **AWS CloudTrail**: hash-chained ops log; no GDPR deletion. Architectural reference only; minimal eng if just used as reference
- **Hyperledger Fabric audit logs**: private-data-purge exists but produces silent delete (not regulator-defensible tombstone). Eng 10-15 weeks; too heavy
- **zk-SNARK based audit**: perfect "verify without revealing data"; impractical per-atom (minutes/proof current SOTA). Practical only as Q2 fallback for deep composition trees. Eng 16-24 weeks for production
- **TPM PCR pattern**: hardware-anchored linear hash-chain analog; useful as trust anchor for deletion-authority key (PCR extends on each deletion event). Eng 2-3 weeks as trust anchor

## Load-bearing novel vs literature-precedent

**Direct literature precedent (no synthesis gap)**:
- Content-addressed atom_id (IPFS, Git, CT)
- Linear-to-DAG audit chain (Git object model, IPLD)
- Tombstone-in-place with hash + authority_sig (Sigstore Rekor revocation, CT annotation)
- Merkle epoch checkpoints + inclusion proofs (CT RFC 9162)
- Encrypted snapshot hardening for long-lived references (S/MIME archival, JWT)

**Novel synthesis (no direct precedent)**:
1. **Subject-rights-triggered deletion flowing into Merkle DAG** (~2-3 weeks): combination of GDPR Art 17 as first-class trigger for atomic tombstone-write + DAG annotation + Merkle checkpoint update not implemented in any public system. CT is append-only; Rekor doesn't implement subject-rights revocation.
2. **Composition-as-verifiable-subgraph with deletion-tolerant atom references** (~3-4 weeks): CT/Rekor treat each entry as independent. DAG composition-back-pointers + subgraph verifier-replay is novel application of Merkle-DAG to audit-log semantics. Closest precedent: W3C PROV-DM (provenance but no crypto verifiability layer).
3. **Hardened-snapshot lifecycle with Art 17 re-deletion targeting** (~2 weeks): pattern of inlining atom data at creation → snapshot becomes Art 17 deletion target → tombstone re-cert of composition has no exact precedent. S/MIME handles key rotation but not subject-rights deletion.

**Net novel synthesis cost: ~3-4 weeks of the 8-12 week total. Remainder is integration on established primitives.**

## Cap_map implications

**PP-3 row** (currently 0.55-0.70 or 0.62-0.75 per Phase 1 partial LIFT proposal):
- Phase 2 design now CONCRETE with eng cost bracketed (6-9 weeks refactor / 8-12 weeks greenfield) and external compliance defensibility mapped to GDPR Art 17 / HIPAA / SOC 2 / EU AI Act
- Recommended next LIFT after Phase 2 implementation: 0.75-0.88 (per testbed Q4 spec)
- New caveat: ~3-4 weeks of net novel synthesis remains (subject-rights-triggered Merkle DAG + composition-subgraph verifier-replay + hardened-snapshot Art 17 re-deletion); not pure integration

**PP-12 row** (currently 0.60-0.75 design-drill HARD_PASS):
- Audit chain DAG + Merkle checkpointing satisfies PP-12's composition-verifier-replay requirement
- ~7 person-week original estimate for PP-12 reduces materially if PP-3 Phase 2 lands first (shared atom-registry infrastructure)
- Recommended row LIFT after PP-3 Phase 2 implementation: 0.65-0.80 (per atom-registry convergence)

## Method notes

- Per [[feedback-no-padding-experiments]]: 1 Sonnet drill (not parallel) because design questions are tightly coupled (atom identity → audit-chain shape → tombstone shape → verifier-replay)
- Per [[feedback-subagent-model-optimization]]: Sonnet appropriate for design-pattern + cross-system-precedent lit-scan
- Per [[feedback-query-privacy-decomposition]]: generic compliance + audit-log terms only; no project-identifying fingerprints
- Per [[feedback-lit-scan-calibration-penalty]]: design recommendations grounded in cross-system precedent (high-precedent items) vs explicitly flagged novel-synthesis areas (~3-4 weeks of total cost)
- Wall time: dispatch + read prereqs + synthesize + write deliverable + routing close ≈ 25 min

## What I'm routing back to orchestrator

This research note ITSELF closes `notes/strategy_request_to_research_atom_registry_design_review_2026-06-01.md` (per its closing instruction). Both this routing AND the testbed-source routing (`notes/strategy_request_to_strategy_atom_registry_design_review_2026-06-01.md`) move to `routed_completed/`.

Testbed picks up the converged design from THIS file for PP-3 Phase 2 implementation (~6-9 weeks; phased per the strategic recommendation section above). PP-12 implementation benefits from shared infrastructure.

Open decisions for orchestrator + testbed:
1. **Phasing approval**: 4 phases (atom identity + tombstone / DAG refactor / hardening + verifier API / Rekor integration). Approve in order, or testbed proposes alternative sequencing?
2. **Sigstore Rekor vs Trillian fork vs build-greenfield**: research recommends Rekor REST API as starting point (3-5 weeks vs 4-6 weeks CT-analog vs 8-12 weeks novel). Confirm.
3. **Vector commitments deferred?** Research recommends DEFER (8-12 weeks novel + cryptographic-library integration; payoff unclear vs Merkle tree at this scale). Confirm.
4. **PP-3 + PP-12 cap_map row LIFT timing**: post-Phase-2-implementation? Or partial LIFT now on design-drill HARD_PASS?


---

Acted-on 2026-06-01: atom registry design adopted; testbed handoff filed; PP-3/PP-12 converged design


Acted-on 2026-06-01: atom registry design adopted; PP-3/PP-12 converged design
