"""Utility helpers for parsing observations and issuing actions."""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional, Union

import numpy
from pysc2.lib import features
from pysc2.lib.actions import RAW_FUNCTIONS, FunctionCall
from pysc2.lib.point import Point

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_ENEMY = features.PlayerRelative.ENEMY
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL

# IDs for common unit/structure types
COMMAND_CENTER_TYPE = 19
BARRACKS_TYPE = 21
PYLON_TYPE = 58
MINERAL_FIELD_TYPE = 341
SCV_TYPE = 45
MARINE_TYPE = 48
# Map references
MID_PT = 16


class ActionType(str, Enum):
    MOVE = "move"
    PATROL = "patrol"
    ATTACK = "attack"
    HARVEST = "harvest"
    BUILD_BARRACKS = "build_barracks"
    TRAIN_MARINE = "train_marine"
    CANCEL = "cancel"


class TargetType(str, Enum):
    UNIT = "unit"
    POINT = "point"


class Timing(str, Enum):
    NOW = "now"
    QUEUED = "queued"

class Coordinate:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


@dataclass(frozen=True)
class Unit:
    """Simplified representation of a unit."""

    tag: int
    unit_type: int
    player: int
    health: int
    shields: int
    x: float
    y: float
    progress: float


@dataclass
class Observation:
    """Simplified representation of a game observation."""

    mineral_count: int
    food_cap: int
    food_used: int
    friendly_units: List[Unit]
    enemy_units: List[Unit]
    neutral_units: List[Unit]


def parse_unit(raw_unit) -> Unit:
    """Parse raw unit data into a :class:`Unit` object."""

    return Unit(
        tag=raw_unit.tag,
        unit_type=raw_unit.unit_type,
        player=raw_unit.alliance,
        health=raw_unit.health,
        shields=raw_unit.shield,
        x=raw_unit.x,
        y=raw_unit.y,
        progress=raw_unit.build_progress,
    )


def parse_obs(raw_obs) -> Observation:
    """Convert a PySC2 observation into an :class:`Observation` object."""
    all_units = [parse_unit(u) for u in raw_obs.observation.raw_units]

    return Observation(
        mineral_count=raw_obs.observation.player.minerals,
        food_cap=raw_obs.observation.player.food_cap,
        food_used=raw_obs.observation.player.food_used,
        friendly_units=[u for u in all_units if u.player == _PLAYER_SELF],
        enemy_units=[u for u in all_units if u.player == _PLAYER_ENEMY],
        neutral_units=[u for u in all_units if u.player == _PLAYER_NEUTRAL],
    )


def action_cmd(
    action: str,
    units: Union[int, Iterable[int]],
    target: Optional[Union[tuple, Unit]] = None,
    timing: str = "now",
) -> FunctionCall:
    """Convert a custom action into a PySC2 FunctionCall."""
    action_enum = ActionType(action)
    u = [units] if isinstance(units, (int, numpy.integer)) else list(units)

    # Infer target type
    if isinstance(target, Unit):
        target_type = TargetType.UNIT
        target_val = target.tag
    elif isinstance(target, tuple):
        target_type = TargetType.POINT
        target_val = Point.build(Coordinate(*target))
    elif target is None:
        target_type = None
        target_val = None
    else:
        raise ValueError("Invalid target type. Must be Unit or tuple.")

    move_actions = {
        ActionType.MOVE: (RAW_FUNCTIONS.Move_unit, RAW_FUNCTIONS.Move_pt),
        ActionType.PATROL: (RAW_FUNCTIONS.Patrol_unit, RAW_FUNCTIONS.Patrol_pt),
        ActionType.ATTACK: (RAW_FUNCTIONS.Attack_unit, RAW_FUNCTIONS.Attack_pt),
    }

    # Select action (function) based on action and target type
    # Movement actions can be to a unit or to a point
    if action_enum in move_actions:
        fn_unit, fn_point = move_actions[action_enum]
        if target_type == TargetType.UNIT:
            return fn_unit(timing, u, target_val)
        elif target_type == TargetType.POINT:
            return fn_point(timing, u, target_val)
        else:
            raise ValueError(f"Action {action_enum.name} requires a target.")

    if action_enum == ActionType.HARVEST:
        return RAW_FUNCTIONS.Harvest_Gather_unit("queued", units, target_val)
    if action_enum == ActionType.BUILD_BARRACKS:
        return RAW_FUNCTIONS.Build_Barracks_pt(timing, units, target_val)
    if action_enum == ActionType.TRAIN_MARINE:
        return RAW_FUNCTIONS.Train_Marine_quick(timing, units)
    if action_enum == ActionType.CANCEL:
        return RAW_FUNCTIONS.Stop_quick(timing, units)
    raise ValueError(f"Unsupported action type: {action_enum}")
