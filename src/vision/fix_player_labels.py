from pathlib import Path


DATASET_DIR = Path(
    "datasets/player_detection"
)


def fix_split(split: str):

    label_dir = (
        DATASET_DIR
        / "labels"
        / split
    )

    fixed_boxes = 0
    total_boxes = 0

    for label_path in sorted(
        label_dir.glob("*.txt")
    ):

        new_lines = []

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

        for line in lines:

            parts = line.split()

            if len(parts) != 5:
                raise ValueError(
                    f"Invalid label: "
                    f"{label_path}: {line}"
                )

            class_id = int(parts[0])

            x = float(parts[1])
            y = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])

            total_boxes += 1

            # YOLO中心座標 → 四隅
            x1 = x - w / 2
            y1 = y - h / 2
            x2 = x + w / 2
            y2 = y + h / 2

            original = (
                x1,
                y1,
                x2,
                y2,
            )

            # 画像範囲へクリップ
            x1 = max(0.0, min(1.0, x1))
            y1 = max(0.0, min(1.0, y1))
            x2 = max(0.0, min(1.0, x2))
            y2 = max(0.0, min(1.0, y2))

            # 完全に画像外などでBoxが消えた場合
            if x2 <= x1 or y2 <= y1:
                print(
                    "削除:",
                    label_path.name,
                    line,
                )
                continue

            if (
                x1,
                y1,
                x2,
                y2,
            ) != original:
                fixed_boxes += 1

                print(
                    "補正:",
                    label_path.name
                )

            # 四隅 → YOLO形式へ戻す
            new_x = (x1 + x2) / 2
            new_y = (y1 + y2) / 2

            new_w = x2 - x1
            new_h = y2 - y1

            new_lines.append(
                f"{class_id} "
                f"{new_x:.6f} "
                f"{new_y:.6f} "
                f"{new_w:.6f} "
                f"{new_h:.6f}"
            )

        with open(
            label_path,
            "w",
            encoding="utf-8",
        ) as f:

            for new_line in new_lines:
                f.write(new_line + "\n")

    return total_boxes, fixed_boxes


def main():

    total = 0
    fixed = 0

    for split in ("train", "val"):

        split_total, split_fixed = (
            fix_split(split)
        )

        total += split_total
        fixed += split_fixed

    print()
    print("Label fixing finished")
    print("総Box数 :", total)
    print("補正Box数:", fixed)


if __name__ == "__main__":
    main()