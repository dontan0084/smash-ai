from pathlib import Path

from ultralytics import YOLO


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

MODEL_PATH = (
    ROOT_DIR
    / "runs"
    / "player_detection"
    / "player_v3"
    / "weights"
    / "best.pt"
)

DATA_YAML = (
    ROOT_DIR
    / "datasets"
    / "player_detection"
    / "data.yaml"
)

IMAGE_SIZES = [
    640,
    416,
    320,
]


def main():

    model = YOLO(
        str(MODEL_PATH)
    )

    print()
    print("Player Detector accuracy benchmark")
    print()

    for image_size in IMAGE_SIZES:

        results = model.val(
            data=str(DATA_YAML),
            imgsz=image_size,
            batch=1,
            workers=0,
            rect=True,
            verbose=False,
        )

        print(
            f"=== imgsz={image_size} ==="
        )

        print(
            f"Precision  : "
            f"{results.box.mp:.3f}"
        )

        print(
            f"Recall     : "
            f"{results.box.mr:.3f}"
        )

        print(
            f"mAP50      : "
            f"{results.box.map50:.3f}"
        )

        print(
            f"mAP50-95   : "
            f"{results.box.map:.3f}"
        )

        print()


if __name__ == "__main__":
    main()