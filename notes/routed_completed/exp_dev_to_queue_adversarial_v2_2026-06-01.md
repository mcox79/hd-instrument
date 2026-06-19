# exp_dev -> queue: Adversarial composition v2 redesigns (2026-06-01)

Status: SHIPPED

Root cause of v1 DEFENSE_UNNECESSARY (catches #164, #165):
  Adversarial queries in v1 were stored keys themselves (keys[i]).
  Stored keys have max_sim=1.0 to themselves -- always accepted by the 0.50
  defense gate. Defense never fires. defense_rate = 0.0 in both v1 experiments.

Fix: subthreshold collision probes with alpha=0.45 < 0.50 threshold.
  q_adv = alpha * k_i + sqrt(1-alpha^2) * noise_perp_scaled
  sim(q_adv, k_i) = alpha * N / N = alpha = 0.45 < 0.50 -> REJECTED.
  Defense gate fires on ~100% of adversarial probes (verified in smoke).

queue=overnight_queue name=path_d_adversarial_composition_v2_n4096 script=experiments/exp_path_d_adversarial_composition_v2_n4096.py prereg=prereqs/2026-06-01_path_d_adversarial_composition_v2_n4096.md timeout=14400
queue=overnight_queue name=adversarial_aqsim_path_d_compose_v2_n4096 script=experiments/exp_adversarial_aqsim_path_d_compose_v2_n4096.py prereg=prereqs/2026-06-01_adversarial_aqsim_path_d_compose_v2_n4096.md timeout=14400


---

Acted-on 2026-06-01: adversarial v2 anchor processed in v308 batch


Acted-on 2026-06-01: adversarial v2 anchor processed in v308 batch
