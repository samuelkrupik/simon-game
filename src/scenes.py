import os

import pygame as pg
from src.components import Menu, Font, InputBox


class _Scene(object):
    def __init__(self, game, next_scene=None):
        self.game = game
        self.next = next_scene
        self.done = False
        self.start_time = None

    def reset(self):
        """Prepare for next time scene has control."""
        self.done = False
        self.start_time = False

    def handle_event(self, event):
        """Overwrite in child."""
        pass

    def update(self, now):
        """If the start time has not been set run necessary startup."""
        if not self.start_time:
            self.start_time = now


class WelcomeScene(_Scene):
    def __init__(self, game, db):
        super().__init__(game, next_scene="main_menu")
        self.db = db
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
            self.game.player.name = self.in_box.get_value()
            self.db.create_player(self.game.player)
            self.done = True
        else:
            self.error_message = validation['message']
            self.print_error = True

    def update(self, now):
        super().update(now)
        self.in_box.update(now)

    def draw(self):
        if self.print_error:
            font = Font(15, color=(255, 20, 20))
            error_text = font.render(self.error_message)
            self.game.screen.blit(error_text, (self.game.width/2 - error_text.get_width()/2, self.game.height-error_text.get_height()-10))

        self.in_box.draw(self.game.screen, (self.game.width/2 - self.in_box.width/2, self.game.height/2 - self.in_box.height/2))
        font = Font(30, color=(252, 186, 3))
        welcome_text = font.render("Welcome")
        tw, th = welcome_text.get_size()
        self.game.screen.blit(welcome_text, (self.game.width/2 - welcome_text.get_width()/2, 200))


class MainMenuScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="show")
        self.menu = Menu('MAIN MENU')
        self.menu.add_button("PLAY!", 'primary', self.play)
        self.menu.add_button("GAME MODE", 'primary', self.game_mode_menu)
        self.menu.add_button("SETTINGS", 'primary', self.settings_menu)
        self.menu.add_button("EXIT", 'danger', self.exit)

    def handle_event(self, event):
        self.menu.handle_event(event)

    def play(self):
        self.done = True

    def exit(self):
        self.game.running = False

    def game_mode_menu(self):
        self.next = "game_mode_menu"
        self.done = True

    def settings_menu(self):
        self.next = "settings_menu"
        self.done = True

    def draw(self):
        self.menu.draw(self.game.screen)


class ShowScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="play")
        self.blink = False
        self.blink_time = 400
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
        self.blink_time = 200
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
        for tile in self.game.tiles:
            self.game.screen.blit(tile.get_img(), tile.position)

    def reset(self):
        super().reset()
        self.game.player.click_count = 0
        self.locked = False


class GameOverScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")
        self.sound = pg.mixer.Sound(os.path.join('assets', 'sounds', 'general', 'game_over.wav'))

    def update(self, now):
        if not self.start_time:
            self.game.sequence = []
            self.sound.play()
        super().update(now)

    def draw(self):
        font = Font(30, color=(255, 0, 0))
        text = font.render("Game over")
        tw, th = text.get_size()
        self.game.screen.blit(text, (self.game.width / 2 - tw / 2, self.game.height / 2 - th / 2))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN:
            self.done = True
