from dataclasses import dataclass, replace
from math import hypot

from src.vision.player_tracker import TrackedPlayer


@dataclass
class LogicalPlayer:
    logical_id: int

    initialized: bool = False
    visible: bool = False

    track_id: int | None = None

    x1: int | None = None
    y1: int | None = None
    x2: int | None = None
    y2: int | None = None

    center_x: float | None = None
    center_y: float | None = None

    vx: float = 0.0
    vy: float = 0.0

    confidence: float | None = None

    missing_frames: int = 0
    last_seen_frame: int | None = None

    @property
    def foot_x(self) -> float | None:

        if (
            self.x1 is None
            or self.x2 is None
        ):
            return None

        return (
            self.x1 + self.x2
        ) / 2

    @property
    def foot_y(self) -> float | None:

        if self.y2 is None:
            return None

        return float(self.y2)


class PlayerIdentityManager:

    def __init__(
        self,
        max_missing_frames: int = 15,
        max_match_distance_px: float = 700.0,
    ):
        self.max_missing_frames = max_missing_frames
        self.max_match_distance_px = max_match_distance_px

        self.players = [
            LogicalPlayer(logical_id=1),
            LogicalPlayer(logical_id=2),
        ]

    def update(
        self,
        detections: list[TrackedPlayer],
        frame_number: int,
    ) -> list[LogicalPlayer]:

        # 今回のupdateで観測できたかを一旦リセット
        for player in self.players:
            player.visible = False

        assigned_players: set[int] = set()
        assigned_detections: set[int] = set()

        candidates = []

        # ======================================
        # 過去位置 + 速度から現在位置を予測
        # ======================================

        for player_index, player in enumerate(
            self.players
        ):

            if not player.initialized:
                continue

            if player.last_seen_frame is None:
                continue

            # 最後に見えてから実際に何capture frame経過したか
            dt = max(
                1,
                frame_number - player.last_seen_frame,
            )

            # 長時間見失っているplayerは
            # 位置だけでは安全に対応できない
            if dt > self.max_missing_frames:
                continue

            predicted_x = (
                player.center_x
                + player.vx * dt
            )

            predicted_y = (
                player.center_y
                + player.vy * dt
            )

            for (
                detection_index,
                detection,
            ) in enumerate(detections):

                distance = hypot(
                    detection.center_x
                    - predicted_x,
                    detection.center_y
                    - predicted_y,
                )

                # Trackerを使う場合、
                # 同じtrack_idなら対応候補として優先
                #
                # Detector直結の場合は
                # track_id=Noneなので何も起きない
                if (
                    player.track_id is not None
                    and detection.track_id is not None
                    and player.track_id
                    == detection.track_id
                ):
                    distance *= 0.5

                candidates.append(
                    (
                        distance,
                        player_index,
                        detection_index,
                    )
                )

        # 距離の近い対応から試す
        candidates.sort(
            key=lambda item: item[0]
        )

        # ======================================
        # DetectionとLogicalPlayerを対応付け
        # ======================================

        for (
            distance,
            player_index,
            detection_index,
        ) in candidates:

            if (
                player_index
                in assigned_players
            ):
                continue

            if (
                detection_index
                in assigned_detections
            ):
                continue

            if (
                distance
                > self.max_match_distance_px
            ):
                continue

            self._assign(
                player=self.players[
                    player_index
                ],
                detection=detections[
                    detection_index
                ],
                frame_number=frame_number,
            )

            assigned_players.add(
                player_index
            )

            assigned_detections.add(
                detection_index
            )

        # ======================================
        # まだ割り当てられていないDetection
        # ======================================

        remaining_detections = [
            detection
            for index, detection
            in enumerate(detections)
            if index
            not in assigned_detections
        ]

        # 初期状態では左側をP1、
        # 右側をP2として仮割り当て
        remaining_detections.sort(
            key=lambda detection:
            detection.center_x
        )

        # ======================================
        # 使用可能なLogicalPlayer slotを探す
        # ======================================

        free_players = []

        for index, player in enumerate(
            self.players
        ):

            if index in assigned_players:
                continue

            if not player.initialized:
                free_players.append(
                    player
                )
                continue

            if player.last_seen_frame is None:
                free_players.append(
                    player
                )
                continue

            missing_frames = (
                frame_number
                - player.last_seen_frame
            )

            # 長時間lostしていたslotは再利用可能
            if (
                missing_frames
                > self.max_missing_frames
            ):
                free_players.append(
                    player
                )

        free_players.sort(
            key=lambda player:
            player.logical_id
        )

        for player, detection in zip(
            free_players,
            remaining_detections,
        ):

            self._assign(
                player=player,
                detection=detection,
                frame_number=frame_number,
            )

            assigned_players.add(
                self.players.index(player)
            )

        # ======================================
        # 今回見つからなかったPlayer
        # ======================================

        for index, player in enumerate(
            self.players
        ):

            if index in assigned_players:
                continue

            if not player.initialized:
                continue

            player.visible = False

            if player.last_seen_frame is not None:

                # update回数ではなく、
                # 実際のcapture frame差を使う
                player.missing_frames = max(
                    0,
                    frame_number
                    - player.last_seen_frame,
                )

            # 一定時間以上lostした場合は
            # 一時Tracker IDと速度を捨てる
            if (
                player.missing_frames
                > self.max_missing_frames
            ):
                player.track_id = None

                player.vx = 0.0
                player.vy = 0.0

        return [
            replace(player)
            for player in self.players
        ]

    def _assign(
        self,
        player: LogicalPlayer,
        detection: TrackedPlayer,
        frame_number: int,
    ) -> None:

        new_x = detection.center_x
        new_y = detection.center_y

        # ======================================
        # 速度計算
        # ======================================

        if (
            player.initialized
            and player.center_x is not None
            and player.center_y is not None
            and player.last_seen_frame is not None
        ):

            dt = max(
                1,
                frame_number
                - player.last_seen_frame,
            )

            player.vx = (
                new_x
                - player.center_x
            ) / dt

            player.vy = (
                new_y
                - player.center_y
            ) / dt

        else:

            player.vx = 0.0
            player.vy = 0.0

        # ======================================
        # 最新状態を保存
        # ======================================

        player.initialized = True
        player.visible = True

        player.track_id = (
            detection.track_id
        )

        player.x1 = detection.x1
        player.y1 = detection.y1
        player.x2 = detection.x2
        player.y2 = detection.y2

        player.center_x = new_x
        player.center_y = new_y

        player.confidence = (
            detection.confidence
        )

        player.missing_frames = 0

        # ここが今回特に重要
        player.last_seen_frame = (
            frame_number
        )