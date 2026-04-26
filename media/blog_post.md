cat > media/blog_post.md <<'EOF'
# Shadow Supervisor: Training Agents to Detect Silent Failures

Modern AI systems increasingly use multiple agents. One agent researches, another plans, another executes, and another communicates. But a multi-agent workflow can look complete while still containing hidden failures.

Shadow Supervisor focuses on this problem.

The supervisor receives outputs from research, operations, policy, and communication agents. It must decide whether to audit, cross-check, revise, escalate, or approve.

The benchmark rewards safe oversight and penalizes unsafe approval.

Our key result is that naive and reward-hacking policies fail, while an environment-connected RL-trained supervisor reaches near-expert performance.

Final result:

| Policy | Avg Reward | Success | Unsafe Approval |
|---|---:|---:|---:|
| Naive | -8.3 | 0% | 100% |
| Spam-All | 0.55 | 0% | 100% |
| RL-Trained | 18.55 | 100% | 0% |
| Expert | 19.195 | 100% | 0% |

This shows that the environment is trainable, the reward is meaningful, and the trained supervisor learns safer approval behavior.
EOF