# ============================================================
#  controller.py  —  Klaviatura boshqaruvi
#  W = oldinga | B = pressing/lowkick | J = zarba
# ============================================================

import time
import pyautogui

from config import KEY_FORWARD, KEY_PRESSING, KEY_SHOOT, SHOOT_HOLD_TIME

pyautogui.FAILSAFE = False   # Burchakka olib borsa to'xtamasin
pyautogui.PAUSE    = 0.0     # Har amal orasida kutish yo'q


class Controller:

    def __init__(self):
        self._held: str | None = None
        self._last: str        = "—"

    # ── ichki yordamchi ──────────────────────────────────────
    def _release(self):
        if self._held:
            try:
                pyautogui.keyUp(self._held)
            except Exception:
                pass
            self._held = None

    def _hold(self, key: str):
        if self._held != key:
            self._release()
            pyautogui.keyDown(key)
            self._held = key

    # ── ochiq metodlar ───────────────────────────────────────
    def press_forward(self):
        """W — oldinga yurish (bosib turadi)."""
        self._hold(KEY_FORWARD)
        self._last = "W (forward)"

    def press_pressing(self):
        """B — pressing yoki low kick (bosib turadi)."""
        self._hold(KEY_PRESSING)
        self._last = "B (pressing)"

    def shoot(self):
        """J — zarba (bir marta, SHOOT_HOLD_TIME davomida)."""
        self._release()
        pyautogui.keyDown(KEY_SHOOT)
        time.sleep(SHOOT_HOLD_TIME)
        pyautogui.keyUp(KEY_SHOOT)
        self._last = "J (shoot) ⚽"

    def release_all(self):
        """Barcha tugmalarni qo'yib yuboradi (bot to'xtaganda)."""
        self._release()
        for k in (KEY_FORWARD, KEY_PRESSING, KEY_SHOOT):
            try:
                pyautogui.keyUp(k)
            except Exception:
                pass
        self._last = "— (released)"

    # ── xususiyat ────────────────────────────────────────────
    @property
    def last_action(self) -> str:
        return self._last

    @property
    def held_key(self) -> str | None:
        return self._held
