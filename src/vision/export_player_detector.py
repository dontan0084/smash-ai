from pathlib import Path

from ultralytics import YOLO


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
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


def main():

    print("Model:")
    print(MODEL_PATH)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    model = YOLO(
        str(MODEL_PATH)
    )

    print()
    print("OpenVINO export start")

    exported_path = model.export(
        format="openvino",
        imgsz=(384, 640),
        dynamic=False,
    )

    print()
    print("OpenVINO export finished")
    print("Exported:")
    print(exported_path)


if __name__ == "__main__":
    main()