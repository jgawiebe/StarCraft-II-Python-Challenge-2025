import sys
from abc import ABC, abstractmethod
from concurrent import futures

import grpc
import exercise3_pb2
import exercise3_pb2_grpc

# IDs for common unit/structure types
COMMAND_CENTER_TYPE = 19
BARRACKS_TYPE = 21
PYLON_TYPE = 60
MINERAL_FIELD_TYPE = 341
SCV_TYPE = 45
MARINE_TYPE = 48
ZEALOT_TYPE = 73


class Policy(ABC):
    """Policies implement the strategy pattern"""

    @abstractmethod
    def get_action(self, obs: exercise3_pb2.Observation) -> exercise3_pb2.Action:
        pass

class RemotePolicy(Policy):
    """Policy skeleton"""
    def __init__(self):
        pass

    def get_action(self, obs: exercise3_pb2.Observation) -> exercise3_pb2.Action:
        return exercise3_pb2.Action(
            action_type=exercise3_pb2.ActionType.NO_OP,
            unit_tag=0,
        )

# Add gRPC controller and server classes here


if __name__ == "__main__":
    sys.exit()
