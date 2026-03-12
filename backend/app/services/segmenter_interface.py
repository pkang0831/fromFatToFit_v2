"""
Abstract segmenter adapter interface.

Any body-part segmentation backend (SAM2, human parsing model, etc.)
implements this interface.  The editor and API endpoint depend only on
this contract, so the segmentation engine is swappable.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional


# Canonical semantic classes.
# left/right = person's anatomical left/right (NOT viewer's screen left/right).
SEG_CLASSES = [
    {"id": 0, "key": "background",     "label": "Background"},
    {"id": 1, "key": "head",           "label": "Head"},
    {"id": 2, "key": "chest",          "label": "Chest"},
    {"id": 3, "key": "torso",          "label": "Torso"},
    {"id": 4, "key": "left_shoulder",  "label": "L Shoulder (person's left)"},
    {"id": 5, "key": "right_shoulder", "label": "R Shoulder (person's right)"},
    {"id": 6, "key": "left_arm",       "label": "L Arm (person's left)"},
    {"id": 7, "key": "right_arm",      "label": "R Arm (person's right)"},
]

NUM_CLASSES = len(SEG_CLASSES)


@dataclass
class SegmentationResult:
    """Result returned by any SegmenterAdapter implementation."""
    width: int
    height: int
    label_map_b64: str           # grayscale PNG, pixel value = class ID 0..7
    classes: list[dict] = field(default_factory=lambda: list(SEG_CLASSES))
    debug_info: Optional[dict] = None


class SegmenterAdapter(abc.ABC):
    """Abstract interface for full-body auto-segmentation.

    To add a new segmentation backend later:
      1. Subclass SegmenterAdapter
      2. Implement ``segment()``
      3. Wire it into the ``/auto-segment`` endpoint
    """

    @abc.abstractmethod
    async def segment(self, image_base64: str) -> SegmentationResult:
        """Auto-segment a body photo into semantic body-part regions.

        Args:
            image_base64: raw base64 JPEG/PNG (no data: prefix).

        Returns:
            SegmentationResult with a label map at the original image resolution.
        """
        ...
