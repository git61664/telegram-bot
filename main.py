# ============================================================
#  main.py  —  DLS Bot — Ishga tushirish nuqtasi
#
#  ISHLATILISHI:
#    python main.py           ← Oddiy ishga tushirish
#    python main.py --calib   ← Kalibratsiyani qayta o'tkazish
#    python main.py --no-gui  ← Debug oynasisiz (tezroq)
#
#  HOTKEY'LAR:
#    F6  →  Bot YOQISH
#    F2  →  Bot O'CHIRISH (pauza)
#    F4  →  Dasturdan chiqish
# ============================================================

import sys
import os
import argparse

# Loyiha root'ini path'ga qo'shish
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


# ──────────────────────────────────────────────────────────
#  Import tekshirish
# ──────────────────────────────────────────────────────────
def check_imports():
    missing = []
    libs = {
        "cv2":       "opencv-python",
        "pyautogui": "pyautogui",
        "numpy":     "numpy",
        "mss":       "mss",
        "keyboard":  "keyboard",
    }
    for mod, pkg in libs.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    return missing


# ──────────────────────────────────────────────────────────
BANNER = r"""
 ____  _     ____    ____   _____  _____
|  _ \| |   / ___|  | __ ) / _ \ \|_   _|
| | | | |   \___ \  |  _ \| | | | | | |
| |_| | |___ ___) | | |_) | |_| | | | |
|____/|_____|____/  |____/ \___/  |_| |

   Dream League Soccer  —  AUTO BOT
   LDPlayer emulyatori uchun
"""

def print_banner():
    print(BANNER)
    print("  ┌──────────────────────────────────────┐")
    print("  │  F6  =  Bot YOQISH                   │")
    print("  │  F2  =  Bot O'CHIRISH (pauza)         │")
    print("  │  F4  =  Dasturdan CHIQISH             │")
    print("  └──────────────────────────────────────┘")
    print()


# ──────────────────────────────────────────────────────────
def main():
    # Argumentlarni parse qilish
    parser = argparse.ArgumentParser(description="DLS Auto Bot")
    parser.add_argument("--calib",  action="store_true",
                        help="Kalibratsiyani qayta o'tkazish")
    parser.add_argument("--no-gui", action="store_true",
                        help="Debug oynasini yopish (tezroq ishlaydi)")
    args = parser.parse_args()

    print_banner()

    # ── 1. Kutubxonalarni tekshir ──
    missing = check_imports()
    if missing:
        print("  ❌ Quyidagi kutubxonalar o'rnatilmagan:")
        for m in missing:
            print(f"       pip install {m}")
        print()
        print("  Barcha kutubxonalarni o'rnatish:")
        print("       pip install -r requirements.txt")
        input("\n  ENTER bosib chiqing...")
        return

    # ── 2. Kutubxonalar import ──
    from config           import load_calibration, DEBUG_SHOW_WINDOW
    from auto_calibrate   import run_calibration

    # --no-gui bayrog'i
    if args.no_gui:
        import config as cfg
        cfg.DEBUG_SHOW_WINDOW = False
        print("  [!] Debug oyna o'chirildi")

    # ── 3. Kalibratsiya ──
    calib = load_calibration()

    if args.calib or calib is None:
        if calib is None:
            print("  ⚠  Kalibratsiya topilmadi — birinchi marta o'tkaziladi.")
        else:
            print("  ↺  Kalibratsiya qayta o'tkazilmoqda...")
        print()

        calib = run_calibration()

        if calib is None:
            print("  ❌ Kalibratsiya muvaffaqiyatsiz. Bot ishga tushmaydi.")
            input("  ENTER bosib chiqing...")
            return

        print("  ✅ Kalibratsiya muvaffaqiyatli!")
        print()
    else:
        print(f"  ✅ Kalibratsiya yuklandi:")
        print(f"     marker_lo = {calib['marker_lo']}")
        print(f"     marker_hi = {calib['marker_hi']}")
        print(f"  (Qayta kalibratsiya: python main.py --calib)")
        print()

    # ── 4. LDPlayer tekshirish ──
    print("  ⏳ LDPlayer oynasi qidirilmoqda...")
    from screen_capture import ScreenCapture
    sc = ScreenCapture()
    fw, fh = sc.size()
    sc.release()
    print(f"  ✅ Ekran hajmi: {fw} x {fh}")
    print()

    # ── 5. Botni ishga tushirish ──
    print("  ✅ Hamma narsa tayyor!")
    print()
    print("  Bot ishga tushmoqda...")
    print("  DLS o'yiniga o'ting va F6 bosing!")
    print()

    from bot import GameBot
    bot = GameBot(calib=calib)
    bot.run()

    print("\n  Xayr! 👋")


# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Windows'da administrator huquqi kerak (keyboard moduli uchun)
    import ctypes
    if os.name == "nt":
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("  ⚠  OGOHLANTIRISH: Administrator huquqi tavsiya etiladi.")
            print("     (keyboard moduli to'liq ishlashi uchun)")
            print("     CMD/PowerShell ni 'Run as Administrator' bilan oching.")
            print()

    main()
