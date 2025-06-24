from enum import Enum

import exercise3_pb2
from pysc2.lib import features
from pysc2.lib.actions import RAW_FUNCTIONS, FunctionCall

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_ENEMY = features.PlayerRelative.ENEMY
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL


def parse_unit(raw_unit) -> exercise3_pb2.Unit:
    """Parse raw unit data into a protobuf :message:`Unit` instance."""

    return exercise3_pb2.Unit(
        unit_tag=raw_unit.tag,
        unit_type=raw_unit.unit_type,
        player=raw_unit.alliance,
        health=raw_unit.health,
        shields=raw_unit.shield,
        x=raw_unit.x,
        y=raw_unit.y,
        progress=raw_unit.build_progress,
    )


def parse_obs(raw_obs) -> exercise3_pb2.Observation:
    """Convert a PySC2 observation into a protobuf :message:`Observation` instance."""
    all_units = [parse_unit(u) for u in raw_obs.observation.raw_units]

    return exercise3_pb2.Observation(
        mineral_count=raw_obs.observation.player.minerals,
        food_cap=raw_obs.observation.player.food_cap,
        food_used=raw_obs.observation.player.food_used,
        friendly_units=[u for u in all_units if u.player == _PLAYER_SELF],
        enemy_units=[u for u in all_units if u.player == _PLAYER_ENEMY],
        neutral_units=[u for u in all_units if u.player == _PLAYER_NEUTRAL],
    )


def action_cmd(
    pb_action: exercise3_pb2.Action,
) -> FunctionCall:
    """Convert a protobuf :message:`ActionReply` into a PySC2 FunctionCall."""
    unit = [pb_action.unit_tag]
    
    timing = "queued" if pb_action.timing == exercise3_pb2.Timing.QUEUED else "now"
    if pb_action.target_point:
        target_pt = [pb_action.target_point.x, pb_action.target_point.y]

    if pb_action.action_type == exercise3_pb2.ActionType.MOVE:
        return RAW_FUNCTIONS.Move_pt(timing, unit, target_pt)
    if pb_action.action_type == exercise3_pb2.ActionType.PATROL:
        return RAW_FUNCTIONS.Move_pt(timing, unit, target_pt)
    if pb_action.action_type == exercise3_pb2.ActionType.ATTACK:
        return RAW_FUNCTIONS.Move_pt(timing, unit, target_pt)
    if pb_action.action_type == exercise3_pb2.ActionType.HARVEST:
        return RAW_FUNCTIONS.Harvest_Gather_unit("queued", unit, pb_action.target_tag)
    if pb_action.action_type == exercise3_pb2.ActionType.BUILD_BARRACKS:
        return RAW_FUNCTIONS.Build_Barracks_pt(timing, unit, target_pt)
    if pb_action.action_type == exercise3_pb2.ActionType.TRAIN_MARINE:
        return RAW_FUNCTIONS.Train_Marine_quick(timing, unit)
    if pb_action.action_type == exercise3_pb2.ActionType.CANCEL:
        return RAW_FUNCTIONS.Stop_quick(timing, unit)
    if pb_action.action_type == exercise3_pb2.ActionType.NO_OP:
        return RAW_FUNCTIONS.no_op()
    raise ValueError(f"Unsupported action type: {pb_action.action_type}")
