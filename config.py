# ============================================================
#  config.py  —  DLS Bot — Barcha sozlamalar
#  Rasmlardan o'lchangan aniq qiymatlar
# ============================================================

import json, os

# ============================================================
#  HOTKEY TUGMALARI
# ============================================================
KEY_BOT_START = 'f6'   # F6 = Bot yoqish
KEY_BOT_STOP  = 'f2'   # F2 = Bot o'chirish
KEY_QUIT      = 'f4'   # F4 = Dasturdan to'liq chiqish

# ============================================================
#  O'YIN TUGMALARI (LDPlayer keyboard mapping)
# ============================================================
KEY_FORWARD  = 'w'    # Joystick yuqori = oldinga
KEY_LEFT     = 'a'    # Joystick chap
KEY_RIGHT    = 'd'    # Joystick o'ng
KEY_PRESSING = 'b'    # PRESSURE / LOW KICK
KEY_SHOOT    = 'j'    # Zarba (A tugmasi)

# ============================================================
#  LDPLAYER
# ============================================================
WINDOW_TITLE    = "LDPlayer"
CAPTURE_REGION  = None    # None = auto topadi

# ============================================================
#  BOT ISHLASH TEZLIGI
# ============================================================
BOT_FPS = 30

# ============================================================
#  YASHIL MARKER (to'p bizda belgisi)
#  Rasmdan ko'ringan: yorqin yashil/moviy-yashil 📍
#  To'p bizda bo'lganda o'yinchi ustida paydo bo'ladi
# ============================================================
MARKER_HSV_LOWER = (45,  150, 150)
MARKER_HSV_UPPER = (95,  255, 255)

# Marker qidiriladigan zona (ekranga nisbatan 0.0-1.0)
MARKER_ZONE_X = (0.05, 0.95)
MARKER_ZONE_Y = (0.20, 0.82)

# Minimal/maksimal piksel soni (shovqin filtri)
MARKER_MIN_PX = 4
MARKER_MAX_PX = 500

# ============================================================
#  B TUGMASI YORLIG'I
#  O'ng pastda ~ x=0.79, y=0.69-0.78
#  "LOW KICK" = to'p bizda | "PRESSURE" = to'p yo'q
# ============================================================
BTN_B_X = (0.73, 0.88)
BTN_B_Y = (0.68, 0.80)

# LOW KICK — yorqin oq yozuv
LOWKICK_HSV_LOWER  = (0,   0,   210)
LOWKICK_HSV_UPPER  = (180, 35,  255)
LOWKICK_PX_THRESH  = 55    # Bu sondan ko'p oq piksel = LOW KICK

# ============================================================
#  DARVOZA ANIQLASH
#  Ekran yuqori qismida oq ramka
# ============================================================
GOAL_HSV_LOWER     = (0,   0,   190)
GOAL_HSV_UPPER     = (180, 40,  255)
GOAL_MIN_AREA      = 1800
GOAL_SEARCH_Y_MAX  = 0.58   # Faqat yuqori 58%

# Zarba uchun darvoza maydoni chegaralari
SHOOT_AREA_CLOSE   = 12000  # Juda yaqin → zarba
SHOOT_AREA_MEDIUM  =  5500  # O'rtacha   → zarba

# ============================================================
#  VAQT SOZLAMALARI
# ============================================================
SHOOT_HOLD_TIME  = 0.18
SHOOT_COOLDOWN   = 0.9
KEY_HOLD_TIME    = 0.05

# ============================================================
#  KALIBRATSIYA FAYLI
#  Auto-kalibrasiya natijasi shu faylga saqlanadi
# ============================================================
CALIB_FILE = os.path.join(os.path.dirname(__file__), "calibration.json")

def load_calibration():
    """Saqlangan kalibratsiya qiymatlarini yuklaydi."""
    if os.path.exists(CALIB_FILE):
        try:
            with open(CALIB_FILE, "r") as f:
                data = json.load(f)
            return data
        except Exception:
            pass
    return None

def save_calibration(data: dict):
    """Kalibratsiya qiymatlarini faylga saqlaydi."""
    with open(CALIB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
#  DEBUG
# ============================================================
DEBUG_SHOW_WINDOW = True
DEBUG_PRINT_INFO  = True
