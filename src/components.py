import os
from typing import Callable, Tuple
import pygame as pg

from src import tools, setup


class Clickable:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def mouse_over(self, mouse_pos):
        mx = mouse_pos[0]
        my = mouse_pos[1]
        if self.x <= mx <= self.x + self.width:
            if self.y <= my <= self.y + self.height:
                return True
        return False

    def click(self, callback: Callable, params: Tuple = ()):
        callback(*params)


class Button(Clickable):
    def __init__(
            self, text: str,
            pos: Tuple,
            action: Callable,
            params: Tuple = (),
            _type: str = "primary"
    ):
        self.bg = pg.image.load(os.path.join("assets", "images", "buttons", f"btn_{_type}.png")).convert_alpha()
        self.font = Font('regular') if _type == 'primary' else Font('regular', color='white')
        self.set_text(text)
        self.pos = pos
        self.type = _type
        self.action = action
        self.params = params
        self.hovering = False
        self.sound = pg.mixer.Sound(tools.parse_path(setup.SOUND_PATH, "buttons", "button.wav"))
        super().__init__(pos[0], pos[1], self.bg.get_width(), self.bg.get_height())

    def draw(self, win):
        win.blit(self.bg, self.pos)
        win.blit(self.text, (
            self.x + (self.bg.get_width() / 2 - self.text.get_width() / 2),
            self.y + (self.bg.get_height() / 2 - self.text.get_height() / 2)
        ))

    def handle_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if self.mouse_over(mouse_pos):
            if event.type == pg.MOUSEBUTTONDOWN:
                self.click()
            elif event.type == pg.MOUSEMOTION:
                if not self.hovering:
                    self.hovering = True
                    self.sound.play()
        else:
            self.hovering = False

    def set_position(self, pos):
        self.pos = pos
        self.x, self.y = pos

    def set_text(self, text):
        self.text = self.font.render(text)

    def click(self, callback: Callable = None, params: Tuple = ()):
        if callback:
            super().click(callback, params)
        self.action(*self.params)


class Tile(Clickable):
    def __init__(self, _id: int, color: str, position: Tuple):
        self.id = _id
        self.color = color
        self.position = position
        self.blink_time = setup.TILE_LIGHT_TIME
        self.active = False
        self.sound = pg.mixer.Sound(tools.parse_path(setup.SOUND_PATH, "tiles", f"{color}.wav"))
        self.img_off = pg.image.load(tools.parse_path(setup.IMG_PATH, "tiles", f"{color}.png")).convert_alpha()
        self.img_on = pg.image.load(tools.parse_path(setup.IMG_PATH, "tiles", f"{color}_on.png")).convert_alpha()
        super().__init__(position[0], position[1], self.img_off.get_width(), self.img_off.get_height())

    def get_img(self):
        if self.active:
            return self.img_on
        else:
            return self.img_off

    def play_sound(self):
        if self.active:
            self.sound.play()

    def click(self, callback: Callable, params: Tuple = ()):
        super().click(callback, params)
        self.play_sound()


class Font:
    def __init__(self, _font: str = "regular", size: str = "md", color: str = "black"):
        """
        Vytvor?? pygame font podla zadan??ho fontu
        Je mo??n?? pou??i?? iba fonty naimportovan?? v setupe
        :param _font: Font z pri??inka assets/fonts
        :param size: Ve??kost definovan?? v setupe
        :param color: Farba definovan?? v setupe
        """
        self.font = pg.font.Font(setup.FONTS[_font], setup.FONT_SIZES[size])
        self.color = setup.COLORS[color]

    def render(self, text: str):
        return self.font.render(text, False, self.color)


class InputBox:
    def __init__(self, pos: Tuple = None, placeholder: str = ""):
        self.pos = None
        self.placeholder = placeholder
        self.x, self.y = None, None
        self.bg = pg.image.load(tools.parse_path(setup.IMG_PATH, 'text_input', "ti_white.png")).convert_alpha()
        self.width, self.height = self.bg.get_size()
        self.value = ""
        self.font = Font(size='sm')
        self.active = False
        self.timer = 0
        self.cursor_visible = False
        self._set_pos(pos) if pos else None

    def activate(self):
        """
        Aktiv??cia boxu - spust?? sa len v pr??pade ak m?? box definovan??
        poz??ciu. Poz??cia m????e by?? definovan?? v kon??truktore alebo pri vykreslen??
        """
        if not self.pos:
            return
        mx, my = pg.mouse.get_pos()
        if self.x <= mx <= self.x + self.width:
            if self.y <= my <= self.y + self.height:
                self.active = True
                return
        self.active = False

    def update(self, now):
        """
        Obnovenie textboxu - ak je textbox akt??vny skontroluje
        a pr??padne obnov?? ??asova?? blikania kurzora
        """
        if self.active and now - setup.BLINK_TIME > self.timer:
            self.cursor_visible = not self.cursor_visible
            self.timer = now

    def input(self, event, on_confirm: Callable, params: Tuple = ()):
        """
        Vstup do text inputu - skontroluje ??i je akt??vny,
        z??ska stla??ene kl??vesy a podla toho vykon?? prislu??n?? akciu.
        [BACKSPACE -> mazanie, ENTER -> callback, * -> pridanie znaku]
        """
        if self.active:
            key = pg.key.get_pressed()
            # backspace -> remove last character from value
            if key[pg.K_BACKSPACE]:
                self.value = self.value[:-1]
            elif key[pg.K_RETURN]:
                on_confirm(*params)
            else:
                self.value += tools.strip_accents(event.unicode)

    def draw(self, screen, pos: Tuple):
        """
        Ak inputbox nem?? definovanu poz??ciu, zadefinuje ju.
        Potom vykresl?? na obrazovku textbox so zadan??m textom,
        ak je aktivovan?? bude sa vykres??ovat aj kurzor.
        """
        if not self.pos:
            self._set_pos(pos)
        if not self.value and not self.active:
            text = self.font.render(self.placeholder)
        else:
            text = self.font.render(self.value)
        tw, th = text.get_size()
        screen.blit(self.bg, self.pos)
        screen.blit(text, (self.x + self.width / 2 - tw / 2, self.y + self.height / 2 - th / 2))
        if self.active and self.cursor_visible:
            pg.draw.rect(screen, (0, 0, 0),
                         (self.x + self.width / 2 + tw / 2, self.y + self.height / 2 - th / 2, 2, th))

    def get_value(self):
        """Vr??ti hodnotu inputboxu o??isten?? od medzier"""
        return self.value.strip()

    def _set_pos(self, pos):
        """Nastav?? poz??ciu"""
        self.pos = pos
        self.x, self.y = pos

    def validate(self, min_length: int = 1, max_length: int = 999):
        """
        Skontroluje zadan?? text pod??a udan??ch parametrov
        minim??lnej a maxim??lnej d????ky a vr??ti prislu??n?? spr??vu.
        """
        if not len(self.get_value()) >= min_length:
            return {
                'success': False,
                'message': "Please, enter at least " + str(min_length) + " characters."
            }
        elif not len(self.get_value()) <= max_length:
            return {
                'success': False,
                'message': "Please, enter max." + str(max_length) + " characters."
            }
        else:
            return {'success': True}


class Menu:
    def __init__(self, title: str = "Menu", margin: int = 20):
        self.buttons_height = 0
        self.width, self.height = pg.display.get_surface().get_size()
        self.title = title
        self.margin = margin
        self.buttons = []
        self.buttons_height = 0
        self.last_hovered = None

    def add_button(self, text: str, action: Callable, params: Tuple = (), _type: str = 'primary'):
        """
        Vytvor?? tla??idlo, a n??slednej prepo????ta
        poz??cie v??etk??ch tla??idiel v menu
        """
        self.buttons.append(Button(text, (0, 0), action, params, _type))
        self._recalculate_button_positions()

    def _recalculate_button_positions(self):
        """Prepo????ta poz??cie tla??idiel"""
        self.buttons_height += self.buttons[0].height + self.margin
        i = 0
        for button in self.buttons:
            button.set_position(
                (
                    self.width / 2 - button.width / 2,
                    self.height / 2 - self.buttons_height / 2 + ((button.height + self.margin) * i)
                )
            )
            i += 1

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, screen):
        font = Font('vintage', 'xl', 'yellow')
        text = font.render(self.title)
        tw, th = text.get_size()
        screen.blit(text, (self.width / 2 - tw / 2, self.margin))
        for button in self.buttons:
            button.draw(screen)


class Table:
    def __init__(self, title: str, data: list, numbering: bool = True):
        self.width, self.height = pg.display.get_surface().get_size()
        self.data = data
        self.numbering = numbering
        self.table = []
        self.title = title
        self.title_font = Font('vintage', 'xl', 'yellow')
        self.header_font = Font('vintage', 'lg', 'yellow')
        self.data_font = Font('regular', 'sm', 'white')
        self.padding = 20
        self.col_count = 0
        self.col_width = self.width

    def add_column(self, col_name: str, key: str, formatter: Callable = None):
        """
        Prid?? st??pec do tabu??ky
        :param col_name: N??zov hlavi??ky st??pca
        :param key: K?????? pre d??ta
        :param formatter: Preform??tovanie d??t
        """
        self.table.append({
            "header": col_name,
            "data": [i[key] for i in self.data]
        })
        if formatter:
            self.table[-1]["data"] = list(map(formatter, self.table[-1]["data"]))
        if self.numbering and self.table[0]["header"] != "No.":
            self.table.insert(0, {
                "header": "No.",
                "data": list(range(1, len(self.data) + 1))
            })
        self.col_width = self.width / len(self.table)

    def draw(self, screen):
        t_text = self.title_font.render(self.title)
        screen.blit(t_text, (self.width / 2 - t_text.get_width() / 2, self.padding))
        for i, col in enumerate(self.table):
            h_txt = self.header_font.render(col['header'])
            screen.blit(h_txt, (i * self.col_width + self.padding, t_text.get_height() + self.padding * 2))
            for j, item in enumerate(col['data']):
                d_text = self.data_font.render(str(item))
                screen.blit(d_text, (
                    i * self.col_width + self.padding,
                    j * (d_text.get_height() * 1.5) + h_txt.get_height() + t_text.get_height() + self.padding * 3))
