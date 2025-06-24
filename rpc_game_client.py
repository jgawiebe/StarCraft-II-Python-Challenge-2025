import grpc
import exercise3_pb2
import exercise3_pb2_grpc
from pysc2.lib.actions import FunctionCall

from rpc_utils import action_cmd


class GameClient:
    """RPC client that fetches actions from a remote controller."""
