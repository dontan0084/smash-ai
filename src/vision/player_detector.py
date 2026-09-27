from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ultralytics import YOLO


@dataclass
class PlayerDetection:
    x1: int
    y1: int
    x2: int
    y2: int

    confidence: float
    class_id: int


class PlayerDetector:

    def __init__(
        self,
        model_path: str | Path,
        confidence_threshold: float = 0.25,
        image_size: int = 640,
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

    def detect(
        self,
        image: np.ndarray,
    ) -> list[PlayerDetection]:

        results = self.model.predict(
            source=image,
            imgsz=self.image_size,
            conf=self.confidence_threshold,
            verbose=False,
        )

        result = results[0]

        detections = []

        if result.boxes is None:
            return detections

        for box in result.boxes:

            x1, y1, x2, y2 = (
                box.xyxy[0]
                .cpu()
                .tolist()
            )

            confidence = float(
                box.conf[0].cpu()
            )

            class_id = int(
                box.cls[0].cpu()
            )

            detections.append(
                PlayerDetection(
                    x1=int(x1),
                    y1=int(y1),
                    x2=int(x2),
                    y2=int(y2),
                    confidence=confidence,
                    class_id=class_id,
                )
            )

        return detections