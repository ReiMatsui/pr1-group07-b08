import cv2
from pathlib import Path

class VideoRecorder:
    """
    画面を録画するクラス
    """
    def __init__(self, session_dir: Path, video_name: str, width: int, height: int, fps: float = 20.0):
        self.video_writer = self._create_writer(session_dir / video_name, width, height, fps)
    
    def _create_writer(self, path, width, height, fps):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    
    def write_frames(self, frame):
        self.video_writer.write(frame)
    
    def release(self):
        self.video_writer.release()