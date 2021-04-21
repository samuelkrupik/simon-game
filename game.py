import datetime
import json
import random
import os.path
from src.components import Tile
from src.scenes import WelcomeScene, MainMenuScene, SettingsMenuScene, CreditsScene, ShowScene, PlayScene, GameOverScene
import pygame as pg


class DB:
    def __init__(self):
        self.db = os.path.join('data', 'db.json')

    def get_player(self, name):
        with open(self.db, "r") as db:
            data = json.load(db)
            for user in data['users']:
                if user['name'] == name:
                    return user
            return None

    def create_player(self, player):


        with open(self.db, "a") as db:
            data = {'users': []}
            print(data)
            data['users'].append({
                "name": player.name,
                "high_score": 0,
                "last_played": player.last_played
            })
            db.write(json.dumps(data))
            db.close()

    def update_player(self, player):
        with open(self.db, "w") as db:
            data = json.load(db)
            for user in data['users']:
                if user['name'] == player.name:
                    user['high_score'] = player.high_score
                    user['last_played'] = player.last_played

            db.write(json.dumps(data))
            db.close()

class Player:
    def __init__(self):
        self.name = ""
        self.score = 0
        self.high_score = 0
        self.click_count = 0
        self.last_played = datetime.datetime.now().timestamp()


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
        self.is_music = True
        self.running = True

    def generate_next(self):
        self.sequence.append(random.randrange(1,4))


class Controller:
    def __init__(self):
        self.game = Game()
        self.db = DB()
        self.scenes = {
            "welcome": WelcomeScene(self.game, self.db),
            "main_menu": MainMenuScene(self.game),
            "settings_menu": SettingsMenuScene(self.game),
            "credits": CreditsScene(self.game),
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
            self.scene.update(now)  # another update to ensure new scene is loaded

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
