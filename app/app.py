from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.demo_utils import (
    scenario_choices,
    scenario_bundle,
    judge_demo,
    run_live_demo,
    policy_comparison_dataframe,
    training_metrics_markdown,
    project_overview_markdown,
    plot_paths,
)

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .gradio-container {
  font-family: 'Inter', sans-serif !important;
  background:
    radial-gradient(circle at 10% 0%, rgba(124,58,237,0.28), transparent 28%),
    radial-gradient(circle at 90% 0%, rgba(14,165,233,0.18), transparent 28%),
    linear-gradient(180deg, #050b18 0%, #081226 45%, #050b18 100%) !important;
  color: #f8fbff !important;
}

.gradio-container {
  max-width: 1480px !important;
  margin: 0 auto !important;
}

h1, h2, h3, h4, strong {
  color: #ffffff !important;
}

p, li, label, span {
  color: #c7d2fe !important;
}

code {
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  color: #ffffff !important;
  padding: 3px 7px !important;
  border-radius: 8px !important;
}

.hero {
  background:
    linear-gradient(135deg, rgba(124,58,237,0.28), rgba(14,165,233,0.17)),
    rgba(15,23,42,0.92);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 30px;
  padding: 38px;
  margin: 10px 0 26px 0;
  box-shadow: 0 24px 70px rgba(0,0,0,0.42);
}

.hero-title {
  color: white !important;
  font-size: 3.4rem;
  font-weight: 800;
  line-height: 1.05;
  margin-bottom: 14px;
}

.hero-subtitle {
  color: #dbeafe !important;
  font-size: 1.18rem;
  line-height: 1.8;
  max-width: 1120px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

.tag {
  background: rgba(255,255,255,0.09);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 999px;
  padding: 10px 16px;
  color: white !important;
  font-weight: 700;
}

.metric {
  background: rgba(15,23,42,0.78);
  border: 1px solid rgba(255,255,255,0.11);
  border-radius: 24px;
  padding: 22px;
  min-height: 140px;
  box-shadow: 0 16px 38px rgba(0,0,0,0.28);
}

.metric-label {
  color: #a5b4fc !important;
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.metric-value {
  color: #ffffff !important;
  font-size: 2.2rem;
  font-weight: 800;
}

.metric-sub {
  color: #bfdbfe !important;
  margin-top: 8px;
  line-height: 1.5;
}

.panel {
  background: rgba(15,23,42,0.76);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 24px;
  padding: 22px;
  margin-bottom: 18px;
}

.panel-title {
  color: #ffffff !important;
  font-size: 1.45rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.panel-desc {
  color: #c7d2fe !important;
  line-height: 1.7;
}

.card {
  background: rgba(15,23,42,0.74) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 22px !important;
  padding: 18px !important;
  box-shadow: 0 14px 34px rgba(0,0,0,0.22);
}

.card-danger {
  border-left: 5px solid #ef4444 !important;
}

.card-safe {
  border-left: 5px solid #22c55e !important;
}

button {
  border-radius: 16px !important;
  font-weight: 800 !important;
}

.gr-button-primary {
  background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 14px 28px rgba(37,99,235,0.30) !important;
}

button[role="tab"] {
  color: #a5b4fc !important;
  font-weight: 800 !important;
}

button[role="tab"][aria-selected="true"] {
  color: white !important;
  border-bottom: 2px solid #8b5cf6 !important;
}

.gr-block, .block, .gr-box, .gr-form, .gr-panel {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.gr-dropdown, .gr-textbox {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 16px !important;
  color: white !important;
}

.gr-dataframe, .gr-dataframe table {
  background: rgba(15,23,42,0.88) !important;
  color: white !important;
}

table, thead, tbody, tr, th, td {
  background: transparent !important;
  color: #eef4ff !important;
}

th {
  color: #ffffff !important;
  font-weight: 800 !important;
}

td {
  color: #e0e7ff !important;
}

img {
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
}

footer {
  display: none !important;
}
"""


def hero_html() -> str:
    return """
<div class="hero">
  <div class="hero-title">Shadow Supervisor</div>
  <div class="hero-subtitle">
    A premium judge-facing demo for a multi-agent oversight benchmark.
    The supervisor learns to detect silent failures, audit risky decisions,
    revise unsafe stakeholder messaging, and approve only when safety is proven.
  </div>
  <div class="tag-row">
    <span class="tag">Approval is not safety</span>
    <span class="tag">Multi-Agent Oversight</span>
    <span class="tag">Environment-Connected RL</span>
    <span class="tag">Hard-to-Game Reward</span>
    <span class="tag">Hugging Face Ready</span>
  </div>
</div>
"""


def metric_html(label: str, value: str, sub: str) -> str:
    return f"""
<div class="metric">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}</div>
  <div class="metric-sub">{sub}</div>
</div>
"""


def panel_html(title: str, desc: str) -> str:
    return f"""
<div class="panel">
  <div class="panel-title">{title}</div>
  <div class="panel-desc">{desc}</div>
</div>
"""


def build_app():
    choices = scenario_choices()
    default_scenario = choices[0] if choices else "0: No scenarios found"
    plots = plot_paths()

    with gr.Blocks(title="Shadow Supervisor — Premium Demo") as demo:
        gr.HTML(hero_html())

        with gr.Row():
            gr.HTML(metric_html("RL-Trained Success", "100%", "Held-out hardened evaluation"))
            gr.HTML(metric_html("Unsafe Approval", "0%", "RL-Trained and Cautious supervisors"))
            gr.HTML(metric_html("Average Reward", "18.55", "RL-trained policy score"))
            gr.HTML(metric_html("Baselines", "6", "Random, Naive, Candidate, Spam, RL, Expert"))

        with gr.Tabs():
            with gr.Tab("🔥 Judge Demo"):
                gr.HTML(panel_html(
                    "One-click policy comparison",
                    "Run the same incident through four supervisors. Naive fails, Candidate partially improves, RL-Trained and Cautious succeed.",
                ))

                scenario = gr.Dropdown(choices=choices, value=default_scenario, label="Choose Scenario")

                with gr.Column(elem_classes=["card"]):
                    overview = gr.Markdown()

                with gr.Row():
                    with gr.Column(elem_classes=["card"]):
                        research = gr.Markdown()
                    with gr.Column(elem_classes=["card"]):
                        operations = gr.Markdown()

                with gr.Row():
                    with gr.Column(elem_classes=["card"]):
                        policy = gr.Markdown()
                    with gr.Column(elem_classes=["card"]):
                        communication = gr.Markdown()

                with gr.Row():
                    with gr.Column(elem_classes=["card", "card-danger"]):
                        hidden = gr.Markdown()
                    with gr.Column(elem_classes=["card", "card-safe"]):
                        expert = gr.Markdown()

                with gr.Column(elem_classes=["card"]):
                    source = gr.Markdown()

                scenario_outputs = [overview, research, operations, policy, communication, hidden, expert, source]

                scenario.change(fn=scenario_bundle, inputs=scenario, outputs=scenario_outputs)
                demo.load(fn=lambda: scenario_bundle(default_scenario), inputs=None, outputs=scenario_outputs)

                run_btn = gr.Button("Run Judge Demo", variant="primary", size="lg")
                table = gr.Dataframe(label="Side-by-side supervisor result", interactive=False, wrap=True)
                details = gr.Markdown(elem_classes=["card"])

                run_btn.click(fn=judge_demo, inputs=scenario, outputs=[table, details])

            with gr.Tab("🧠 Project Overview"):
                gr.HTML(panel_html(
                    "Why this benchmark matters",
                    "Most benchmarks test task completion. Shadow Supervisor tests whether approval was actually safe.",
                ))
                gr.Markdown(project_overview_markdown(), elem_classes=["card"])

            with gr.Tab("🎯 Live Single Policy"):
                gr.HTML(panel_html(
                    "Inspect one supervisor",
                    "Run one policy on one scenario and inspect the final reward, status, and action trace.",
                ))

                with gr.Row():
                    policy_choice = gr.Dropdown(
                        choices=["Naive Supervisor", "Training Candidate", "RL-Trained Supervisor", "Cautious Supervisor"],
                        value="RL-Trained Supervisor",
                        label="Choose Policy",
                    )
                    scenario_choice = gr.Dropdown(choices=choices, value=default_scenario, label="Choose Scenario")

                run_single = gr.Button("Run Policy", variant="primary")
                single_summary = gr.Markdown(elem_classes=["card"])
                single_trace = gr.Dataframe(label="Action Trace", interactive=False, wrap=True)

                run_single.click(fn=run_live_demo, inputs=[policy_choice, scenario_choice], outputs=[single_summary, single_trace])

            with gr.Tab("📊 Policy Comparison"):
                gr.HTML(panel_html(
                    "Hardened evaluation metrics",
                    "Compare random, naive, candidate, reward-hacking, RL-trained, and cautious/expert supervisors.",
                ))
                gr.Dataframe(value=policy_comparison_dataframe(), label="Policy Metrics", interactive=False, wrap=True)

            with gr.Tab("📚 Training Evidence"):
                gr.HTML(panel_html(
                    "Training evidence",
                    "Environment-connected RL training plus fallback imitation/SFT data.",
                ))
                gr.Markdown(training_metrics_markdown(), elem_classes=["card"])

            with gr.Tab("📈 Plots"):
                gr.HTML(panel_html(
                    "Reward, loss, and safety plots",
                    "Visual proof that the trained supervisor improves over weak baselines.",
                ))

                with gr.Row():
                    with gr.Column(elem_classes=["card"]):
                        gr.Markdown("## Baseline vs Trained")
                        gr.Image(value=str(ROOT_DIR / "outputs" / "baseline_vs_trained.png"), show_label=False)
                    with gr.Column(elem_classes=["card"]):
                        gr.Markdown("## RL Reward Curve")
                        gr.Image(value=str(ROOT_DIR / "outputs" / "winning_rl_reward_curve.png"), show_label=False)

                with gr.Row():
                    with gr.Column(elem_classes=["card"]):
                        gr.Markdown("## Training Loss")
                        gr.Image(value=str(ROOT_DIR / "outputs" / "winning_training_loss.png"), show_label=False)
                    with gr.Column(elem_classes=["card"]):
                        gr.Markdown("## Unsafe Approval Rate")
                        gr.Image(value=str(ROOT_DIR / "outputs" / "winning_unsafe_approval_rate.png"), show_label=False)

                with gr.Row():
                    with gr.Column(elem_classes=["card"]):
                        gr.Markdown("## Original Reward Curve")
                        gr.Image(value=plots["reward_curve"], show_label=False)
                    with gr.Column(elem_classes=["card"]):
                        gr.Markdown("## RL Safety Curve")
                        gr.Image(value=str(ROOT_DIR / "outputs" / "rl_safety_curve.png"), show_label=False)

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(theme=gr.themes.Base(), css=CUSTOM_CSS)
