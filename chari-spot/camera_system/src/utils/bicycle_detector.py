from ultralytics import YOLO
import cv2
from typing import Tuple, List
import threading
import queue
import numpy as np
from loguru import logger
import subprocess
import numpy
import time


class BicycleDetector:
    """
    フレームから自転車を検出するクラス
    """
    def __init__(self, model_path: str = "yolov8n.pt", 
                 confidence_threshold: float = 0.3,
                 detection_threshold: float = 5.0,
                 payment_grace_period: float = 60.0): 
        
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        self.bicycle_frame_queue = queue.Queue(maxsize=10)
        self.bicycle_result_queue = queue.Queue(maxsize=10) 

        self.detection_threshold = detection_threshold
        self.detect_started: dict[int, float] = {}   # slot -> start_time
        self.announced_slots: set[int] = set()   # ←これを追加
        
        self.payment_grace_period = payment_grace_period
        self.paid_slots: set[int] = set()               # ← ❷ 支払い済スロット
        self.payment_timers: dict[int, threading.Timer] = {}  # ← ❸ 猶予タイマ
        
        self.if_announce_done = False
        
        self.running = threading.Event()
        self.bicycle_detection_thread = threading.Thread(target=self.detect)
        self.bicycle_detection_thread.daemon = True
        self.running.set()
        
        
    @staticmethod
    def get_slot(cx: int, w: int) -> int:
        """
        バウンディングボックス中心 x 座標から
        1 行 4 列（左から 1-4）のスロット番号を返す
        """
        col = cx * 4 // w          # 0,1,2,3
        return col + 1             # → 1-4
    
    def mark_payment_completed(self, slot_no: int):
        """QR決済が完了したときに呼ぶ"""
        self.paid_slots.add(slot_no)
        # 進行中のタイマがあれば止める
        t = self.payment_timers.pop(slot_no, None)
        if t and t.is_alive():
            t.cancel()
        logger.info(f"slot{slot_no}: 支払い完了を受信")
        
    def _check_payment_status(self, slot_no: int):
        """猶予時間後に呼ばれるコールバック"""
        self.payment_timers.pop(slot_no, None)  # 終了したタイマを削除
        if slot_no in self.paid_slots:
            logger.info(f"slot{slot_no}: 期限内に支払い済み")
            return
        # まだ未払い: アナウンス
        self.announce_payment_not_done(slot_no)
        
    def announce_payment_not_done(self, slot_no: int):
        try:
            subprocess.run([
                "say", "-v", "Kyoko",
                f"スロット{slot_no}で支払いが行われていません。"
                "ただちに支払いを行ってください。録画を開始します。"
            ])
        except Exception as e:
            logger.error(f"未払いアナウンスに失敗しました: {e}")
             
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
            
    def announce_bicycle_detected(self, slot_no: int):
        try:
            subprocess.run([
                "say", "-v", "Kyoko",
                f"スロット{slot_no}で自転車が検出されました。"
                "ちゅうりんする場合は、5分以内にQRコードから支払いを行なってください。"
                "5分を過ぎても支払いが行われずにちゅうりんしている場合は録画を開始します。"
            ])
        except Exception as e:
            logger.error(f"音声アナウンスに失敗しました: {e}")
            
        if slot_no not in self.payment_timers:
            t = threading.Timer(self.payment_grace_period,
                                self._check_payment_status,
                                args=(slot_no,))
            t.daemon = True
            self.payment_timers[slot_no] = t
            t.start()


    def detect(self):
        """
        フレームを取り出して YOLO 推論し、バウンディングボックスと
        スロットごとに一定時間以上検出された場合だけ音声案内する。
        """
        while self.running.is_set():
            # --- フレーム取得 ---------------------------------------------------
            try:
                frame = self.bicycle_frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # --- バリデーション -------------------------------------------------
            if not isinstance(frame, np.ndarray):
                logger.error(f"frame の型が不正です: {type(frame)}")
                continue
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            if frame.ndim != 3 or frame.shape[2] != 3:
                logger.error(f"frame の形状が不正です: {frame.shape}")
                continue

            # --- 推論 -----------------------------------------------------------
            results = self.model(frame)[0]
            bboxes: list[tuple[int, int, int, int]] = []
            current_slots: set[int] = set()    # 今フレームで自転車が写っているスロット
            h, w = frame.shape[:2]

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf   = float(box.conf[0])

                if self.model.names[cls_id] != "bicycle" or conf <= self.confidence_threshold:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bboxes.append((x1, y1, x2, y2))

                cx = (x1 + x2) // 2
                slot_no = self.get_slot(cx, w)           # 1–4
                current_slots.add(slot_no)

            now = time.time()

            # --- スロット毎の検出継続時間チェック -------------------------------
            for slot in range(1, 5):
                if slot in current_slots:
                    # 検出継続中: 開始時間を記録 or 継続時間を更新
                    if slot not in self.detect_started:
                        self.detect_started[slot] = now
                    # しきい値経過 & 未アナウンスなら案内
                    elif (now - self.detect_started[slot] >= self.detection_threshold
                        and slot not in self.announced_slots):
                        threading.Thread(
                            target=self.announce_bicycle_detected,
                            args=(slot,),
                            daemon=True
                        ).start()
                        self.announced_slots.add(slot)
                else:
                    # 今フレームに写っていない: 状態リセット
                    self.reset_slot(slot)

            # --- 描画とキュー格納 ---------------------------------------------
            self.draw_boxes(frame, bboxes)
            if not self.bicycle_result_queue.full():
                bicycle_found = bool(bboxes)
                self.bicycle_result_queue.put((bicycle_found, bboxes, frame))


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
         
    def draw_guidelines(self, frame):
        h, w = frame.shape[:2]
        for i in range(1, 4):                     # 1/4, 2/4, 3/4 の位置
            x = i * w // 4
            cv2.line(frame, (x, 0), (x, h), (0, 255, 0), 1)   
            
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
        
    def reset_slot(self, slot_no: int):
        self.detect_started.pop(slot_no, None)
        self.announced_slots.discard(slot_no)
        self.paid_slots.discard(slot_no)
        t = self.payment_timers.pop(slot_no, None)
        if t and t.is_alive():
            t.cancel()