from pathlib import Path

import cv2


DATASET_DIR = Path("datasets/player_detection")

MAX_WIDTH = 1280
MAX_HEIGHT = 720


def resize_for_display(image):

    height, width = image.shape[:2]

    scale = min(
        MAX_WIDTH / width,
        MAX_HEIGHT / height,
        1.0,
    )

    display_width = int(width * scale)
    display_height = int(height * scale)

    return cv2.resize(
        image,
        (display_width, display_height),
    )


def load_boxes(
    label_path: Path,
    width: int,
    height: int,
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

            if class_id != 0:
                continue

            x_center = float(parts[1])
            y_center = float(parts[2])
            box_width = float(parts[3])
            box_height = float(parts[4])

            x1 = int(
                (x_center - box_width / 2)
                * width
            )

            y1 = int(
                (y_center - box_height / 2)
                * height
            )

            x2 = int(
                (x_center + box_width / 2)
                * width
            )

            y2 = int(
                (y_center + box_height / 2)
                * height
            )

            boxes.append(
                (x1, y1, x2, y2)
            )

    return boxes


def save_boxes(
    label_path: Path,
    boxes,
    width: int,
    height: int,
):

    label_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        label_path,
        "w",
        encoding="utf-8",
    ) as f:

        for x1, y1, x2, y2 in boxes:

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


def label_image(
    image_path: Path,
    label_path: Path,
):

    original = cv2.imread(
        str(image_path)
    )

    if original is None:
        raise RuntimeError(
            f"Could not read: {image_path}"
        )

    display = resize_for_display(
        original
    )

    height, width = display.shape[:2]

    boxes = load_boxes(
        label_path,
        width,
        height,
    )

    drawing = False
    start_point = None
    current_point = None


    def mouse_callback(
        event,
        x,
        y,
        flags,
        param,
    ):

        nonlocal drawing
        nonlocal start_point
        nonlocal current_point

        if event == cv2.EVENT_LBUTTONDOWN:

            drawing = True

            start_point = (x, y)
            current_point = (x, y)

        elif (
            event == cv2.EVENT_MOUSEMOVE
            and drawing
        ):

            current_point = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:

            drawing = False

            x1 = min(
                start_point[0],
                x,
            )

            y1 = min(
                start_point[1],
                y,
            )

            x2 = max(
                start_point[0],
                x,
            )

            y2 = max(
                start_point[1],
                y,
            )

            # 小さすぎる誤クリックは無視
            if (
                x2 - x1 > 5
                and y2 - y1 > 5
            ):
                boxes.append(
                    (x1, y1, x2, y2)
                )

            start_point = None
            current_point = None


    window_name = "Player Labeler"

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_AUTOSIZE,
    )

    cv2.setMouseCallback(
        window_name,
        mouse_callback,
    )

    while True:

        canvas = display.copy()

        # 保存済みBounding Box
        for x1, y1, x2, y2 in boxes:

            cv2.rectangle(
                canvas,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                canvas,
                "fighter",
                (x1, max(y1 - 5, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

        # 現在ドラッグ中のBox
        if (
            drawing
            and start_point is not None
            and current_point is not None
        ):

            cv2.rectangle(
                canvas,
                start_point,
                current_point,
                (255, 255, 255),
                2,
            )

        cv2.putText(
            canvas,
            f"{image_path.name}  "
            f"boxes={len(boxes)}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            canvas,
            "Drag=fighter  S=save/next  U=undo  C=clear  Q=quit",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

        cv2.imshow(
            window_name,
            canvas,
        )

        key = (
            cv2.waitKey(10)
            & 0xFF
        )

        # save + next
        if key == ord("s"):

            save_boxes(
                label_path,
                boxes,
                width,
                height,
            )

            return "next"

        # undo
        if key == ord("u"):

            if boxes:
                boxes.pop()

        # clear
        if key == ord("c"):

            boxes.clear()

        # quit
        if key == ord("q"):

            return "quit"


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
        f"画像数: {len(samples)}"
    )

    print()
    print("操作:")
    print("  左ドラッグ : fighterを囲む")
    print("  S          : 保存して次へ")
    print("  U          : 最後のBoxを取り消す")
    print("  C          : Boxを全部消す")
    print("  Q          : 終了")
    print()


    for index, (
        split,
        image_path,
        label_path,
    ) in enumerate(samples):

        print(
            f"[{index + 1}/{len(samples)}] "
            f"{split}: "
            f"{image_path.name}"
        )

        result = label_image(
            image_path,
            label_path,
        )

        if result == "quit":
            break


    cv2.destroyAllWindows()

    print()
    print("ラベリング終了")


if __name__ == "__main__":
    main()