from env.shadow_supervisor_env import ShadowSupervisorEnv


def test_env_reset_and_step():
    env = ShadowSupervisorEnv(scenario_path="data/scenarios_eval.json")
    obs = env.reset(seed=123, scenario_index=0)

    assert isinstance(obs, dict)

    next_state, reward, done, info = env.step("assign_research")

    assert isinstance(next_state, dict)
    assert isinstance(reward, (int, float))
    assert isinstance(done, bool)
    assert isinstance(info, dict)


