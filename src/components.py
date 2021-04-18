import json
import os
from typing import Callable, Tuple
import pygame as pg


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

    def click(self, callback: Callable, *args, **kwargs):
        callback(*args, **kwargs)


class Button(Clickable):
    def __init__(
            self, text: str,
            position: Tuple,
            action: Callable,
            _type: str = "primary"
    ):
        self.bg = pg.image.load(os.path.join("assets", "images", "buttons", f"btn_{_type}.png")).convert_alpha()
        font = Font(18) if _type == 'primary' else Font(18, color=(255, 255, 255))
        self.text = font.render(text)
        self.position = position
        self.action = action
        super().__init__(position[0], position[1], self.bg.get_width(), self.bg.get_height())

    def draw(self, win):
        win.blit(self.bg, self.position)
        win.blit(self.text, (
            self.x + (self.bg.get_width() / 2 - self.text.get_width() / 2),
            self.y + (self.bg.get_height() / 2 - self.text.get_height() / 2)
        ))

    def set_position(self, pos):
        self.position = pos
        self.x = pos[0]
        self.y = pos[1]


class Tile(Clickable):
    def __init__(self, _id: int, color: str, position: Tuple):
        self.id = _id
        self.color = color
        self.position = position
        self.img_off = pg.image.load(os.path.join("assets", "images", "tiles", f"{color}.png")).convert_alpha()
        self.img_on = pg.image.load(os.path.join("assets", "images", "tiles", f"{color}_on.png")).convert_alpha()
        super().__init__(position[0], position[1], self.img_off.get_width(), self.img_off.get_height())


class Font:
    def __init__(self, size, color: Tuple = (0, 0, 0)):
        self.font = pg.font.Font(os.path.join('assets', 'fonts', 'back_to_1982.ttf'), size)
        self.color = color

    def size(self, text: str):
        return self.font.size(text)

    def render(self, text: str):
        return self.font.render(text, False, self.color)


class InputBox:
    def __init__(self, pos: Tuple):
        self.pos = pos
        self.x, self.y = pos
        self.bg = pg.image.load(os.path.join('assets', 'images', 'text_input', "text_box.png")).convert_alpha()
        self.width, self.height = self.bg.get_size()
        self.value = ""
        self.font = Font(18)
        self.active = True

    def activate(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = pg.mouse.get_pos()
            if self.x <= mx <= self.x+self.width:
                if self.y <= mx <= self.y+self.height:
                    self.active = True
                    return
            self.active = False

    def input(self, event):
        if not self.active:
            self.activate(event)
        if self.active:
            if event.type == pg.KEYDOWN:
                key = pg.key.get_pressed()
                # backspace -> remove last character from value
                if key[pg.K_BACKSPACE]:
                    self.value = self.value[:-1]
                else:
                    self.value += event.unicode
                    print(self.value)

    def draw(self, screen):
        screen.blit(self.bg, self.pos)
        text = self.font.render(self.value)
        tw, th = text.get_size()
        screen.blit(text, (self.x + self.width / 2 - tw / 2, self.y + self.height / 2 - th / 2))

    def save_JSON(self, filename: str):
        # if file has suffix remove it
        if filename.endswith(".json"):
            filename = filename.replace(".json", "")
        # open file
        with open(f"{filename}.json") as file:
            # load data
            data = json.load(file)
            for item in data:
                print(item)


class Menu:
    def __init__(self, title: str = "Menu", margin: int = 20):
        self.buttons_height = 0
        self.width, self.height = pg.display.get_surface().get_size()
        self.title = title
        self.margin = margin
        self.buttons = []
        self.buttons_height = 0

    def add_button(self, text: str, _type: str, action: Callable):
        # create button - set position to origin
        self.buttons.insert(0, Button(text, (0, 0), action, _type))
        # recalculate all positions
        self._recalculate_button_positions()

    def _recalculate_button_positions(self):
        self.buttons_height += self.buttons[0].height + self.margin
        print(self.buttons_height)
        for i in range(len(self.buttons)):
            self.buttons[i].set_position(
                (
                    self.width / 2 - self.buttons[i].width / 2,
                    self.height / 2 - self.buttons_height / 2 + ((self.buttons[i].height + self.margin) * i)
                )
            )

    def draw(self, screen):
        font = Font(30, color=(252, 186, 3))
        text = font.render(self.title)
        tw, th = text.get_size()
        screen.blit(text, (self.width / 2 - tw / 2, self.margin))
        for button in self.buttons:
            button.draw(screen)
