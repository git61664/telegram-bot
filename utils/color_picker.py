# ============================================================
#  utils/color_picker.py  —  Rang sozlash yordamchi vositasi
#
#  Ishlatilishi:
#    python utils/color_picker.py
#  Sichqoncha bilan ekrandagi rangni bosing → HSV qiymatlarini ko'ring
#  Bu qiymatlarni config.py'dagi BALL_HSV va GOAL_HSV ga kiriting.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from screen_capture import ScreenCapture


# Global o'zgaruvchilar
_frame_global = None


def mouse_callback(event, x, y, flags, param):
    """Sichqoncha bosilganda o'sha pikseldagi HSV qiymatini chiqaradi."""
    global _frame_global
    if event == cv2.EVENT_LBUTTONDOWN and _frame_global is not None:
        bgr_pixel = _frame_global[y, x]
        hsv_img   = cv2.cvtColor(
            np.uint8([[bgr_pixel]]), cv2.COLOR_BGR2HSV
        )
        h, s, v = hsv_img[0][0]
        print(f"  Koordinat: ({x}, {y})  |  BGR: {bgr_pixel}  |  HSV: ({h}, {s}, {v})")
        print(f"  config.py uchun:")
        delta = 20
        print(f"    LOWER = ({max(0,h-delta)}, {max(0,s-delta)}, {max(0,v-40)})")
        print(f"    UPPER = ({min(180,h+delta)}, {min(255,s+delta)}, 255)")
        print("-" * 50)


def main():
    global _frame_global
    cap = ScreenCapture()
    cv2.namedWindow("Color Picker")
    cv2.setMouseCallback("Color Picker", mouse_callback)

    print("=" * 50)
    print("  Rang tanlash vositasi")
    print("  Ekranda kerakli ob'ektga LMB bosing")
    print("  Chiqish: Q")
    print("=" * 50)

    while True:
        frame = cap.capture()
        _frame_global = frame
        cv2.imshow("Color Picker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
