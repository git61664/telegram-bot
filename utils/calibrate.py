# ============================================================
#  utils/calibrate.py
#
#  Yashil marker va B-tugma rangini kalibrlash vositasi.
#
#  Ishlatilishi:
#    python utils/calibrate.py
#
#  1. DLS o'yinida to'pni oling (LOW KICK holati)
#  2. Yashil 📍 marker ustiga sichqoncha bilan bosing
#     → Marker HSV qiymatlari chiqadi
#  3. B tugmasi ustidagi "LOW KICK" yozuviga bosing
#     → B tugmasi HSV qiymatlari chiqadi
#  4. Chiqarilgan qiymatlarni config.py ga ko'chiring
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from screen_capture import ScreenCapture

cap        = ScreenCapture()
frame_ref  = None
click_log  = []


def mouse_cb(event, x, y, flags, param):
    global frame_ref
    if event != cv2.EVENT_LBUTTONDOWN or frame_ref is None:
        return

    bgr = frame_ref[y, x].astype(np.uint8)
    hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

    d = 18   # delta
    lo = (max(0,   h-d), max(0,   s-40), max(0,   v-50))
    hi = (min(180, h+d), min(255, s+40), 255)

    entry = {
        "xy":  (x, y),
        "bgr": tuple(bgr.tolist()),
        "hsv": (h, s, v),
        "lo":  lo,
        "hi":  hi,
    }
    click_log.append(entry)
    idx = len(click_log)

    print(f"\n  [{idx}] ({x},{y})  BGR={entry['bgr']}  HSV=({h},{s},{v})")
    print(f"       config.py:")
    print(f"         LOWER = {lo}")
    print(f"         UPPER = {hi}")
    print()

    if idx == 1:
        print("  ✅ Marker rangi olindi.")
        print("  Endi B tugmasining 'LOW KICK' yozuviga bosing...")
    elif idx == 2:
        print("  ✅ B tugmasi rangi olindi.")
        _print_summary()


def _print_summary():
    if len(click_log) < 2:
        return
    m = click_log[0]
    b = click_log[1]
    print("\n" + "=" * 54)
    print("  config.py ga quyidagilarni ko'chiring:")
    print("=" * 54)
    print(f"# Yashil marker (to'p bizda belgisi)")
    print(f"MARKER_HSV_LOWER = {m['lo']}")
    print(f"MARKER_HSV_UPPER = {m['hi']}")
    print()
    print(f"# B tugmasi LOW KICK yozuvi")
    print(f"LOWKICK_LABEL_HSV_LOWER = {b['lo']}")
    print(f"LOWKICK_LABEL_HSV_UPPER = {b['hi']}")
    print("=" * 54)


def main():
    global frame_ref
    cv2.namedWindow("Calibrate")
    cv2.setMouseCallback("Calibrate", mouse_cb)

    print("=" * 54)
    print("  DLS Bot — Rang Kalibratsiyasi")
    print("=" * 54)
    print("  1. DLS'da TO'PNI OLING (LOW KICK holati bo'lsin)")
    print("  2. Yashil 📍 MARKER ustiga LMB bosing")
    print("  3. B tugmasidagi 'LOW KICK' yozuviga LMB bosing")
    print("  Chiqish: Q")
    print("=" * 54)

    while True:
        frame      = cap.capture()
        frame_ref  = frame.copy()
        disp       = frame_ref.copy()

        # Ko'rsatma
        step = len(click_log)
        msgs = [
            "1-qadam: Yashil MARKER ustiga bosing",
            "2-qadam: B tugmasi 'LOW KICK' yozuviga bosing",
            "Tayyor! Q bosib chiqing.",
        ]
        cv2.putText(disp, msgs[min(step, 2)], (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        # Bosilgan nuqtalar
        for i, e in enumerate(click_log):
            x, y = e["xy"]
            cv2.circle(disp, (x, y), 8, (0, 255, 0), 2)
            cv2.putText(disp, str(i+1), (x+10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)

        cv2.imshow("Calibrate", disp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if len(click_log) < 2:
        print("\n  Kalibratsiya tugallanmadi (2 ta nuqta kerak edi).")


if __name__ == "__main__":
    main()
