import pygame as pg
from src import setup, tools
from src.components import Menu, Font, InputBox, Button, Table

"""
Scény sa registrujú v src.setup v liste SCENES
"""


class _Scene(object):
    """
    Základná scéna, obsahujúca potrebné vlastnosti.
    Všetky ostatné scény musia dediť z tejto scény
   """

    def __init__(self, game, next_scene: str = None, previous_scene: str = None):
        self.game = game
        self.next = next_scene
        self.previous = previous_scene
        self.done = False
        self.start_time = None

    def reset(self):
        """Pripravenie scény pre ďalšie použitie"""
        self.done = False
        self.start_time = False

    def back(self):
        """Prejdenie na predchádzajúcu scénu (ak je definovaná)"""
        if self.previous:
            self.next = self.previous
            self.done = True

    def handle_event(self, event):
        """Spracovanie eventov hry, nutné prepísanie v jednotlivých scénach"""
        pass

    def draw(self):
        """Vykreslenie scény, nutné prepísanie v jednotlivých scénach"""
        pass

    def update(self, now):
        """
        Obnovenie scény. Ak štart. čas nebol nastavený,
        nastaví ho. Ďalšia logika v jednotlivých scénach.
        """
        if not self.start_time:
            self.start_time = now


class Welcome(_Scene):
    """Uvítacia scéna"""

    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")
        self.in_box = InputBox(placeholder="Enter username")
        self.validation_message = ""
        self.start_btn = Button("Start", (0, 0), self.start_or_error)
        self.start_btn.set_position((self.game.width / 2 - self.start_btn.width / 2, self.game.height / 2 + 30))
        self.reconnect_btn = Button("Retry", (0, 0), self.reconnect, _type="danger")
        self.reconnect_btn.set_position(
            (self.game.width / 2 - self.reconnect_btn.width / 2, self.game.height / 2 + 30))

    def handle_event(self, event):
        if self.game.player.is_connected:
            self.start_btn.handle_event(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                self.in_box.activate()
            if event.type == pg.KEYDOWN:
                self.in_box.input(event, on_confirm=self.start_or_error)
        else:
            self.reconnect_btn.handle_event(event)

    def start_or_error(self):
        validation = self.in_box.validate(min_length=3, max_length=10)
        if validation['success']:
            self.game.player.create_user(self.in_box.get_value())
            self.done = True
        else:
            self.validation_message = validation['message']

    def reconnect(self):
        self.game.player.is_connected = tools.check_internet()

    def update(self, now):
        super().update(now)
        self.in_box.update(now)

    def draw(self):
        err_font = Font('regular', 'sm', 'red')

        # Uvítací text
        font = Font('vintage', '2xl', 'yellow')
        welcome_text = font.render("Welcome!")
        self.game.screen.blit(welcome_text, (
            self.game.width / 2 - welcome_text.get_width() / 2, self.game.height / 2 - welcome_text.get_height() - 20))

        # Chyba zadaného mena
        if self.validation_message:
            v_text = err_font.render(self.validation_message)
            self.game.screen.blit(v_text, (
                self.game.width / 2 - v_text.get_width() / 2, self.game.height * 2 / 3 - 20))

        # Zobrazí input box ak je user pripojený, ak nie, zobrazí error
        if self.game.player.is_connected:
            self.in_box.draw(
                self.game.screen,
                (self.game.width / 2 - self.in_box.width / 2, self.game.height / 2 - self.in_box.height / 2)
            )
            self.start_btn.draw(self.game.screen)
        else:
            c_text = err_font.render("You are not connected to internet.")
            c2_text = err_font.render("Please, try to reconnect.")
            self.game.screen.blit(c_text, (
                self.game.width / 2 - c_text.get_width() / 2, self.game.height / 2 - c_text.get_height()))
            self.game.screen.blit(c2_text, (
                self.game.width / 2 - c2_text.get_width() / 2, self.game.height / 2))
            self.reconnect_btn.draw(self.game.screen)


class MainMenu(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="show")
        self.menu = Menu('MAIN MENU')
        self.menu.add_button("PLAY!", self.play)
        self.menu.add_button("MY STATS", self.my_stats)
        self.menu.add_button("STATS", self.stats)
        self.menu.add_button("CREDITS", self.credits)
        self.menu.add_button("EXIT", self.exit, _type="danger")

    def handle_event(self, event):
        self.menu.handle_event(event)

    def play(self):
        self.next = 'show'
        self.done = True

    def my_stats(self):
        self.next = 'my_stats'
        self.done = True

    def stats(self):
        self.next = 'stats'
        self.done = True

    def credits(self):
        self.next = "credits"
        self.done = True

    def exit(self):
        self.game.running = False

    def draw(self):
        self.menu.draw(self.game.screen)


class MyStats(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu", previous_scene="main_menu")
        self.table = Table("Your scores", self.game.player.scores)
        self.back_btn = Button('BACK', (0, 0), self.back)
        self.back_btn.set_position((self.game.width / 2 - self.back_btn.width / 2,
                                    self.game.height - self.back_btn.height * 2))

    def handle_event(self, event):
        self.back_btn.handle_event(event)

    def update(self, now):
        if not self.start_time:
            self.game.player.get_user_scores()
            self.table.data = self.game.player.scores
            self.table.add_column('Score', 'score')
            self.table.add_column('Date', 'created_at', tools.format_date)
        super().update(now)

    def draw(self):
        self.table.draw(self.game.screen)
        self.back_btn.draw(self.game.screen)

    def reset(self):
        self.table.table = []
        super().reset()


class Stats(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu", previous_scene="main_menu")
        self.table = Table("Top scores", self.game.player.scores)
        self.back_btn = Button('BACK', (0, 0), self.back)
        self.back_btn.set_position((self.game.width / 2 - self.back_btn.width / 2,
                                    self.game.height - self.back_btn.height * 2))

    def handle_event(self, event):
        self.back_btn.handle_event(event)

    def update(self, now):
        if not self.start_time:
            self.game.get_top_scores()
            self.table.data = self.game.top_scores
            self.table.add_column('Score', 'score')
            self.table.add_column('Player', 'user')
            self.table.add_column('Date', 'created_at', tools.format_date)
        super().update(now)

    def draw(self):
        self.table.draw(self.game.screen)
        self.back_btn.draw(self.game.screen)

    def reset(self):
        self.table.table = []
        super().reset()


class Credits(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="play", previous_scene="main_menu")
        self.back_btn = Button('BACK', (0, 0), action=self.back)
        self.back_btn.set_position(
            (self.game.width / 2 - self.back_btn.width / 2, self.game.height - self.back_btn.height * 2))
        self.title_font = Font('vintage', 'xl', 'yellow')
        self.text_font = Font(color='light')
        self.py_img = pg.image.load(tools.parse_path(setup.IMG_PATH, "others", "python.png")).convert_alpha()

    def draw(self):
        credits_text = self.title_font.render('CREDITS')
        self.game.screen.blit(credits_text, (self.game.width / 2 - credits_text.get_width() / 2, 20))
        self.game.screen.blit(self.py_img,
                              (self.game.width / 2 - self.py_img.get_width() / 2, 20 + credits_text.get_height()))

        text = "Sounds: www.freesound.org\n" \
               "Author: Samuel Krupík\n" \
               "Year: 2021"

        texts = tools.split_multiline(text)
        for i, t in enumerate(texts):
            r = self.text_font.render(t)
            rw, rh = r.get_size()
            self.game.screen.blit(r, (self.game.width / 2 - rw / 2, self.game.height / 2 + 20 + rh * 1.5 * i))
        self.back_btn.draw(self.game.screen)

    def handle_event(self, event):
        self.back_btn.handle_event(event)


class Show(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="play")
        self.blink = False
        self.blink_time = setup.TILE_LIGHT_TIME
        self.sequence_index = 0
        self.counter = -1
        self.timer = 0
        self.can_play_sound = False

    def update(self, now):
        super().update(now)

        # kontrola púštania zvuku (reset pri každom update aby sa pustil len raz)
        self.can_play_sound = False

        # prvý update -> generuj nové číslo
        if self.timer == 0:
            self.timer = now
            self.game.generate_next()

        # prešiel cyklus bliknutia -> reset
        if now - self.blink_time > self.timer:
            self.timer = now
            self.counter += 1
            self.blink = not self.blink
            # ak je počítadlo párne -> pustí zvuk (inak by hral dvakrat)
            if self.counter % 2 == 0:
                self.can_play_sound = True
                if self.counter >= 2:
                    self.sequence_index += 1

        # prechádzanie a nastavenie aktívnej Tile
        for tile in self.game.tiles:
            tile.active = False
            if self.sequence_index < len(self.game.sequence):
                if self.blink and tile.id == self.game.sequence[self.sequence_index]:
                    tile.active = True

        # posledný -> koniec
        if self.sequence_index == len(self.game.sequence):
            self.done = True
            return

    def draw(self):
        font = Font(color="light")
        text = font.render("Simon's move")
        tw, th = text.get_size()
        self.game.screen.blit(text, (self.game.width / 2 - tw / 2, self.game.height / 2 - th / 2))
        for tile in self.game.tiles:
            self.game.screen.blit(tile.get_img(), tile.position)
            if self.can_play_sound:
                tile.play_sound()

    def reset(self):
        super().reset()
        self.timer = 0
        self.counter = -1
        self.blink = False
        self.sequence_index = 0


class Play(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="show")
        self.timer = 0
        self.blink_time = setup.TILE_CLICK_LIGHT_TIME
        self.was_clicked = False
        self.locked = False

    def tile_clicked(self, tile):
        if tile.id == self.game.sequence[self.game.player.click_count]:
            self.game.player.click_count += 1
            if self.game.player.click_count == len(self.game.sequence):
                self.game.player.score += 1
                self.locked = True
                self.next = "show"
        else:
            self.next = "game_over"
            self.done = True

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # kliknutie na Tile s posledným indexom v sekvencii -> nepočuvaj dalšie kliknutia
            if self.locked:
                return
            # deaktivuje všetky Tiles okrem kliknutej
            for tile in self.game.tiles:
                tile.active = False
                self.was_clicked = True
                if tile.mouse_over(pg.mouse.get_pos()):
                    tile.active = True
                    tile.click(self.tile_clicked, params=(tile,))

    def update(self, now):
        super().update(now)
        # kliknutie na Tile -> spusti časovač
        if self.was_clicked:
            self.timer = now
            self.was_clicked = False
        # po bliknutí resetuje aktívny stav
        if now - self.blink_time > self.timer:
            for tile in self.game.tiles:
                tile.active = False
            # posledný -> koniec
            if self.locked:
                self.done = True

    def draw(self):
        font = Font(color="white")
        text = font.render("Your move")
        tw, th = text.get_size()
        self.game.screen.blit(text, (self.game.width / 2 - tw / 2, self.game.height / 2 - th / 2))
        for tile in self.game.tiles:
            self.game.screen.blit(tile.get_img(), tile.position)

    def reset(self):
        super().reset()
        self.game.player.click_count = 0
        self.locked = False


class GameOver(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")
        self.sound = pg.mixer.Sound(tools.parse_path(setup.SOUND_PATH, 'general', 'game_over.wav'))
        self.is_highscore = False
        self.continue_text_visible = False
        self.timer = 0

    def update(self, now):
        if not self.start_time:
            self.is_highscore = self.game.player.create_score()
            self.game.sequence = []
            self.sound.play()
        if now - setup.BLINK_TIME > self.timer:
            self.continue_text_visible = not self.continue_text_visible
            self.timer = now
        super().update(now)

    def draw(self):
        if self.is_highscore:
            font = Font("regular", "lg", "yellow")
            text = font.render("Wooah, new high score!")
            tw, th = text.get_size()
            self.game.screen.blit(text, (self.game.width / 2 - tw / 2, 160))

        font = Font("regular", "xl", "light")
        text = font.render(f"Your score: {self.game.player.score}")
        tw, th = text.get_size()
        self.game.screen.blit(text, (self.game.width / 2 - tw / 2, 200))

        font = Font("vintage", "2xl", "red")
        text = font.render("Game over")
        tw, th = text.get_size()
        self.game.screen.blit(text, (self.game.width / 2 - tw / 2, self.game.height / 2 - th / 2))

        if self.continue_text_visible:
            font = Font("regular", "md", "light")
            text = font.render("[click anywhere to continue]")
            tw, th = text.get_size()
            self.game.screen.blit(text, (self.game.width / 2 - tw / 2, 350))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN:
            self.done = True

    def reset(self):
        super().reset()
        self.game.player.score = 0
        self.game.player.get_user_scores()
