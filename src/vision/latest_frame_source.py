import threading
import time

from src.vision.video_source import (
    VideoFrame,
    VideoSource,
)


class LatestFrameSource:
    def __init__(
        self,
        source: VideoSource,
    ):
        self.source = source

        self._latest_frame: VideoFrame | None = None
        self._lock = threading.Lock()

        self._running = False
        self._thread: threading.Thread | None = None

        self._received_frames = 0

    def start(self):

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
        )

        self._thread.start()

    def _capture_loop(self):

        while self._running:

            frame = self.source.read()

            if frame is None:
                continue

            with self._lock:
                self._latest_frame = frame

            self._received_frames += 1

    def get_latest(
        self,
    ) -> VideoFrame | None:

        with self._lock:

            if self._latest_frame is None:
                return None

            return self._latest_frame

    @property
    def received_frames(self):
        return self._received_frames

    def close(self):

        self._running = False

        if self._thread is not None:
            self._thread.join(
                timeout=1.0
            )

        self.source.close()