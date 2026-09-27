from pathlib import Path

import cv2
from ultralytics import YOLO


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

DATASET_DIR = (
    ROOT_DIR
    / "datasets"
    / "player_detection"
)

MODEL_PATH = (
    ROOT_DIR
    / "runs"
    / "player_detection"
    / "player_v2"
    / "weights"
    / "best.pt"
)

CONFIDENCE_THRESHOLD = 0.10
MAX_FIGHTERS = 2


def label_missing(
    model: YOLO,
    split: str,
):

    image_dir = (
        DATASET_DIR
        / "images"
        / split
    )

    label_dir = (
        DATASET_DIR
        / "labels"
        / split
    )

    label_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    created = 0
    skipped = 0

    for image_path in sorted(
        image_dir.glob("*.jpg")
    ):

        label_path = (
            label_dir
            / f"{image_path.stem}.txt"
        )

        # 既存ラベルは絶対に触らない
        if label_path.exists():
            skipped += 1
            continue

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            raise RuntimeError(
                f"Could not read {image_path}"
            )

        height, width = image.shape[:2]

        results = model.predict(
            source=image,
            imgsz=640,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,
        )

        boxes = []

        if results[0].boxes is not None:

            for box in results[0].boxes:

                if int(box.cls[0]) != 0:
                    continue

                confidence = float(
                    box.conf[0]
                )

                x1, y1, x2, y2 = (
                    box.xyxy[0]
                    .cpu()
                    .tolist()
                )

                boxes.append(
                    (
                        confidence,
                        x1,
                        y1,
                        x2,
                        y2,
                    )
                )

        boxes.sort(
            reverse=True,
            key=lambda item: item[0],
        )

        boxes = boxes[:MAX_FIGHTERS]

        with open(
            label_path,
            "w",
            encoding="utf-8",
        ) as f:

            for (
                confidence,
                x1,
                y1,
                x2,
                y2,
            ) in boxes:

                # 画像範囲内へクリップ
                x1 = max(
                    0.0,
                    min(width, x1),
                )

                y1 = max(
                    0.0,
                    min(height, y1),
                )

                x2 = max(
                    0.0,
                    min(width, x2),
                )

                y2 = max(
                    0.0,
                    min(height, y2),
                )

                if x2 <= x1 or y2 <= y1:
                    continue

                xc = (
                    (x1 + x2) / 2
                ) / width

                yc = (
                    (y1 + y2) / 2
                ) / height

                w = (
                    x2 - x1
                ) / width

                h = (
                    y2 - y1
                ) / height

                f.write(
                    f"0 "
                    f"{xc:.6f} "
                    f"{yc:.6f} "
                    f"{w:.6f} "
                    f"{h:.6f}\n"
                )

        created += 1

    return created, skipped


def main():

    model = YOLO(
        str(MODEL_PATH)
    )

    train_created, train_skipped = (
        label_missing(
            model,
            "train",
        )
    )

    val_created, val_skipped = (
        label_missing(
            model,
            "val",
        )
    )

    print()
    print("Auto labeling finished")

    print()
    print("train")
    print(
        " new labels:",
        train_created,
    )
    print(
        " existing skipped:",
        train_skipped,
    )

    print()
    print("val")
    print(
        " new labels:",
        val_created,
    )
    print(
        " existing skipped:",
        val_skipped,
    )


if __name__ == "__main__":
    main()