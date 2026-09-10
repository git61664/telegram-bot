# ============================================================
#  vision.py  —  DLS ekranini tahlil qilish
#
#  ANIQLASH USULLARI (rasmlardan o'rganildi):
#
#  1. YASHIL MARKER (📍) — BIRLAMCHI
#     To'p bizda bo'lganda o'yinchi ustida yorqin yashil
#     marker ko'rinadi. Eng ishonchli belgi.
#
#  2. B TUGMASI YORLIG'I — IKKILAMCHI
#     "LOW KICK"  (ko'p oq piksel) = to'p bizda
#     "PRESSURE"  (kam oq piksel)  = to'p bizda emas
#
#  3. DARVOZA — oq to'rtburchak kontur
#     Ekranning yuqori 58% qismida qidiriladi.
#     Maydoni qanchalik katta = shunchalik yaqin.
# ============================================================

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Tuple

from config import (
    MARKER_HSV_LOWER, MARKER_HSV_UPPER,
    MARKER_ZONE_X, MARKER_ZONE_Y,
    MARKER_MIN_PX, MARKER_MAX_PX,
    BTN_B_X, BTN_B_Y,
    LOWKICK_HSV_LOWER, LOWKICK_HSV_UPPER, LOWKICK_PX_THRESH,
    GOAL_HSV_LOWER, GOAL_HSV_UPPER,
    GOAL_MIN_AREA, GOAL_SEARCH_Y_MAX,
    SHOOT_AREA_CLOSE, SHOOT_AREA_MEDIUM,
)


# ============================================================
#  DATA CLASSLAR
# ============================================================

@dataclass
class OwnershipInfo:
    owned:         bool  = False
    method:        str   = "unknown"
    marker_px:     int   = 0
    marker_x:      int   = -1
    marker_y:      int   = -1
    btn_px:        int   = 0


@dataclass
class GoalInfo:
    found:     bool  = False
    area:      float = 0.0
    cx:        int   = -1
    cy:        int   = -1
    direction: str   = "center"   # left | center | right
    distance:  str   = "far"      # far | medium | close


# ============================================================
#  ASOSIY SINF
# ============================================================

class VisionSystem:

    def __init__(self, fw: int, fh: int):
        self.fw = fw
        self.fh = fh

        # Marker qidirish zonasi (piksel)
        self.mz_x1 = int(fw * MARKER_ZONE_X[0])
        self.mz_x2 = int(fw * MARKER_ZONE_X[1])
        self.mz_y1 = int(fh * MARKER_ZONE_Y[0])
        self.mz_y2 = int(fh * MARKER_ZONE_Y[1])

        # B tugmasi zonasi (piksel)
        self.bz_x1 = int(fw * BTN_B_X[0])
        self.bz_x2 = int(fw * BTN_B_X[1])
        self.bz_y1 = int(fh * BTN_B_Y[0])
        self.bz_y2 = int(fh * BTN_B_Y[1])

        # Darvoza qidirish chegarasi
        self.goal_cut = int(fh * GOAL_SEARCH_Y_MAX)

        # Kalibratsiya bilan yangilash mumkin
        self.marker_lo = np.array(MARKER_HSV_LOWER, dtype=np.uint8)
        self.marker_hi = np.array(MARKER_HSV_UPPER, dtype=np.uint8)

    # ----------------------------------------------------------
    def apply_calibration(self, calib: dict):
        """auto_calibrate.py dan kelgan qiymatlarni qo'llaydi."""
        if "marker_lo" in calib and "marker_hi" in calib:
            self.marker_lo = np.array(calib["marker_lo"], dtype=np.uint8)
            self.marker_hi = np.array(calib["marker_hi"], dtype=np.uint8)
            print(f"[Vision] Kalibratsiya qo'llandi: "
                  f"marker_lo={calib['marker_lo']} "
                  f"marker_hi={calib['marker_hi']}")

    # ----------------------------------------------------------
    #  YORDAMCHI METODLAR
    # ----------------------------------------------------------
    @staticmethod
    def _to_hsv(bgr: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(bgr, (3, 3), 0)
        return cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    @staticmethod
    def _count(mask: np.ndarray) -> int:
        return int(cv2.countNonZero(mask))

    def _crop(self, frame, x1, y1, x2, y2) -> np.ndarray:
        h, w = frame.shape[:2]
        x1, x2 = max(0, x1), min(w, x2)
        y1, y2 = max(0, y1), min(h, y2)
        return frame[y1:y2, x1:x2]

    # ----------------------------------------------------------
    #  1. YASHIL MARKER ANIQLASH
    # ----------------------------------------------------------
    def _detect_marker(self, frame: np.ndarray) -> OwnershipInfo:
        crop = self._crop(frame, self.mz_x1, self.mz_y1, self.mz_x2, self.mz_y2)
        if crop.size == 0:
            return OwnershipInfo()

        hsv  = self._to_hsv(crop)
        mask = cv2.inRange(hsv, self.marker_lo, self.marker_hi)

        # Shovqin tozalash
        k    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

        count = self._count(mask)

        if MARKER_MIN_PX <= count <= MARKER_MAX_PX:
            # Markazini hisoblash
            M = cv2.moments(mask)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"]) + self.mz_x1
                cy = int(M["m01"] / M["m00"]) + self.mz_y1
                return OwnershipInfo(
                    owned=True, method="MARKER✓",
                    marker_px=count, marker_x=cx, marker_y=cy
                )

        return OwnershipInfo(marker_px=count)

    # ----------------------------------------------------------
    #  2. B TUGMASI YORLIG'I
    # ----------------------------------------------------------
    def _detect_btn_label(self, frame: np.ndarray) -> tuple[bool, int]:
        """
        B tugmasi zonasidagi oq piksellarni sanaydi.
        Ko'p oq = LOW KICK (bizda), kam oq = PRESSURE (yo'q).
        Qaytaradi: (is_lowkick, pixel_count)
        """
        crop = self._crop(frame, self.bz_x1, self.bz_y1, self.bz_x2, self.bz_y2)
        if crop.size == 0:
            return False, 0

        hsv   = self._to_hsv(crop)
        lo    = np.array(LOWKICK_HSV_LOWER, dtype=np.uint8)
        hi    = np.array(LOWKICK_HSV_UPPER, dtype=np.uint8)
        mask  = cv2.inRange(hsv, lo, hi)
        count = self._count(mask)

        return count >= LOWKICK_PX_THRESH, count

    # ----------------------------------------------------------
    #  ASOSIY: TO'P EGALIGI
    # ----------------------------------------------------------
    def detect_ownership(self, frame: np.ndarray) -> OwnershipInfo:
        # Avval marker tekshir (ishonchli)
        info = self._detect_marker(frame)
        if info.owned:
            _, btn_px        = self._detect_btn_label(frame)
            info.btn_px      = btn_px
            return info

        # Marker yo'q — B tugmasi yorlig'ini tekshir
        is_lk, btn_px = self._detect_btn_label(frame)
        if is_lk:
            return OwnershipInfo(
                owned=True, method="BTN:LOW_KICK",
                marker_px=info.marker_px, btn_px=btn_px
            )

        return OwnershipInfo(
            owned=False, method="PRESSURE",
            marker_px=info.marker_px, btn_px=btn_px
        )

    # ----------------------------------------------------------
    #  3. DARVOZA ANIQLASH
    # ----------------------------------------------------------
    def detect_goal(self, frame: np.ndarray) -> GoalInfo:
        top = frame[:self.goal_cut, :]
        hsv = self._to_hsv(top)

        lo   = np.array(GOAL_HSV_LOWER, dtype=np.uint8)
        hi   = np.array(GOAL_HSV_UPPER, dtype=np.uint8)
        mask = cv2.inRange(hsv, lo, hi)

        k    = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k)

        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        info      = GoalInfo()
        best_area = 0.0

        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area < GOAL_MIN_AREA:
                continue
            peri   = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
            if len(approx) < 4:
                continue
            if area > best_area:
                best_area = area
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx, cy = x + w // 2, y + h // 2

                info.found = True
                info.area  = area
                info.cx    = cx
                info.cy    = cy

                # Yo'nalish
                mid = self.fw // 2
                off = self.fw * 0.13
                if   cx < mid - off: info.direction = "left"
                elif cx > mid + off: info.direction = "right"
                else:                info.direction = "center"

                # Masofa
                if   area >= SHOOT_AREA_CLOSE:  info.distance = "close"
                elif area >= SHOOT_AREA_MEDIUM:  info.distance = "medium"
                else:                            info.distance = "far"

        return info

    # ----------------------------------------------------------
    #  DEBUG OVERLAY
    # ----------------------------------------------------------
    def draw_debug(self, frame: np.ndarray,
                   own: OwnershipInfo,
                   goal: GoalInfo,
                   state: str,
                   bot_active: bool) -> np.ndarray:

        d = frame.copy()
        h, w = d.shape[:2]

        # ── Marker qidirish zonasi ──
        cv2.rectangle(d,
            (self.mz_x1, self.mz_y1), (self.mz_x2, self.mz_y2),
            (0, 200, 80), 1)

        # ── B tugmasi zonasi ──
        bc = (0, 240, 0) if own.owned else (0, 60, 255)
        cv2.rectangle(d,
            (self.bz_x1, self.bz_y1), (self.bz_x2, self.bz_y2),
            bc, 1)

        # ── Yashil marker ──
        if own.marker_x > 0:
            cv2.circle(d, (own.marker_x, own.marker_y), 12, (0, 255, 80), 2)
            cv2.drawMarker(d, (own.marker_x, own.marker_y),
                           (0, 255, 80), cv2.MARKER_CROSS, 16, 2)

        # ── Darvoza ──
        if goal.found:
            gc = (50, 50, 255)
            cv2.circle(d, (goal.cx, goal.cy), 16, gc, 3)
            cv2.putText(d,
                f"GOAL {goal.distance.upper()} {goal.direction} ({int(goal.area)}px)",
                (goal.cx - 60, goal.cy - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, gc, 1)

        # ── HUD Panel ──
        ov = d.copy()
        cv2.rectangle(ov, (0, 0), (w, 100), (0, 0, 0), -1)
        cv2.addWeighted(ov, 0.55, d, 0.45, 0, d)

        # Bot holati
        status_c = (0, 230, 0) if bot_active else (0, 60, 255)
        status_t = "● ACTIVE  [F2=stop]" if bot_active else "● PAUSED  [F1=start]"
        cv2.putText(d, status_t, (10, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_c, 2)

        # To'p holati
        ball_t = f"BALL: {'BIZDA ✓  ' if own.owned else 'YO\\'Q ✗ '} [{own.method}]"
        ball_c = (0, 230, 0) if own.owned else (0, 80, 255)
        cv2.putText(d, ball_t, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, ball_c, 2)

        # State + piksel info
        cv2.putText(d,
            f"STATE: {state:<10}  marker={own.marker_px}px  btn={own.btn_px}px",
            (10, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1)

        cv2.putText(d, "F1=START  F2=STOP  F4=QUIT",
            (10, 94), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (120, 120, 255), 1)

        return d
