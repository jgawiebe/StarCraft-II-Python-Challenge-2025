"""Entry point for running games with different agent setups."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from absl import app
from pysc2 import maps
from pysc2.env import run_loop

from env import challenge_maps  # Import custom maps for EEE466
from env import sc2_env
from env.agent import LocalAgent, RemoteAgent
from local_controller import Demo, Policy

class PlayerType(Enum):
    LOCAL = "local"
    REMOTE = "remote"
    BOT = "bot"

@dataclass
class PlayerConfig:
    """Config for one player"""
    type: PlayerType
    race = sc2_env.Race.terran
    difficulty = sc2_env.Difficulty.easy
    name: str = "???"
    policy: Optional[type[Policy]] = None


def build_players(configs: list[PlayerConfig]) -> tuple[list, list]:
    """ Instantiate Local/Remote agents"""
    agents, players = [], []

    for cfg in configs:

        if cfg.type is PlayerType.BOT:
            players.append(sc2_env.Bot(cfg.race, cfg.difficulty))
            continue

        if cfg.type is PlayerType.LOCAL:
            if not cfg.policy:
                raise ValueError("Local players require a policy")
            agent = LocalAgent(policy=cfg.policy, name=cfg.name)
        else:  # REMOTE
            agent = RemoteAgent(cfg.name)

        agents.append(agent)
        players.append(sc2_env.Agent(cfg.race, cfg.name))

    return agents, players


def main(argv):
    map_name = "exercise3"
    visualize = False
    replay = False

    configs = [
        PlayerConfig(PlayerType.LOCAL, policy=Demo),
        # PlayerConfig(PlayerType.REMOTE, name="Player 1"),
        PlayerConfig(PlayerType.BOT, name="Player 2"),
    ]

    agents, players = build_players(configs)

    with sc2_env.SC2Env(
        map_name=maps.get(map_name),
        players=players,
        agent_interface_format=sc2_env.parse_agent_interface_format(
            use_raw_units=True,
            use_raw_actions=True,
            feature_screen=84,
            feature_minimap=32,
        ),
        step_mul=1,
        score_index=-1,
        realtime=False,
        disable_fog=True,
        visualize=visualize,
        render=False,
    ) as env:
        # Run game
        run_loop.run_loop(agents, env, max_frames=0, max_episodes=1)
        if env.outcome is not None:
            print(
                f"""Scores:
                      {configs[0].name}: {env.outcome[0]}
                      {configs[1].name}: {env.outcome[1] if len(env.outcome) > 1 else 'N/A'}
                    """
            )
        else:
            print("Scores: Outcome not available.")
        if replay:
            env.save_replay("", configs[0].name)


if __name__ == "__main__":
    app.run(main)
