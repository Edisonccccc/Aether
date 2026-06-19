from __future__ import annotations

from abc import ABC, abstractmethod
from aether.models.context_graph import ContextGraph


class InputAdapter(ABC):
    @abstractmethod
    def parse(self, input_data: str) -> ContextGraph:
        """Transform raw input into a Context Graph."""
        ...
