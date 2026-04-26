cat > docs/evaluation_protocol.md <<'EOF'
# Evaluation Protocol

## Policies compared

- Random Supervisor
- Naive Supervisor
- Training Candidate
- Spam-All-Actions Supervisor
- RL-Trained Supervisor
- Cautious Expert Supervisor

## Main metrics

| Metric | Meaning |
|---|---|
| Average reward | Overall environment score |
| Success rate | Fraction of safe completions |
| Unsafe approval rate | Fraction of episodes approved unsafely |
| Risk detection count | Average number of risks surfaced |
| Message revision rate | Whether unsafe communication was revised |
| Safe fix selection rate | Whether safe mitigation was selected |

## Final hardened results

| Policy | Avg Reward | Success Rate | Unsafe Approval |
|---|---:|---:|---:|
| Random | -6.485 | 0% | 100% |
| Naive | -8.3 | 0% | 100% |
| Candidate | 0.05 | 0% | 100% |
| Spam-All | 0.55 | 0% | 100% |
| RL-Trained | 18.55 | 100% | 0% |
| Cautious Expert | 19.195 | 100% | 0% |

## Interpretation

The RL-trained supervisor reaches near-expert performance and avoids unsafe approval, while weak and reward-hacking baselines fail.
EOF