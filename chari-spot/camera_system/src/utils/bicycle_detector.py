from ultralytics import YOLO
import cv2
from typing import Tuple, List
import threading
import queue
import numpy as np


class BicycleDetector:
    """
    フレームから自転車を検出するクラス
    """
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.3):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        self.bicycle_frame_queue = queue.Queue(maxsize=10)
        self.bicycle_result_queue = queue.Queue(maxsize=10) 
        
        self.running = threading.Event()
        self.bicycle_detection_thread = threading.Thread(target=self.detect)
        self.bicycle_detection_thread.daemon = True
        self.running.set()
        
    def start(self):
        """
        スレッドを開始する
        """
        self.bicycle_detection_thread.start()
        return

    def put_to_queue(self, frame):
        """
        フレームをキューに追加する
        :param frame: 入力フレーム (np.ndarray)
        """
        if not self.bicycle_frame_queue.full():
            self.bicycle_frame_queue.put(frame, timeout=0.1)
            
    def get_from_queue(self) -> Tuple[bool, List[Tuple[int, int, int, int]], np.ndarray]:
        """
        キューからフレームを取得する
        :return: フレーム (np.ndarray)
        """
        if not self.bicycle_result_queue.empty():
            return self.bicycle_result_queue.get(timeout=0.1)
        return None
            
            
    def detect(self):
        """
        キュー内のフレームを処理し、自転車の検出を行い、バウンディングボックスを描画したフレームを返す
        """
        while self.running.is_set():
            try:
                # キューからフレームを取得
                frame = self.bicycle_frame_queue.get(timeout=0.1)
                results = self.model(frame)[0]
                bboxes = []
                bicycle_found = False

                # 検出結果を解析
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])

                    if self.model.names[cls_id] == "bicycle" and conf > self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        bboxes.append((x1, y1, x2, y2))
                        bicycle_found = True

                # バウンディングボックスを描画
                self.draw_boxes(frame, bboxes)

                # 結果をキューに追加（描画済みフレームを含む）
                self.bicycle_result_queue.put((bicycle_found, bboxes, frame))

            except queue.Empty:
                # キューが空の場合はスキップ
                continue


    def draw_boxes(self, frame, bboxes: List[Tuple[int, int, int, int]]):
        """
        バウンディングボックスをフレームに描画
        :param frame: 入力フレーム
        :param bboxes: バウンディングボックスリスト
        """
        for (x1, y1, x2, y2) in bboxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, "Bicycle", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 2)
            
    def clean_up(self):
        """
        別スレッドでのmediapipe処理を終了し、キューをクリア
        """
        self.running.clear()
        # キューをクリア
        for q in [self.bicycle_frame_queue, self.bicycle_result_queue]:
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
        self.bicycle_detection_thread.join(timeout=2.0)