import random
from abc import ABC, abstractmethod

from pysc2.lib.actions import RAW_FUNCTIONS, FunctionCall

from .local_utils import (
    BARRACKS_TYPE,
    COMMAND_CENTER_TYPE,
    MARINE_TYPE,
    MID_PT,
    MINERAL_FIELD_TYPE,
    PYLON_TYPE,
    SCV_TYPE,
    Observation,
    action_cmd,
)


class Policy(ABC):
    """Policies implement the strategy pattern"""

    @abstractmethod
    def get_action(self, obs) -> object:
        pass


class Ostrich(Policy):
    """Example policy that does nothing."""

    def __init__(self):
        self.name = "Ostrich"

    def get_action(self, obs) -> FunctionCall:
        return RAW_FUNCTIONS.no_op()


class Demo(Policy):
    """Gather minerals, build barracks, train marine, then attack."""

    def __init__(self):
        self.name = "Demo"
        self._built_barracks = False
        self._trained_marine = False

    def get_action(self, obs: Observation) -> FunctionCall:
        # Collect unit‐object lists and their tags
        scv_units = [u for u in obs.friendly_units if u.unit_type == SCV_TYPE]

        barracks = [u.tag for u in obs.friendly_units if u.unit_type == BARRACKS_TYPE]

        marines = [u.tag for u in obs.friendly_units if u.unit_type == MARINE_TYPE]

        mineral_fields = [
            mf for mf in obs.neutral_units if mf.unit_type == MINERAL_FIELD_TYPE
        ]
        minerals = obs.mineral_count

        # If you have a barracks and ≥50 minerals, queue up a Marine
        if barracks and minerals >= 50:
            return action_cmd(action="train_marine", units=barracks[0], timing="queue")

        # Otherwise pick a random SCV action
        choice = random.choice(["harvest", "build_barracks", "attack"])
        if choice == "harvest":
            # gather from a mineral field
            return action_cmd(
                action="harvest",
                units=scv_units[0].tag,
                target=mineral_fields[0],  # pass the Unit object
            )

        if choice == "build_barracks" and minerals >= 150:
            # build at a fixed point
            return action_cmd(
                action="build_barracks",
                units=scv_units[0].tag,
                target=(12.5, 15.5),  # x,y coordinates
            )

        if choice == "attack":
            if obs.enemy_units:
                # attack the first enemy unit
                return action_cmd(
                    action="attack",
                    units=scv_units[0].tag,
                    target=obs.enemy_units[0],  # pass the Unit object
                )
        return RAW_FUNCTIONS.no_op()
