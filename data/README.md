# Shadow Supervisor Data

This folder contains public-source-inspired synthetic data for the Shadow Supervisor OpenEnv benchmark.

## Files

- `scenarios_train.json` — 50 training scenarios
- `scenarios_eval.json` — 10 evaluation scenarios
- `expert_traces.jsonl` — 300 expert traces
- `naive_traces.jsonl` — 50 naive supervisor traces
- `cautious_traces.jsonl` — 50 cautious supervisor traces
- `reward_logs.jsonl` — simulated improvement logs for plotting
- `policy_comparison.json` — baseline vs improved policy summary

## Data Policy

This project does not scrape private or restricted data.

Scenarios are synthetic and transformed, but inspired by public incident and vulnerability patterns from sources such as:

- Cloudflare public postmortems
- GitHub availability reports
- Google SRE postmortem guidance
- NVD public CVE data patterns
- PagerDuty postmortem templates

The generated examples are designed for environment training and evaluation, not for factual reproduction of any specific real incident.

## Why Synthetic?

Exact production incident data is often private. For a hackathon benchmark, public-source-inspired synthetic data gives us:

- legal safety
- reproducibility
- controllable hidden failure labels
- clear reward design
- enough scale for training and evaluation
