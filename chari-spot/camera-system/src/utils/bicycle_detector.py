from ultralytics import YOLO
import cv2
from typing import Tuple, List


class BicycleDetector:
    """
    フレームから自転車を検出するクラス
    """
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.3):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, frame) -> Tuple[bool, List[Tuple[int, int, int, int]]]:
        """
        自転車の検出を行う
        :param frame: 入力フレーム (np.ndarray)
        :return: 自転車が検出されたか、検出された自転車のバウンディングボックスリスト
        """
        results = self.model(frame)[0]
        bboxes = []
        bicycle_found = False

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            if self.model.names[cls_id] == "bicycle" and conf > self.confidence_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bboxes.append((x1, y1, x2, y2))
                bicycle_found = True

        return bicycle_found, bboxes

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
