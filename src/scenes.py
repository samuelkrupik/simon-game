import pygame as pg
from src import setup, tools
from src.components import Menu, Font, InputBox, Button

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


class WelcomeScene(_Scene):
    """Uvítacia scéna"""
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")
        self.in_box = InputBox()
        self.error_message = ""
        self.print_error = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.in_box.activate()
        if event.type == pg.KEYDOWN:
            self.in_box.input(event, on_confirm=self.start_or_error)

    def start_or_error(self):
        validation = self.in_box.validate(min_length=3)
        if validation['success']:
            self.game.player.create_user(self.in_box.get_value())
            self.done = True
        else:
            self.error_message = validation['message']
            self.print_error = True

    def update(self, now):
        super().update(now)
        self.in_box.update(now)

    def draw(self):
        if self.print_error:
            font = Font('indiagonal', 'sm', 'red')
            error_text = font.render(self.error_message)
            self.game.screen.blit(error_text, (self.game.width/2 - error_text.get_width()/2, self.game.height-error_text.get_height()-10))

        self.in_box.draw(self.game.screen, (self.game.width/2 - self.in_box.width/2, self.game.height/2 - self.in_box.height/2))
        font = Font('vintage', '2xl', 'yellow')
        welcome_text = font.render("Welcome")
        self.game.screen.blit(welcome_text, (self.game.width/2 - welcome_text.get_width()/2, 200))


class MainMenuScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="show")
        self.menu = Menu('MAIN MENU')
        self.menu.add_button("PLAY!", self.play)
        self.menu.add_button("PROFILE", self.profile)
        self.menu.add_button("STATS", self.stats)
        self.menu.add_button("SETTINGS", self.settings)
        self.menu.add_button("CREDITS", self.credits)
        self.menu.add_button("EXIT", self.exit, _type="danger")

    def handle_event(self, event):
        self.menu.handle_event(event)

    def play(self):
        self.next = 'show'
        self.done = True

    def profile(self):
        self.next = 'profile'
        self.done = True

    def stats(self):
        self.next = 'stats'
        self.done = True

    def settings(self):
        self.next = "settings_menu"
        self.done = True

    def credits(self):
        self.next = "credits"
        self.done = True

    def exit(self):
        self.game.running = False

    def draw(self):
        self.menu.draw(self.game.screen)


# TODO: Zobraziť tabuľku dosiahnutých top výsledkov, highscore a meno
class ProfileScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")

    def handle_event(self, event):
        pass

    def draw(self):
        pass


# TODO: Zobraziť tabuľku najlepších výsledkov všetkých hráčov
class StatsScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")

    def handle_event(self, event):
        pass

    def draw(self):
        pass


class SettingsMenuScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="show", previous_scene="main_menu")
        self.menu = Menu('SETTINGS')
        self.menu.add_button(self._get_music_text(), self.music)
        self.menu.add_button("BACK", self.back)

    def handle_event(self, event):
        self.menu.handle_event(event)

    def draw(self):
        self.menu.draw(self.game.screen)

    def music(self):
        self.game.is_music = not self.game.is_music
        self.menu.buttons[0].set_text(self._get_music_text())

    def _get_music_text(self):
        return "Music off" if self.game.is_music else "Music on"


class CreditsScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="play", previous_scene="main_menu")
        self.back_btn = Button('BACK', (0,0), action=self.back)
        self.back_btn.set_position((self.game.width/2 - self.back_btn.width/2, self.game.height/2 - self.back_btn.height/2))

    def draw(self):
        font = Font('vintage', 'xl', 'yellow')
        credits_text = font.render('CREDITS')
        font = Font(color='yellow')
        name_text = font.render("Samuel Krupík")
        year_text = font.render("2021")
        self.game.screen.blit(credits_text, (self.game.width / 2 - credits_text.get_width()/2, 20))
        self.game.screen.blit(name_text, (self.game.width/2 - name_text.get_width()/2, 200))
        self.game.screen.blit(year_text, (self.game.width/2 - year_text.get_width()/2, 230))
        self.back_btn.draw(self.game.screen)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.back_btn.mouse_over(pg.mouse.get_pos()):
                self.back_btn.click(self.back_btn.action)


class ShowScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="play")
        self.blink = False
        self.blink_time = setup.TILE_LIGHT_TIME
        self.sequence_index = 0
        self.counter = -1
        self.timer = 0
        self.can_play_sound = False

    def update(self, now):
        # update parent
        super().update(now)

        # ensure sound is played only once per blink
        self.can_play_sound = False

        # first update
        # reset timer, generate new number
        if self.timer == 0:
            self.timer = now
            self.game.generate_next()

        # blink time passed
        # reset timer, increase count, reverse blinking
        if now - self.blink_time > self.timer:
            self.timer = now
            self.counter += 1
            self.blink = not self.blink
            # counter is even
            # increase current sequence index
            if self.counter % 2 == 0:
                self.can_play_sound = True
                if self.counter >= 2:
                    self.sequence_index += 1

        # loop through tiles
        # ensure current sequence index exists in sequence
        # set active tile
        for tile in self.game.tiles:
            tile.active = False
            if self.sequence_index < len(self.game.sequence):
                if self.blink and tile.id == self.game.sequence[self.sequence_index]:
                    tile.active = True

        # last sequence index -> scene done
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


class PlayScene(_Scene):
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
            # if last item from sequence was clicked -> do not listen for clicks
            if self.locked:
                return
            # loop through and deactivate all tiles
            for tile in self.game.tiles:
                tile.active = False
                self.was_clicked = True
                # mouse was hovering over tile
                # handle click, set to active
                if tile.mouse_over(pg.mouse.get_pos()):
                    tile.active = True
                    tile.click(self.tile_clicked, params=(tile,))

    def update(self, now):
        # update parent
        super().update(now)
        # if tile was clicked in handle event method set timer
        if self.was_clicked:
            self.timer = now
            self.was_clicked = False
        # reset active state after blink time
        if now - self.blink_time > self.timer:
            for tile in self.game.tiles:
                tile.active = False
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


class GameOverScene(_Scene):
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

        font = Font("regular","xl", "light")
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
