from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ultralytics import YOLO


@dataclass
class TrackedPlayer:
    track_id: int | None

    x1: int
    y1: int
    x2: int
    y2: int

    confidence: float

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2


class PlayerTracker:

    def __init__(
        self,
        model_path: str | Path,
        confidence_threshold: float = 0.25,
        image_size: int = 640,
        tracker: str = "botsort.yaml",
    ):

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = YOLO(
            str(self.model_path)
        )

        self.confidence_threshold = (
            confidence_threshold
        )

        self.image_size = image_size
        self.tracker = tracker

    def track(
        self,
        image: np.ndarray,
    ) -> list[TrackedPlayer]:

        results = self.model.track(
            source=image,
            persist=True,
            tracker=self.tracker,
            imgsz=self.image_size,
            conf=self.confidence_threshold,
            verbose=False,
        )

        result = results[0]

        if result.boxes is None:
            return []

        if result.boxes.id is None:
            return []

        xyxy = (
            result.boxes.xyxy
            .cpu()
            .tolist()
        )

        confidences = (
            result.boxes.conf
            .cpu()
            .tolist()
        )

        class_ids = (
            result.boxes.cls
            .int()
            .cpu()
            .tolist()
        )

        track_ids = (
            result.boxes.id
            .int()
            .cpu()
            .tolist()
        )

        players = []

        for (
            box,
            confidence,
            class_id,
            track_id,
        ) in zip(
            xyxy,
            confidences,
            class_ids,
            track_ids,
        ):

            if class_id != 0:
                continue

            x1, y1, x2, y2 = box

            players.append(
                TrackedPlayer(
                    track_id=track_id,

                    x1=int(x1),
                    y1=int(y1),
                    x2=int(x2),
                    y2=int(y2),

                    confidence=float(
                        confidence
                    ),
                )
            )

        return players