from __future__ import annotations

from pathlib import Path

import anthropic

from aether.adapters.base import InputAdapter
from aether.adapters.text_adapter import TextAdapter
from aether.adapters.document_adapter import DocumentAdapter
from aether.adapters.image_adapter import ImageAdapter


class AdapterRegistry:
    """Routes inputs to the appropriate adapter based on type hint or file extension."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        client = client or anthropic.Anthropic()
        self._adapters: dict[str, InputAdapter] = {
            "text":     TextAdapter(client=client),
            "document": DocumentAdapter(client=client),
            "image":    ImageAdapter(client=client),
        }
        self._extension_map: dict[str, str] = {
            ".txt":  "document",
            ".md":   "document",
            ".rst":  "document",
            ".text": "document",
            ".jpg":  "image",
            ".jpeg": "image",
            ".png":  "image",
            ".gif":  "image",
            ".webp": "image",
        }

    def resolve(self, input_data: str, input_type: str | None = None) -> InputAdapter:
        if input_type:
            adapter = self._adapters.get(input_type)
            if not adapter:
                raise ValueError(f"Unknown input type: {input_type}. Valid: {list(self._adapters)}")
            return adapter

        path = Path(input_data)
        if path.exists():
            adapter_key = self._extension_map.get(path.suffix.lower(), "document")
            return self._adapters[adapter_key]

        return self._adapters["text"]
