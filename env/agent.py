"""Agent implementations used by ``run.py``."""

from __future__ import annotations
from typing import Any, Callable, Type

from pysc2.agents import base_agent
from pysc2.lib.actions import FunctionCall


import rpc_utils
from local_controller import local_utils
from rpc_game_client import GameClient


class BaseCustomAgent(base_agent.BaseAgent):
    """Base class for custom agents."""

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

    def setup(self, obs_spec, action_spec) -> None:
        super().setup(obs_spec, action_spec)
        if "raw_units" not in obs_spec:
            raise Exception("This agent requires the raw_units observation.")

    def step(self, obs) -> FunctionCall:
        # Return default no-op FunctionCall if not implemented
        return FunctionCall(0, [])


class RemoteAgent(BaseCustomAgent):
    """Agent controlled remotely via RPC."""

    def __init__(self, name) -> None:
        self.name = name
        self.game_client = GameClient()
        super().__init__(self.name)

    def step(self, obs) -> FunctionCall:
        super().step(obs)
        observation = rpc_utils.parse_obs(obs)
        return self.game_client.get_action(observation)

class LocalAgent(BaseCustomAgent):
    """Agent controlled by a local policy object."""

    def __init__(self, policy, name) -> None:
        self.policy = policy()
        self.name = getattr(self.policy, "name", None) or name
        super().__init__(self.name)
        

    def step(self, obs) -> FunctionCall:
        super().step(obs)
        observation = local_utils.parse_obs(obs)
        return self.policy.get_action(observation)


class Bot:
    """Container for bot player metadata."""

    def __init__(self, name: str) -> None:
        self.name = name
