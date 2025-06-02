from ultralytics import YOLO
import cv2
from typing import Tuple, List
import threading
import queue
import numpy as np
from loguru import logger
import subprocess
from collections import defaultdict
import time
import httpx
from urllib.parse import urlencode

class BicycleDetector:
    """
    駐輪スロット 4 つを横一列に配置し、自転車検出・支払い確認・音声案内を行う。
    音声は 1 本のワーカースレッドで直列再生するため重ならない。
    """

    # ------------------------------------------------------------------ #
    # 初期化
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.3,
        detection_threshold: float = 15.0,        # [秒] スロット内滞在判定
        payment_grace_period: float = 60.0,       # [秒] 支払い猶予
        slot_gap_px: int = 20,                   # スロット間ギャップ幅
        payment_api_base: str = "http://localhost:8000/payments/public",
    ):
        # ---- YOLO ----------------------------------------------------- #
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

        # ---- スレッド間キュー ----------------------------------------- #
        self.bicycle_frame_queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=10)
        self.bicycle_result_queue: "queue.Queue[Tuple[bool, list, np.ndarray]]" = queue.Queue(maxsize=10)

        # ---- 検出・支払い状態 ----------------------------------------- #
        self.detection_threshold = detection_threshold
        self.detect_started: dict[int, float] = {}      # slot -> first_detect_time
        self.announced_slots: set[int] = set()          # 検出案内済みスロット
        self.announced_paid_slots: set[int] = set()

        self.payment_grace_period = payment_grace_period
        self.paid_slots: set[int] = set()               # 支払い完了スロット
        self.payment_timers: dict[int, threading.Timer] = {}

        # ---- 検出ロスト判定 ------------------------------------------ #
        self.lost_frames = defaultdict(int)
        self.lost_threshold = 3000000000000                      # 連続ロストでリセット

        # ---- スロット描画関連 ---------------------------------------- #
        self.slot_gap_px = slot_gap_px

        # ---- 実行フラグ --------------------------------------------- #
        self.running = threading.Event()
        self.running.set()

        # ---- 検出スレッド ------------------------------------------- #
        self.bicycle_detection_thread = threading.Thread(
            target=self.detect, daemon=True
        )

        # ---- TTS ワーカースレッド ----------------------------------- #
        self.announcement_queue: "queue.Queue[str]" = queue.Queue(maxsize=50)
        self.announcement_worker = threading.Thread(
            target=self._announcement_loop, daemon=True
        )
        
        self.payment_api_base = payment_api_base
        self.payment_poll_interval = 5.0      # [秒] ポーリング周期
        self.payment_poll_worker = threading.Thread(
            target=self._payment_poll_loop, daemon=True
        )

    # ------------------------------------------------------------------ #
    # 公開 API
    # ------------------------------------------------------------------ #
    def start(self):
        """検出スレッドと TTS ワーカーを開始"""
        self.bicycle_detection_thread.start()
        self.announcement_worker.start()
        self.payment_poll_worker.start()

    def put_to_queue(self, frame: np.ndarray):
        """カメラフレームを検出キューへ投入"""
        try:
            self.bicycle_frame_queue.put(frame, timeout=0.1)
        except queue.Full:
            pass

    def get_from_queue(self) -> Tuple[bool, List[Tuple[int, int, int, int]], np.ndarray] | None:
        """描画済みフレームと検出結果を取得（利用側 UI 用）"""
        try:
            return self.bicycle_result_queue.get(timeout=0.1)
        except queue.Empty:
            return None

    def mark_payment_completed(self, slot_no: int):
        """QR 決済完了を外部から通知"""
        self.paid_slots.add(slot_no)
        # 猶予タイマーを停止
        t = self.payment_timers.pop(slot_no, None)
        if t and t.is_alive():
            t.cancel()

        logger.info(f"slot{slot_no}: 支払い完了を受信")

        # まだアナウンスしていなければ読上げ
        if slot_no not in self.announced_paid_slots:
            threading.Thread(
                target=self.announce_payment_completed,
                args=(slot_no,),
                daemon=True,
            ).start()
            self.announced_paid_slots.add(slot_no)

    def clean_up(self):
        """全スレッド停止・キュークリア"""
        self.running.clear()

        # 検出スレッド停止
        self.bicycle_detection_thread.join(timeout=2.0)

        # TTS ワーカースレッド停止
        self.announcement_worker.join(timeout=2.0)

        for q in (self.bicycle_frame_queue, self.bicycle_result_queue, self.announcement_queue):
            with q.mutex:
                q.queue.clear()

    # ------------------------------------------------------------------ #
    # 内部ユーティリティ
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_slot(cx: int, w: int, gap: int) -> int:
        """
        横 4 スロット＋ 3 ギャップ配置。
        ギャップ領域なら 0、スロットなら 1–4 を返す。
        """
        slot_w = (w - 3 * gap) // 4
        for i in range(4):
            start = i * (slot_w + gap)
            end = start + slot_w
            if start <= cx < end:
                return i + 1
        return 0

    def _enqueue_tts(self, message: str):
        """TTS メッセージをキューに追加（満杯なら破棄）"""
        try:
            self.announcement_queue.put_nowait(message)
        except queue.Full:
            logger.warning("TTS queue full ― message dropped")

    def _announcement_loop(self):
        """キューから 1 つずつ取り出して `say` で読み上げ"""
        while self.running.is_set() or not self.announcement_queue.empty():
            try:
                msg = self.announcement_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                subprocess.run(["say", "-v", "Kyoko", msg])
            except Exception as e:
                logger.error(f"TTS failed: {e}")
            self.announcement_queue.task_done()

    # ------------------------------------------------------------------ #
    # 音声案内生成
    # ------------------------------------------------------------------ #
    def announce_bicycle_detected(self, slot_no: int):
        msg = (
            f"スロット{slot_no}で自転車が検出されました。"
            "ちゅうりんする場合は、5分以内にQRコードから支払いを行なってください。"
            "5分を過ぎても支払いが行われずにちゅうりんしている場合は録画を保存します。"
        )
        self._enqueue_tts(msg)

        # 支払い猶予タイマをセット
        if slot_no not in self.payment_timers:
            t = threading.Timer(
                self.payment_grace_period,
                self._check_payment_status,
                args=(slot_no,),
            )
            t.daemon = True
            self.payment_timers[slot_no] = t
            t.start()

    def announce_payment_not_done(self, slot_no: int):
        msg = (
            f"スロット{slot_no}で支払いが行われていません。"
            "ただちに支払いを行ってください。録画を開始します。"
        )
        self._enqueue_tts(msg)

    def announce_payment_completed(self, slot_no: int):
        msg = (
            f"スロット{slot_no}のお支払いを確認しました。"
            "ご利用ありがとうございます。"
        )
        self._enqueue_tts(msg)

    def _check_payment_status(self, slot_no: int):
        """猶予時間後に支払い確認"""
        self.payment_timers.pop(slot_no, None)
        if slot_no in self.paid_slots:
            logger.info(f"slot{slot_no}: 期限内に支払い済み")
            return
        self.announce_payment_not_done(slot_no)

    # ------------------------------------------------------------------ #
    # 検出メインループ
    # ------------------------------------------------------------------ #
    def detect(self):
        while self.running.is_set():
            # -------- フレーム取得 ------------------------------------ #
            try:
                frame = self.bicycle_frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # -------- 入力検証 ---------------------------------------- #
            if not isinstance(frame, np.ndarray):
                logger.error(f"frame の型が不正: {type(frame)}")
                continue
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            if frame.ndim != 3 or frame.shape[2] != 3:
                logger.error(f"frame の形状が不正: {frame.shape}")
                continue

            # -------- YOLO 推論 -------------------------------------- #
            results = self.model(frame)[0]
            bboxes: list[Tuple[int, int, int, int]] = []
            current_slots: set[int] = set()
            h, w = frame.shape[:2]

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if self.model.names[cls_id] != "bicycle" or conf <= self.confidence_threshold:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bboxes.append((x1, y1, x2, y2))

                cx = (x1 + x2) // 2
                slot_no = self.get_slot(cx, w, self.slot_gap_px)
                if slot_no == 0:
                    continue
                current_slots.add(slot_no)

            now = time.time()

            # -------- スロット滞在判定 -------------------------------- #
            for slot in range(1, 5):
                if slot in current_slots:
                    self.lost_frames[slot] = 0
                    if slot not in self.detect_started:
                        self.detect_started[slot] = now
                    elif (
                        now - self.detect_started[slot] >= self.detection_threshold
                        and slot not in self.announced_slots
                    ):
                        threading.Thread(
                            target=self.announce_bicycle_detected,
                            args=(slot,),
                            daemon=True,
                        ).start()
                        self.announced_slots.add(slot)
                else:
                    self.lost_frames[slot] += 1
                    if self.lost_frames[slot] >= self.lost_threshold:
                        self.reset_slot(slot)
                        self.lost_frames[slot] = 0

            # -------- 描画 & 結果送信 -------------------------------- #
            self.draw_boxes(frame, bboxes)
            self.draw_guidelines(frame)

            if not self.bicycle_result_queue.full():
                self.bicycle_result_queue.put((bool(bboxes), bboxes, frame))

    # ------------------------------------------------------------------ #
    # 描画関連
    # ------------------------------------------------------------------ #
    @staticmethod
    def draw_boxes(frame: np.ndarray, bboxes: List[Tuple[int, int, int, int]]):
        for (x1, y1, x2, y2) in bboxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                frame,
                "Bicycle",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

    def draw_guidelines(self, frame: np.ndarray):
        h, w = frame.shape[:2]
        g = self.slot_gap_px
        slot_w = (w - 3 * g) // 4
        for i in range(1, 4):
            x0 = i * slot_w + (i - 1) * g
            cv2.rectangle(frame, (x0, 0), (x0 + g - 1, h), (180, 180, 180), -1)
            cv2.line(frame, (x0, 0), (x0, h), (0, 255, 0), 1)
            cv2.line(frame, (x0 + g, 0), (x0 + g, h), (0, 255, 0), 1)

    # ----------------------- 支払い確認ループ ------------------------
    def _payment_poll_loop(self):
        """
        ① self.announced_slots（滞在判定＆案内済み）を走査  
        ② サーバーの paid 状態をチェック  
        ③ true なら mark_payment_completed() を呼ぶ
        """
        client = httpx.Client(timeout=3.0)
        while self.running.is_set():
            # 監視対象スロットは “案内済み & まだ支払い未完了”
            target_slots = [
                s for s in self.announced_slots if s not in self.paid_slots
            ]
            for slot in target_slots:
                params = urlencode({"spot_id": 1, "slot_id": slot})
                url = f"{self.payment_api_base}?{params}"
                try:
                    r = client.get(url)
                    if r.status_code == 200:
                        data = r.json()  # {"paid": true / false}
                        if data.get("paid") is True:
                            self.mark_payment_completed(slot)
                    elif r.status_code == 404:
                        logger.debug(f"slot{slot}: まだ DB にレコードなし")
                    else:
                        logger.warning(f"slot{slot}: API error {r.status_code}: {r.text}")
                except httpx.RequestError as e:
                    logger.error(f"API request failed: {e}")
            # 次の周回までスリープ
            time.sleep(self.payment_poll_interval)
        client.close()
    # ------------------------------------------------------------------ #
    # スロット状態リセット
    # ------------------------------------------------------------------ #
    def reset_slot(self, slot_no: int):
        self.detect_started.pop(slot_no, None)
        self.announced_slots.discard(slot_no)
        self.announced_paid_slots.discard(slot_no)
        self.paid_slots.discard(slot_no)
        t = self.payment_timers.pop(slot_no, None)
        if t and t.is_alive():
            t.cancel()
