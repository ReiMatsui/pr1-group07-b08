import cv2
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime
from pathlib import Path
import queue
import numpy

from utils.camera_manager import CameraManager
from utils.video_recorder import VideoRecorder
from utils.bicycle_detector import BicycleDetector


class App(BaseModel):
    """
    カメラ映像を取得し、自転車の検出を行うアプリケーションクラス
    """
    model_config = {
        "arbitrary_types_allowed": True
    }
    camera_no: int = Field(default=0, description="使用するカメラの番号")
    video_name: str = Field(default="output.mp4", description="保存するビデオの名前")
    session_dir: Path = None  # セッションディレクトリを保持
    camera_manager: CameraManager = None
    video_recorder: VideoRecorder = None

    def __init__(self, **data):
        super().__init__(**data)
        # セッションディレクトリを作成
        self.session_dir = self._create_session_dir()
        # CameraManagerとVideoRecorderを初期化
        self.camera_manager = CameraManager(camera_no=self.camera_no)
        self.video_recorder = VideoRecorder(
            session_dir=self.session_dir,
            video_name=self.video_name,
            width=1280,
            height=720,
            fps=20.0
        )
            
    def _create_session_dir(self):
        session_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = Path("output") / session_start_time
        session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"セッションディレクトリを作成しました: {session_dir}")
        return session_dir
    
    def run(self):
        """
        メインアプリケーションループ
        """
        cv2.startWindowThread()
        bicycle_detector = BicycleDetector()
        bicycle_detector.start()    
        logger.info("自転車検出器を初期化しました")
        try:
            while(self.camera_manager.capture.isOpened()):
                frame = self.camera_manager.get_frames()
                
                if frame is None:
                    logger.error("フレームの取得に失敗しました")
                    continue
                
                try:
                    bicycle_detector.put_to_queue(frame.copy())
                except queue.Full:
                    continue
                
                try:
                    processed_tuple =  bicycle_detector.get_from_queue()
                    if processed_tuple is None:
                        logger.error("processed_frameがNoneです")
                        continue
                    processed_frame = processed_tuple[2]
                except queue.Empty:
                    continue
                
                logger.info(f"processed_frameのサイズ: {processed_frame.shape}")
                # 画面にフレームを表示
                self.camera_manager.imshow("Camera", processed_frame)
                
                # 録画する
                self.video_recorder.write_frames(processed_frame)
                
                # 'q'キーで終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
        finally:
            # リソースの解放
            self.camera_manager.release()
            self.video_recorder.release()
            cv2.destroyAllWindows()
            
if __name__ == "__main__":
    app = App()
    app.run()