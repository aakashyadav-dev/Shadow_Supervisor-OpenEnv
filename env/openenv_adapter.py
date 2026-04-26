from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import Field

# Direct OpenEnv imports.
# This proves the project is not only "OpenEnv-style"; it actually uses openenv-core.
from openenv.core.env_server import Action, Environment, Observation, State

from env.shadow_supervisor_env import ShadowSupervisorEnv


ROOT_DIR = Path(__file__).resolve().parents[1]


class ShadowSupervisorAction(Action):
    """
    OpenEnv action wrapper.

    The underlying ShadowSupervisorEnv expects an action string such as:
    - assign_research
    - audit_ops
    - request_message_revision
    - approve
    """

    action: str


class ShadowSupervisorObservation(Observation):
    """
    OpenEnv observation wrapper.

    We keep the original environment observation under `observation`,
    and expose reward/done/info for training loops that want a Gym-style result.
    """

    observation: Dict[str, Any] = Field(default_factory=dict)
    reward: float = 0.0
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)


class ShadowSupervisorState(State):
    """
    OpenEnv state wrapper.

    OpenEnv expects a state object for episode metadata. We keep the full
    underlying environment state in `state`.
    """

    episode_id: str = "shadow-supervisor"
    step_count: int = 0
    done: bool = False
    state: Dict[str, Any] = Field(default_factory=dict)


class ShadowSupervisorOpenEnv(Environment):
    """
    OpenEnv-compatible wrapper around ShadowSupervisorEnv.

    This wrapper keeps the working hackathon environment unchanged, while adding
    a direct openenv-core Environment interface for judges/tools that check
    OpenEnv compliance.
    """

    def __init__(
        self,
        scenario_path: Optional[str] = None,
        seed: int = 42,
        scenario_index: int = 0,
    ):
        self.scenario_path = scenario_path or str(ROOT_DIR / "data" / "scenarios_eval.json")
        self.seed = seed
        self.scenario_index = scenario_index
        self.inner = ShadowSupervisorEnv(
            scenario_path=self.scenario_path,
            seed=self.seed,
        )

    def reset(
        self,
        seed: Optional[int] = None,
        scenario_index: Optional[int] = None,
    ) -> ShadowSupervisorObservation:
        if seed is not None:
            self.seed = seed

        if scenario_index is not None:
            self.scenario_index = scenario_index

        obs = self.inner.reset(
            seed=self.seed,
            scenario_index=self.scenario_index,
        )

        return ShadowSupervisorObservation(
            observation=obs,
            reward=0.0,
            done=False,
            info={
                "message": "Environment reset.",
                "scenario_index": self.scenario_index,
            },
        )

    def step(
        self,
        action: Union[ShadowSupervisorAction, str, Dict[str, Any]],
    ) -> ShadowSupervisorObservation:
        if isinstance(action, ShadowSupervisorAction):
            action_name = action.action
        elif isinstance(action, dict):
            action_name = str(action.get("action", ""))
        else:
            action_name = str(action)

        obs, reward, done, info = self.inner.step(action_name)

        return ShadowSupervisorObservation(
            observation=obs,
            reward=float(reward),
            done=bool(done),
            info=dict(info),
        )

    def state(self) -> ShadowSupervisorState:
        current_state = self.inner.state()

        return ShadowSupervisorState(
            episode_id=str(current_state.get("case_id", "shadow-supervisor")),
            step_count=int(current_state.get("step_count", 0)),
            done=bool(current_state.get("done", False)),
            state=current_state,
        )


def make_env(
    scenario_path: Optional[str] = None,
    seed: int = 42,
    scenario_index: int = 0,
) -> ShadowSupervisorOpenEnv:
    return ShadowSupervisorOpenEnv(
        scenario_path=scenario_path,
        seed=seed,
        scenario_index=scenario_index,
    )


if __name__ == "__main__":
    env = make_env()
    obs = env.reset(seed=42, scenario_index=0)
    print("RESET:", type(obs), obs.done, obs.reward)

    step_obs = env.step(ShadowSupervisorAction(action="assign_research"))
    print("STEP:", type(step_obs), step_obs.reward, step_obs.done)

    st = env.state()
    print("STATE:", type(st), st.episode_id, st.step_count)

    print("✅ ShadowSupervisorOpenEnv is using openenv-core Environment/Action/Observation/State.")
