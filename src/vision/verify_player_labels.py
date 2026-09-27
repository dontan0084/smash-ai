from pathlib import Path

import cv2


DATASET_DIR = Path("datasets/player_detection")

MAX_WIDTH = 1280
MAX_HEIGHT = 720


def load_yolo_labels(
    label_path: Path,
    image_width: int,
    image_height: int,
):

    boxes = []

    if not label_path.exists():
        return boxes

    with open(
        label_path,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            x_center = float(parts[1])
            y_center = float(parts[2])
            box_width = float(parts[3])
            box_height = float(parts[4])

            x1 = int(
                (x_center - box_width / 2)
                * image_width
            )

            y1 = int(
                (y_center - box_height / 2)
                * image_height
            )

            x2 = int(
                (x_center + box_width / 2)
                * image_width
            )

            y2 = int(
                (y_center + box_height / 2)
                * image_height
            )

            boxes.append(
                (
                    class_id,
                    x1,
                    y1,
                    x2,
                    y2,
                )
            )

    return boxes


def resize_for_display(image):

    height, width = image.shape[:2]

    scale = min(
        MAX_WIDTH / width,
        MAX_HEIGHT / height,
        1.0,
    )

    new_width = int(width * scale)
    new_height = int(height * scale)

    resized = cv2.resize(
        image,
        (new_width, new_height),
    )

    return resized, scale


def main():

    samples = []

    for split in ("train", "val"):

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

        for image_path in sorted(
            image_dir.glob("*.jpg")
        ):

            label_path = (
                label_dir
                / f"{image_path.stem}.txt"
            )

            samples.append(
                (
                    split,
                    image_path,
                    label_path,
                )
            )


    print(
        f"確認する画像数: {len(samples)}"
    )

    print()
    print("操作:")
    print("  D / → : 次の画像")
    print("  A / ← : 前の画像")
    print("  Q      : 終了")
    print()


    index = 0

    window_name = "Label Verification"

    while 0 <= index < len(samples):

        split, image_path, label_path = (
            samples[index]
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            raise RuntimeError(
                f"Could not read: {image_path}"
            )

        height, width = image.shape[:2]

        boxes = load_yolo_labels(
            label_path,
            width,
            height,
        )

        # 元画像上にBoxを描画
        for (
            class_id,
            x1,
            y1,
            x2,
            y2,
        ) in boxes:

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                3,
            )

            cv2.putText(
                image,
                "fighter",
                (
                    x1,
                    max(y1 - 10, 20),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )


        display, scale = resize_for_display(
            image
        )

        text = (
            f"[{index + 1}/{len(samples)}] "
            f"{split} "
            f"{image_path.name} "
            f"boxes={len(boxes)}"
        )

        cv2.putText(
            display,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow(
            window_name,
            display,
        )

        key = (
            cv2.waitKey(0)
            & 0xFF
        )

        # D
        if key == ord("d"):
            index += 1

        # A
        elif key == ord("a"):
            index = max(
                index - 1,
                0,
            )

        # 右矢印
        elif key == 83:
            index += 1

        # 左矢印
        elif key == 81:
            index = max(
                index - 1,
                0,
            )

        # Q
        elif key == ord("q"):
            break


    cv2.destroyAllWindows()

    print()
    print("Label verification finished")


if __name__ == "__main__":
    main()