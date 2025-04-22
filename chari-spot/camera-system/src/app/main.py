import cv2
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime
from pathlib import Path

from chari-spot.camerasystem.src.utils.camera_manager import CameraManager
from src.utils.video_recorder import VideoRecorder
from src.utils.bicycle_detector import BicycleDetector


class App(BaseModel):
    """
    カメラ映像を取得し、自転車の検出を行うアプリケーションクラス
    """
    camera_no: int = Field(default=0, description="使用するカメラの番号")
    video_name: str = Field(default="output.mp4", description="保存するビデオの名前")
    camera_manager: CameraManager = CameraManager(camera_no=0)
    video_recorder: VideoRecorder = VideoRecorder(
        session_dir=Path("output") / datetime.now().strftime("%Y%m%d_%H%M%S"),
        video_name="output.mp4",
        width=640,
        height=480,
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
        detector = BicycleDetector()
        
        while(self.camera_manager.capture.isOpened()):
            ret, frame = self.camera_manager.get_frames()
            
            if ret:
                # フレーム取得後に検出処理を実行
                bicycle_found, boxes = detector.detect(frame)

                # バウンディングボックスの描画
                if bicycle_found:
                    detector.draw_boxes(frame, boxes)
                # 画面にフレームを表示
                self.camera_manager.imshow("Camera", frame)
                
                # 録画する
                self.video_recorder.write_frames(frame)
                
                # 'q'キーで終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                logger.error("フレームの取得に失敗しました")
                break