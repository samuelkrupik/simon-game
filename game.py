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
        self.game_state = 0  # 0 -> menu | 1 -> computer is displaying sequence | 2 -> user move
        self.click_count = 0
        self.score = 0
        self.__load_tiles()

    def run(self, fps: int = 60):
        running = True
        while running:
            self.clock.tick(fps)

            if self.game_state == 2:
                self._listen_clicks()
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
        for tile in self.tiles:
            self.win.blit(tile.img_off, tile.position)
        pygame.display.update()
        print("update")

    def __load_tiles(self):
        self.tiles = [
            Tile("red", (self.screen_rect.width / 2 + 10, 20)),
            Tile("blue", (self.screen_rect.width / 2 + 10, self.screen_rect.height / 2 + 10)),
            Tile("yellow", (20, self.screen_rect.height / 2 + 10)),
            Tile("green", (20, 20)),
        ]

    def _generate(self):
        self.gen_sequence.append(rnd.randrange(1, 4))

    def _listen_clicks(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for tile in self.tiles:
                    if tile.mouse_over(mouse_pos):
                        tile.click(self.check_click, tile)

    def check_click(self, tile):
        if tile.id == self.gen_sequence[self.click_count]:
            self.click_count += 1
            return True
        return False


class Font:
    def __init__(self, size, font: str = ''):
        if not font:
            font = 'assets/fonts/back_to_1982.ttf'
        self.font = pygame.font.Font(font, size)

    def render(self, text: str, color: Tuple = (0, 0, 0), antialiasing: bool = False):
        return self.font.render(text, antialiasing, color)


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

    def click(self, callback, *args, **kwargs):
        callback(*args, **kwargs)


class Tile(Clickable):
    def __init__(self, color: str, position: Tuple):
        self.color = color
        self.position = position
        self.img_off = pygame.image.load(os.path.join('assets', 'images', 'tiles', f"{color}.png")).convert_alpha()
        self.img_on = pygame.image.load(os.path.join('assets', 'images', 'tiles', f"{color}_on.png")).convert_alpha()
        super().__init__(position[0], position[1], self.img_off.get_width(), self.img_off.get_height())


class Button(Clickable):
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
        font = Font(font_size)
        self.text = font.render(text, font_color, antialiasing)
        self.bg_color = bg_color
        self.padding = padding
        super().__init__(x, y, self.text.get_width() + padding[0] * 2, self.text.get_height() + padding[1] * 2)

    def draw(self, win):
        pygame.draw.rect(win, self.bg_color, (self.x, self.y, self.width, self.height))
        win.blit(self.text, (self.x + self.padding[0], self.y + self.padding[1]))
