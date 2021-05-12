import os
import time
import unicodedata
from datetime import datetime, timedelta
import requests


def parse_path(path: str, *paths):
    """
    Vytvorí cestu za použitia správnych separátov
    Cesta vstupujuca do funkcie musí bať oddelena znakom '/'
    Okrem prvého argumentu je možné pridať aj dalšie cesty alebo názov súboru
    """
    path_list = path.split('/')
    return os.path.join(*path_list, *paths)


def load_fonts(font_dir: str):
    """
    Prehľadá špecifikovaný priečinok s fontami a vráti dictionary
    kde kľuč je názov fontu bez koncovky a hodnota je cesta k fontu
    """
    fonts = {}
    font_list = os.listdir(parse_path(font_dir))
    for font in font_list:
        name, ext = os.path.splitext(font)
        fonts[name] = parse_path(font_dir, font)
    return fonts


def snake_to_pascal(text: str):
    """Konvertuje text zo 'snake_case' do 'PascalCase'"""
    return text.replace("_", " ").title().replace(" ", "")


def strip_accents(text: str):
    """Odstráni/ nahradí špeciálne znaky (napr. ščťž -> sctz)"""
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')


def split_multiline(text: str):
    """
    Konvertuje blok textu z viacerými riadkami na
    list s jednotlivými riadkami. (Podľa znaku '\n')
    """
    return list(filter(lambda x: len(x) > 0, text.split("\n")))


def check_internet():
    """Detekuje či je používateľ pripojený k internetu"""
    connection = None
    try:
        r = requests.head("https://google.com", timeout=5)
        r.raise_for_status()
        print("Internet connection detected.")
        connection = True
    except:
        print("Internet connection not detected.")
        connection = False
    finally:
        return connection


def get_utc_offset():
    """Vráti hodnotu reprezentujúcu posun v hodínách od UTC času"""
    utc = time.gmtime()
    local = time.localtime()
    return local.tm_hour - utc.tm_hour


def str_to_date(datestr: str, _format: str = "%a, %d %b %Y %H:%M:%S -%f"):
    """
    Skonvertuje text na datetime objekt so správnym posunom času
    V prípade ak sa nepodarí dátum skonvertovať, vráti aktuálny dátum
    """
    offset = get_utc_offset()
    date = None
    try:
        date = datetime.strptime(datestr, _format) + timedelta(hours=offset)
    except:
        date = datetime.now()
    finally:
        return date


def format_date(datestr: str):
    """Formátuje dátum z reťazca"""
    date = str_to_date(datestr)
    return date.strftime('%d %b %Y')
