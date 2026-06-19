from __future__ import annotations

from pathlib import Path

import anthropic

from aether.adapters.base import InputAdapter
from aether.adapters.text_adapter import TextAdapter
from aether.models.context_graph import ContextGraph


class DocumentAdapter(InputAdapter):
    """Reads a text/markdown document from disk and delegates to TextAdapter."""

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".rst", ".text"}

    def __init__(self, client: anthropic.Anthropic | None = None):
        self._text_adapter = TextAdapter(client=client)

    def parse(self, input_data: str) -> ContextGraph:
        """input_data is a file path."""
        path = Path(input_data)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {input_data}")
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        content = path.read_text(encoding="utf-8")
        prompt = (
            f"The following is a document titled '{path.name}'.\n\n"
            f"Extract all goals, systems, components, assets, capabilities, "
            f"actors, and constraints from it.\n\n"
            f"{content}"
        )
        return self._text_adapter.parse(prompt)
