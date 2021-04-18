import random

from src.components import Tile
from src.scenes import WelcomeScene, MainMenuScene, ShowScene, PlayScene, GameOverScene
import pygame as pg


class Player:
    def __init__(self):
        self.name = ""
        self.score = 0
        self.click_count = 0


class Game:
    def __init__(self):
        """Standard setup and initial scene creation."""
        self.screen = pg.display.get_surface()
        self.player = Player()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.width, self.height = self.screen.get_size()
        self.colors = {"background": (18, 32, 47)}
        self.tiles = [
            Tile(1, "red", (self.width/ 2 + 10, 20)),
            Tile(2, "blue", (self.width / 2 + 10, self.height / 2 + 10)),
            Tile(3, "yellow", (20, self.width / 2 + 10)),
            Tile(4, "green", (20, 20))
        ]
        self.sequence = []
        self.running = True

    def generate_next(self):
        self.sequence.append(random.randrange(1,4))


class Controller:
    def __init__(self):
        self.game = Game()
        self.scenes = {
            "welcome": WelcomeScene(self.game),
            "main_menu": MainMenuScene(self.game),
            "show": ShowScene(self.game),
            "play": PlayScene(self.game),
            "game_over": GameOverScene(self.game),
        }
        self.scene = self.scenes['welcome']

    def get_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.running = False
            self.scene.handle_event(event)

    def update(self):
        now = pg.time.get_ticks()
        self.scene.update(now)
        if self.scene.done:
            self.scene.reset()
            self.scene = self.scenes[self.scene.next]

    def draw(self):
        self.game.screen.fill(self.game.colors['background'])
        if self.scene.start_time:
            self.scene.draw()

    def main_loop(self):
        while self.game.running:
            self.get_events()
            self.update()
            self.draw()
            pg.display.update()
            self.game.clock.tick(self.game.fps)
