"""Bang mau, font, khung hinh, ham easing.

Mau doc truc tiep tu 21 keyframe cua video tham chieu (reference/keyframes).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

# ---------------------------------------------------------------- khung hinh
W, H = 1080, 1920          # 9:16 doc cho TikTok / Reels / Shorts
FPS = 30
SS = 2                     # supersample: ve o 2x roi thu nho -> chong rang cua

# Vung an toan: TikTok phu UI o day duoi va le phai
SAFE_TOP = 150
SAFE_BOTTOM = 1660
SAFE_X = 70

# Cac dai bo cuc doc. Day len cao hon giua khung: TikTok phu UI o day duoi,
# va mat nguoi xem nam o nua tren.
BAND_TITLE = (150, 430)      # tieu de
BAND_STAGE = (330, 1340)     # san dien: hop, mui ten, timeline...
BAND_CAPTION = (1250, 1410)  # phu de: dat gan noi dung, khong troi xuong day
# Duoi 1570 la vung TikTok phu UI (mo ta, nut) -> khong dat gi quan trong.

# ------------------------------------------------------------------- mau sac
PAPER = (250, 250, 245)
INK = (34, 34, 34)
RED = (211, 47, 47)
GREEN = (46, 125, 50)
BLUE = (21, 101, 192)
PURPLE = (94, 53, 177)
AMBER = (239, 154, 0)
PINK = (233, 30, 99)
GREY = (158, 158, 158)
GREY_DARK = (110, 110, 110)
DOT = (205, 205, 195)
HIGHLIGHT = (255, 237, 160)
STICKY_YELLOW = (253, 246, 205)
STICKY_BLUE = (219, 234, 249)
STICKY_GREEN = (216, 241, 221)

PALETTE = {
    "ink": INK, "red": RED, "green": GREEN, "blue": BLUE,
    "purple": PURPLE, "amber": AMBER, "pink": PINK,
    "grey": GREY, "grey_dark": GREY_DARK,
}
STICKY_TONES = {
    "yellow": (STICKY_YELLOW, AMBER),
    "blue": (STICKY_BLUE, BLUE),
    "green": (STICKY_GREEN, GREEN),
}


def color(name, default=INK):
    if isinstance(name, (tuple, list)):
        return tuple(name)
    return PALETTE.get(name, default)


# --------------------------------------------------------------------- font
_FONTS = {
    # vai tro         -> (file, truc wght neu la variable font)
    # --- theme whiteboard: chu viet tay
    "display": ("PlaypenSans[wght].ttf", 700),
    "display_bold": ("PlaypenSans[wght].ttf", 800),
    "body": ("PatrickHand-Regular.ttf", None),
    # --- theme brutalist: chu poster cuc dam + grotesque
    "slab": ("Phudu[wght].ttf", 800),
    "slab_black": ("Phudu[wght].ttf", 900),
    "grot": ("BeVietnamPro-SemiBold.ttf", None),
    "grot_black": ("BeVietnamPro-Black.ttf", None),
    "grot_med": ("BeVietnamPro-Medium.ttf", None),
    # --- dung chung
    "mono": ("JetBrainsMono[wght].ttf", 500),
}
_cache = {}


def font(role, size):
    """Tra ve ImageFont da nhan supersample. Cache theo (role, size)."""
    from PIL import ImageFont
    key = (role, size)
    if key in _cache:
        return _cache[key]
    fname, wght = _FONTS[role]
    f = ImageFont.truetype(os.path.join(FONT_DIR, fname), int(size * SS))
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass  # khong phai variable font hoac PIL thieu ho tro -> bo qua
    _cache[key] = f
    return f


# ------------------------------------------------------------------- easing
def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else (hi if v > hi else v)


def ease_out(p):
    """Cubic ease-out: nhanh luc dau, cham luc cuoi. Dung cho nét ve."""
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ease_in_out(p):
    p = clamp(p)
    return 3 * p * p - 2 * p * p * p


def s(v):
    """Nhan toa do theo supersample."""
    return int(round(v * SS))
