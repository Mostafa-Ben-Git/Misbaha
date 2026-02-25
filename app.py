import ctypes
import customtkinter as ctk
from pynput import mouse, keyboard
import json
import os
import sys
import threading
import time
from datetime import datetime

try:
    import pystray
    from PIL import Image, ImageDraw

    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════
# PYINSTALLER BUILD SUPPORT
# ═══════════════════════════════════════════════════════════════════════════
if len(sys.argv) > 1 and sys.argv[1] == "build":
    try:
        import PyInstaller.__main__
    except ImportError:
        print("PyInstaller not found. Installing...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller.__main__

    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    icon_path = os.path.join(script_dir, "asset", "icon.ico")
    audio_path = os.path.join(script_dir, "asset", "audio.wav")

    pyinstaller_args = [
        script_path,
        "--onefile",
        "--windowed",
        f"--icon={icon_path}",
        "--add-data",
        f"{audio_path};asset",
        "--add-data",
        f"{icon_path};asset",
        "--name",
        "Misbaha",
        "--hidden-import",
        "pystray._win32",
        "--hidden-import",
        "PIL._tkinter_finder",
    ]
    print("Building with PyInstaller...")
    PyInstaller.__main__.run(pyinstaller_args)
    sys.exit(0)

# ─────────────────────────────────────────
# CONSTANTS & DHIKR DATABASE
# ─────────────────────────────────────────
DHIKR_LIST = [
    {
        "key": "subhanallah",
        "arabic": "سُبْحَانَ اللهِ",
        "translit": "Subhan Allah",
        "meaning": "Glory be to Allah",
        "target": 33,
    },
    {
        "key": "alhamdulillah",
        "arabic": "الْحَمْدُ لِلَّهِ",
        "translit": "Alhamdulillah",
        "meaning": "All praise is due to Allah",
        "target": 33,
    },
    {
        "key": "allahuakbar",
        "arabic": "اللهُ أَكْبَرُ",
        "translit": "Allahu Akbar",
        "meaning": "Allah is the Greatest",
        "target": 33,
    },
    {
        "key": "lailaha",
        "arabic": "لَا إِلَهَ إِلَّا اللهُ",
        "translit": "La ilaha illallah",
        "meaning": "There is no deity except Allah",
        "target": 100,
    },
    {
        "key": "subhanallahwb",
        "arabic": "سُبْحَانَ اللهِ وَبِحَمْدِهِ",
        "translit": "Subhan Allahi wa bihamdih",
        "meaning": "Glory & praise be to Allah",
        "target": 100,
    },
    {
        "key": "astaghfirullah",
        "arabic": "أَسْتَغْفِرُ اللهَ",
        "translit": "Astaghfirullah",
        "meaning": "I seek forgiveness from Allah",
        "target": 100,
    },
    {
        "key": "salawat",
        "arabic": "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ",
        "translit": "Allahumma salli ala Muhammad",
        "meaning": "O Allah, send blessings upon Muhammad ﷺ",
        "target": 100,
    },
    {
        "key": "hawqala",
        "arabic": "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللهِ",
        "translit": "La hawla wa la quwwata illa billah",
        "meaning": "No might except with Allah",
        "target": 33,
    },
    {
        "key": "hasbunallah",
        "arabic": "حَسْبُنَا اللهُ وَنِعْمَ الْوَكِيلُ",
        "translit": "Hasbunallahu wa ni'mal wakil",
        "meaning": "Allah is sufficient for us",
        "target": 33,
    },
    {
        "key": "subhanallahaz",
        "arabic": "سُبْحَانَ اللهِ الْعَظِيمِ",
        "translit": "Subhan Allahil Azim",
        "meaning": "Glory be to Allah, the Most Great",
        "target": 100,
    },
]

COMMON_TARGETS = [33, 99, 100, 500, 1000]

GREEN_DARK = "#059669"
GREEN_MID = "#10b981"
GREEN_LIGHT = "#d1fae5"
GREEN_BG = "#f0fdf4"
GREEN_DEEP = "#064e3b"
AMBER_BG = "#fef3c7"
AMBER_TEXT = "#92400e"
AMBER_DARK = "#78350f"
CARD_LIGHT = "white"
CARD_DARK = "#1e293b"
TEXT_MUTED = ("#6b7280", "#9ca3af")
BLUE = ("#3b82f6", "#2563eb")
BLUE_HOVER = ("#2563eb", "#1d4ed8")
RED = ("#ef4444", "#dc2626")
RED_HOVER = ("#dc2626", "#b91c1c")


# ═══════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "en": {
        "app_title": "Misbaha",
        "subtitle": "Digital Tasbih Counter",
        "change_dhikr": "🔄  Change Dhikr",
        "count_btn": "+ Count  (Middle Mouse / Spacebar)",
        "undo": "↩  Undo",
        "reset": "🔄  Reset",
        "total": "Total",
        "target": "Target",
        "set": "Set",
        "custom_target": "Custom target…",
        "active_shortcut": "Active Shortcut",
        "change": "Change",
        "sessions": "💾  Sessions",
        "save_current": "Save current",
        "no_sessions": "No saved sessions yet.",
        "count": "Count",
        "cycles": "Cycles",
        "elapsed": "Elapsed",
        "add_custom_dhikr": "➕  Add Custom Dhikr",
        "new_session": "🎴  New Session",
        "choose_dhikr": "Choose Dhikr",
        "select": "Select",
        "add_custom_title": "Add Custom Dhikr",
        "arabic_text": "Arabic text (required)",
        "transliteration": "Transliteration",
        "meaning": "Meaning",
        "target_count": "Target count",
        "save_select": "Save & Select",
        "choose_input": "Choose Input Method",
        "middle_mouse": "🖱️  Middle Mouse Button",
        "keyboard_shortcut": "⌨️  Keyboard Shortcut",
        "shortcut_hint": "e.g. Ctrl+Space, Alt+C, Ctrl+Shift+T",
        "press_shortcut": "Press your desired key combo\n(at least 2 keys)",
        "waiting": "Waiting…",
        "dark_mode": "🌙  Dark Mode",
        "light_mode": "☀️  Light Mode",
        "language": "Language",
        "load": "Load",
        "tray_show": "Show Misbaha",
        "tray_hide": "Hide to Tray",
        "tray_quit": "Quit",
        "tray_minimized": "Misbaha running in background",
        "tray_minimized_msg": "Click the tray icon to restore.",
        "cycle_done_title": "Cycle Complete! 🎉",
        "cycle_done_msg": "You completed a full round of \n{dhikr}.",
    },
    "ar": {
        "app_title": "مسبحة",
        "subtitle": "عداد التسبيح الرقمي",
        "change_dhikr": "🔄  تغيير الذكر",
        "count_btn": "+ عد  (الماوس الأوسط / مسافة)",
        "undo": "↩  تراجع",
        "reset": "🔄  إعادة تعيين",
        "total": "المجموع",
        "target": "الهدف",
        "set": "تعيين",
        "custom_target": "هدف مخصص…",
        "active_shortcut": "الاختصار النشط",
        "change": "تغيير",
        "sessions": "💾  الجلسات",
        "save_current": "حفظ الحالية",
        "no_sessions": "لا توجد جلسات محفوظة بعد.",
        "count": "العدد",
        "cycles": "الدورات",
        "elapsed": "المنقضي",
        "add_custom_dhikr": "➕  إضافة ذكر مخصص",
        "new_session": "🎴  جلسة جديدة",
        "choose_dhikr": "اختيار الذكر",
        "select": "اختيار",
        "add_custom_title": "إضافة ذكر مخصص",
        "arabic_text": "النص العربي (مطلوب)",
        "transliteration": "النطق",
        "meaning": "المعنى",
        "target_count": "عدد الهدف",
        "save_select": "حفظ واختيار",
        "choose_input": "اختيار طريقة الإدخال",
        "middle_mouse": "🖱️  زر الماوس الأوسط",
        "keyboard_shortcut": "⌨️  اختصار لوحة المفاتيح",
        "shortcut_hint": "مثال: Ctrl+Space, Alt+C, Ctrl+Shift+T",
        "press_shortcut": "اضغط المفاتيح المطلوبة\n(مفتاحان على الأقل)",
        "waiting": "في الانتظار…",
        "dark_mode": "🌙  الوضع المظلم",
        "light_mode": "☀️  الوضع الفاتح",
        "language": "اللغة",
        "load": "تحميل",
        "tray_show": "إظهار المسبحة",
        "tray_hide": "إخفاء في الحاوية",
        "tray_quit": "خروج",
        "tray_minimized": "المسبحة تعمل في الخلفية",
        "tray_minimized_msg": "انقر على أيقونة الحاوية للاستعادة.",
        "cycle_done_title": "اكتملت الدورة! 🎉",
        "cycle_done_msg": "لقد أتممت دورة كاملة من \n{dhikr}.",
    },
}


def get_config_path():
    config_dir = os.path.join(os.path.expanduser("~"), ".tasbih")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return os.path.join(config_dir, "tasbih_settings.json")


def get_resource_path(filename):
    """Get path to bundled resource (works for both dev and PyInstaller)."""
    if getattr(sys, "frozen", False):
        # Running as compiled .exe - files are in temp directory (sys._MEIPASS)
        base_path = sys._MEIPASS
    else:
        # Running as script - files are relative to this script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


def play_beep():
    """Play beep sound with fallback to asset/audio.wav."""

    def _play():
        if sys.platform == "win32":

            try:
                import winsound

                audio_path = get_resource_path("asset/audio.wav")
                if os.path.exists(audio_path):
                    winsound.PlaySound(
                        audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                    return
            except Exception:
                pass

        try:
            print("\a", end="", flush=True)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()


# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────
class TasbihCounter:
    def __init__(self):
        # Initialize state before loading settings
        self.count = 0
        self.target = 33
        self.cycles = 0
        self.total = 0
        self.start_ts = time.time()
        self.current_dhikr = DHIKR_LIST[0].copy()
        self.custom_dhikr = {}
        self.shortcut_type = "mouse"
        self.current_shortcut = "Middle Mouse"
        self.mouse_listener = None
        self.keyboard_listener = None
        self.sessions = []
        self.current_session = None
        self._anim_job = None
        self._save_job = None
        self.lang = "en"
        self.dark_mode = True
        self.tray_icon = None
        self._tray_thread = None
        self._window_hidden = False  # tracks whether window is minimized to tray

        # Load settings before UI setup
        self.load_settings()

        # Apply theme
        ctk.set_appearance_mode("dark" if self.dark_mode else "light")
        ctk.set_default_color_theme("green")

        # Create window
        self.app = ctk.CTk()
        self.app.title("مسبحة — Misbaha")
        self.app.geometry("460x820")
        self.app.minsize(420, 600)
        self.app.resizable(True, True)
        # Set icon if available
        try:
            icon_path = get_resource_path("asset/icon.ico")
            if os.path.exists(icon_path):
                self.app.iconbitmap(icon_path)
        except Exception:
            pass  # Continue without icon if it fails

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TasbihCounter")

        # Build UI
        self.build_ui()
        self.app.update()
        self.start_listener()
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Minimize → hide to tray
        self.app.bind("<Unmap>", self._on_minimize)
        self._tick()
        # Start system tray in background
        self.setup_tray()

    # ════════════════════════════════════════
    # TRANSLATION
    # ════════════════════════════════════════
    def t(self, key):
        """Get translated string for key."""
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)

    def set_language(self, lang):
        """Change language and rebuild UI."""
        self.lang = lang
        self.save_settings()
        self.build_ui()

    # ════════════════════════════════════════
    # THEME
    # ════════════════════════════════════════
    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        ctk.set_appearance_mode("dark" if self.dark_mode else "light")
        self.save_settings()
        self.build_ui()

    # ══════════════════════════════════════
    # BUILD UI
    # ══════════════════════════════════════
    def build_ui(self):
        for w in self.app.winfo_children():
            w.destroy()

        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=1)

        root = ctk.CTkFrame(self.app, fg_color=(GREEN_BG, GREEN_DEEP), corner_radius=0)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        # ── Header ─────────────────────────
        self._build_header(root)

        # ── Scrollable content ─────────────
        scroll = ctk.CTkScrollableFrame(root, fg_color="transparent", corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        self._build_dhikr_card(scroll)
        self._build_counter_card(scroll)
        self._build_progress_card(scroll)
        self._build_target_row(scroll)
        self._build_shortcut_card(scroll)
        self._build_sessions_card(scroll)
        self._build_bottom_buttons(scroll)

    # ── Header ─────────────────────────────
    def _build_header(self, parent):
        hdr = ctk.CTkFrame(
            parent, fg_color=(GREEN_MID, GREEN_DARK), corner_radius=0, height=90
        )
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)
        hdr.grid_columnconfigure(1, weight=0)

        # Title container (left side)
        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.grid(row=0, column=0, rowspan=2, pady=(8, 0), sticky="w", padx=14)

        ctk.CTkLabel(
            title_frame, text="مسبحة", font=("Arial", 42, "bold"), text_color="white"
        ).pack()
        ctk.CTkLabel(
            title_frame,
            text=self.t("subtitle"),
            font=("Segoe UI", 12),
            text_color=(GREEN_LIGHT, GREEN_LIGHT),
        ).pack()

        # Controls (right side)
        ctrl_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        ctrl_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=14)

        # Language toggle
        lang_btn = ctk.CTkButton(
            ctrl_frame,
            text="AR" if self.lang == "en" else "EN",
            font=("Segoe UI", 11, "bold"),
            width=40,
            height=28,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            corner_radius=6,
            command=lambda: self.set_language("ar" if self.lang == "en" else "en"),
        )
        lang_btn.pack(pady=(0, 4))

        # Theme toggle
        theme_btn = ctk.CTkButton(
            ctrl_frame,
            text=self.t("light_mode") if self.dark_mode else self.t("dark_mode"),
            font=("Segoe UI", 10),
            width=100,
            height=26,
            fg_color=GREEN_DARK,
            hover_color=GREEN_MID,
            corner_radius=6,
            command=self.toggle_theme,
        )
        theme_btn.pack()

    # ── Current Dhikr card ─────────────────
    def _build_dhikr_card(self, parent):
        card = self._card(parent, row=0)
        card.grid_columnconfigure(0, weight=1)

        d = self.current_dhikr
        ctk.CTkLabel(
            card,
            text=d["arabic"],
            font=("Arial", 28, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
            justify="center",
        ).grid(row=0, column=0, pady=(12, 2), padx=14)
        ctk.CTkLabel(
            card,
            text=d["translit"],
            font=("Segoe UI", 13, "italic"),
            text_color=(GREEN_DARK, GREEN_MID),
        ).grid(row=1, column=0, pady=0)
        ctk.CTkLabel(
            card, text=d["meaning"], font=("Segoe UI", 11), text_color=TEXT_MUTED
        ).grid(row=2, column=0, pady=(0, 10))

        ctk.CTkButton(
            card,
            text=self.t("change_dhikr"),
            font=("Segoe UI", 12, "bold"),
            height=34,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            corner_radius=8,
            command=self.open_dhikr_picker,
        ).grid(row=3, column=0, padx=14, pady=(0, 12), sticky="ew")

    # ── Big counter card ───────────────────
    def _build_counter_card(self, parent):
        card = self._card(parent, row=1)
        card.grid_columnconfigure((0, 1), weight=1)

        in_cycle = self._in_cycle()
        self.count_label = ctk.CTkLabel(
            card,
            text=str(in_cycle),
            font=("Arial", 90, "bold"),
            text_color=(GREEN_MID, GREEN_MID),
        )
        self.count_label.grid(row=0, column=0, columnspan=2, pady=(10, 4))

        self.total_label = ctk.CTkLabel(
            card,
            text=f"{self.t('total')}: {self.total}",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
        )
        self.total_label.grid(row=1, column=0, columnspan=2, pady=(0, 6))

        ctk.CTkButton(
            card,
            text=self.t("count_btn"),
            font=("Segoe UI", 13, "bold"),
            height=48,
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=10,
            command=self.increment,
        ).grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 4), sticky="ew")

        ctk.CTkButton(
            card,
            text=self.t("undo"),
            font=("Segoe UI", 12, "bold"),
            height=38,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            corner_radius=9,
            command=self.undo,
        ).grid(row=3, column=0, padx=(12, 4), pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            card,
            text=self.t("reset"),
            font=("Segoe UI", 12, "bold"),
            height=38,
            fg_color=RED,
            hover_color=RED_HOVER,
            corner_radius=9,
            command=self.reset,
        ).grid(row=3, column=1, padx=(4, 12), pady=(0, 12), sticky="ew")

    # ── Progress card ──────────────────────
    def _build_progress_card(self, parent):
        card = self._card(parent, row=2)
        card.grid_columnconfigure(0, weight=1)

        in_cycle = self._in_cycle()
        pct = in_cycle / self.target if self.target else 0

        self.progress_bar = ctk.CTkProgressBar(
            card,
            height=16,
            corner_radius=8,
            progress_color=(GREEN_MID, GREEN_DARK),
            fg_color=(GREEN_LIGHT, GREEN_DEEP),
        )
        self.progress_bar.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="ew")
        self.progress_bar.set(pct)

        self.progress_label = ctk.CTkLabel(
            card,
            text=f"{in_cycle} / {self.target}",
            font=("Segoe UI", 13, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
        )
        self.progress_label.grid(row=1, column=0, pady=0)

        self.cycles_label = ctk.CTkLabel(
            card,
            text=f"{self.t('cycles')}: {self.cycles}   •   {self.t('elapsed')}: 0m",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
        )
        self.cycles_label.grid(row=2, column=0, pady=(2, 12))

    # ── Target row ─────────────────────────
    def _build_target_row(self, parent):
        card = self._card(parent, row=3)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=self.t("target"),
            font=("Segoe UI", 11, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
        ).grid(row=0, column=0, pady=(10, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        for i, t in enumerate(COMMON_TARGETS):
            row.grid_columnconfigure(i, weight=1)
            active = t == self.target
            ctk.CTkButton(
                row,
                text=str(t),
                width=52,
                height=34,
                font=("Segoe UI", 12, "bold"),
                fg_color=(
                    GREEN_MID if active else "gray80",
                    GREEN_DARK if active else "gray30",
                ),
                hover_color=(GREEN_DARK, "#047857"),
                corner_radius=8,
                command=lambda t=t: self.set_target(t),
            ).grid(row=0, column=i, padx=3)

        custom_row = ctk.CTkFrame(card, fg_color="transparent")
        custom_row.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        custom_row.grid_columnconfigure(0, weight=1)

        self.custom_target_entry = ctk.CTkEntry(
            custom_row, placeholder_text=self.t("custom_target"), height=32
        )
        self.custom_target_entry.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            custom_row,
            text=self.t("set"),
            width=50,
            height=32,
            font=("Segoe UI", 11, "bold"),
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=8,
            command=self.set_custom_target,
        ).grid(row=0, column=1)

    # ── Shortcut card ──────────────────────
    def _build_shortcut_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=(AMBER_BG, "#92400e"), corner_radius=12)
        card.grid(row=4, column=0, sticky="ew", padx=14, pady=5)
        card.grid_columnconfigure(1, weight=1)

        icon = "🖱️" if self.shortcut_type == "mouse" else "⌨️"
        ctk.CTkLabel(card, text=icon, font=("Arial", 22)).grid(
            row=0, column=0, padx=(14, 8), pady=10
        )

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(
            info,
            text=self.t("active_shortcut"),
            font=("Segoe UI", 9),
            text_color=(AMBER_TEXT, AMBER_BG),
        ).grid(row=0, column=0, sticky="w")
        self.shortcut_label = ctk.CTkLabel(
            info,
            text=self.current_shortcut,
            font=("Segoe UI", 12, "bold"),
            text_color=(AMBER_DARK, "#fde68a"),
        )
        self.shortcut_label.grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            card,
            text=self.t("change"),
            width=64,
            height=30,
            font=("Segoe UI", 11, "bold"),
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=7,
            command=self.open_shortcut_settings,
        ).grid(row=0, column=2, padx=(6, 12))

    # ── Sessions card ──────────────────────
    def _build_sessions_card(self, parent):
        card = self._card(parent, row=5)
        card.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hdr,
            text=self.t("sessions"),
            font=("Segoe UI", 12, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            hdr,
            text=self.t("save_current"),
            width=100,
            height=28,
            font=("Segoe UI", 11, "bold"),
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=7,
            command=self.save_session,
        ).grid(row=0, column=1)

        self.session_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.session_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        self.session_frame.grid_columnconfigure(0, weight=1)
        self._refresh_session_list()

    def _refresh_session_list(self):
        for w in self.session_frame.winfo_children():
            w.destroy()

        if not self.sessions:
            ctk.CTkLabel(
                self.session_frame,
                text=self.t("no_sessions"),
                font=("Segoe UI", 11),
                text_color=TEXT_MUTED,
            ).grid(row=0, column=0, pady=4)
            return

        for i, s in enumerate(reversed(self.sessions[-10:])):  # show last 10
            idx = len(self.sessions) - 1 - i
            row_f = ctk.CTkFrame(
                self.session_frame, fg_color=("gray92", "gray20"), corner_radius=8
            )
            row_f.grid(row=i, column=0, sticky="ew", pady=2)
            row_f.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row_f,
                text=s["dhikr_arabic"][:18]
                + ("…" if len(s["dhikr_arabic"]) > 18 else ""),
                font=("Arial", 13, "bold"),
                text_color=(GREEN_DARK, GREEN_MID),
                width=140,
                anchor="w",
            ).grid(row=0, column=0, padx=(10, 4), pady=4)

            ctk.CTkLabel(
                row_f,
                text=f"{self.t('count')}: {s['count']}  {self.t('cycles')}: {s['cycles']}  {s['date']}",
                font=("Segoe UI", 10),
                text_color=TEXT_MUTED,
            ).grid(row=0, column=1, sticky="w")

            ctk.CTkButton(
                row_f,
                text=self.t("load"),
                width=50,
                height=26,
                font=("Segoe UI", 10, "bold"),
                fg_color=BLUE,
                hover_color=BLUE_HOVER,
                corner_radius=6,
                command=lambda s=s: self.load_session(s),
            ).grid(row=0, column=2, padx=4)

            ctk.CTkButton(
                row_f,
                text="✕",
                width=26,
                height=26,
                font=("Segoe UI", 10, "bold"),
                fg_color=RED,
                hover_color=RED_HOVER,
                corner_radius=6,
                command=lambda idx=idx: self.delete_session(idx),
            ).grid(row=0, column=3, padx=(0, 6))

    # ── Bottom buttons ─────────────────────
    def _build_bottom_buttons(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=6, column=0, sticky="ew", padx=14, pady=(4, 18))
        row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            row,
            text=self.t("add_custom_dhikr"),
            font=("Segoe UI", 12, "bold"),
            height=40,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            corner_radius=9,
            command=self.open_add_dhikr,
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            row,
            text=self.t("new_session"),
            font=("Segoe UI", 12, "bold"),
            height=40,
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=9,
            command=self.new_session,
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    # ── Helper: plain card ─────────────────
    def _card(self, parent, row):
        c = ctk.CTkFrame(
            parent,
            fg_color=(CARD_LIGHT, CARD_DARK),
            corner_radius=14,
            border_width=1,
            border_color=(GREEN_LIGHT, GREEN_DEEP),
        )
        c.grid(row=row, column=0, sticky="ew", padx=14, pady=5)
        c.grid_columnconfigure(0, weight=1)
        return c

    # ══════════════════════════════════════
    # COUNTER LOGIC
    # ══════════════════════════════════════
    def _in_cycle(self):
        if self.target <= 0:
            return self.count
        v = self.count % self.target
        return self.target if (v == 0 and self.count > 0) else v

    def increment(self, event=None):
        self.count += 1
        self.total += 1
        old_cycles = self.cycles
        self.cycles = self.count // self.target if self.target else 0
        self._update_display(cycle_done=(self.cycles > old_cycles))
        self._debounced_save()
        self._flash_count()

    def undo(self):
        if self.count > 0:
            self.count -= 1
            self.total = max(0, self.total - 1)
            self.cycles = self.count // self.target if self.target else 0
            self._update_display()
            self._debounced_save()

    def reset(self):
        self.count = 0
        self.cycles = 0
        self.total = 0
        self.start_ts = time.time()
        self._update_display()
        self.save_settings()

    def set_target(self, t):
        self.target = t
        self.count = 0
        self.cycles = 0
        self._update_display()
        self.save_settings()
        self.build_ui()

    def set_custom_target(self):
        try:
            t = int(self.custom_target_entry.get())
            if t > 0:
                self.set_target(t)
        except ValueError:
            pass

    # ══════════════════════════════════════
    # DISPLAY UPDATE
    # ══════════════════════════════════════
    def _update_display(self, cycle_done=False):
        in_cycle = self._in_cycle()
        pct = in_cycle / self.target if self.target else 0

        self.count_label.configure(text=str(in_cycle))
        self.total_label.configure(text=f"{self.t('total')}: {self.total}")
        self.progress_bar.set(pct)
        self.progress_label.configure(text=f"{in_cycle} / {self.target}")
        self._update_cycle_label()

        if cycle_done:
            self._animate_cycle_complete()
            if self._window_hidden and TRAY_AVAILABLE and self.tray_icon:
                # App is in background → use tray notification (its sound = the alert)
                title = self.t("cycle_done_title")
                msg = self.t("cycle_done_msg").format(
                    dhikr=self.current_dhikr["arabic"]
                )
                threading.Thread(
                    target=self.tray_icon.notify,
                    args=(msg, title),
                    daemon=True,
                ).start()
            else:
                # App is visible → play custom beep only
                threading.Thread(target=play_beep, daemon=True).start()

    def _update_cycle_label(self):
        elapsed = int((time.time() - self.start_ts) / 60)
        try:
            self.cycles_label.configure(
                text=f"{self.t('cycles')}: {self.cycles}   •   {self.t('elapsed')}: {elapsed}m"
            )
        except Exception:
            pass

    def _tick(self):
        """Update elapsed time every 30 s."""
        self._update_cycle_label()
        self.app.after(30_000, self._tick)

    # ── Animations ─────────────────────────
    def _flash_count(self):
        if self._anim_job:
            self.app.after_cancel(self._anim_job)
        self.count_label.configure(text_color=("#047857", "#047857"))
        self._anim_job = self.app.after(
            220, lambda: self.count_label.configure(text_color=(GREEN_MID, GREEN_MID))
        )

    def _animate_cycle_complete(self):
        orig = self.progress_bar.cget("progress_color")
        flash = ("#fbbf24", "#d97706")

        def step(n=0):
            if n < 6:
                self.progress_bar.configure(
                    progress_color=flash if n % 2 == 0 else orig
                )
                self.app.after(90, lambda: step(n + 1))
            else:
                self.progress_bar.configure(progress_color=orig)

        step()

    # ══════════════════════════════════════
    # SESSIONS
    # ══════════════════════════════════════
    def save_session(self):
        s = {
            "dhikr_key": self.current_dhikr["key"],
            "dhikr_arabic": self.current_dhikr["arabic"],
            "count": self.count,
            "cycles": self.cycles,
            "total": self.total,
            "target": self.target,
            "date": datetime.now().strftime("%d/%m %H:%M"),
        }
        self.sessions.append(s)
        self.save_settings()
        self._refresh_session_list()

    def load_session(self, s):
        # find dhikr
        found = next((d for d in DHIKR_LIST if d["key"] == s.get("dhikr_key")), None)
        if found:
            self.current_dhikr = found.copy()
        self.count = s["count"]
        self.cycles = s["cycles"]
        self.total = s.get("total", s["count"])
        self.target = s["target"]
        self.start_ts = time.time()
        self.save_settings()
        self.build_ui()

    def delete_session(self, idx):
        if 0 <= idx < len(self.sessions):
            self.sessions.pop(idx)
            self.save_settings()
            self._refresh_session_list()

    def new_session(self):
        self.count = 0
        self.cycles = 0
        self.total = 0
        self.start_ts = time.time()
        self._update_display()
        self.save_settings()

    # ══════════════════════════════════════
    # DHIKR PICKER
    # ══════════════════════════════════════
    def open_dhikr_picker(self):
        win = ctk.CTkToplevel(self.app)
        win.title(self.t("choose_dhikr"))
        win.geometry("420x560")
        win.transient(self.app)
        win.grab_set()
        self._center(win, 420, 560)

        scroll = ctk.CTkScrollableFrame(win, fg_color=(GREEN_BG, GREEN_DEEP))
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            scroll,
            text=self.t("choose_dhikr"),
            font=("Segoe UI", 16, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
        ).grid(row=0, column=0, pady=(14, 8))

        all_dhikr = DHIKR_LIST + list(self.custom_dhikr.values())
        for i, d in enumerate(all_dhikr):
            card = ctk.CTkFrame(
                scroll,
                fg_color=(CARD_LIGHT, CARD_DARK),
                corner_radius=10,
                border_width=1,
                border_color=(GREEN_LIGHT, GREEN_DEEP),
            )
            card.grid(row=i + 1, column=0, sticky="ew", padx=12, pady=4)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card,
                text=d["arabic"],
                font=("Arial", 18, "bold"),
                text_color=(GREEN_DARK, GREEN_MID),
                width=140,
                anchor="center",
            ).grid(row=0, column=0, rowspan=2, padx=(10, 6), pady=8)

            ctk.CTkLabel(
                card,
                text=d["translit"],
                font=("Segoe UI", 11, "italic"),
                text_color=(GREEN_DARK, GREEN_MID),
                anchor="w",
            ).grid(row=0, column=1, sticky="w", pady=(8, 0))
            ctk.CTkLabel(
                card,
                text=f"{d['meaning']} — ×{d['target']}",
                font=("Segoe UI", 10),
                text_color=TEXT_MUTED,
                anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(0, 8))

            ctk.CTkButton(
                card,
                text=self.t("select"),
                width=60,
                height=28,
                font=("Segoe UI", 11, "bold"),
                fg_color=(GREEN_MID, GREEN_DARK),
                hover_color=(GREEN_DARK, "#047857"),
                corner_radius=7,
                command=lambda d=d: [self._select_dhikr(d), win.destroy()],
            ).grid(row=0, column=2, rowspan=2, padx=(4, 10))

    def _select_dhikr(self, d):
        self.current_dhikr = d.copy()
        self.target = d["target"]
        self.count = 0
        self.cycles = 0
        self.save_settings()
        self.build_ui()

    # ══════════════════════════════════════
    # ADD CUSTOM DHIKR
    # ══════════════════════════════════════
    def open_add_dhikr(self):
        win = ctk.CTkToplevel(self.app)
        win.title(self.t("add_custom_title"))
        win.geometry("400x420")
        win.transient(self.app)
        win.grab_set()
        self._center(win, 400, 420)

        frame = ctk.CTkFrame(win, fg_color=(GREEN_BG, GREEN_DEEP))
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text=self.t("add_custom_title"),
            font=("Segoe UI", 16, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
        ).grid(row=0, column=0, pady=(0, 14))

        fields = [
            (self.t("arabic_text"), "arabic"),
            (self.t("transliteration"), "translit"),
            (self.t("meaning"), "meaning"),
        ]
        entries = {}
        for r, (label, key) in enumerate(fields, start=1):
            ctk.CTkLabel(
                frame,
                text=label,
                font=("Segoe UI", 11, "bold"),
                text_color=(GREEN_DARK, GREEN_MID),
                anchor="w",
            ).grid(row=r * 2 - 1, column=0, sticky="w")
            e = ctk.CTkEntry(frame, height=34)
            e.grid(row=r * 2, column=0, sticky="ew", pady=(0, 8))
            entries[key] = e

        ctk.CTkLabel(
            frame,
            text=self.t("target_count"),
            font=("Segoe UI", 11, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
            anchor="w",
        ).grid(row=7, column=0, sticky="w")
        target_e = ctk.CTkEntry(frame, height=34)
        target_e.insert(0, "33")
        target_e.grid(row=8, column=0, sticky="ew", pady=(0, 14))

        def save():
            arabic = entries["arabic"].get().strip()
            if not arabic:
                return
            try:
                t = int(target_e.get())
            except ValueError:
                t = 33
            key = f"custom_{arabic[:10]}"
            d = {
                "key": key,
                "arabic": arabic,
                "translit": entries["translit"].get().strip(),
                "meaning": entries["meaning"].get().strip(),
                "target": t,
            }
            self.custom_dhikr[key] = d
            self._select_dhikr(d)
            win.destroy()

        ctk.CTkButton(
            frame,
            text=self.t("save_select"),
            height=42,
            font=("Segoe UI", 13, "bold"),
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=10,
            command=save,
        ).grid(row=9, column=0, sticky="ew")

    # ══════════════════════════════════════
    # SHORTCUT SETTINGS
    # ══════════════════════════════════════
    def open_shortcut_settings(self):
        win = ctk.CTkToplevel(self.app)
        win.title(self.t("change"))
        win.geometry("380x320")
        win.transient(self.app)
        win.grab_set()
        self._center(win, 380, 320)

        frame = ctk.CTkFrame(win, fg_color=(GREEN_BG, GREEN_DEEP))
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text=self.t("choose_input"),
            font=("Segoe UI", 16, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
        ).grid(row=0, column=0, pady=(0, 18))

        ctk.CTkButton(
            frame,
            text=self.t("middle_mouse"),
            font=("Segoe UI", 14, "bold"),
            height=56,
            fg_color=(GREEN_MID, GREEN_DARK),
            hover_color=(GREEN_DARK, "#047857"),
            corner_radius=12,
            command=lambda: self._set_mouse(win),
        ).grid(row=1, column=0, sticky="ew", pady=6)

        ctk.CTkLabel(
            frame, text="— or —", font=("Segoe UI", 11), text_color=TEXT_MUTED
        ).grid(row=2, column=0, pady=4)

        ctk.CTkButton(
            frame,
            text=self.t("keyboard_shortcut"),
            font=("Segoe UI", 14, "bold"),
            height=56,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            corner_radius=12,
            command=lambda: self._prompt_keyboard(win),
        ).grid(row=3, column=0, sticky="ew", pady=6)

        ctk.CTkLabel(
            frame,
            text=self.t("shortcut_hint"),
            font=("Segoe UI", 10),
            text_color=TEXT_MUTED,
        ).grid(row=4, column=0, pady=(14, 0))

    def _set_mouse(self, win):
        self.shortcut_type = "mouse"
        self.current_shortcut = "Middle Mouse"
        self.save_settings()
        self.start_listener()
        win.destroy()
        self.build_ui()

    def _prompt_keyboard(self, parent_win):
        parent_win.destroy()
        win = ctk.CTkToplevel(self.app)
        win.title(self.t("change"))
        win.geometry("340x180")
        win.transient(self.app)
        win.grab_set()
        self._center(win, 340, 180)

        frame = ctk.CTkFrame(win, fg_color=(GREEN_BG, GREEN_DEEP))
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=self.t("press_shortcut"),
            font=("Segoe UI", 13, "bold"),
            text_color=(GREEN_DARK, GREEN_MID),
            justify="center",
        ).pack(pady=(0, 10))

        disp = ctk.CTkLabel(
            frame,
            text=self.t("waiting"),
            font=("Segoe UI", 16, "bold"),
            text_color=(GREEN_MID, GREEN_MID),
        )
        disp.pack(pady=10)

        pressed = set()

        def on_press(k):
            pressed.add(k)
            disp.configure(text=self._fmt(pressed))

        def on_release(k):
            if len(pressed) >= 2:
                s = self._fmt(pressed)
                self.shortcut_type = "keyboard"
                self.current_shortcut = s
                self.save_settings()
                self.start_listener()
                win.destroy()
                self.build_ui()

        tl = keyboard.Listener(on_press=on_press, on_release=on_release)
        tl.start()
        win.protocol("WM_DELETE_WINDOW", lambda: (tl.stop(), win.destroy()))

    def _fmt(self, keys):
        mods, main = [], None
        for k in keys:
            if k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                mods.append("ctrl")
            elif k in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                mods.append("alt")
            elif k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                mods.append("shift")
            else:
                try:
                    main = k.char
                except Exception:
                    main = str(k).replace("Key.", "")
        parts = mods + ([main] if main else [])
        return "<" + ">+<".join(parts) + ">"

    # ══════════════════════════════════════
    # LISTENERS
    # ══════════════════════════════════════
    def start_listener(self):
        for listener in (self.mouse_listener, self.keyboard_listener):
            if listener:
                try:
                    listener.stop()
                except Exception:
                    pass
        self.mouse_listener = self.keyboard_listener = None

        if self.shortcut_type == "mouse":

            def on_click(x, y, btn, pressed):
                if btn == mouse.Button.middle and pressed:
                    self.app.after(0, self.increment)

            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.mouse_listener.start()
        else:
            try:
                combo = keyboard.HotKey.parse(self.current_shortcut)

                def activate():
                    self.app.after(0, self.increment)

                hk = keyboard.HotKey(combo, activate)

                def on_press(k):
                    hk.press(self.keyboard_listener.canonical(k))

                def on_release(k):
                    hk.release(self.keyboard_listener.canonical(k))

                self.keyboard_listener = keyboard.Listener(
                    on_press=on_press, on_release=on_release
                )
                self.keyboard_listener.start()
            except Exception as e:
                print(f"Keyboard listener error: {e}")

    # ══════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════
    def save_settings(self):
        data = {
            "count": self.count,
            "cycles": self.cycles,
            "total": self.total,
            "target": self.target,
            "shortcut_type": self.shortcut_type,
            "shortcut": self.current_shortcut,
            "current_dhikr": self.current_dhikr,
            "custom_dhikr": self.custom_dhikr,
            "sessions": self.sessions,
            "lang": self.lang,
            "dark_mode": self.dark_mode,
        }
        try:
            with open(get_config_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

    def load_settings(self):
        path = get_config_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            self.count = d.get("count", 0)
            self.cycles = d.get("cycles", 0)
            self.total = d.get("total", self.count)
            self.target = d.get("target", 33)
            self.shortcut_type = d.get("shortcut_type", "mouse")
            self.current_shortcut = d.get("shortcut", "Middle Mouse")
            self.current_dhikr = d.get("current_dhikr", DHIKR_LIST[0].copy())
            self.custom_dhikr = d.get("custom_dhikr", {})
            self.sessions = d.get("sessions", [])
            self.lang = d.get("lang", "en")
            self.dark_mode = d.get("dark_mode", True)
        except Exception as e:
            print(f"Load error: {e}")

    def _debounced_save(self):
        if self._save_job:
            self.app.after_cancel(self._save_job)
        self._save_job = self.app.after(600, self.save_settings)

    # ══════════════════════════════════════
    # SYSTEM TRAY
    # ══════════════════════════════════════
    def setup_tray(self):
        if not TRAY_AVAILABLE:
            return

        def create_image():
            # Try to load icon.ico, fallback to generated green circle
            icon_path = get_resource_path("asset/icon.ico")
            if os.path.exists(icon_path):
                return Image.open(icon_path)

            # Fallback icon
            img = Image.new("RGB", (64, 64), color=(5, 150, 105))  # GREEN_DARK
            d = ImageDraw.Draw(img)
            d.ellipse([10, 10, 54, 54], fill=(16, 185, 129))  # GREEN_MID
            return img

        def on_open(icon, item):
            self.restore_from_tray()

        def on_exit(icon, item):
            icon.stop()
            self.app.after(0, self.quit_app)

        menu = pystray.Menu(
            pystray.MenuItem(lambda item: self.t("tray_show"), on_open, default=True),
            pystray.MenuItem(lambda item: self.t("tray_quit"), on_exit),
        )

        self.tray_icon = pystray.Icon("Misbaha", create_image(), "Misbaha", menu)
        self._tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self._tray_thread.start()

    def hide_to_tray(self):
        self._window_hidden = True
        self.app.withdraw()
        if TRAY_AVAILABLE and self.tray_icon:
            title = self.t("tray_minimized")
            msg = self.t("tray_minimized_msg")
            threading.Thread(
                target=self.tray_icon.notify,
                args=(msg, title),
                daemon=True,
            ).start()

    def restore_from_tray(self):
        self._window_hidden = False
        self.app.after(0, self.app.deiconify)
        self.app.after(100, self.app.focus_force)

    def quit_app(self):
        self.save_settings()
        for listener in (self.mouse_listener, self.keyboard_listener):
            if listener:
                try:
                    listener.stop()
                except:
                    pass
        if self.tray_icon:
            self.tray_icon.stop()
        self.app.quit()
        sys.exit(0)

    # ══════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════
    @staticmethod
    def _center(win, w, h):
        win.update_idletasks()
        x = (win.winfo_screenwidth() - w) // 2
        y = (win.winfo_screenheight() - h) // 2
        win.geometry(f"+{x}+{y}")

    def _on_minimize(self, event):
        """Called when the window is iconified (minimized). Hide to tray instead."""
        # Only act on the root window event, and only if not already hidden
        if event.widget is self.app and not self._window_hidden:
            # Use after() to let tkinter finish the minimize first
            self.app.after(50, self.hide_to_tray)

    def on_closing(self):
        """X button → quit entirely."""
        self.quit_app()

    def run(self):
        self.app.mainloop()


# ─────────────────────────────────────────
if __name__ == "__main__":
    TasbihCounter().run()
