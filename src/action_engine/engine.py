from src.schemas.action import (
    ActionToken,
    ActionType,
    Direction,
)

from src.schemas.controller_state import ControllerState

FULL_HOP_HOLD_FRAMES = 8

class ActionEngine:

    def compile(
        self,
        action: ActionToken,
        previous_state: ControllerState | None = None,
    ) -> list[ControllerState]:

        if previous_state is None:
            previous_state = ControllerState()

        duration = action.duration_frames or 1

        # =========================================
        # 何もしない
        # =========================================

        if action.action_type == ActionType.NO_OP:

            return [
                ControllerState()
                for _ in range(duration)
            ]

        # =========================================
        # 通常のスティック移動
        # =========================================

        if action.action_type == ActionType.MOVE:

            lx, ly = self._direction_to_stick(
                direction=action.direction,
                strength=action.strength,
            )

            return [
                ControllerState(
                    lx=lx,
                    ly=ly,
                )
                for _ in range(duration)
            ]

        # =========================================
        # ダッシュ
        # =========================================

        if action.action_type == ActionType.DASH:

            if action.direction == Direction.LEFT:
                lx = -1.0

            elif action.direction == Direction.RIGHT:
                lx = 1.0

            else:
                raise ValueError(
                    "DASH direction must be LEFT or RIGHT"
                )

            states = []

            # すでに同じ方向へスティックを倒している場合、
            # いったんニュートラルへ戻してから倒す
            if (
                lx > 0
                and previous_state.lx > 0.2
            ) or (
                lx < 0
                and previous_state.lx < -0.2
            ):
                states.append(
                    ControllerState()
                )

            states.extend(
                ControllerState(
                    lx=lx,
                    ly=0.0,
                )
                for _ in range(duration)
            )

            return states

        # =========================================
        # ジャンプ
        # =========================================

        if action.action_type == ActionType.JUMP:

            hold_frames = (
                action.duration_frames
                or FULL_HOP_HOLD_FRAMES
            )

            states = [
                ControllerState(
                    x=True
                )
                for _ in range(hold_frames)
            ]

            # ジャンプボタンを離す
            states.append(
                ControllerState()
            )

            return states

        # =========================================
        # ショートホップ
        # =========================================

        if action.action_type == ActionType.SHORT_HOP:

            return [
                # X + Y 同時押し
                ControllerState(
                    x=True,
                    y=True,
                ),

                # 次フレームで離す
                ControllerState(),
            ]

        # =========================================
        # 通常攻撃
        # =========================================

        if action.action_type == ActionType.ATTACK:

            if action.direction != Direction.NEUTRAL:
                raise ValueError(
                    "ATTACK must use NEUTRAL direction"
                )

            return [
                ControllerState(
                    a=True,
                ),
                ControllerState(),
            ]

        # =========================================
        # 必殺技
        # =========================================

        if action.action_type == ActionType.SPECIAL:

            lx, ly = self._direction_to_stick(
                direction=action.direction,
                strength=1.0,
            )

            return [
                ControllerState(
                    lx=lx,
                    ly=ly,
                    b=True,
                ),
                ControllerState(),
            ]

        # =========================================
        # つかみ
        # =========================================

        if action.action_type == ActionType.GRAB:

            return [
                ControllerState(
                    zr=True,
                ),
                ControllerState(),
            ]

        # =========================================
        # シールド
        # =========================================

        if action.action_type == ActionType.SHIELD:

            duration = action.duration_frames or 1

            states = [
                ControllerState(
                    zl=True,
                )
                for _ in range(duration)
            ]

            # 最後にシールドを離す
            states.append(
                ControllerState()
            )

            return states

        # =========================================
        # 強攻撃
        # =========================================

        if action.action_type == ActionType.TILT:

            if action.direction == Direction.NEUTRAL:
                raise ValueError(
                    "TILT requires a direction"
                )

            rx, ry = self._direction_to_right_stick(
                action.direction
            )

            return [
                ControllerState(
                    rx=rx,
                    ry=ry,
                ),

                # 右スティックをニュートラルへ戻す
                ControllerState(),
            ]

        # =========================================
        # 空中攻撃
        # =========================================

        if action.action_type == ActionType.AERIAL:

            # ニュートラル空中攻撃
            if action.direction == Direction.NEUTRAL:

                return [
                    ControllerState(
                        a=True,
                    ),

                    ControllerState(),
                ]

            # 方向付き空中攻撃
            rx, ry = self._direction_to_right_stick(
                action.direction
            )

            return [
                ControllerState(
                    rx=rx,
                    ry=ry,
                ),

                ControllerState(),
            ]

        # =========================================
        # スマッシュ攻撃
        # =========================================

        if action.action_type == ActionType.SMASH:

            if action.direction == Direction.NEUTRAL:
                raise ValueError(
                    "SMASH requires a direction"
                )

            lx, ly = self._direction_to_stick(
                direction=action.direction,
                strength=1.0,
            )

            states = []

            # すでに同方向へ倒している場合は、
            # flickを作るため一度ニュートラルへ戻す
            if self._needs_flick_reset(
                previous_state,
                lx,
                ly,
            ):
                states.append(
                    ControllerState()
                )

            charge_frames = (
                action.duration_frames or 1
            )

            # 方向 + A
            states.extend(
                ControllerState(
                    lx=lx,
                    ly=ly,
                    a=True,
                )
                for _ in range(charge_frames)
            )

            # 入力を離す
            states.append(
                ControllerState()
            )

            return states

        # =========================================
        # その場回避
        # =========================================

        if action.action_type == ActionType.DODGE:

            if action.direction != Direction.NEUTRAL:
                raise ValueError(
                    "DODGE must use NEUTRAL direction"
                )

            return [
                # まずシールド
                ControllerState(
                    zl=True,
                ),

                # シールド中に下入力
                ControllerState(
                    zl=True,
                    ly=1.0,
                ),

                # 離す
                ControllerState(),
            ]

        # =========================================
        # 前後回避 / ロール
        # =========================================

        if action.action_type == ActionType.ROLL:

            if action.direction == Direction.LEFT:
                lx = -1.0

            elif action.direction == Direction.RIGHT:
                lx = 1.0

            else:
                raise ValueError(
                    "ROLL direction must be LEFT or RIGHT"
                )

            return [
                # まずシールド
                ControllerState(
                    zl=True,
                ),

                # シールド中に横入力
                ControllerState(
                    zl=True,
                    lx=lx,
                ),

                # 離す
                ControllerState(),
            ]

        # =========================================
        # 台降り
        # =========================================

        if action.action_type == ActionType.DROP_THROUGH:

            if action.direction != Direction.NEUTRAL:
                raise ValueError(
                    "DROP_THROUGH must use NEUTRAL direction"
                )

            states = []

            # すでに下入力中なら、一度ニュートラルへ
            if previous_state.ly > 0.2:
                states.append(
                    ControllerState()
                )

            # 下へflick
            states.append(
                ControllerState(
                    ly=1.0,
                )
            )

            # ニュートラルへ戻す
            states.append(
                ControllerState()
            )

            return states

        # =========================================
        # まだ未実装
        # =========================================

        raise NotImplementedError(
            f"Action not implemented yet: "
            f"{action.action_type.value}"
        )

    # =============================================
    # Direction → 左スティック
    # =============================================

    def _direction_to_stick(
        self,
        direction: Direction,
        strength: float,
    ) -> tuple[float, float]:

        if direction == Direction.NEUTRAL:
            return 0.0, 0.0

        if direction == Direction.LEFT:
            return -strength, 0.0

        if direction == Direction.RIGHT:
            return strength, 0.0

        if direction == Direction.UP:
            return 0.0, -strength

        if direction == Direction.DOWN:
            return 0.0, strength

        raise ValueError(
            f"Unknown direction: {direction}"
        )

    # =============================================
    # Direction → 右スティック
    # =============================================

    def _direction_to_right_stick(
        self,
        direction: Direction,
    ) -> tuple[float, float]:

        if direction == Direction.LEFT:
            return -1.0, 0.0

        if direction == Direction.RIGHT:
            return 1.0, 0.0

        if direction == Direction.UP:
            return 0.0, -1.0

        if direction == Direction.DOWN:
            return 0.0, 1.0

        raise ValueError(
            "Right stick direction must be "
            "LEFT, RIGHT, UP or DOWN"
        )



    def _needs_flick_reset(
        self,
        previous_state: ControllerState,
        lx: float,
        ly: float,
    ) -> bool:

        threshold = 0.2

        if lx > 0:
            return previous_state.lx > threshold

        if lx < 0:
            return previous_state.lx < -threshold

        if ly > 0:
            return previous_state.ly > threshold

        if ly < 0:
            return previous_state.ly < -threshold

        return False