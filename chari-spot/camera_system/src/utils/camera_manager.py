import cv2
import numpy
from loguru import logger

class CameraManager:
    """
    カメラ映像を取得するクラス
    """
    def __init__(self, camera_no: int = 0):
        self.capture = cv2.VideoCapture(camera_no)
        
        # 画質を取得し低めに設定する
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) //4)
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT) //4)
        
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # OpenCVが調整する場合があるので再取得
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # FPSを取得
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        logger.info(f"カメラのFPS: {self.fps}")

    def get_frames(self):
        self.ret, self.frame = self.capture.read()
        
        if self.ret:
            return cv2.flip(self.frame, 1)
        return None
    
    def imshow(self, window_name: str, image: numpy.ndarray):
        try:
            cv2.imshow(window_name, image)
        except Exception as e:
            logger.error(f"画像表示/保存中のエラー: {e}")  
            
    def release(self):
        self.capture.release()