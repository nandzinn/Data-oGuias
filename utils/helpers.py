"""
utils/helpers.py
Funções utilitárias gerais para o DocStamp Pro.
"""

import re
import ctypes
import ctypes.wintypes
from datetime import datetime


def center_window_on_cursor_monitor(window, win_w: int, win_h: int):
    """
    Centraliza uma janela tkinter/customtkinter no monitor onde o cursor está.
    Funciona corretamente com múltiplos monitores, incluindo coordenadas negativas.
    """
    window.update_idletasks()

    # Obtém posição atual do cursor
    pt = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    cx, cy = pt.x, pt.y

    # Enumera todos os monitores
    monitors = []

    def _monitor_callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = lprcMonitor.contents
        monitors.append((r.left, r.top, r.right, r.bottom))
        return 1

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.c_long
    )
    ctypes.windll.user32.EnumDisplayMonitors(
        None, None, MONITORENUMPROC(_monitor_callback), 0
    )

    # Encontra o monitor que contém o cursor
    target = monitors[0] if monitors else (0, 0, 1920, 1080)
    for (ml, mt, mr, mb) in monitors:
        if ml <= cx < mr and mt <= cy < mb:
            target = (ml, mt, mr, mb)
            break

    ml, mt, mr, mb = target
    mon_w = mr - ml
    mon_h = mb - mt
    x = ml + (mon_w - win_w) // 2
    y = mt + (mon_h - win_h) // 2

    window.geometry(f"{win_w}x{win_h}+{x}+{y}")


# ── Paleta de cores padrão por funcionário ────────────────────────────────────
PRESET_COLORS = [
    {"name": "Laranja",   "hex": "#F97316"},
    {"name": "Azul",      "hex": "#2563EB"},
    {"name": "Verde",     "hex": "#16A34A"},
    {"name": "Vermelho",  "hex": "#DC2626"},
    {"name": "Roxo",      "hex": "#9333EA"},
    {"name": "Rosa",      "hex": "#EC4899"},
    {"name": "Ciano",     "hex": "#0891B2"},
    {"name": "Amarelo",   "hex": "#CA8A04"},
    {"name": "Grafite",   "hex": "#374151"},
    {"name": "Preto",     "hex": "#111827"},
]


def format_date_br(date_obj=None) -> str:
    """Formata uma data no padrão brasileiro DD/MM/AAAA."""
    if date_obj is None:
        date_obj = datetime.now()
    return date_obj.strftime("%d/%m/%Y")


def validate_email(email: str) -> bool:
    """Valida o formato de e-mail."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_hex_color(hex_color: str) -> bool:
    """Valida se uma string é uma cor hexadecimal válida."""
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    return bool(re.match(pattern, hex_color))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Valida a força da senha.
    Retorna (válido, mensagem).
    """
    if len(password) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"\d", password):
        return False, "A senha deve conter pelo menos um número."
    return True, "Senha válida."


def truncate_filename(filename: str, max_length: int = 40) -> str:
    """Trunca o nome do arquivo para exibição."""
    if len(filename) <= max_length:
        return filename
    name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
    truncated = name[:max_length - len(ext) - 4] + "..." + ("." + ext if ext else "")
    return truncated


def get_color_name(hex_color: str) -> str:
    """Retorna o nome da cor para um hex da paleta, ou o próprio hex."""
    for color in PRESET_COLORS:
        if color["hex"].lower() == hex_color.lower():
            return color["name"]
    return hex_color
