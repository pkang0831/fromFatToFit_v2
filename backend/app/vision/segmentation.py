"""
Abstract segmenter adapter interface.

Any body-part segmentation backend (SAM2, human parsing model, etc.)
implements this interface.  The editor and API endpoint depend only on
this contract, so the segmentation engine is swappable.

Anatomical convention
---------------------
left/right = person's anatomical left/right (NOT viewer's screen left/right).
In a standard front-facing photo, the person's LEFT side appears on the
viewer's RIGHT.  Mirror selfies reverse this.  The segmenter does NOT
auto-detect mirror orientation — the user corrects via the editor.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional


# Canonical semantic classes (pixel value in the label map).
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
class CandidateSegment:
    """One SAM2 mask proposal that survived initial filtering.

    Stored so the frontend can later implement click-to-reassign:
    the user clicks a segment, sees its current class, and picks a new one.
    """
    segment_id: int
    assigned_class: int              # 0-7 (0 = rejected / unassigned)
    score: float                     # assignment confidence ∈ [0, 1]
    bbox: tuple[int, int, int, int]  # (x0, y0, x1, y1) in image pixels
    area: int                        # pixel count of the mask
    centroid: tuple[float, float]    # normalized (cx, cy) ∈ [0,1]²
    mask_rle: str                    # COCO-style run-length encoding
    rejection_reason: Optional[str]  # None → accepted, else reason string

    def to_dict(self) -> dict:
        return {
            "segment_id": self.segment_id,
            "assigned_class": self.assigned_class,
            "score": round(self.score, 4),
            "bbox": list(self.bbox),
            "area": self.area,
            "centroid": [round(c, 4) for c in self.centroid],
            "mask_rle": self.mask_rle,
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class SegmentationResult:
    """Result returned by any SegmenterAdapter implementation."""
    width: int
    height: int
    label_map_b64: str               # grayscale PNG, pixel value = class ID 0..7
    foreground_mask_b64: str = ""    # binary PNG, white = accepted person pixels
    editable_region_b64: str = ""    # binary PNG, white = dilated foreground (safe edit zone)
    classes: list[dict] = field(default_factory=lambda: list(SEG_CLASSES))
    candidate_segments: list[dict] = field(default_factory=list)
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
            SegmentationResult with label map, foreground mask,
            editable region, and candidate segments.
        """
        ...
