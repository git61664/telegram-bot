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
        self._held: set[str] = set()
        self._last: str        = "—"

    # ── ichki yordamchi ──────────────────────────────────────
    def _release(self):
        for key in tuple(self._held):
            try:
                pyautogui.keyUp(key)
            except Exception:
                pass
        self._held.clear()

    def _hold(self, key: str):
        if key not in self._held:
            pyautogui.keyDown(key)
            self._held.add(key)

    def _hold_movement(self):
        self._hold(KEY_FORWARD)
        self._hold(KEY_PRESSING)

    # ── ochiq metodlar ───────────────────────────────────────
    def press_forward(self):
        """W+B — doimiy oldinga yurish va pressing."""
        self._hold_movement()
        self._last = "W+B (forward/pressing)"

    def press_pressing(self):
        """W+B — doimiy oldinga yurish va pressing."""
        self._hold_movement()
        self._last = "W+B (forward/pressing)"

    def shoot(self):
        """W+B ni saqlagan holda J ni 200 ms bosadi."""
        self._hold_movement()
        pyautogui.keyDown(KEY_SHOOT)
        time.sleep(0.2)
        pyautogui.keyUp(KEY_SHOOT)
        self._last = "W+B + J (shoot)"

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
        return "+".join(sorted(self._held)) or None
