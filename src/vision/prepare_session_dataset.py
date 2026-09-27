import shutil
from pathlib import Path


SOURCE_ROOT = Path(
    "recordings/player_collection"
)

DATASET_ROOT = Path(
    "datasets/player_detection"
)


def clear_directory(directory: Path):

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in directory.iterdir():

        if path.is_file():
            path.unlink()


def copy_session(
    session_dir: Path,
    destination_dir: Path,
):

    copied = 0

    for image_path in sorted(
        session_dir.glob("*.jpg")
    ):

        # セッション間で同名画像が上書きされないようにする
        new_name = (
            f"{session_dir.name}"
            f"__{image_path.name}"
        )

        shutil.copy2(
            image_path,
            destination_dir / new_name,
        )

        copied += 1

    return copied


def main():

    sessions = sorted([
        path
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir()
    ])

    if len(sessions) < 2:
        raise RuntimeError(
            "At least 2 sessions are required"
        )

    print("検出されたセッション:")

    for session in sessions:
        print(" ", session.name)

    print()

    # 最後のセッションだけval
    train_sessions = sessions[:-1]
    val_sessions = sessions[-1:]

    train_image_dir = (
        DATASET_ROOT
        / "images"
        / "train"
    )

    val_image_dir = (
        DATASET_ROOT
        / "images"
        / "val"
    )

    train_label_dir = (
        DATASET_ROOT
        / "labels"
        / "train"
    )

    val_label_dir = (
        DATASET_ROOT
        / "labels"
        / "val"
    )

    # 以前の20枚とラベルを削除
    for directory in (
        train_image_dir,
        val_image_dir,
        train_label_dir,
        val_label_dir,
    ):
        clear_directory(directory)

    train_count = 0
    val_count = 0

    print("=== TRAIN ===")

    for session in train_sessions:

        count = copy_session(
            session,
            train_image_dir,
        )

        train_count += count

        print(
            session.name,
            "->",
            count,
            "images",
        )

    print()
    print("=== VAL ===")

    for session in val_sessions:

        count = copy_session(
            session,
            val_image_dir,
        )

        val_count += count

        print(
            session.name,
            "->",
            count,
            "images",
        )

    print()
    print("Dataset preparation finished")
    print("train:", train_count)
    print("val  :", val_count)


if __name__ == "__main__":
    main()