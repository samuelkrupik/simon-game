import datetime
import random
import importlib
import pygame as pg
from src import setup, tools
from src.components import Tile
import requests as req


class Api:
    @staticmethod
    def return_response(response:req.Response):
        if response.status_code == 200 or response.status_code == 201:
            return response.json(), response.status_code
        else:
            return False, response.status_code

    @staticmethod
    def get(endpoint: str):
        endpoint = endpoint.strip('/')
        res = req.get(setup.SERVER_URL + '/' + endpoint)
        return Api.return_response(res)

    @staticmethod
    def post(endpoint: str, data: dict):
        endpoint = endpoint.strip('/')
        res = req.post(setup.SERVER_URL + '/' + endpoint, data=data)
        return Api.return_response(res)


class Player:
    def __init__(self):
        self._id = 0
        self.name = 'Player'
        self.high_score = 0
        self.score = 0
        self.scores = []
        self.click_count = 0

    def create_user(self, name):
        """Vytvorí nového používatela alebo vráti už existujúceho"""
        res, status = Api.post('users', {'name': name})
        if not res:
            return False
        data = res['data']
        self._id = data['id']
        self.name = data['name']
        self.high_score = data['high_score']
        self.get_user_scores()

    def get_user_scores(self):
        """Získa top 10 dosiahnutých skóre pre daného používateľa"""
        res, status = Api.get(f'user/{self._id}/top-scores')
        if res:
            self.scores = res['data']

    def create_score(self):
        """Pošle skóre na server a vráti info či je nové skóre najlepšie"""
        res, code = Api.post('scores', {'score': self.score, 'user_id': self._id})
        if self.score > self.high_score:
            self.high_score = self.score
            return True
        else:
            return False


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
        self.scene = self.scenes[setup.START_SCENE]

    def generate_next(self):
        """
        Vygeneruje ďalšie náhodné číslo do sekvencie
        Čísla od 1 do 4 súhlasia s id jednotlivých tiles
        """
        self.sequence.append(random.randint(1, 4))

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
