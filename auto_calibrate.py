# ============================================================
#  auto_calibrate.py  —  Avtomatik kalibratsiya
#
#  Maqsad:
#    Birinchi ishga tushganda yoki "kalib" buyrug'i berilganda
#    foydalanuvchidan 2 ta klik oladi va rang qiymatlarini
#    calibration.json ga saqlaydi.
#
#  Ishlatilishi:
#    python auto_calibrate.py          ← to'g'ridan-to'g'ri
#    yoki main.py ichida chaqiriladi
#
#  Jarayon:
#    1. "To'pni ol" → yashil marker paydo bo'ladi
#    2. Marker ustiga LMB bosing → rang olinadi
#    3. Natija calibration.json ga saqlanadi
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import cv2
import numpy as np
import time

from screen_capture import ScreenCapture
from config         import save_calibration, load_calibration, CALIB_FILE


# ──────────────────────────────────────────────────────────
#  Rang delta — kalibratsiya paytida qo'llaniladigan tolerans
# ──────────────────────────────────────────────────────────
DELTA_H = 18   # Hue  ±
DELTA_S = 50   # Saturation  (pastga)
DELTA_V = 60   # Value       (pastga)


class AutoCalibrator:

    def __init__(self):
        self.cap       = ScreenCapture()
        self.fw, self.fh = self.cap.size()
        self._clicks   = []
        self._frame    = None
        self.result    = None

    # ──────────────────────────────────────────────────────
    def _mouse_cb(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if self._frame is None:
            return

        # O'sha pikselning BGR → HSV
        bgr  = self._frame[y, x].astype(np.uint8)
        hsv  = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

        lo = (
            max(0,   h - DELTA_H),
            max(0,   s - DELTA_S),
            max(0,   v - DELTA_V),
        )
        hi = (
            min(180, h + DELTA_H),
            min(255, s + DELTA_S),
            255,
        )

        self._clicks.append({
            "xy": (x, y), "bgr": bgr.tolist(),
            "hsv": (h, s, v), "lo": lo, "hi": hi
        })
        idx = len(self._clicks)
        print(f"\n  [{idx}] ({x},{y})  HSV=({h},{s},{v})")
        print(f"       LOWER={lo}  UPPER={hi}")

    # ──────────────────────────────────────────────────────
    def run(self) -> dict | None:
        """
        Kalibratsiya oynasini ochadi va foydalanuvchidan
        yashil marker ustiga klik oladi.
        Qaytaradi: {"marker_lo": [...], "marker_hi": [...]}
        """
        print("\n" + "═" * 56)
        print("  AUTO KALIBRATSIYA")
        print("═" * 56)
        print("  1. DLS o'yinida to'pni OLING (LOW KICK holati)")
        print("  2. O'yinchi ustidagi YASHIL 📍 MARKER ga LMB bosing")
        print("  3. Tayyor bo'lgach ENTER yoki Q bosing")
        print("═" * 56)
        print("  3 soniyadan keyin oyna ochiladi...")
        time.sleep(3)

        cv2.namedWindow("Kalibratsiya", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Kalibratsiya", self._mouse_cb)

        while True:
            frame        = self.cap.capture()
            self._frame  = frame.copy()
            disp         = frame.copy()
            fh, fw       = disp.shape[:2]

            # Ko'rsatmalar
            step = len(self._clicks)
            if step == 0:
                msg   = "Yashil MARKER ustiga LMB bosing"
                color = (0, 240, 255)
            else:
                msg   = f"Olingan! ENTER yoki Q bosing  (yana bosish = qayta olish)"
                color = (0, 230, 0)

            # Yarim shaffof panel
            ov = disp.copy()
            cv2.rectangle(ov, (0, 0), (fw, 70), (0, 0, 0), -1)
            cv2.addWeighted(ov, 0.6, disp, 0.4, 0, disp)
            cv2.putText(disp, "KALIBRATSIYA", (10, 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(disp, msg, (10, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

            # Bosilgan nuqtalarni ko'rsat
            for i, c in enumerate(self._clicks):
                cx, cy = c["xy"]
                cv2.circle(disp, (cx, cy), 14, (0, 255, 80), 2)
                cv2.circle(disp, (cx, cy), 4,  (0, 255, 80), -1)

                # Marker rangini test mask sifatida ko'rsat
                test_lo  = np.array(c["lo"],  dtype=np.uint8)
                test_hi  = np.array(c["hi"],  dtype=np.uint8)
                hsv_full = cv2.cvtColor(
                    cv2.GaussianBlur(frame, (3,3), 0),
                    cv2.COLOR_BGR2HSV
                )
                mask = cv2.inRange(hsv_full, test_lo, test_hi)
                # Mask ni overlay sifatida yashil rang bilan ko'rsat
                green_ov = np.zeros_like(disp)
                green_ov[mask > 0] = (0, 255, 80)
                cv2.addWeighted(green_ov, 0.35, disp, 0.65, 0, disp)

            cv2.imshow("Kalibratsiya", disp)
            key = cv2.waitKey(1) & 0xFF

            # Enter yoki Q → saqlash
            if key in (13, ord('q'), ord('Q')):   # 13 = Enter
                if self._clicks:
                    break
                else:
                    print("  Hech narsa tanlanmadi, davom eting...")

            # ESC → bekor qilish
            if key == 27:
                print("  Kalibratsiya bekor qilindi.")
                cv2.destroyAllWindows()
                self.cap.release()
                return None

        cv2.destroyAllWindows()

        # Bir nechta klik bo'lsa, o'rtacha qiymat
        if len(self._clicks) > 1:
            lo = tuple(
                int(np.mean([c["lo"][i] for c in self._clicks]))
                for i in range(3)
            )
            hi = tuple(
                int(np.mean([c["hi"][i] for c in self._clicks]))
                for i in range(3)
            )
        else:
            lo = self._clicks[0]["lo"]
            hi = self._clicks[0]["hi"]

        calib = {"marker_lo": list(lo), "marker_hi": list(hi)}
        save_calibration(calib)

        print(f"\n  ✅ Kalibratsiya saqlandi: {CALIB_FILE}")
        print(f"     marker_lo = {lo}")
        print(f"     marker_hi = {hi}")
        print("═" * 56)

        self.cap.release()
        return calib


# ──────────────────────────────────────────────────────────
def run_calibration() -> dict | None:
    """main.py dan chaqiriladigan funksiya."""
    cal = AutoCalibrator()
    return cal.run()


# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = run_calibration()
    if result:
        print("\n  Endi  python main.py  bilan botni ishga tushirishingiz mumkin.")
