# ============================================================
#  bot.py  —  Asosiy bot logikasi
#
#  HOTKEYS:
#    F1  →  Bot YOQISH
#    F2  →  Bot O'CHIRISH (pauza)
#    F4  →  Dasturdan TO'LIQ CHIQISH
#
#  STATE MACHINE:
#  ┌──────────────┬────────────────────────────┬───────────┐
#  │   HOLAT      │         SHART              │   AMAL    │
#  ├──────────────┼────────────────────────────┼───────────┤
#  │  PRESSURE    │ Marker yo'q + PRESSURE     │  B tugma  │
#  │  RUNNING     │ Marker bor / LOW KICK      │  W tugma  │
#  │  SHOOTING    │ LOW KICK + darvoza yaqin   │  J tugma  │
#  │  PAUSED      │ F2 bosilgan                │  hech nima│
#  └──────────────┴────────────────────────────┴───────────┘
# ============================================================

import time
import threading
import cv2
import keyboard

from config import (
    KEY_BOT_START, KEY_BOT_STOP, KEY_QUIT,
    BOT_FPS, SHOOT_AREA_MEDIUM, SHOOT_COOLDOWN,
    DEBUG_SHOW_WINDOW, DEBUG_PRINT_INFO,
)
from screen_capture import ScreenCapture
from vision         import VisionSystem, OwnershipInfo, GoalInfo
from controller     import Controller


# ============================================================
class GameBot:

    S_PRESSURE = "PRESSURE"
    S_RUNNING  = "RUNNING"
    S_SHOOTING = "SHOOTING"
    S_PAUSED   = "PAUSED"

    def __init__(self, vision: VisionSystem = None, calib: dict = None):
        print("[Bot] Ishga tayyorlanmoqda...")
        self.cap    = ScreenCapture()
        fw, fh      = self.cap.size()

        if vision is not None:
            self.vis = vision
        else:
            self.vis = VisionSystem(fw, fh)

        if calib:
            self.vis.apply_calibration(calib)

        self.ctrl          = Controller()
        self.state         = self.S_PAUSED
        self._active       = False      # F1/F2 boshqaradi
        self._running      = False      # Ana tsikl
        self._last_shoot   = 0.0
        self._frame_delay  = 1.0 / BOT_FPS
        self._lock         = threading.Lock()

        # Hotkey'larni ro'yxatdan o'tkazish
        keyboard.add_hotkey(KEY_BOT_START, self._on_start, suppress=True)
        keyboard.add_hotkey(KEY_BOT_STOP,  self._on_stop,  suppress=True)
        keyboard.add_hotkey(KEY_QUIT,      self._on_quit,  suppress=True)

        print(f"[Bot] Hotkey'lar tayyor:  "
              f"{KEY_BOT_START.upper()}=yoqish  "
              f"{KEY_BOT_STOP.upper()}=o'chirish  "
              f"{KEY_QUIT.upper()}=chiqish")

    # ──────────────────────────────────────────────────────
    #  HOTKEY HANDLERLARI  (boshqa threaddan chaqiriladi)
    # ──────────────────────────────────────────────────────
    def _on_start(self):
        with self._lock:
            if not self._active:
                self._active = True
                self.state   = self.S_PRESSURE
                print(f"\n  ▶  Bot YOQILDI  ({KEY_BOT_START.upper()})")

    def _on_stop(self):
        with self._lock:
            if self._active:
                self._active = False
                self.state   = self.S_PAUSED
                self.ctrl.release_all()
                print(f"\n  ■  Bot TO'XTATILDI  ({KEY_BOT_STOP.upper()})")

    def _on_quit(self):
        self._active  = False
        self._running = False
        self.ctrl.release_all()
        print(f"\n  ✕  Chiqilmoqda  ({KEY_QUIT.upper()})")

    # ──────────────────────────────────────────────────────
    #  STATE MACHINE
    # ──────────────────────────────────────────────────────
    def _decide(self, own: OwnershipInfo, goal: GoalInfo) -> str:
        if not own.owned:
            return self.S_PRESSURE

        now = time.time()
        if (goal.found
                and goal.area >= SHOOT_AREA_MEDIUM
                and goal.distance in ("close", "medium")
                and now - self._last_shoot >= SHOOT_COOLDOWN):
            return self.S_SHOOTING

        return self.S_RUNNING

    def _execute(self, new_state: str):
        if new_state == self.S_PRESSURE:
            self.ctrl.press_pressing()

        elif new_state == self.S_RUNNING:
            self.ctrl.press_forward()

        elif new_state == self.S_SHOOTING:
            self.ctrl.shoot()
            self._last_shoot = time.time()
            time.sleep(0.22)   # Zarba animatsiyasi

        self.state = new_state

    # ──────────────────────────────────────────────────────
    #  ASOSIY TSIKL
    # ──────────────────────────────────────────────────────
    def run(self):
        self._running = True
        print("=" * 58)
        print("  DLS BOT  —  tayyor")
        print(f"  {KEY_BOT_START.upper()} = YOQISH   "
              f"{KEY_BOT_STOP.upper()} = TO'XTATISH   "
              f"{KEY_QUIT.upper()} = CHIQISH")
        print("=" * 58)

        try:
            while self._running:
                t0 = time.time()

                frame = self.cap.capture()

                with self._lock:
                    active = self._active

                if active:
                    own  = self.vis.detect_ownership(frame)
                    goal = self.vis.detect_goal(frame)
                    ns   = self._decide(own, goal)
                    self._execute(ns)
                else:
                    own  = OwnershipInfo()
                    goal = GoalInfo()

                # ── Konsol logi ──
                if DEBUG_PRINT_INFO:
                    if active:
                        ball_s = "BIZDA✓" if own.owned else "YO'Q✗ "
                        goal_s = (f"{goal.distance:<6} {goal.direction:<7}"
                                  f" a={int(goal.area)}"
                                  if goal.found else "—              ")
                        print(
                            f"\r  [{self.state:<10}] "
                            f"ball={ball_s} ({own.method:<14}) | "
                            f"darvoza={goal_s} | "
                            f"{self.ctrl.last_action:<18}",
                            end="", flush=True
                        )
                    else:
                        print(
                            f"\r  [PAUSED]  "
                            f"F1 bosing → botni yoqish ...",
                            end="", flush=True
                        )

                # ── Debug oyna ──
                if DEBUG_SHOW_WINDOW:
                    dbg = self.vis.draw_debug(
                        frame, own, goal, self.state, active
                    )
                    cv2.imshow("DLS Bot", dbg)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('1'):      # oynada ham F1 o'rniga '1'
                        self._on_start()
                    elif key == ord('2'):    # oynada ham F2 o'rniga '2'
                        self._on_stop()
                    elif key == 27:          # ESC = chiqish
                        self._on_quit()

                # ── FPS cheklash ──
                dt = time.time() - t0
                sl = self._frame_delay - dt
                if sl > 0:
                    time.sleep(sl)

        except KeyboardInterrupt:
            print("\n  Ctrl+C bosildi.")
        finally:
            self._cleanup()

    # ──────────────────────────────────────────────────────
    def _cleanup(self):
        self._active  = False
        self._running = False
        self.ctrl.release_all()
        self.cap.release()
        cv2.destroyAllWindows()
        try:
            keyboard.remove_hotkey(KEY_BOT_START)
            keyboard.remove_hotkey(KEY_BOT_STOP)
            keyboard.remove_hotkey(KEY_QUIT)
        except Exception:
            pass
        print("\n  Barcha tugmalar qo'yib yuborildi.")
        print("=" * 58)
