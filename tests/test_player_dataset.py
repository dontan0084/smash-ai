import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)


DATASET_DIR = Path(
    "datasets/player_detection"
)


def check_split(split: str):

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

    images = sorted(
        image_dir.glob("*.jpg")
    )

    assert images, (
        f"No images found in {image_dir}"
    )

    total_boxes = 0
    zero_box_images = 0

    for image_path in images:

        label_path = (
            label_dir
            / f"{image_path.stem}.txt"
        )

        assert label_path.exists(), (
            f"Missing label: {label_path}"
        )

        with open(
            label_path,
            "r",
            encoding="utf-8",
        ) as f:
            lines = [
                line.strip()
                for line in f
                if line.strip()
            ]

        if len(lines) == 0:
            zero_box_images += 1

        total_boxes += len(lines)

        for line in lines:

            parts = line.split()

            assert len(parts) == 5, (
                f"Invalid label format: "
                f"{label_path}: {line}"
            )

            class_id = int(parts[0])

            assert class_id == 0, (
                f"Unexpected class: "
                f"{label_path}: {class_id}"
            )

            x, y, w, h = map(
                float,
                parts[1:],
            )

            assert 0.0 <= x <= 1.0
            assert 0.0 <= y <= 1.0

            assert 0.0 < w <= 1.0
            assert 0.0 < h <= 1.0

            left = x - w / 2
            top = y - h / 2
            right = x + w / 2
            bottom = y + h / 2

            EPSILON = 1e-5

            assert left >= -EPSILON, (
                f"Box exceeds left edge: "
                f"{label_path}\n"
                f"{line}\n"
                f"left={left}"
            )

            assert top >= -EPSILON, (
                f"Box exceeds top edge: "
                f"{label_path}\n"
                f"{line}\n"
                f"top={top}"
            )

            assert right <= 1.0 + EPSILON, (
                f"Box exceeds right edge: "
                f"{label_path}\n"
                f"{line}\n"
                f"right={right}"
            )

            assert bottom <= 1.0 + EPSILON, (
                f"Box exceeds bottom edge: "
                f"{label_path}\n"
                f"{line}\n"
                f"bottom={bottom}"
            )

    print()
    print(split)
    print(" images:", len(images))
    print(" boxes :", total_boxes)
    print(
        " zero-box images:",
        zero_box_images,
    )

    return len(images)


train_count = check_split("train")
val_count = check_split("val")

assert train_count == 160
assert val_count == 40

print()
print("Player dataset test: OK")