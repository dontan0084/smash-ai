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
    / "smoke_test"
    / "weights"
    / "best.pt"
)


# 弱い初期モデルなので少し低め
CONFIDENCE_THRESHOLD = 0.10

# 1対1なので最大2体だけ使う
MAX_FIGHTERS = 2


def auto_label_split(
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

    image_paths = sorted(
        image_dir.glob("*.jpg")
    )

    zero_count = 0
    one_count = 0
    two_count = 0

    print()
    print(f"=== {split.upper()} ===")

    for index, image_path in enumerate(
        image_paths,
        start=1,
    ):

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            raise RuntimeError(
                f"Could not read: {image_path}"
            )

        height, width = image.shape[:2]

        results = model.predict(
            source=image,
            imgsz=640,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,
        )

        result = results[0]

        detections = []

        if result.boxes is not None:

            for box in result.boxes:

                confidence = float(
                    box.conf[0].cpu()
                )

                class_id = int(
                    box.cls[0].cpu()
                )

                # fighter classだけ
                if class_id != 0:
                    continue

                x1, y1, x2, y2 = (
                    box.xyxy[0]
                    .cpu()
                    .tolist()
                )

                detections.append(
                    {
                        "confidence": confidence,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    }
                )

        # confidenceが高い順
        detections.sort(
            key=lambda item: item["confidence"],
            reverse=True,
        )

        # 1対1なので上位2個まで
        detections = detections[
            :MAX_FIGHTERS
        ]

        label_path = (
            label_dir
            / f"{image_path.stem}.txt"
        )

        with open(
            label_path,
            "w",
            encoding="utf-8",
        ) as f:

            for detection in detections:

                x1 = detection["x1"]
                y1 = detection["y1"]
                x2 = detection["x2"]
                y2 = detection["y2"]

                x_center = (
                    (x1 + x2) / 2
                ) / width

                y_center = (
                    (y1 + y2) / 2
                ) / height

                box_width = (
                    x2 - x1
                ) / width

                box_height = (
                    y2 - y1
                ) / height

                f.write(
                    f"0 "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{box_width:.6f} "
                    f"{box_height:.6f}\n"
                )

        count = len(detections)

        if count == 0:
            zero_count += 1

        elif count == 1:
            one_count += 1

        else:
            two_count += 1

        print(
            f"\r"
            f"{index}/{len(image_paths)} "
            f"boxes={count}",
            end="",
        )

    print()

    return {
        "images": len(image_paths),
        "zero": zero_count,
        "one": one_count,
        "two": two_count,
    }


def main():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    print("Model:")
    print(MODEL_PATH)

    print()
    print(
        "Confidence threshold:",
        CONFIDENCE_THRESHOLD,
    )

    model = YOLO(
        str(MODEL_PATH)
    )

    train_stats = auto_label_split(
        model,
        "train",
    )

    val_stats = auto_label_split(
        model,
        "val",
    )

    print()
    print("=== RESULT ===")

    for split, stats in (
        ("train", train_stats),
        ("val", val_stats),
    ):

        print()
        print(split)
        print(
            "  images:",
            stats["images"],
        )
        print(
            "  0 boxes:",
            stats["zero"],
        )
        print(
            "  1 box :",
            stats["one"],
        )
        print(
            "  2 boxes:",
            stats["two"],
        )

    print()
    print("Auto labeling finished")


if __name__ == "__main__":
    main()