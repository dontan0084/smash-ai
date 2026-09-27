from pathlib import Path

from ultralytics import YOLO


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

DATA_YAML = (
    ROOT_DIR
    / "datasets"
    / "player_detection"
    / "data.yaml"
)

RUNS_DIR = (
    ROOT_DIR
    / "runs"
    / "player_detection"
)


def main():

    print("Dataset:")
    print(DATA_YAML)

    print()
    print("YOLO model loading...")

    model = YOLO(
        "yolo26n.pt"
    )

    print()
    print("Training Player Detector v2")

    model = YOLO("yolo26n.pt")

    results = model.train(
        data=str(DATA_YAML),

        epochs=50,
        imgsz=640,
        batch=4,
        workers=0,

        project=str(RUNS_DIR),
        name="player_v3",
        exist_ok=True,

        patience=15,
    )

    print()
    print("Training finished")

    print(
        "Result directory:",
        results.save_dir,
    )


if __name__ == "__main__":
    main()