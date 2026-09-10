# ============================================================
#  screen_capture.py  —  Ekrandan tasvir olish
#  LDPlayer oynasini avtomatik topadi
# ============================================================

import numpy as np
import mss
import cv2

try:
    import win32gui
    import win32con
    _WIN32 = True
except ImportError:
    _WIN32 = False

from config import WINDOW_TITLE, CAPTURE_REGION


class ScreenCapture:

    def __init__(self):
        self.sct    = mss.mss()
        self.region = self._find_region()

    # ----------------------------------------------------------
    def _find_region(self) -> dict:
        if CAPTURE_REGION is not None:
            return CAPTURE_REGION

        if _WIN32:
            hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
            if not hwnd:
                # "LDPlayer" nomi bilan boshlanadigan oynani qidirish
                def _cb(h, extra):
                    t = win32gui.GetWindowText(h)
                    if WINDOW_TITLE.lower() in t.lower():
                        extra.append(h)
                found = []
                win32gui.EnumWindows(_cb, found)
                hwnd = found[0] if found else None

            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                rect = win32gui.GetWindowRect(hwnd)
                region = {
                    "top":    rect[1],
                    "left":   rect[0],
                    "width":  rect[2] - rect[0],
                    "height": rect[3] - rect[1],
                }
                # Sarlavha panelini olib tashlash (~30px)
                region["top"]    += 30
                region["height"] -= 30
                print(f"[Screen] LDPlayer topildi: {region}")
                return region

        mon = self.sct.monitors[1]
        print(f"[Screen] LDPlayer topilmadi — to'liq ekran: {mon}")
        return dict(mon)

    # ----------------------------------------------------------
    def refresh(self):
        """Oyna ko'chirilganda koordinatalarni yangilaydi."""
        self.region = self._find_region()

    # ----------------------------------------------------------
    def capture(self) -> np.ndarray:
        """BGR formatda numpy array qaytaradi."""
        shot = self.sct.grab(self.region)
        frame = np.array(shot)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # ----------------------------------------------------------
    def size(self) -> tuple[int, int]:
        """(width, height)"""
        return self.region["width"], self.region["height"]

    # ----------------------------------------------------------
    def release(self):
        self.sct.close()
