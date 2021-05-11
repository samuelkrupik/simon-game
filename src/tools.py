import os
import unicodedata


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
