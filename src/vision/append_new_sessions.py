import shutil
from pathlib import Path


SOURCE_ROOT = Path(
    "recordings/player_collection"
)

DATASET_ROOT = Path(
    "datasets/player_detection"
)


def get_existing_sessions():

    existing = set()

    for split in ("train", "val"):

        image_dir = (
            DATASET_ROOT
            / "images"
            / split
        )

        for image_path in image_dir.glob("*.jpg"):

            # 例:
            # session_20260927_021721__frame_00000060.jpg

            if "__" not in image_path.name:
                continue

            session_name = (
                image_path.name.split("__")[0]
            )

            existing.add(session_name)

    return existing


def copy_session(
    session_dir: Path,
    split: str,
):

    destination = (
        DATASET_ROOT
        / "images"
        / split
    )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    copied_paths = []

    for image_path in sorted(
        session_dir.glob("*.jpg")
    ):

        new_name = (
            f"{session_dir.name}"
            f"__{image_path.name}"
        )

        destination_path = (
            destination
            / new_name
        )

        if destination_path.exists():
            continue

        shutil.copy2(
            image_path,
            destination_path,
        )

        copied_paths.append(
            destination_path
        )

    return copied_paths


def main():

    existing_sessions = (
        get_existing_sessions()
    )

    all_sessions = sorted([
        path
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir()
    ])

    new_sessions = [
        session
        for session in all_sessions
        if session.name
        not in existing_sessions
    ]

    print("既存セッション数:")
    print(len(existing_sessions))

    print()
    print("新規セッション:")

    for session in new_sessions:
        print(" ", session.name)

    if len(new_sessions) != 3:

        raise RuntimeError(
            f"Expected 3 new sessions, "
            f"but found {len(new_sessions)}"
        )

    # 最初の2つをtrain
    train_sessions = (
        new_sessions[:2]
    )

    # 最後の1つをval
    val_sessions = (
        new_sessions[2:]
    )

    added_train = []
    added_val = []

    print()
    print("=== TRAINへ追加 ===")

    for session in train_sessions:

        paths = copy_session(
            session,
            "train",
        )

        added_train.extend(paths)

        print(
            session.name,
            "->",
            len(paths),
            "images",
        )

    print()
    print("=== VALへ追加 ===")

    for session in val_sessions:

        paths = copy_session(
            session,
            "val",
        )

        added_val.extend(paths)

        print(
            session.name,
            "->",
            len(paths),
            "images",
        )

    print()
    print("追加完了")
    print(
        "train追加:",
        len(added_train),
    )
    print(
        "val追加  :",
        len(added_val),
    )


if __name__ == "__main__":
    main()