import os
import sys
from typing import Tuple, Callable
import pygame
import random as rnd


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
        self.bg = pygame.image.load(os.path.join('assets', 'images', 'buttons', f"btn_{_type}.png")).convert_alpha()
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
    def __init__(self, color: str, position: Tuple):
        self.color = color
        self.position = position
        self.img_off = pygame.image.load(os.path.join('assets', 'images', 'tiles', f"{color}.png")).convert_alpha()
        self.img_on = pygame.image.load(os.path.join('assets', 'images', 'tiles', f"{color}_on.png")).convert_alpha()
        super().__init__(position[0], position[1], self.img_off.get_width(), self.img_off.get_height())


class Font:
    def __init__(self, size, font: str = '', color: Tuple = (0, 0, 0), antialiasing: bool = False):
        if not font:
            font = 'assets/fonts/back_to_1982.ttf'
        self.font = pygame.font.Font(font, size)
        self.color = color
        self.AA = antialiasing

    def size(self, text: str):
        return self.font.size(text)

    def render(self, text: str):
        return self.font.render(text, self.AA, self.color)

    def draw(self, text: str, win, position: Tuple):
        rendered = self.render(text)
        win.blit(rendered, position)


class Menu:
    def __init__(self, pos: Tuple, size: Tuple, title: str = "Menu", bg_color: Tuple = (0, 0, 0), margin: int = 20):
        self.buttons_height = 0
        self.x = pos[0]
        self.y = pos[1]
        self.width = size[0]
        self.height = size[1]
        self.title = title
        self.bg_color = bg_color
        self.margin = margin
        self.buttons = []
        self.buttons_height = 0

    def add_button(self, text: str, color: str, action: Callable):
        # create button - set position to origin
        self.buttons.insert(0, Button(text, (0, 0), action, color))
        # recalculate all positions
        self._recalculate_button_positions()

    def _recalculate_button_positions(self):
        self.buttons_height += self.buttons[0].height + self.margin
        print(self.buttons_height)
        for i in range(len(self.buttons)):
            self.buttons[i].set_position(
                (
                    self.width / 2 - self.buttons[i].width/2,
                    self.height / 2 - self.buttons_height / 2 + ((self.buttons[i].height + self.margin) * i)
                )
            )

    def draw(self, win):
        pygame.draw.rect(win, self.bg_color, (self.x, self.y, self.width, self.height))
        font = Font(30, color=(252, 186, 3))
        tw, th = font.size(self.title)
        font.draw(self.title, win, (self.width / 2 - tw / 2, 10))
        for button in self.buttons:
            button.draw(win)


class Game:

    def __init__(self, caption: str = "Game"):
        pygame.font.init()
        pygame.display.set_caption(caption)
        self.bg_color = (18, 32, 47)
        self.gen_sequence = []
        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode((560, 560))
        self.screen_rect = self.win.get_rect()
        self.game_state = 0  # 0 -> menu | 1 -> computer is displaying sequence | 2 -> user move | 3 -> game paused
        self.click_count = 0
        self.score = 0
        self._init_menus()
        self._init_tiles()

    def run(self, fps: int = 60):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

            self.clock.tick(fps)
            self.inputs()
            self.redraw_window()

    def redraw_window(self):
        if self.game_state == 0:
            self._draw_menu()
        if self.game_state == 1:
            self.win.fill(self.bg_color)
            for tile in self.tiles['tiles']:
                self.win.blit(tile.img_off, tile.position)
        pygame.display.update()

    def _init_tiles(self):
        self.tiles = {
            "tiles": [
                Tile("red", (self.screen_rect.width / 2 + 10, 20)),
                Tile("blue", (self.screen_rect.width / 2 + 10, self.screen_rect.height / 2 + 10)),
                Tile("yellow", (20, self.screen_rect.height / 2 + 10)),
                Tile("green", (20, 20)),
            ],
            "sequence": [],
            "light_time": 200
        }

    def _generate(self):
        self.gen_sequence.append(rnd.randrange(1, 4))

    def pause(self):
        self.pause_menu.draw(self.win)

    def inputs(self):
        gs = self.game_state
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # if in menu
                if gs == 0:
                    for button in self.menu.buttons:
                        if button.mouse_over(mouse_pos):
                            button.click(button.action)
                # if user can play (sequence not playing)
                if gs == 2:
                    for tile in self.tiles['tiles']:
                        if tile.mouse_over(mouse_pos):
                            tile.click(self.check_click, tile)

        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            if gs == 1 or gs == 2:
                self.game_state = 0
            if gs == 3:
                self.game_state = 2

    def play(self):
        self.game_state = 1

    def resume(self):
        pass

    def set_game_state(self):
        pass

    def exit(self):
        pygame.quit()

    def _draw_menu(self):
        self.menu.draw(self.win)

    def _init_menus(self):
        # main menu
        self.menu = Menu((0, 0), self.screen_rect.size, bg_color=self.bg_color)
        self.menu.add_button("PLAY!", 'primary', self.play)
        self.menu.add_button("EXIT", 'danger', self.exit)
        # pause menu
        self.pause_menu = Menu((0, 0), self.screen_rect.size, "Pause")
        self.pause_menu.add_button('RESUME', 'primary', self.resume)
        self.pause_menu.add_button('MAIN MENU', 'primary', self.set_game_state)

    def check_click(self, tile):
        if tile.id == self.gen_sequence[self.click_count]:
            self.click_count += 1
            return True
        return False
