import cv2
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime
from pathlib import Path
import queue

from src.utils.camera_manager import CameraManager
from src.utils.video_recorder import VideoRecorder
from src.utils.bicycle_detector import BicycleDetector


class App(BaseModel):
    """
    カメラ映像を取得し、自転車の検出を行うアプリケーションクラス
    """
    model_config = {
        "arbitrary_types_allowed": True
    }
        
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
        bicycle_detector = BicycleDetector()
        bicycle_detector.start()    
        logger.info("自転車検出器を初期化しました")
        try:
            while(self.camera_manager.capture.isOpened()):
                frame = self.camera_manager.get_frames()
                
                if frame is None:
                    logger.error("フレームの取得に失敗しました")
                    break
                
                try:
                    bicycle_detector.put_to_queue(frame)
                except queue.Full:
                    continue
                
                try:
                    processed_frame =  bicycle_detector.get_from_queue()
                except queue.Empty:
                    continue
                
                # 画面にフレームを表示
                self.camera_manager.imshow("Camera", processed_frame)
                
                # 録画する
                self.video_recorder.write_frames(processed_frame)
                
                # 'q'キーで終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                else:
                    logger.error("フレームの取得に失敗しました")
                    break
            
        finally:
            # リソースの解放
            self.camera_manager.release()
            self.video_recorder.release()
            cv2.destroyAllWindows()
            
if __name__ == "__main__":
    app = App()
    app.run()
    logger.info("アプリケーションを開始します")