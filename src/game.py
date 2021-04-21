import datetime
import random
import importlib
import pygame as pg
from src import setup, tools
from src.components import Tile


class Player:
    def __init__(self):
        self.name = ""
        self.score = 0
        self.high_score = 0
        self.click_count = 0
        self.last_played = datetime.datetime.now().timestamp()


class Game:
    def __init__(self):
        self.player = Player()
        self.screen = pg.display.get_surface()
        self.width, self.height = self.screen.get_size()
        self.clock = pg.time.Clock()
        self.tiles = [
            Tile(1, "red", (self.width / 2 + 10, 20)),
            Tile(2, "blue", (self.width / 2 + 10, self.height / 2 + 10)),
            Tile(3, "yellow", (20, self.width / 2 + 10)),
            Tile(4, "green", (20, 20))
        ]
        self.sequence = []
        self.is_music = True
        self.running = True
        self.scenes = self.attach_scenes()
        self.scene = self.scenes[setup.START_SCENE] if self.scenes else None

    def generate_next(self):
        """
        Vygeneruje ďalšie náhodné číslo do sekvencie
        Čísla od 1 do 4 súhlasia s id jednotlivých tiles
        """
        self.sequence.append(random.randrange(1, 4))

    def attach_scenes(self):
        """
        Dynamický import všetkých zaregistrovaných scén v
        setup súbore. V každej scéne je prítupný game objekt.
        """
        try:
            scenes = {}
            scene_module = importlib.import_module("src.scenes")
            for scene in setup.SCENES:
                class_name = tools.snake_to_pascal(scene) + 'Scene'
                scene_class = getattr(scene_module, class_name)
                scenes[scene] = scene_class(self)
            return scenes
        except:
            self.running = False

    def get_events(self):
        """
        Získa eventy, skontroluje či nenastal pokyn vypnutia v
        tom prípade vypne hru. Inak pošle eventy do aktuálnej scény
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            self.scene.handle_event(event)

    def update(self):
        """
        Obnoví aktuálne aktívnu scénu. Skontroluje či je aktuálna scéna
        stále aktívna. Ak nie, resetuje ju, prejde na ďalšiu scénu. Nová
        scéna sa musí znova obnoviť aby sa zamedzilo prebliknutiu obrazovky.
        """
        now = pg.time.get_ticks()
        self.scene.update(now)
        if self.scene.done:
            self.scene.reset()
            self.scene = self.scenes[self.scene.next]
            self.scene.update(now)

    def draw(self):
        """
        Vyplní okno farbou špecifikovanou v setupe
        a zavolá vykreslenie aktuálne aktívnej scény
        """
        self.screen.fill(setup.COLORS['background'])
        if self.scene.start_time:
            self.scene.draw()

    def main_loop(self):
        """
        Hlavný cyklus bežiaci pokiaľ nenastane event vypnutia.
        Obnovovacia frekvencia cyklu je špecifikovaná v setupe
        """
        while self.running:
            self.get_events()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(setup.FPS)


# class DB:
#     def __init__(self):
#         self.db = os.path.join('data', 'db.json')
#
#     def get_player(self, name):
#         with open(self.db, "r") as db:
#             data = json.load(db)
#             for user in data['users']:
#                 if user['name'] == name:
#                     return user
#             return None
#
#     def create_player(self, player):
#
#         with open(self.db, "a") as db:
#             data = {'users': []}
#             print(data)
#             data['users'].append({
#                 "name": player.name,
#                 "high_score": 0,
#                 "last_played": player.last_played
#             })
#             db.write(json.dumps(data))
#             db.close()
#
#     def update_player(self, player):
#         with open(self.db, "w") as db:
#             data = json.load(db)
#             for user in data['users']:
#                 if user['name'] == player.name:
#                     user['high_score'] = player.high_score
#                     user['last_played'] = player.last_played
#
#             db.write(json.dumps(data))
#             db.close()
