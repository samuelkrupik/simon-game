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
    def __init__(self, _id: int, color: str, position: Tuple):
        self.id = _id
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

class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.click_count = 0


class Game:

    def __init__(self, caption: str = "Game"):
        pygame.font.init()
        pygame.display.set_caption(caption)
        self.bg_color = (18, 32, 47)
        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode((560, 560))
        self.screen_rect = self.win.get_rect()
        self.game_state = 0  # 0 -> menu | 1 -> playing sequence | 2 -> user move | 3 -> game paused | 4 -> game over
        self.click_count = 0
        self.score = 0
        self.player = Player('Samo')
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

    def _draw_sequence(self):
        # generate new number to sequence
        self._generate()
        # sequence loop
        for tile_id in self.tiles['sequence']:
            # fill window
            self.win.fill(self.bg_color)
            # display powered off tiles
            for tile in self.tiles['tiles']:
                self.win.blit(tile.img_off, tile.position)
            pygame.display.update()
            pygame.time.delay(self.tiles['light_time'])
            # fill window again
            self.win.fill(self.bg_color)
            # display powered on tile and others as off
            for tile in self.tiles['tiles']:
                if tile.id != tile_id:
                    self.win.blit(tile.img_off, tile.position)
                else:
                    self.win.blit(tile.img_on, tile.position)
            pygame.display.update()
            pygame.time.delay(self.tiles['light_time'])
            self.tiles['curr_id'] += 1
        # done playing -> reset
        if self.tiles['curr_id'] == len(self.tiles['sequence']):
            self.tiles['curr_id'] = 0
            self.game_state = 2

    def _draw_user_move(self):
        self.win.fill(self.bg_color)
        for tile in self.tiles['tiles']:
            self.win.blit(tile.img_off, tile.position)

    def redraw_window(self):
        if self.game_state == 0:
            self._draw_menu()
        elif self.game_state == 1:
            self._draw_sequence()
        elif self.game_state == 2:
            self._draw_user_move()
        pygame.display.update()

    def _init_tiles(self):
        self.tiles = {
            "tiles": [
                Tile(1, "red", (self.screen_rect.width / 2 + 10, 20)),
                Tile(2, "blue", (self.screen_rect.width / 2 + 10, self.screen_rect.height / 2 + 10)),
                Tile(3, "yellow", (20, self.screen_rect.height / 2 + 10)),
                Tile(4, "green", (20, 20)),
            ],
            "sequence": [],
            "light_time": 400,
            "curr_id": 0
        }

    def _generate(self):
        self.tiles['sequence'].append(rnd.randrange(1, 4))

    def pause(self):
        self.pause_menu.draw(self.win)

    def inputs(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # if in menu
                if self.game_state == 0:
                    for button in self.menu.buttons:
                        if button.mouse_over(mouse_pos):
                            button.click(button.action)
                # if user can play (sequence not playing)
                if self.game_state == 2:
                    for tile in self.tiles['tiles']:
                        if tile.mouse_over(mouse_pos):
                            tile.click(self.check_click, tile)

        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            pass

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
        print('clicked on tile', tile.id)
        print('current tile:', self.tiles['sequence'][self.player.click_count])
        if tile.id == self.tiles['sequence'][self.player.click_count]:
            self.player.click_count += 1
            if self.player.click_count == len(self.tiles['sequence']):
                print('click count is more than sequence -> resetting')
                self.player.score += 1
                self.player.click_count = 0
                self.game_state = 1
        # if player fails -> game over
        # else:
        #     self.game_state = 4
