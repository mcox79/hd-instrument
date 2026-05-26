# Pre-registration: wave14_bet_f_sketch5_kerdock_coset_topology

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Bet F rehab Sketch 5 (Strategy enumerated; queue-jumping #4 → urgent for pipeline)
Author: experiment_dev session, pipeline tick 78

## Why

Strategy's Bet F rehab request file enumerated 5 R28-supplied sketches.
Sketch 5: "Topology-by-coset (Kerdock structure) — store facts in Kerdock
cosets where each coset relationship IS the topological invariant. Codebook
geometry carries the topology, not the data encoding."

This sketch is buildable WITHOUT Research's full pass because Kerdock infra
exists (4-coset codebook from v3, sample_kerdock_keys assigns coset labels).
Test: store facts with explicit coset labels; apply noise; recover correct
coset assignment. If coset recovery >> chance, Kerdock geometry IS a
topological-protection primitive.

Queue-jumps Strategy's sequence (which had Research items first) per user
pipeline-depth pressure — but the sketch is Strategy-listed, not invented.

## Mechanism

  codebook, info = make_kerdock_4coset_codebook(N)  # 4 cosets each of N codewords
  # Sample M facts, each tagged with its coset index (0..3)
  fact_indices = random sample of M codeword positions
  fact_cosets = floor(fact_indices / N)  # coset label per fact
  
  # Encode substrate W = Hebbian sum over outer products
  W = sum_i outer(codebook[fact_indices[i]], coset_label_atom[fact_cosets[i]])

  for p_noise in [0, 0.02, 0.05, 0.10, 0.20]:
    W_noisy = bit-flip noise at rate p (perturb stored W entries)
    for each fact:
      retrieved_coset_atom = W_noisy @ codebook[fact_indices[i]]
      predicted_coset = argmax(coset_label_atoms @ retrieved_coset_atom)
      record correct = (predicted_coset == fact_cosets[i])
    recovery_rate[p] = mean(correct)

## Verdict labels

- BET_F_S5_TOPOLOGY_PROTECTED (recovery > 0.85 at p=0.05; sharp decay vs random control)
- BET_F_S5_PARTIAL (0.4 < recovery <= 0.85 at p=0.05)
- BET_F_S5_KILLED (recovery <= 0.4 at p=0.05; Kerdock geometry doesn't carry topology)
- BET_F_S5_INCONCLUSIVE

## Runtime: ~5 min CPU/GPU
