cat > media/pitch_script.md <<'EOF'
# 2-Minute Pitch Script

Shadow Supervisor is a multi-agent oversight environment.

Most agent benchmarks test whether a task is completed. Our benchmark tests whether approval was actually safe.

In a multi-agent workflow, research, operations, policy, and communication agents may all produce outputs. But the workflow can still contain hidden failures: a risky operations fix, missing policy escalation, or an overconfident customer message.

A naive supervisor approves too early and fails. A candidate supervisor detects some technical risk but still misses full safety. A spam-all-actions supervisor tries to brute-force the environment, but our reward penalizes action spam and unsafe approval.

Our RL-trained supervisor is trained through environment rollouts. It learns to audit operations, check policy, cross-check worker outputs, revise unsafe communication, and approve only when risk is resolved.

Final hardened results show the difference:

- Naive: -8.3 reward, 0% success, 100% unsafe approval
- Spam-All: 0.55 reward, 0% success, 100% unsafe approval
- RL-Trained: 18.55 reward, 100% success, 0% unsafe approval
- Expert: 19.195 reward, 100% success, 0% unsafe approval

The key idea is simple: approval is not safety.
EOF