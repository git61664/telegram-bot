# ============================================================
#  utils/find_regions.py
#
#  Radar va B-tugma mintaqalarini vizual topish vositasi.
#
#  Ishlatilishi:
#    python utils/find_regions.py
#
#  Sichqoncha bilan ekranda:
#    - Avval radarning YUQORI-CHAP burchagini bosing
#    - Keyin radarning PASTKI-O'NG burchagini bosing
#    - Keyin UI B-tugmaning YUQORI-CHAP burchagini bosing
#    - Keyin UI B-tugmaning PASTKI-O'NG burchagini bosing
#
#  Natija: config.py uchun qiymatlar chiqariladi.
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from screen_capture import ScreenCapture

cap        = ScreenCapture()
fw, fh     = cap.get_dimensions()
points     = []
labels     = [
    "RADAR: yuqori-chap",
    "RADAR: pastki-o'ng",
    "UI B-tugma: yuqori-chap",
    "UI B-tugma: pastki-o'ng",
]
frame_copy = None


def mouse_cb(event, x, y, flags, param):
    global frame_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        idx = len(points)
        if idx < len(labels):
            points.append((x, y))
            print(f"  [{idx+1}/{len(labels)}] {labels[idx]} → ({x}, {y})")
            if len(points) == len(labels):
                print_config()


def print_config():
    (rx1, ry1), (rx2, ry2) = points[0], points[1]
    (ux1, uy1), (ux2, uy2) = points[2], points[3]

    r_cx = (rx1 + rx2) / 2 / fw
    r_cy = (ry1 + ry2) / 2 / fh
    r_w  = (rx2 - rx1) / fw
    r_h  = (ry2 - ry1) / fh

    u_x1 = rx1 / fw if ux1 == 0 else ux1 / fw
    u_x2 = rx2 / fw if ux2 == 0 else ux2 / fw
    u_y1 = uy1 / fh
    u_y2 = uy2 / fh

    print("\n" + "=" * 52)
    print("  config.py ga quyidagi qiymatlarni ko'chiring:")
    print("=" * 52)
    print(f"RADAR_CENTER_X = {r_cx:.3f}")
    print(f"RADAR_CENTER_Y = {r_cy:.3f}")
    print(f"RADAR_WIDTH    = {r_w:.3f}")
    print(f"RADAR_HEIGHT   = {r_h:.3f}")
    print()
    print(f"UI_BUTTON_B_REGION_X = ({ux1/fw:.3f}, {ux2/fw:.3f})")
    print(f"UI_BUTTON_B_REGION_Y = ({uy1/fh:.3f}, {uy2/fh:.3f})")
    print("=" * 52)


def main():
    global frame_copy
    cv2.namedWindow("Find Regions")
    cv2.setMouseCallback("Find Regions", mouse_cb)

    print("=" * 52)
    print("  Mintaqalarni topish vositasi")
    print("  LDPlayer'da DLS o'ynab tursin.")
    print()
    for i, lbl in enumerate(labels):
        print(f"  {i+1}. {lbl} — LMB bosing")
    print()
    print("  Chiqish: Q")
    print("=" * 52)

    colors = [(0,255,255), (0,255,255), (255,150,0), (255,150,0)]

    while True:
        frame      = cap.capture()
        frame_copy = frame.copy()

        # Bosib bo'lingan nuqtalarni ko'rsat
        for i, (px, py) in enumerate(points):
            cv2.circle(frame_copy, (px, py), 6, colors[i], -1)
            cv2.putText(frame_copy, str(i+1), (px+8, py),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 1)

        # Ko'rsatma
        if len(points) < len(labels):
            txt = f"Bosing: {labels[len(points)]}"
            cv2.putText(frame_copy, txt, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        cv2.imshow("Find Regions", frame_copy)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
