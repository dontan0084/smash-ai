import random
import shutil
from pathlib import Path


def prepare_detection_dataset(
    source_dir: str | Path,
    dataset_dir: str | Path,
    train_ratio: float = 0.8,
    seed: int = 42,
) -> tuple[int, int]:

    if not 0.0 < train_ratio < 1.0:
        raise ValueError(
            "train_ratio must be between 0 and 1"
        )

    source_dir = Path(source_dir)
    dataset_dir = Path(dataset_dir)

    train_dir = dataset_dir / "images" / "train"
    val_dir = dataset_dir / "images" / "val"

    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    image_paths = sorted([
        path
        for path in source_dir.iterdir()
        if path.suffix.lower()
        in {".jpg", ".jpeg", ".png"}
    ])

    if not image_paths:
        raise RuntimeError(
            f"No images found in {source_dir}"
        )

    # 毎回同じ分割になるよう固定
    rng = random.Random(seed)
    rng.shuffle(image_paths)

    train_count = int(
        len(image_paths) * train_ratio
    )

    train_images = image_paths[:train_count]
    val_images = image_paths[train_count:]

    # 既存画像を一度削除
    for directory in (train_dir, val_dir):

        for path in directory.iterdir():

            if path.is_file():
                path.unlink()

    # train
    for image_path in train_images:

        shutil.copy2(
            image_path,
            train_dir / image_path.name,
        )

    # val
    for image_path in val_images:

        shutil.copy2(
            image_path,
            val_dir / image_path.name,
        )

    return (
        len(train_images),
        len(val_images),
    )


if __name__ == "__main__":

    train_count, val_count = (
        prepare_detection_dataset(
            source_dir="recordings/sample_frames",
            dataset_dir="datasets/player_detection",
            train_ratio=0.8,
            seed=42,
        )
    )

    print("データセット分割完了")
    print("train:", train_count)
    print("val  :", val_count)