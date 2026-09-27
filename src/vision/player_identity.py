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
    ) -> list[LogicalPlayer]:

        # このupdateで観測できたかをリセット
        for player in self.players:
            player.visible = False

        assigned_players = set()
        assigned_detections = set()

        candidates = []

        # ======================================
        # 過去位置 + 速度から対応候補を作る
        # ======================================

        for player_index, player in enumerate(
            self.players
        ):

            if not player.initialized:
                continue

            if (
                player.missing_frames
                > self.max_missing_frames
            ):
                continue

            predicted_x = (
                player.center_x
                + player.vx
                * (player.missing_frames + 1)
            )

            predicted_y = (
                player.center_y
                + player.vy
                * (player.missing_frames + 1)
            )

            for detection_index, detection in enumerate(
                detections
            ):

                distance = hypot(
                    detection.center_x - predicted_x,
                    detection.center_y - predicted_y,
                )

                # Tracker IDが同じなら少し優先
                if (
                    player.track_id is not None
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

        candidates.sort(
            key=lambda item: item[0]
        )

        # ======================================
        # 距離が近い組み合わせから割り当て
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
                self.players[player_index],
                detections[detection_index],
            )

            assigned_players.add(
                player_index
            )

            assigned_detections.add(
                detection_index
            )

        # ======================================
        # 未割り当てDetection
        # 新規または長時間lostしたSlotへ入れる
        # ======================================

        remaining_detections = [
            detection
            for index, detection
            in enumerate(detections)
            if index not in assigned_detections
        ]

        remaining_detections.sort(
            key=lambda detection:
            detection.center_x
        )

        free_players = [
            player
            for index, player
            in enumerate(self.players)
            if (
                index not in assigned_players
                and (
                    not player.initialized
                    or player.missing_frames
                    > self.max_missing_frames
                )
            )
        ]

        free_players.sort(
            key=lambda player:
            player.logical_id
        )

        for player, detection in zip(
            free_players,
            remaining_detections,
        ):
            self._assign(
                player,
                detection,
            )

            assigned_players.add(
                self.players.index(player)
            )

        # ======================================
        # 見失ったPlayer
        # ======================================

        for index, player in enumerate(
            self.players
        ):

            if index in assigned_players:
                continue

            if player.initialized:
                player.missing_frames += 1
                player.visible = False

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
    ) -> None:

        new_x = detection.center_x
        new_y = detection.center_y

        if (
            player.initialized
            and player.center_x is not None
            and player.center_y is not None
        ):
            elapsed = max(
                1,
                player.missing_frames + 1,
            )

            player.vx = (
                new_x - player.center_x
            ) / elapsed

            player.vy = (
                new_y - player.center_y
            ) / elapsed

        else:
            player.vx = 0.0
            player.vy = 0.0

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