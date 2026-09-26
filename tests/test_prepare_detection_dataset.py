import sys
import tempfile
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import cv2
import numpy as np

from src.vision.prepare_detection_dataset import (
    prepare_detection_dataset,
)


with tempfile.TemporaryDirectory() as temp:

    temp_dir = Path(temp)

    source_dir = temp_dir / "source"
    dataset_dir = temp_dir / "dataset"

    source_dir.mkdir()

    # 20枚のダミー画像
    for i in range(20):

        image = np.zeros(
            (100, 100, 3),
            dtype=np.uint8,
        )

        cv2.imwrite(
            str(source_dir / f"frame_{i:03d}.jpg"),
            image,
        )

    train_count, val_count = (
        prepare_detection_dataset(
            source_dir=source_dir,
            dataset_dir=dataset_dir,
            train_ratio=0.8,
            seed=42,
        )
    )

    assert train_count == 16
    assert val_count == 4

    train_files = list(
        (dataset_dir / "images" / "train")
        .glob("*.jpg")
    )

    val_files = list(
        (dataset_dir / "images" / "val")
        .glob("*.jpg")
    )

    assert len(train_files) == 16
    assert len(val_files) == 4


print("Dataset preparation test: OK")