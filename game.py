import os
from typing import Tuple, Callable

import pygame
import random as rnd

class Game:

    def __init__(self, caption: str = "Game"):
        pygame.font.init()
        pygame.display.set_caption(caption)
        self.bg_color = (18, 32, 47)
        self.gen_sequence = []
        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode((560, 560))
        self.screen_rect = self.win.get_rect()
        self.menu_active = True
        self.__load_tiles()

    def run(self, fps: int = 60):
        running = True
        while running:
            self.clock.tick(fps)
            self.redraw_window()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    def __draw_menu(self, win):
        font = Font(100)
        text = font.render("Menu", (211, 142, 35))
        button = Button("My button", 10, 10, 15, (255, 0, 0), (48, 36, 154), padding=(25, 20))
        button.draw(win)
        win.blit(text, (200, 200))

    def redraw_window(self):
        self.win.fill(self.bg_color)
        for color, tile in self.tiles.items():
            self.win.blit(tile['image_off'], tile['position'])
        pygame.display.update()
        print("update")

    def __load_tiles(self):
        self.tiles = {
            "red": {
                "id": 1,
                "position": (self.screen_rect.width / 2 + 10, 21)
            },
            "blue": {
                "id": 2,
                "position": (self.screen_rect.width / 2 + 10, self.screen_rect.height / 2 + 10)
            },
            "yellow": {
                "id": 3,
                "position": (21, self.screen_rect.height / 2 + 10)
            },
            "green": {
                "id": 4,
                "position": (21, 21)
            }
        }
        for color in self.tiles:
            tile_off = pygame.image.load(os.path.join('assets', 'images', 'tiles', f"{color}.png"))
            tile_on = pygame.image.load(os.path.join('assets', 'images', 'tiles', f"{color}_on.png"))
            self.tiles[color]["image_off"] = tile_off.convert_alpha()
            self.tiles[color]["image_on"] = tile_on.convert_alpha()

    def _generate(self):
        self.gen_sequence.append(rnd.randrange(1,4))


class Font:
    def __init__(self, size, font: str = ''):
        if not font:
            font = 'assets/fonts/back_to_1982.ttf'
        self.font = pygame.font.Font(font, size)

    def render(self, text: str, color: Tuple = (0, 0, 0), antialiasing: bool = False):
        return self.font.render(text, antialiasing, color)


class Button:
    def __init__(
            self, text: str,
            x: int,
            y: int,
            font_size: int = 10,
            font_color: Tuple = (0, 0, 0),
            bg_color: Tuple = (255, 255, 255),
            padding: Tuple = (10, 10),
            antialiasing: bool = False
    ):
        self.x = x
        self.y = y
        font = Font(font_size)
        self.text = font.render(text, font_color, antialiasing)
        self.full_width = self.text.get_width() + padding[0] * 2
        self.full_height = self.text.get_height() + padding[1] * 2
        self.bg_color = bg_color
        self.padding = padding

    def draw(self, win):
        pygame.draw.rect(win, self.bg_color, (self.x, self.y, self.full_width, self.full_height))
        win.blit(self.text, (self.x + self.padding[0], self.y + self.padding[1]))

    def click(self, _mouse_pos):
        x1 = _mouse_pos[0]
        y1 = _mouse_pos[1]
        if self.x <= x1 <= self.x + self.full_width and self.y <= y1 <= self.y + self.full_height:
            return True
        else:
            return False
