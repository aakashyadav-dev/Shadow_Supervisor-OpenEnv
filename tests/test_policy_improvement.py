from env.shadow_supervisor_env import ShadowSupervisorEnv
from agents.naive_policy import NaiveSupervisorPolicy
from agents.rl_policy import RLEnvTrainedPolicy


def test_rl_beats_naive_policy():
    env1 = ShadowSupervisorEnv(scenario_path="data/scenarios_eval.json")
    naive = NaiveSupervisorPolicy().run_episode(env1, scenario_index=0, seed=42)

    env2 = ShadowSupervisorEnv(scenario_path="data/scenarios_eval.json")
    rl = RLEnvTrainedPolicy().run_episode(env2, scenario_index=0, seed=42)

    assert rl["total_reward"] > naive["total_reward"]
    assert rl["success"] is True