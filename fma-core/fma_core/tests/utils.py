from __future__ import annotations

import json
from dataclasses import dataclass, field
from io import StringIO


@dataclass
class ModelData:
    data: list

    def open(self, *args):
        return StringIO(json.dumps(self.data))


@dataclass(frozen=True)
class Client:
    id: str


@dataclass
class ModelUpdate:
    data: list | np.ndarray
    client: Client


@dataclass
class ModelAggregate:
    result: any
    id: int | None = None


@dataclass
class ModelArtifact:
    values: ModelData


@dataclass
class ClientList:
    clients: list[Client]

    def all(self):
        return self.clients


@dataclass
class FederatedModel:
    clients: ClientList
    aggregates: list[ModelAggregate] = field(default_factory=list)
    current_artifact: ModelArtifact | None = None
    aggregator: str | None = None


def create_model_file(data: list[int | float]):
    """Simulation of creating a model file"""
    return ModelData(data=data)


@dataclass
class Task:
    """Used to run construct a valid parameter for the post_agg_service function."""

    args: list
    success: bool

    def __init__(self, args, success):
        """Initialization of the Task class.

        :param args: Arguments
        :type args: Dict, optional
        :param success: The initial task success status
        :type success: bool
        """
        self.args = args
        self.success = success
