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
                
                if not isinstance(processed_frame, numpy.ndarray):
                    logger.error(f"processed_frameの型が不正です: {type(processed_frame)}")
                    continue

                if processed_frame.ndim != 3 or processed_frame.shape[2] != 3:
                    logger.error(f"processed_frameの形状が不正です: {processed_frame.shape}")
                    continue
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