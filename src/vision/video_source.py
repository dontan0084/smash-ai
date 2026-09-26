from abc import ABC, abstractmethod
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class VideoFrame:
    frame_number: int
    timestamp: float
    image: np.ndarray


class VideoSource(ABC):

    @abstractmethod
    def read(self) -> VideoFrame | None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class FileVideoSource(VideoSource):

    def __init__(self, path: str):

        self.cap = cv2.VideoCapture(path)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open video: {path}"
            )

        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )

        if self.fps <= 0:
            raise RuntimeError(
                "Video FPS could not be detected"
            )

        self.frame_number = 0

    def read(self) -> VideoFrame | None:

        ret, image = self.cap.read()

        if not ret:
            return None

        timestamp = (
            self.frame_number / self.fps
        )

        result = VideoFrame(
            frame_number=self.frame_number,
            timestamp=timestamp,
            image=image,
        )

        self.frame_number += 1

        return result

    def close(self) -> None:
        self.cap.release()

import time


class CaptureVideoSource(VideoSource):

    def __init__(
        self,
        device_index: int = 1,
        width: int = 1920,
        height: int = 1080,
        fps: float = 60.0,
    ):

        self.cap = cv2.VideoCapture(
            device_index,
            cv2.CAP_DSHOW,
        )

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open capture device: "
                f"{device_index}"
            )

        # キャプチャーボード側の形式
        self.cap.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"MJPG"),
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            width,
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            height,
        )

        self.cap.set(
            cv2.CAP_PROP_FPS,
            fps,
        )

        self.frame_number = 0

        # read() が返ってきた時刻を測るための基準
        self.start_time = time.perf_counter()

    def read(self) -> VideoFrame | None:

        ret, image = self.cap.read()

        if not ret:
            return None

        timestamp = (
            time.perf_counter()
            - self.start_time
        )

        result = VideoFrame(
            frame_number=self.frame_number,
            timestamp=timestamp,
            image=image,
        )

        self.frame_number += 1

        return result

    def close(self) -> None:
        self.cap.release()