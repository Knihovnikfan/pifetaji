"""
D&D — Конструктор персонажів (Kivy)

Примітки:
- Код адаптовано під телефон (розміри/шрифти/відступи винесені в клас UI).
- Фонова картинка використовується лише на головному меню (щоб не «з'їжджали» блоки на інших екранах).
- Нічого суттєвого з логіки не видаляється: виправлення — це або стилізація, або сумісні «аліаси» для стабільного запуску.
"""


import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.metrics import dp, sp
from kivy.utils import platform


if platform == 'android':
    Window.softinput_mode = 'below_target'
# ====== UI (Phone-friendly) ======
# Усі розміри/відступи винесені сюди, щоб було легко налаштовувати під телефон.
class UI:
    # Theme colors (RGBA 0..1). Used by button styling helpers.
    BTN_BG = (0.10, 0.22, 0.16, 1.0)  # deep green, solid
    BTN_FG = (1, 1, 1, 1)
    SCREEN_BG = (0.10, 0.12, 0.12, 1.0)  # суцільний фон для екранів (крім меню)
    SPIN_BG = (0.12, 0.26, 0.19, 1.0)     # фон для Spinner (solid)
    TXT_ON_DARK = (1, 1, 1, 1)

    # Базова ширина (dp), від якої рахується масштаб.
    BASE_WIDTH_DP = 360.0

    # Мін/макс масштаб (щоб не «роз'їжджалося» на дуже малих/великих екранах).
    SCALE_MIN = 0.85
    SCALE_MAX = 1.40

    # Поточний масштаб (обчислюється в init()).
    scale = 1.0

    @classmethod
    def init(cls):
        # На телефоні орієнтуємось на коротшу сторону екрана.
        w, h = Window.size
        short_side = float(min(w, h))
        cls.scale = max(cls.SCALE_MIN, min(short_side / cls.BASE_WIDTH_DP, cls.SCALE_MAX))

    # Helpers
    @classmethod
    def dpx(cls, value: float) -> float:
        return dp(value * cls.scale)

    @classmethod
    def spx(cls, value: float) -> float:
        return sp(value * cls.scale)

    # === Відступи/інтервали ===
    PAD_LG = 0.0
    PAD_MD = 0.0
    PAD_SM = 0.0
    PAD_XS = 0.0
    SPACING_LG = 0.0
    SPACING_MD = 0.0
    SPACING_SM = 0.0
    SPACING_XS = 0.0

    # === Висоти елементів ===
    BTN_LIST_H = 0.0
    ROW_H = 0.0
    CELL_H = 0.0

    BTN_PRIMARY_H = 0.0
    BTN_SECONDARY_H = 0.0
    BTN_SMALL_H = 0.0
    BTN_BAR_H = 0.0
    TAB_H = 0.0
    INPUT_H = 0.0

    # === Розміри шрифтів ===
    FS_LG = 0.0
    FS_MD = 0.0
    FS_SM = 0.0

    @classmethod
    def compute(cls):
        # Padding
        cls.PAD_LG = cls.dpx(12)
        cls.PAD_MD = cls.dpx(10)
        cls.PAD_SM = cls.dpx(8)
        cls.PAD_XS = cls.dpx(6)

        # Spacing
        cls.SPACING_LG = cls.dpx(10)
        cls.SPACING_MD = cls.dpx(8)
        cls.SPACING_SM = cls.dpx(6)
        cls.SPACING_XS = cls.dpx(6)

        # Heights

        # Widths (fixed column widths to avoid ugly wrapping)
        cls.W_INFO = cls.dpx(30)   # small "i" button
        cls.W_CODE = cls.dpx(44)   # currency code column
        cls.W_TYPE = cls.dpx(72)   # type column/button width
        cls.W_ADD  = cls.dpx(76)   # add button width
        cls.W_AMT  = cls.dpx(78)   # amount input column
        cls.W_RATE = cls.dpx(120)  # rate/equivalence column

        # Heights
        cls.BTN_LIST_H = cls.dpx(18)
        cls.BTN_PRIMARY_H = cls.dpx(20)
        cls.BTN_SECONDARY_H = cls.dpx(18)
        cls.BTN_SMALL_H = cls.dpx(18)
        cls.BTN_BAR_H = cls.dpx(20)
        cls.ROW_H = cls.dpx(20)
        cls.CELL_H = cls.dpx(20)
        cls.TAB_H = cls.dpx(20)
        cls.INPUT_H = cls.dpx(22)

        # Fonts
        cls.FS_LG = cls.spx(18)
        cls.FS_MD = cls.spx(16)
        cls.FS_SM = cls.spx(14)
        cls.FS_XS = cls.spx(12)



        # Button fonts (smaller for phone so long labels fit)
        cls.FS_BTN = cls.spx(10)
        cls.FS_BTN_SM = cls.spx(9)
        cls.FS_BTN_LG = cls.spx(10)

        # Corner radius
        cls.RADIUS_SM = cls.dpx(10)

        # Input font (slightly smaller than labels for density)
        cls.FS_INP = cls.spx(14)
# Ініціалізація UI-констант
UI.init()
UI.compute()

# ====== THEME / BACKGROUNDS ======
_ASSET_DIR = os.path.dirname(__file__)
BG_SOURCES = [
    os.path.join(_ASSET_DIR, "forest_bg.png"),
    os.path.join(_ASSET_DIR, "forest_bg.png"),
    os.path.join(_ASSET_DIR, "forest_bg.png"),
]


def _make_bg_image(source: str):
    """Create a background image without using deprecated allow_stretch/keep_ratio.

    - Newer Kivy: prefer fit_mode
    - Older Kivy: fall back to allow_stretch/keep_ratio
    """
    img = KivyImage(source=source)
    # Newer Kivy versions
    if hasattr(img, "fit_mode"):
        # 'fill' fills the available area (no aspect keep) similar to keep_ratio=False.
        try:
            img.fit_mode = "fill"
        except Exception:
            pass
    else:
        # Legacy properties (may be deprecated in newer Kivy)
        try:
            img.allow_stretch = True
            img.keep_ratio = False
        except Exception:
            pass
    return img


def themed_container(content, bg_index=0, overlay_opacity=0.55, use_image=True):
    """Контейнер для екранів.

    - use_image=True: фонове зображення + затемнення (використовуємо ТІЛЬКИ для головного меню).
    - use_image=False: повертаємо *сам контент* з суцільним фоном (стабільно як у v2 і не ламає кліки).
    """

    # --- ВАРІАНТ 1: звичайний екран (без фон-картинки) ---
    if not use_image:
        # Важливо: НЕ додаємо додаткові FloatLayout/overlay, бо вони інколи можуть
        # перехоплювати та/або ламати кліки на деяких збірках/драйверах.
        with content.canvas.before:
            Color(*UI.SCREEN_BG)
            content._rect_bg = Rectangle(pos=content.pos, size=content.size)
        content.bind(pos=lambda inst, *_: setattr(inst._rect_bg, "pos", inst.pos))
        content.bind(size=lambda inst, *_: setattr(inst._rect_bg, "size", inst.size))
        content.size_hint = (1, 1)
        return content

    # --- ВАРІАНТ 2: головне меню з фон-картинкою ---
    root = FloatLayout()

    bg = _make_bg_image(BG_SOURCES[bg_index % len(BG_SOURCES)])
    bg.size_hint = (1, 1)
    bg.pos_hint = {"x": 0, "y": 0}
    bg.disabled = True  # не перехоплює дотики
    root.add_widget(bg)

    # Затемнення для читабельності
    overlay = Widget()
    overlay.disabled = True  # не перехоплює дотики
    with overlay.canvas:
        Color(0, 0, 0, overlay_opacity)
        overlay._rect = Rectangle(pos=root.pos, size=root.size)
    root.bind(pos=lambda inst, *_: setattr(overlay._rect, "pos", inst.pos))
    root.bind(size=lambda inst, *_: setattr(overlay._rect, "size", inst.size))
    root.add_widget(overlay)

    # Контент поверх (клікабельний)
    content.size_hint = (1, 1)
    content.pos_hint = {"x": 0, "y": 0}
    root.add_widget(content)
    return root

    # Суцільний фон (всі інші екрани): без центрування/оверлеїв — як у старих версіях.
    with root.canvas.before:
        Color(*UI.SCREEN_BG)
        root._rect = Rectangle(pos=root.pos, size=root.size)
    root.bind(pos=lambda inst, *_: setattr(inst._rect, "pos", inst.pos))
    root.bind(size=lambda inst, *_: setattr(inst._rect, "size", inst.size))

    # Контент заповнює екран — так не буде «дивних» відступів справа/знизу.
    content.size_hint = (1, 1)
    content.pos_hint = {"x": 0, "y": 0}
    root.add_widget(content)
    return root

class Card(BoxLayout):
    """A simple rounded 'card' container for nicer separation."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = kwargs.get("padding", UI.PAD_SM)
        self.spacing = kwargs.get("spacing", UI.SPACING_SM)
        self.orientation = kwargs.get("orientation", "vertical")
        self.size_hint_y = None
        self.height = kwargs.get("height", UI.dpx(72))
        with self.canvas.before:
            Color(0.10, 0.16, 0.13, 1.0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[UI.dpx(10)])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

class LevelStepper(BoxLayout):
    """Simple +/- stepper for integer level selection (phone-friendly).

    Replaces a free TextInput to avoid keyboard issues and invalid values.
    """

    value = NumericProperty(0)
    min_value = NumericProperty(0)
    max_value = NumericProperty(20)

    def __init__(self, value=0, min_value=0, max_value=20, **kwargs):
        super().__init__(orientation="horizontal", spacing=UI.SPACING_XS, **kwargs)
        self.min_value = int(min_value)
        self.max_value = int(max_value)
        self.value = int(value)

        # Fixed height for stable layouts on different DPIs
        if self.size_hint_y is None or self.size_hint_y != 0:
            self.size_hint_y = None
        self.height = kwargs.get("height", UI.INPUT_H)

        self.btn_minus = Button(text="−", size_hint=(None, 1), width=UI.dpx(40))
        style_button(self.btn_minus, role="small", wrap=False)
        self.btn_minus.bind(on_release=lambda *_: self.step(-1))

        self.lbl = Label(text=str(self.value), size_hint=(1, 1), halign="center", valign="middle")
        self.lbl.bind(size=lambda *_: setattr(self.lbl, "text_size", self.lbl.size))

        self.btn_plus = Button(text="+", size_hint=(None, 1), width=UI.dpx(40))
        style_button(self.btn_plus, role="small", wrap=False)
        self.btn_plus.bind(on_release=lambda *_: self.step(1))

        self.add_widget(self.btn_minus)
        self.add_widget(self.lbl)
        self.add_widget(self.btn_plus)

        self.bind(value=self._sync)

    def _sync(self, *_):
        self.value = int(self.value)
        self.value = max(int(self.min_value), min(int(self.max_value), int(self.value)))
        self.lbl.text = str(int(self.value))

    def step(self, delta: int):
        self.value = int(self.value) + int(delta)



# ====== MOBILE UI HELPERS ======
def style_action_button(btn):
    """Єдиний стиль для коротких action-кнопок (Редагувати/Видалити) на телефоні."""
    # Менший шрифт + автоматичне перенесення, щоб текст не обрізався.
    btn.font_size = UI.FS_BTN_SM
    btn.halign = "center"
    btn.valign = "middle"
    btn.shorten = True
    btn.shorten_from = "right"
    # Дозволяємо перенос рядка в межах кнопки
    def _sync_text_size(inst, _):
        w = max(1, inst.width - UI.PAD_XS * 2)
        inst.text_size = (w, None)
    btn.bind(size=_sync_text_size)
    _sync_text_size(btn, None)


def apply_bg(widget, rgba, radius=0):
    """Малює суцільний фон на віджеті через canvas.before (не впливає на touch)."""
    from kivy.graphics import Color, Rectangle
    # очистити попередні інструкції (щоб не нашаровувалося при повторних викликах)
    if not hasattr(widget, "_bg_instr"):
        widget._bg_instr = []
    # remove previous
    try:
        for instr in widget._bg_instr:
            widget.canvas.before.remove(instr)
    except Exception:
        pass
    widget._bg_instr = []
    with widget.canvas.before:
        c = Color(*rgba)
        r = Rectangle(pos=widget.pos, size=widget.size)
    widget._bg_instr = [c, r]

    def _upd(_inst, _):
        r.pos = widget.pos
        r.size = widget.size

    widget.bind(pos=_upd, size=_upd)


def style_button(btn, role="primary", wrap=False):
    """Єдиний стиль для кнопок на телефоні (один колір, читабельний текст)."""
    btn.size_hint_y = None

    # Уніфіковані висоти
    if role == "small":
        btn.height = UI.BTN_SMALL_H
        btn.font_size = UI.FS_BTN_SM
    else:
        # primary/secondary/bar → однакова типографіка
        btn.height = UI.BTN_PRIMARY_H
        btn.font_size = UI.FS_BTN

    # один колір для всіх кнопок
    try:
        btn.background_normal = ""
        btn.background_down = ""
        btn.background_color = UI.BTN_BG
        btn.color = UI.BTN_FG
    except Exception:
        pass

    # Текст
    btn.halign = "center"
    btn.valign = "middle"
    if wrap:
        # 2 рядки
        btn.shorten = False
        def _sync(inst, _):
            w = max(1, inst.width - UI.PAD_SM * 2)
            inst.text_size = (w, None)
        btn.bind(size=_sync)
        _sync(btn, None)
    else:
        # 1 рядок, скорочення справа
        btn.text_size = (None, None)
        btn.shorten = True
        btn.shorten_from = "right"
def style_spinner(sp):
    """
    Безпечний стиль для Spinner (НЕ ламає відкриття списку).
    Важливо: НЕ форсуємо open() і НЕ чіпаємо dropdown/option_cls, бо це
    в окремих середовищах (Windows/Android) дає або "не відкривається", або краш.
    """
    sp.font_size = UI.FS_BTN  # той самий розмір, що й у кнопок "Додати"
    sp.size_hint_y = None
    sp.height = UI.INPUT_H
    sp.halign = "left"
    sp.valign = "middle"
    sp.shorten = True
    sp.shorten_from = "right"

    # Текст по ширині (щоб не "вилазив")
    def _sync(inst, _):
        w = max(1, inst.width - UI.PAD_SM * 2)
        inst.text_size = (w, None)
    sp.bind(size=_sync)
    _sync(sp, None)

    # Візуально під тему робимо через canvas, не через background_* (так стабільніше)
    apply_bg(sp, UI.SPIN_BG, radius=UI.RADIUS_SM)

    # Колір тексту
    try:
        sp.color = UI.TXT_ON_DARK
    except Exception:
        pass


def style_textinput(inp, role: str = "default"):
    """Єдиний стиль TextInput на телефоні.

    role:
      - default: стандартний розмір (UI.FS_INP)
      - sm: менший (UI.FS_SM) — для коротких полів у попапах
      - xs: дуже малий (UI.FS_XS) — для описів/довгих текстів
    """
    if role == "xs":
        inp.font_size = getattr(UI, "FS_XS", UI.FS_SM)
    elif role == "sm":
        inp.font_size = UI.FS_SM
    else:
        inp.font_size = getattr(UI, "FS_INP", UI.FS_MD)

    inp.size_hint_y = None
    inp.height = UI.INPUT_H
    # multiline виставляємо локально на місці (щоб не ламати форми)

    inp.background_normal = ""
    inp.background_active = ""
    inp.background_color = (1, 1, 1, 1)
    inp.foreground_color = (0, 0, 0, 1)


def popup_phone(title, content, *, width_ratio=0.92, height_ratio=0.62, modal=False):
    """Попап розміру телефону: ширина ~екран, висота адаптивна."""
    w, h = Window.size
    ph = max(UI.dpx(220), min(int(h * height_ratio), int(h * 0.88)))
    popup = Popup(
        title=title,
        content=content,
        size_hint=(width_ratio, None),
        height=ph,
        auto_dismiss=not modal,
    )
    return popup


def toast_phone(title, message):
    """Коротке повідомлення (помилка/готово), яке не ламає верстку на телефоні."""
    lbl = Label(text=message, halign="center", valign="middle")
    def _sync(inst, _):
        lbl.text_size = (max(1, inst.width - UI.PAD_MD * 2), None)
    box = BoxLayout(orientation="vertical", padding=UI.PAD_MD, spacing=UI.SPACING_SM)
    box.add_widget(lbl)
    p = Popup(title=title, content=box, size_hint=(0.92, None), height=UI.dpx(180))
    p.open()
# ====== ДОВІДНИКИ ======
CLASSES_INFO = {
    "Воїн": "Експерт у будь-якій зброї та обладунках. Найбільш гнучкий боєць.",
    "Варвар": "Дикий воїтель, що впадає в лють, отримуючи менше шкоди та завдаючи нищівних ударів.",
    "Паладин": "Святий лицар, що поєднує важку броню, лікування та магічні удари Карою.",
    "Чародій": "Має вроджений магічний хист і може змінювати властивості заклинань (метамагія).",
    "Бард": "Використовує музику та слова для натхнення союзників і контролю над ворогами.",
    "Жрець": "Служить богу, вміє ефективно лікувати, підсилювати групу та нищити нежить.",
    "Монах": "Мастер бойових мистецтв, використовує швидкість та удари кулаками (енергія Кі).",
    "Слідопит": "Мисливець та виживальник, майстер стрільби з лука та вистежування ворогів.",
    "Чарівник": "Вчений-маг, що вивчає заклинання за книгами, має найбільший арсенал магії.",
    "Чаклун": "Отримує магічну силу через угоду з могутнім покровителем.",
    "Друїд": "Захисник природи, здатний перетворюватися на тварин та керувати стихіями.",
    "Плут": "Мастер потайливості та точних ударів, спеціаліст зі злому та пасток."
}

RACES_INFO = {
    "Людина": "Універсальна раса, яка адаптується до будь-якої ролі.",
    "Ельф": "Витончені та магічні довгожителі. Мають гострий зір та імунітет до магічного сну.",
    "Дварф": "Міцні та витривалі майстри, стійкі до отрут. Ідеальні воїни та ковалі.",
    "Гафлінг": "Маленькі та спритні. Їхня головна фішка — неймовірна удача.",
    "Напіворк": "Могутні воїни, яких дуже важко вбити завдяки несамовитій витривалості.",
    "Дракононароджений": "Нащадок драконів, що може видихати стихійне руйнування.",
    "Гном": "Маленькі винахідники з гострим розумом та магічним опором.",
    "Тифлінг": "Нащадки демонічних ліній, мають опір до вогню та вроджену магію темряви."
}

WEAPON_INFO = {
    "Меч": "Середня шкода, універсальна.",
    "Сокира": "Висока шкода, велична вага.",
    "Лук": "Дальній бій, вимагає спритності.",
    "Кинджал": "Швидкий, бонус до критів.",
    "Кийок": "Магічний фокус, слабка шкода.",
    "Спис": "Дальність та можливість метання.",
    "Молот": "Потужна дробяча зброя проти броні."
}

ARMOR_INFO = {
    "Без броні": "Немає броні, повна рухливість.",
    "Легка броня": "Для спритних класів, не обмежує скритність.",
    "Середня броня": "Баланс захисту й мобільності.",
    "Важка броня": "Максимальний захист, вимагає великої сили." 
}

CLASS_EQUIP = {
    "Воїн": {"weapons": ["Меч", "Сокира", "Лук"], "armors": ["Важка броня", "Середня броня", "Легка броня"]},
    "Варвар": {"weapons": ["Сокира", "Меч"], "armors": ["Середня броня", "Без броні"]},
    "Паладин": {"weapons": ["Меч", "Молот"], "armors": ["Важка броня", "Середня броня"]},
    "Друїд": {"weapons": ["Кийок", "Кинджал", "Спис"], "armors": ["Без броні", "Легка броня", "Середня броня"]},
    "Плут": {"weapons": ["Кинджал", "Лук"], "armors": ["Легка броня"]},
    "Чаклун": {"weapons": ["Кийок", "Кинджал"], "armors": ["Без броні", "Легка броня"]},
    "Чарівник": {"weapons": ["Кийок", "Кинджал"], "armors": ["Без броні"]},
    "Бард": {"weapons": ["Меч", "Кинджал", "Лук"], "armors": ["Легка броня"]},
    "Жрець": {"weapons": ["Молот", "Спис", "Кийок"], "armors": ["Середня броня", "Важка броня"]},
    "Монах": {"weapons": ["Кийок", "Спис"], "armors": ["Без броні"]},
    "Слідопит": {"weapons": ["Лук", "Меч"], "armors": ["Легка броня", "Середня броня"]},
    "Чародій": {"weapons": ["Кийок", "Кинджал"], "armors": ["Без броні"]}
}

# ====== Керування валютами ======
class CurrencyManager:
    def __init__(self):
        self.rates = {'CP': 0.01, 'SP': 0.1, 'EP': 0.5, 'GP': 1.0, 'PP': 10.0}
        self.order = ['CP', 'SP', 'EP', 'GP', 'PP']

    @property
    def codes(self):
        """List of currency codes in display order (UI compatibility helper)."""
        return list(self.order)

    def add_currency(self, code:str, rate_to_gp:float):
        code = code.strip().upper()
        if not code:
            raise ValueError('Порожній код')
        if code in self.rates:
            raise ValueError('Валюта вже існує')
        self.rates[code] = float(rate_to_gp)
        self.order.append(code)

    def set_rate(self, code:str, rate_to_gp:float):
        if code not in self.rates:
            raise KeyError('Валюта не знайдена')
        self.rates[code] = float(rate_to_gp)

    def to_gp(self, amounts:dict)->float:
        total=0.0
        for c,v in amounts.items():
            try: val=float(v)
            except Exception: val=0.0
            total+=self.rates.get(c,0.0)*val
        return total

    def total_to_gp(self, amounts:dict)->float:
        """Backward-compatible alias used by UI."""
        return self.to_gp(amounts)

# ====== Екрани ======
class MainMenu(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        layout=BoxLayout(orientation='vertical',spacing=UI.SPACING_SM,padding=UI.PAD_LG)
        layout.add_widget(Label(text='D&D Character Creator', size_hint_y=None, height=UI.ROW_H, font_size=UI.FS_LG))
        btn_create=Button(text='Створити персонажа',size_hint_y=None, height=UI.BTN_PRIMARY_H)
        style_button(btn_create, role='primary')
        btn_create.bind(on_release=lambda i:setattr(self.manager,'current','create'))
        layout.add_widget(btn_create)
        btn_ready=Button(text='Готові персонажі',size_hint_y=None, height=UI.BTN_PRIMARY_H)
        style_button(btn_ready, role='primary')
        btn_ready.bind(on_release=lambda i:setattr(self.manager,'current','ready'))
        layout.add_widget(btn_ready)
        self.add_widget(themed_container(layout, bg_index=0, use_image=True))

class CreateCharacter(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app=App.get_running_app()
        layout=BoxLayout(orientation='vertical',spacing=UI.SPACING_SM,padding=UI.PAD_MD)
        self.name_input=TextInput(hint_text="Ім'я персонажа", size_hint_y=None, height=UI.INPUT_H)
        style_textinput(self.name_input)
        layout.add_widget(self.name_input)

        # клас з info
        row=BoxLayout(size_hint=(1,None), height=UI.ROW_H,spacing=UI.SPACING_SM)
        self.class_spinner=Spinner(text='Оберіть клас',values=list(CLASSES_INFO.keys()))
        style_spinner(self.class_spinner)
        btn_info=Button(text='i', size_hint=(None, 1), width=UI.dpx(44))
        style_button(btn_info, role='small')
        btn_info.bind(on_release=lambda i:self.show_info(self.class_spinner.text,CLASSES_INFO))
        row.add_widget(self.class_spinner)
        row.add_widget(btn_info)
        layout.add_widget(row)

        # раса з info
        row2=BoxLayout(size_hint=(1,None), height=UI.ROW_H,spacing=UI.SPACING_SM)
        self.race_spinner=Spinner(text='Оберіть расу',values=list(RACES_INFO.keys()))
        style_spinner(self.race_spinner)
        btn_info2=Button(text='i', size_hint=(None, 1), width=UI.dpx(44))
        style_button(btn_info2, role='small')
        btn_info2.bind(on_release=lambda i:self.show_info(self.race_spinner.text,RACES_INFO))
        row2.add_widget(self.race_spinner)
        row2.add_widget(btn_info2)
        layout.add_widget(row2)

        # рівень
        # Рівень (0..20): кнопки -1/+1 (без клавіатури)
        self.level_value = 0
        lvl_row = BoxLayout(size_hint=(1, None), height=UI.ROW_H, spacing=UI.SPACING_SM)
        btn_minus = Button(text='-1', size_hint=(None, 1), width=UI.dpx(72))
        style_button(btn_minus, role='small')
        self.level_label = Label(text=f'Рівень: {self.level_value}', size_hint=(1, 1), color=UI.TXT_ON_DARK)
        btn_plus = Button(text='+1', size_hint=(None, 1), width=UI.dpx(72))
        style_button(btn_plus, role='small')
        def _upd_level(_delta):
            self.level_value = max(0, min(20, self.level_value + _delta))
            self.level_label.text = f'Рівень: {self.level_value}'
        btn_minus.bind(on_release=lambda _i: _upd_level(-1))
        btn_plus.bind(on_release=lambda _i: _upd_level(+1))
        lvl_row.add_widget(btn_minus)
        lvl_row.add_widget(self.level_label)
        lvl_row.add_widget(btn_plus)
        layout.add_widget(lvl_row)


        # зброя/броня
        # Блок зроблено «телефонним»: у 2 рядки для кожного вибору.
        equip_box = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=UI.SPACING_SM)

        equip_title = Label(
            text='Зброя та броня (залежить від класу):',
            size_hint=(1, None),
            height=UI.ROW_H
        )
        equip_box.add_widget(equip_title)

        # --- ЗБРОЯ: 1) вибір 2) інфо + додати
        w_block = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=UI.SPACING_XS)
        w_top = BoxLayout(size_hint=(1, None), height=UI.INPUT_H)
        self.weapon_spinner = Spinner(text='Зброя', values=[], size_hint=(1, 1))
        style_spinner(self.weapon_spinner)
        w_top.add_widget(self.weapon_spinner)

        w_bottom = BoxLayout(size_hint=(1, None), height=UI.BTN_SMALL_H, spacing=UI.SPACING_SM)
        btn_w_info = Button(text='i', size_hint=(None, None), width=UI.dpx(32), height=UI.BTN_SMALL_H)
        style_button(btn_w_info, role='small')
        btn_w_info.bind(on_release=lambda i: self.show_info(self.weapon_spinner.text, WEAPON_INFO))

        add_w_btn = Button(text='Додати', size_hint=(1, None), height=UI.BTN_SMALL_H)
        style_button(add_w_btn, role='primary')
        add_w_btn.bind(on_release=self.add_selected_weapon)

        w_bottom.add_widget(btn_w_info)
        w_bottom.add_widget(add_w_btn)

        w_block.add_widget(w_top)
        w_block.add_widget(w_bottom)
        w_block.height = w_top.height + w_bottom.height + UI.SPACING_XS
        equip_box.add_widget(w_block)

        # --- ОБЛАДУНКИ: 1) вибір 2) інфо + додати
        a_block = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=UI.SPACING_XS)
        a_top = BoxLayout(size_hint=(1, None), height=UI.INPUT_H)
        self.armor_spinner = Spinner(text='Обладунки', values=[], size_hint=(1, 1))
        style_spinner(self.armor_spinner)
        a_top.add_widget(self.armor_spinner)

        a_bottom = BoxLayout(size_hint=(1, None), height=UI.BTN_SMALL_H, spacing=UI.SPACING_SM)
        btn_a_info = Button(text='i', size_hint=(None, None), width=UI.dpx(32), height=UI.BTN_SMALL_H)
        style_button(btn_a_info, role='small')
        btn_a_info.bind(on_release=lambda i: self.show_info(self.armor_spinner.text, ARMOR_INFO))

        add_a_btn = Button(text='Додати', size_hint=(1, None), height=UI.BTN_SMALL_H)
        style_button(add_a_btn, role='primary')
        add_a_btn.bind(on_release=self.add_selected_armor)

        a_bottom.add_widget(btn_a_info)
        a_bottom.add_widget(add_a_btn)

        a_block.add_widget(a_top)
        a_block.add_widget(a_bottom)
        a_block.height = a_top.height + a_bottom.height + UI.SPACING_XS
        equip_box.add_widget(a_block)

        # Висота контейнера: заголовок + 2 блоки + відступи
        equip_box.height = equip_title.height + w_block.height + a_block.height + UI.SPACING_SM * 2

        layout.add_widget(equip_box)

        # кнопки
        btn_save=Button(text='Зберегти персонажа',size_hint_y=None, height=UI.BTN_PRIMARY_H)
        style_button(btn_save, role='primary')
        btn_save.bind(on_release=self.save_character)
        layout.add_widget(btn_save)
        btn_back=Button(text='Назад',size_hint_y=None, height=UI.BTN_SECONDARY_H)
        style_button(btn_back, role='secondary')
        btn_back.bind(on_release=lambda i:setattr(self.manager,'current','menu'))
        layout.add_widget(btn_back)
        self.class_spinner.bind(text=self.update_equip_options)
        # Ініціалізація списків зброї/броні одразу (щоб Spinner відкривався з першого разу)
        self.update_equip_options()
        self.add_widget(layout)

    def update_equip_options(self,*args):
        cls = self.class_spinner.text
        weapons = []
        armors = []
        if cls in CLASS_EQUIP:
            weapons = list(CLASS_EQUIP[cls].get('weapons', []))
            armors = list(CLASS_EQUIP[cls].get('armors', []))
        # fallback: якщо клас ще не обраний або нема запису — даємо загальний список
        if not weapons:
            all_w = []
            for v in CLASS_EQUIP.values():
                all_w.extend(v.get('weapons', []))
            weapons = sorted(set(all_w))
        if not armors:
            all_a = []
            for v in CLASS_EQUIP.values():
                all_a.extend(v.get('armors', []))
            armors = sorted(set(all_a))
        self.weapon_spinner.values = weapons
        self.armor_spinner.values = armors
        # якщо поточне значення не в списку — ставимо перше
        if self.weapon_spinner.text not in weapons:
            self.weapon_spinner.text = weapons[0] if weapons else 'Зброя'
        if self.armor_spinner.text not in armors:
            self.armor_spinner.text = armors[0] if armors else 'Обладунки'

    def show_info(self, key, info_dict):
        """Показує довідку у зручному pop-up (текст не «вилазить»)."""
        if not key or key in ('Зброя', 'Обладунки', 'Тип', 'Клас', 'Раса'):
            return
        if key not in info_dict:
            return

        # Контент: скрол + кнопка закриття
        box = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_SM)

        scroll = ScrollView(size_hint=(1, 1))
        lbl = Label(
            text=info_dict[key],
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        # Перенос рядків під ширину попапу
        def _update_text_size(*_):
            lbl.text_size = (scroll.width - UI.PAD_SM * 2, None)
            lbl.texture_update()
            lbl.height = lbl.texture_size[1]

        scroll.bind(width=_update_text_size)
        _update_text_size()

        scroll.add_widget(lbl)
        box.add_widget(scroll)

        close_btn = Button(text='Закрити', size_hint=(1, None), height=UI.BTN_PRIMARY_H)
        style_button(close_btn, role='secondary')
        box.add_widget(close_btn)

        popup = Popup(title=key, content=box, size_hint=(0.92, 0.75), auto_dismiss=True)
        close_btn.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def add_selected_weapon(self,*args):
        w=self.weapon_spinner.text
        if w and w!='Зброя':
            if 'tmp_inventory' not in self.app.__dict__: self.app.tmp_inventory=[]
            self.app.tmp_inventory.append({'type':'weapon','name':w})
            Popup(title='Додано',content=Label(text=f'Додано {w}'),size_hint=(0.9,0.3)).open()

    def add_selected_armor(self,*args):
        a=self.armor_spinner.text
        if a and a!='Обладунки':
            if 'tmp_inventory' not in self.app.__dict__: self.app.tmp_inventory=[]
            self.app.tmp_inventory.append({'type':'armor','name':a})
            Popup(title='Додано',content=Label(text=f'Додано {a}'),size_hint=(0.9,0.3)).open()

    def save_character(self,*args):
        name=self.name_input.text.strip()
        # Рівень беремо зі степера (-1/+1), діапазон 0..20
        level = int(getattr(self, 'level_value', 0))
        if level < 0:
            level = 0
        if level > 20:
            level = 20
        if not name or self.class_spinner.text=='Оберіть клас' or self.race_spinner.text=='Оберіть расу':
            Popup(title='Помилка',content=Label(text="Заповніть ім'я, клас і расу"),size_hint=(0.9,0.3)).open()
            return
        inv=[]
        if hasattr(self.app,'tmp_inventory') and self.app.tmp_inventory:
            inv=self.app.tmp_inventory.copy()
            self.app.tmp_inventory.clear()
        char={'name':name,'class':self.class_spinner.text,'race':self.race_spinner.text,'level':level,'inventory':inv,'money':{code:0 for code in self.app.currency.order}}
        self.app.characters.append(char)
        self.app.save_characters()
        Popup(title='Готово',content=Label(text=f"Персонаж '{name}' збережено."),size_hint=(0.9,0.3)).open()
        setattr(self.manager,'current','menu')

class ReadyCharacters(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.current_popup = None

        root = BoxLayout(orientation='vertical', padding=UI.PAD_LG, spacing=UI.SPACING_SM)
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=UI.SPACING_SM, size_hint=(1, None))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        btn_back = Button(text='Назад', size_hint_y=None, height=UI.BTN_SECONDARY_H)
        style_button(btn_back, role='secondary')
        btn_back.bind(on_release=lambda i: setattr(self.manager, 'current', 'menu'))
        root.add_widget(btn_back)

        self.add_widget(themed_container(root, bg_index=2, use_image=False))

    def on_pre_enter(self, *args):
        self.refresh_ready_list()

    def refresh_ready_list(self):
        self.grid.clear_widgets()
        for char in getattr(self.manager, 'app', self.app).characters:
            btn = Button(
                font_size=UI.FS_SM,
                text=f"{char['name']} — {char['class']} ({char['race']}) lvl {char['level']}",
                size_hint=(1, None), height=UI.BTN_LIST_H,
                halign="left", valign="middle"
            )
            # Ensure text stays inside and doesn't create strange right margins on some DPI/scales
            btn.bind(size=lambda inst, *_: setattr(inst, "text_size", (inst.width - UI.PAD_MD * 2, None)))

            btn.bind(on_release=lambda i, ch=char: self.open_character(ch))
            self.grid.add_widget(btn)

    # ---------- Методи для редагування/додавання валют ----------
    def edit_rates(self, char, refresh_callback=None):
        content = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)
        inputs = {}

        rows_box = BoxLayout(orientation='vertical', spacing=UI.SPACING_XS, size_hint_y=None)
        rows_box.bind(minimum_height=rows_box.setter('height'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(rows_box)

        for code in self.app.currency.order:
            row = BoxLayout(size_hint=(1, None), height=UI.INPUT_H, spacing=UI.SPACING_SM)
            lbl = Label(text=f"{code} → GP:", size_hint=(None, None), width=UI.dpx(90), height=UI.INPUT_H)
            lbl.halign='left'; lbl.valign='middle'
            row.add_widget(lbl)
            inp = TextInput(text=str(self.app.currency.rates.get(code,1)), multiline=False, input_filter='float', size_hint=(1, None), height=UI.INPUT_H)
            style_textinput(inp)
            row.add_widget(inp)
            inputs[code] = inp
            rows_box.add_widget(row)

        content.add_widget(scroll)

        save_btn = Button(text='Зберегти', size_hint_y=None, height=UI.BTN_SECONDARY_H)
        style_button(save_btn, role='secondary')
        close_btn = Button(text='Закрити', size_hint_y=None, height=UI.BTN_SECONDARY_H)
        style_button(close_btn, role='secondary')
        btns = BoxLayout(size_hint_y=None, height=UI.BTN_SECONDARY_H, spacing=UI.SPACING_SM)
        btns.add_widget(close_btn)
        btns.add_widget(save_btn)

        def save(*_):
            for code, widget in inputs.items():
                try:
                    self.app.currency.rates[code] = float(widget.text)
                except Exception:
                    self.app.currency.rates[code] = 1
            if refresh_callback:
                refresh_callback()
            toast_phone('Готово', 'Курси оновлено')
            popup.dismiss()

        save_btn.bind(on_release=save)
        content.add_widget(btns)
        popup = popup_phone('Редагувати курси валют', content, height_ratio=0.70, modal=False)
        close_btn.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def add_currency(self, char, refresh_callback=None):
        content = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)
        code_input = TextInput(hint_text='Код валюти (наприклад, USD)', multiline=False, size_hint_y=None, height=UI.INPUT_H)
        style_textinput(code_input, role='sm')
        rate_input = TextInput(hint_text='Курс до GP', multiline=False, input_filter='float', size_hint_y=None, height=UI.INPUT_H)
        style_textinput(rate_input, role='sm')
        save_btn = Button(text='Додати', size_hint_y=None, height=UI.BTN_SECONDARY_H)
        style_button(save_btn, role='secondary')
        close_btn = Button(text='Закрити', size_hint_y=None, height=UI.BTN_SECONDARY_H)
        style_button(close_btn, role='secondary')

        lbl1 = Label(text='Нова валюта:', size_hint_y=None, height=UI.ROW_H, halign='left', valign='middle', font_size=UI.FS_SM)
        content.add_widget(lbl1)
        content.add_widget(code_input)
        lbl2 = Label(text='Курс до GP:', size_hint_y=None, height=UI.ROW_H, halign='left', valign='middle', font_size=UI.FS_SM)
        content.add_widget(lbl2)
        content.add_widget(rate_input)
        btns = BoxLayout(size_hint_y=None, height=UI.BTN_SECONDARY_H, spacing=UI.SPACING_SM)
        btns.add_widget(close_btn)
        btns.add_widget(save_btn)
        content.add_widget(btns)

        def save(*_):
            code = code_input.text.strip()
            try:
                rate = float(rate_input.text)
            except Exception:
                toast_phone('Помилка', 'Курс має бути числом')
                return
            if not code:
                toast_phone('Помилка', 'Введіть код валюти')
                return
            if code in self.app.currency.rates:
                toast_phone('Помилка', 'Валюта вже існує')
                return
            self.app.currency.rates[code] = rate
            self.app.currency.order.append(code)
            if refresh_callback:
                refresh_callback()
            toast_phone('Готово', 'Валюта додана')
            popup.dismiss()

        save_btn.bind(on_release=save)
        popup = popup_phone('Додати валюту', content, height_ratio=0.55, modal=False)
        close_btn.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    # ---------- Відкриття персонажа ----------
    def open_character(self, char, start_tab='Основне'):
        panel = TabbedPanel(do_default_tab=False)
        panel.size_hint = (1, 1)
        panel.tab_height = UI.TAB_H

        # -------- Основне --------
        tab_main = TabbedPanelItem(text='Основне')
        box_main = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)
        box_main.size_hint_y = None
        box_main.bind(minimum_height=box_main.setter('height'))

        name_row = BoxLayout(size_hint=(1, None), height=UI.ROW_H, spacing=UI.SPACING_SM)
        name_label = Label(text="Ім'я:", size_hint=(0.25, None), height=UI.INPUT_H, valign='middle')
        name_input = TextInput(text=char['name'])
        style_textinput(name_input)
        name_row.add_widget(name_label)
        name_row.add_widget(name_input)
        box_main.add_widget(name_row)

        level_row = BoxLayout(size_hint=(1, None), height=UI.ROW_H, spacing=UI.SPACING_SM)
        level_label = Label(text="Рівень:", size_hint=(0.25,1))
        level_stepper = LevelStepper(value=int(char.get('level', 1)), min_value=0, max_value=20)
        level_row.add_widget(level_label)
        level_row.add_widget(level_stepper)
        box_main.add_widget(level_row)

        save_main_btn = Button(text="Зберегти основне", size_hint_y=None, height=UI.BTN_PRIMARY_H)
        style_button(save_main_btn, role='primary')

        def save_main(*_):
            new_name = name_input.text.strip()
            new_level = int(level_stepper.value)
            if False:
                try:
                    new_level = int(level_input.text)
                except Exception:
                    pass
            if not new_name:
                Popup(title='Помилка', content=Label(text="Ім'я не може бути пустим"), size_hint=(0.6,0.3)).open()
                return
            char['name'] = new_name
            char['level'] = new_level
            self.app.save_characters()
            toast_phone('Готово', 'Збережено')
            self.current_popup.dismiss()
            self.open_character(char, start_tab='Основне')

        save_main_btn.bind(on_release=save_main)
        box_main.add_widget(save_main_btn)
        tab_main.content = box_main
        panel.add_widget(tab_main)

        # -------- Інвентар --------
        tab_inv = TabbedPanelItem(text='Інвентар')
        inv_panel = TabbedPanel(do_default_tab=False)
        inv_panel.tab_height = UI.TAB_H
        panel.tab_height = UI.TAB_H

        tab_items = TabbedPanelItem(text='Предмети')
        items_box = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)

        items_scroll = ScrollView(size_hint=(1,0.75))
        items_grid = GridLayout(cols=1, size_hint_y=None, spacing=UI.SPACING_SM)
        items_grid.bind(minimum_height=items_grid.setter('height'))
        items_scroll.add_widget(items_grid)
        items_box.add_widget(items_scroll)

        def refresh_items():
            items_grid.clear_widgets()
            inv = char.get('inventory', [])
            for idx, item in enumerate(inv):
                # Card per item: title row + actions row
                card = Card(size_hint_y=None, padding=UI.PAD_XS, spacing=UI.SPACING_XS)
                card.bind(minimum_height=card.setter('height'))
                title = Label(
                    text=f"{item.get('name','?')} — {item.get('type','?')}",
                    size_hint_y=None,
                    halign='left',
                    valign='middle',
                    font_size=UI.FS_MD,
                )
                title.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width), None)))
                title.bind(texture_size=lambda inst, ts: setattr(inst, 'height', ts[1] + UI.dpx(6)))
                sub = None
                desc = (item.get('description','') or '').strip()
                if desc:
                    sub = Label(
                        text=desc,
                        size_hint_y=None,
                        halign='left',
                        valign='middle',
                        font_size=UI.FS_SM,
                    )
                    sub.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width), None)))
                    sub.bind(texture_size=lambda inst, ts: setattr(inst, 'height', ts[1] + UI.dpx(4)))

                actions = BoxLayout(orientation='horizontal', spacing=UI.SPACING_SM, size_hint_y=None, height=UI.BTN_SMALL_H)
                edit_btn = Button(text='Редагувати', size_hint=(1, 1))
                del_btn = Button(text='Видалити', size_hint=(1, 1))
                style_button(edit_btn, role='small', wrap=False)
                style_button(del_btn, role='small', wrap=False)

                def edit_item(inst, i=idx):
                    popup_content = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)
                    type_input = TextInput(text=char['inventory'][i].get('type',''), multiline=False, size_hint_y=None, height=UI.INPUT_H)
                    name_input2 = TextInput(text=char['inventory'][i].get('name',''), multiline=False, size_hint_y=None, height=UI.INPUT_H)
                    desc_input = TextInput(text=char['inventory'][i].get('description',''), multiline=False, size_hint_y=None, height=UI.INPUT_H)
                    style_textinput(type_input); style_textinput(name_input2); style_textinput(desc_input)

                    btns = BoxLayout(size_hint_y=None, height=UI.BTN_SECONDARY_H, spacing=UI.SPACING_SM)
                    save_btn2 = Button(text='Зберегти')
                    cancel_btn2 = Button(text='Закрити')
                    style_button(save_btn2, role='secondary')
                    style_button(cancel_btn2, role='secondary')
                    btns.add_widget(cancel_btn2)
                    btns.add_widget(save_btn2)

                    def save_edits(*_):
                        char['inventory'][i]['type'] = type_input.text.strip()
                        char['inventory'][i]['name'] = name_input2.text.strip()
                        char['inventory'][i]['description'] = desc_input.text.strip()
                        self.app.save_characters()
                        edit_popup.dismiss()
                        refresh_items()

                    popup_content.add_widget(Label(text='Тип предмета:', size_hint_y=None, height=UI.ROW_H))
                    popup_content.add_widget(type_input)
                    popup_content.add_widget(Label(text='Назва предмета:', size_hint_y=None, height=UI.ROW_H))
                    popup_content.add_widget(name_input2)
                    popup_content.add_widget(Label(text='Опис/характеристики:', size_hint_y=None, height=UI.ROW_H))
                    popup_content.add_widget(desc_input)
                    popup_content.add_widget(btns)

                    save_btn2.bind(on_release=save_edits)
                    cancel_btn2.bind(on_release=lambda *_: edit_popup.dismiss())

                    edit_popup = popup_phone('Редагувати предмет', popup_content, height_ratio=0.60, modal=False)
                    edit_popup.open()

                def del_item(inst, i=idx):
                    try:
                        char['inventory'].pop(i)
                    except Exception:
                        return
                    self.app.save_characters()
                    refresh_items()

                edit_btn.bind(on_release=edit_item)
                del_btn.bind(on_release=del_item)
                actions.add_widget(edit_btn)
                actions.add_widget(del_btn)

                card.add_widget(title)
                if sub is not None:
                    card.add_widget(sub)
                card.add_widget(actions)
                items_grid.add_widget(card)


        add_form = BoxLayout(orientation='vertical', size_hint=(1, None),
                             height=UI.INPUT_H * 2 + UI.SPACING_SM, spacing=UI.SPACING_SM)

        row1 = BoxLayout(size_hint=(1, None), height=UI.INPUT_H, spacing=UI.SPACING_SM)
        new_name = TextInput(hint_text='Назва предмета')
        style_textinput(new_name)

        type_spinner = Spinner(text='Тип', values=['weapon', 'armor', 'item'], size_hint=(None, 1), width=UI.W_TYPE)
        type_spinner.font_size = UI.FS_BTN

        row1.add_widget(new_name)
        row1.add_widget(type_spinner)

        row2 = BoxLayout(size_hint=(1, None), height=UI.INPUT_H, spacing=UI.SPACING_SM)
        description_input = TextInput(hint_text='Опис/характеристики')
        style_textinput(description_input)

        add_btn = Button(text='Додати', size_hint=(None, 1), width=UI.W_ADD)
        style_button(add_btn, role='small')

        row2.add_widget(description_input)
        row2.add_widget(add_btn)

        add_form.add_widget(row1)
        add_form.add_widget(row2)

        def do_add_item(*_):
            name = new_name.text.strip()
            t = type_spinner.text
            desc = description_input.text.strip()
            if not name:
                toast_phone('Помилка', 'Введіть назву')
                return
            char.setdefault('inventory', []).append({'type':t,'name':name,'description':desc})
            self.app.save_characters()
            refresh_items()

        add_btn.bind(on_release=do_add_item)
        items_box.add_widget(add_form)
        tab_items.content = items_box
        inv_panel.add_widget(tab_items)

            # -------- Закляття --------
        tab_spells = TabbedPanelItem(text='Закляття')
        spells_box = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)

        spells_scroll = ScrollView(size_hint=(1,0.75))
        spells_grid = GridLayout(cols=1, size_hint_y=None, spacing=UI.SPACING_SM)
        spells_grid.bind(minimum_height=spells_grid.setter('height'))
        spells_scroll.add_widget(spells_grid)
        spells_box.add_widget(spells_scroll)

        def refresh_spells():
            spells_grid.clear_widgets()
            spells = char.get('spells', [])
            for idx, spell in enumerate(spells):
                card = Card(size_hint_y=None, padding=UI.PAD_XS, spacing=UI.SPACING_XS)
                card.bind(minimum_height=card.setter('height'))
                title = Label(text=f"{spell.get('name','?')}", size_hint_y=None, 
                              halign='left', valign='middle', font_size=UI.FS_MD)
                title.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width), None)))
                title.bind(texture_size=lambda inst, ts: setattr(inst, 'height', ts[1] + UI.dpx(6)))
                sub = Label(text=f"{spell.get('description','')}", size_hint_y=None, 
                            halign='left', valign='middle', font_size=UI.FS_SM)
                sub.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width), None)))
                sub.bind(texture_size=lambda inst, ts: setattr(inst, 'height', ts[1] + UI.dpx(4)))

                actions = BoxLayout(orientation='horizontal', spacing=UI.SPACING_SM, size_hint_y=None, height=UI.BTN_SMALL_H)
                edit_btn = Button(text='Редагувати')
                del_btn = Button(text='Видалити')
                style_button(edit_btn, role='small', wrap=False)
                style_button(del_btn, role='small', wrap=False)

                def edit_spell(inst, i=idx):
                    popup_content = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)
                    name_inp = TextInput(text=char['spells'][i].get('name',''), multiline=False, size_hint_y=None, height=UI.INPUT_H)
                    desc_inp = TextInput(text=char['spells'][i].get('description',''), multiline=False, size_hint_y=None, height=UI.INPUT_H)
                    style_textinput(name_inp, role='sm'); style_textinput(desc_inp, role='xs')

                    btns = BoxLayout(size_hint_y=None, height=UI.BTN_SECONDARY_H, spacing=UI.SPACING_SM)
                    cancel_btn = Button(text='Закрити')
                    save_btn = Button(text='Зберегти')
                    style_button(cancel_btn, role='secondary')
                    style_button(save_btn, role='secondary')
                    btns.add_widget(cancel_btn); btns.add_widget(save_btn)

                    def save_edits(*_):
                        char['spells'][i]['name'] = name_inp.text.strip()
                        char['spells'][i]['description'] = desc_inp.text.strip()
                        self.app.save_characters()
                        pop.dismiss()
                        refresh_spells()

                    popup_content.add_widget(Label(text='Назва:', size_hint_y=None, height=UI.ROW_H))
                    popup_content.add_widget(name_inp)
                    popup_content.add_widget(Label(text='Опис:', size_hint_y=None, height=UI.ROW_H))
                    popup_content.add_widget(desc_inp)
                    popup_content.add_widget(btns)

                    save_btn.bind(on_release=save_edits)
                    cancel_btn.bind(on_release=lambda *_: pop.dismiss())
                    pop = popup_phone('Редагувати закляття', popup_content, height_ratio=0.60, modal=False)
                    pop.open()

                def del_spell(inst, i=idx):
                    try:
                        char['spells'].pop(i)
                    except Exception:
                        return
                    self.app.save_characters()
                    refresh_spells()

                edit_btn.bind(on_release=edit_spell)
                del_btn.bind(on_release=del_spell)
                actions.add_widget(edit_btn); actions.add_widget(del_btn)

                card.add_widget(title)
                if sub is not None:
                    card.add_widget(sub)
                card.add_widget(actions)
                spells_grid.add_widget(card)


        add_row_spells = BoxLayout(size_hint=(1, None), height=UI.ROW_H, spacing=UI.SPACING_SM)
        new_spell_name = TextInput(hint_text='Назва закляття')
        style_textinput(new_spell_name)
        new_spell_desc = TextInput(hint_text='Опис')
        style_textinput(new_spell_desc)
        add_spell_btn = Button(text='Додати')
        style_button(add_spell_btn, role='small')

        def do_add_spell(*_):
            name = new_spell_name.text.strip()
            desc = new_spell_desc.text.strip()
            if not name:
                toast_phone('Помилка', 'Введіть назву закляття')
                return
            char.setdefault('spells', []).append({'name':name, 'description':desc})
            self.app.save_characters()
            refresh_spells()

        add_spell_btn.bind(on_release=do_add_spell)
        add_row_spells.add_widget(new_spell_name)
        add_row_spells.add_widget(new_spell_desc)
        add_row_spells.add_widget(add_spell_btn)
        spells_box.add_widget(add_row_spells)

        tab_spells.content = spells_box
        inv_panel.add_widget(tab_spells)
        refresh_spells()



        refresh_items()
        tab_inv.content = inv_panel
        panel.add_widget(tab_inv)

        # -------- Гаманець --------
        tab_wallet = TabbedPanelItem(text='Гаманець')
        wallet_box = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_SM)

        wallet_inputs = []

        total_label = Label(text=f"Загалом у GP: {self.app.currency.total_to_gp(char.get('money',{}))}",
                           size_hint_y=None, height=UI.ROW_H, font_size=UI.FS_MD, halign='left', valign='middle')
        total_label.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width), None)))
        wallet_box.add_widget(total_label)

        table_scroll = ScrollView(size_hint=(1, 1))
        table_list = GridLayout(cols=1, size_hint_y=None, spacing=UI.SPACING_SM, padding=(0, UI.PAD_XS))
        table_list.bind(minimum_height=table_list.setter('height'))
        table_scroll.add_widget(table_list)
        wallet_box.add_widget(table_scroll)

        btn_row = BoxLayout(orientation='vertical', size_hint=(1, None), height=(UI.BTN_SMALL_H*3 + UI.SPACING_SM*2 + UI.PAD_XS*2),
                            spacing=UI.SPACING_SM, padding=(UI.PAD_XS, UI.PAD_XS))
        btn_edit_rates = Button(text='Редагувати курси')
        btn_add_currency = Button(text='Додати валюту')
        btn_save_wallet = Button(text='Зберегти гаманець')
        for _b in (btn_edit_rates, btn_add_currency, btn_save_wallet):
            _b.size_hint_y = None
            _b.height = UI.BTN_SMALL_H
            _b.size_hint_x = 1

        style_button(btn_edit_rates, role='small')
        style_button(btn_add_currency, role='small')
        style_button(btn_save_wallet, role='secondary')
        btn_row.add_widget(btn_edit_rates)
        btn_row.add_widget(btn_add_currency)
        btn_row.add_widget(btn_save_wallet)
        wallet_box.add_widget(btn_row)

        def refresh_wallet_table():
            table_list.clear_widgets()
            wallet_inputs.clear()
            money = char.get('money', {})
            # Update total
            total_label.text = f"Загалом у GP: {self.app.currency.total_to_gp(money)}"
            for code in self.app.currency.codes:
                card = Card(height=UI.INPUT_H + UI.ROW_H + UI.PAD_XS*2)
                # row: code + amount
                row = BoxLayout(size_hint=(1, None), height=UI.INPUT_H, spacing=UI.SPACING_SM)
                code_lbl = Label(text=code, size_hint=(None, 1), width=UI.W_CODE,
                                 font_size=UI.FS_MD, halign='left', valign='middle')
                code_lbl.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width), None)))
                amt = TextInput(text=str(money.get(code, 0.0)))
                style_textinput(amt, role='sm')
                row.add_widget(code_lbl)
                row.add_widget(amt)
                card.add_widget(row)
                rate_val = self.app.currency.rates.get(code, 1.0)
                rate_lbl = Label(text=f"1 {code} = {rate_val} GP", size_hint_y=None, height=UI.ROW_H,
                                 font_size=UI.FS_SM, halign='left', valign='middle')
                rate_lbl.bind(size=lambda inst, *_: setattr(inst, 'text_size', (max(1, inst.width - UI.PAD_XS), None)))
                card.add_widget(rate_lbl)
                table_list.add_widget(card)
                wallet_inputs.append((code, amt))

        refresh_wallet_table()
        btn_edit_rates.bind(on_release=lambda *_: self.edit_rates(char, refresh_callback=refresh_wallet_table))
        btn_add_currency.bind(on_release=lambda *_: self.add_currency(char, refresh_callback=refresh_wallet_table))

        def save_wallet(*_):
            for code, widget in wallet_inputs:
                try:
                    char['money'][code] = float(widget.text)
                except Exception:
                    char['money'][code] = 0.0
            self.app.save_characters()
            toast_phone('Готово', 'Гаманець збережено')
            refresh_wallet_table()  # залишаємо на вкладці

        btn_save_wallet.bind(on_release=save_wallet)
        refresh_wallet_table()
        tab_wallet.content = wallet_box
        panel.add_widget(tab_wallet)

                # ---------- Відкриття Popup з кнопками ----------
        popup_content = BoxLayout(orientation='vertical', spacing=UI.SPACING_SM, padding=UI.PAD_XS)
        popup_content.add_widget(panel)  # сам TabbedPanel

        # Кнопки Закрити і Видалити
        btn_row2 = BoxLayout(size_hint=(1, None), height=UI.BTN_BAR_H, spacing=UI.SPACING_SM, padding=(UI.PAD_XS, UI.PAD_XS))
        btn_close = Button(text='Закрити')
        btn_delete = Button(text='Видалити персонажа')
        style_button(btn_close, role='secondary')
        style_button(btn_delete, role='secondary')

        btn_close.bind(on_release=lambda *_: popup.dismiss())
        btn_delete.bind(on_release=lambda *_: self.delete_character(char, popup))

        btn_row2.add_widget(btn_close)
        btn_row2.add_widget(btn_delete)
        popup_content.add_widget(btn_row2)

        popup = Popup(title=f"Персонаж: {char['name']}", content=themed_container(popup_content, bg_index=2, overlay_opacity=0.60, use_image=False), size_hint=(0.98, 0.98), auto_dismiss=False)
        self.current_popup = popup
        popup.open()


        # ---------- Встановлюємо активну вкладку ----------
        for t in panel.tab_list:
            if t.text == start_tab:
                panel.switch_to(t)
                break

    def delete_character(self, char, popup):
        if char in self.app.characters:
            self.app.characters.remove(char)
            self.app.save_characters()
            popup.dismiss()
            self.refresh_ready_list()





# ====== App ======
class DnDApp(App):
    def build(self):
        self.currency=CurrencyManager()
        self.characters=[]
        self.load_characters()
        sm=ScreenManager()
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(CreateCharacter(name='create'))
        sm.add_widget(ReadyCharacters(name='ready'))
        return sm

    def save_characters(self):
        try:
            with open('characters.json','w',encoding='utf-8') as f:
                json.dump(self.characters,f,ensure_ascii=False,indent=2)
        except Exception as e:
            print('Save error:',e)

    def load_characters(self):
        try:
            with open('characters.json','r',encoding='utf-8') as f:
                self.characters=json.load(f)
        except Exception:
            self.characters=[]

if __name__=='__main__':
    DnDApp().run()

# NOTE: залишено як у вихідному файлі (не впливає на виконання).
DnDApp