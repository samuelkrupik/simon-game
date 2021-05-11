import json
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
        self.sound = pg.mixer.Sound(tools.parse_path(setup.SOUND_PATH, "buttons", "button.wav"))
        super().__init__(pos[0], pos[1], self.bg.get_width(), self.bg.get_height())

    def draw(self, win):
        win.blit(self.bg, self.pos)
        win.blit(self.text, (
            self.x + (self.bg.get_width() / 2 - self.text.get_width() / 2),
            self.y + (self.bg.get_height() / 2 - self.text.get_height() / 2)
        ))

    def set_position(self, pos):
        self.pos = pos
        self.x, self.y = pos

    def set_text(self, text):
        self.text = self.font.render(text)


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
        Vytvorí pygame font podla zadaného fontu
        Je možné použiť iba fonty naimportované v setupe
        :param _font: Font z pričinka assets/fonts
        :param size: Veľkost definovaná v setupe
        :param color: Farba definovaná v setupe
        """
        self.font = pg.font.Font(setup.FONTS[_font], setup.FONT_SIZES[size])
        self.color = setup.COLORS[color]

    def render(self, text: str, multiline: bool = False):
        if not multiline:
            return self.font.render(text, False, self.color)

    def draw(self, text: str, screen, pos: Tuple, multiline: bool = False):
        if multiline:
            rows = tools.split_multiline(text)
            for i, row in enumerate(rows):
                tw, th = self.font.size(row)

class InputBox:
    def __init__(self, pos: Tuple = None):
        self.pos = None
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
        Aktivácia boxu - spustí sa len v prípade ak má box definovanú
        pozíciu. Pozícia môže byť definovaná v konštruktore alebo pri vykreslení
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
        Obnovenie textboxu - ak je textbox aktívny skontroluje
        a prípadne obnoví časovač blikania kurzora
        """
        if self.active and now - setup.BLINK_TIME > self.timer:
            self.cursor_visible = not self.cursor_visible
            self.timer = now

    def input(self, event, on_confirm: Callable, params: Tuple = ()):
        """
        Vstup do text inputu - skontroluje či je aktívny,
        získa stlačene klávesy a podla toho vykoná prislušnú akciu.
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
        Ak inputbox nemá definovanu pozíciu, zadefinuje ju.
        Potom vykreslí na obrazovku textbox so zadaným textom,
        ak je aktivovaný bude sa vykresľovat aj kurzor.
        """
        if not self.pos:
            self._set_pos(pos)
        text = self.font.render(self.value)
        tw, th = text.get_size()
        screen.blit(self.bg, self.pos)
        screen.blit(text, (self.x + self.width / 2 - tw / 2, self.y + self.height / 2 - th / 2))
        if self.active and self.cursor_visible:
            pg.draw.rect(screen, (0, 0, 0),
                         (self.x + self.width / 2 + tw / 2, self.y + self.height / 2 - th / 2, 2, th))

    def get_value(self):
        """Vráti hodnotu inputboxu očistenú od medzier"""
        return self.value.strip()

    def _set_pos(self, pos):
        """Nastaví pozíciu"""
        self.pos = pos
        self.x, self.y = pos

    def validate(self, min_length: int = 1, max_length: int = 999):
        """
        Skontroluje zadaný text podľa udaných parametrov
        minimálnej a maximálnej dĺžky a vráti prislušnú správu.
        """
        if not len(self.get_value()) >= min_length:
            return {
                'success': False,
                'message': "Value must be at least " + str(min_length) + " characters long!"
            }
        elif not len(self.get_value()) <= max_length:
            return {
                'success': False,
                'message': "Value must be at most " + str(max_length) + " characters long!"
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
        # create button - set position to origin
        self.buttons.append(Button(text, (0, 0), action, params, _type))
        # recalculate all positions
        self._recalculate_button_positions()

    def _recalculate_button_positions(self):
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
        mouse_pos = pg.mouse.get_pos()
        for button in self.buttons:
            if button.mouse_over(mouse_pos):
                if event.type == pg.MOUSEBUTTONDOWN:
                    button.click(button.action)
                elif event.type == pg.MOUSEMOTION:
                    if not self.last_hovered == button:
                        self.last_hovered = button
                        button.sound.play()
            else:
                if button == self.last_hovered:
                    self.last_hovered = None

    def draw(self, screen):
        font = Font('vintage', 'xl', 'yellow')
        text = font.render(self.title)
        tw, th = text.get_size()
        screen.blit(text, (self.width / 2 - tw / 2, self.margin))
        for button in self.buttons:
            button.draw(screen)
