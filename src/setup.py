from src import tools

# Nastavenie veľkosti, názvu okna
# definovanie obnovovacej frekvencie
SCREEN_SIZE = (560, 560)
CAPTION = "SIMON"
FPS = 60

# Zadefinovanie najpoužívanejších ciest
# ku súborom. Fonty, obrázky a zvuky.
FONT_PATH = "assets/fonts"
IMG_PATH = "assets/images"
SOUND_PATH = "assets/sounds"

# Načítanie fontov z priečinka a definovanie niekoľkých
# veľkostí pre písmo. Iné veľkosti by sa nemali používať.
FONTS = tools.load_fonts(FONT_PATH)
FONT_SIZES = {
    "xs": 10,
    "sm": 15,
    "md": 20,
    "lg": 25,
    "xl": 35,
    "2xl": 50,
    "3xl": 75
}

# Definovanie farieb
# V hre by sa mali používať len farby tu definované
COLORS = {
    "black": (0, 0, 0),
    "yellow": (252, 186, 3),
    "red": (235, 94, 42),
    "white": (255, 255, 255),
    "dark": (20, 20, 20),
    "light": (220, 220, 220),
    "background": (18, 32, 47),
}

# Čas v milisekundách udávajúci ako dlho bude
# dlaždica pri prehrávaní sekvencie svietiť/nesvietť
TILE_LIGHT_TIME = 300

# Čas v milisekundách udávajúci ako
# dlho bude dlaždica po stlačení svietiť
TILE_CLICK_LIGHT_TIME = 200

# Čas v milisekundách pre všeobecné elementy
# Napr. blikanie kurzora alebo textu na obrazovke
BLINK_TIME = 500

# Pridanie nových scén do hry TU
# List musí obsahovať názov scény v "snake_case"
# Samotná inicializácia scén prebieha v triede Game
SCENES = [
    "welcome",
    "main_menu",
    "my_stats",
    "stats",
    "credits",
    "show",
    "play",
    "game_over",
]

# Začiatočná scéna
START_SCENE = "welcome"

# Adresa servera
SERVER_URL = 'https://simon-backend.azurewebsites.net'
