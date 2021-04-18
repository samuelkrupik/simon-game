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
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")
        self.in_box = InputBox((200,200))

    def handle_event(self, event):
        self.in_box.input(event)
        if event.type == pg.KEYDOWN:
            if pg.key.get_pressed()[pg.K_RETURN]:
                self.done = True

    def draw(self):
        self.in_box.draw(self.game.screen)
        font = Font(30, color=(252, 186, 3))
        text = font.render("Welcome")
        tw, th = text.get_size()
        self.game.screen.blit(text, (100, 100))


class MainMenuScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="show")
        self.menu = Menu('MAIN MENU')
        self.menu.add_button("PLAY!", 'primary', self.play)
        self.menu.add_button("GAME MODE", 'primary', self.game_mode_menu)
        self.menu.add_button("SETTINGS", 'primary', self.settings_menu)
        self.menu.add_button("EXIT", 'danger', pg.quit)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()
            for button in self.menu.buttons:
                if button.mouse_over(mouse_pos):
                    button.click(button.action)

    def play(self):
        self.done = True

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
        self.active_tile = 0
        self.counter = 0
        self.timer = 0

    def update(self, now):
        super().update(now)
        if not self.timer:
            self.game.generate_next()
            self.timer = now
            return
        if now - self.blink_time > self.timer:
            self.timer = now
            self.counter += 1
            self.blink = not self.blink
            if self.counter % 2 == 1 and self.counter > 2:
                self.active_tile += 1

        if self.active_tile == len(self.game.sequence):
            self.done = True

    # TODO: Fix blink when switching to play scene
    def draw(self):
        for tile in self.game.tiles:
            if tile.id == self.game.sequence[self.active_tile] and self.blink:
                self.game.screen.blit(tile.img_on, tile.position)
            else:
                self.game.screen.blit(tile.img_off, tile.position)

    def reset(self):
        super().reset()
        self.timer = 0
        self.counter = 0
        self.blink = False
        self.active_tile = 0


class PlayScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="game_over")

    def check_click(self, tile):
        if tile.id == self.game.sequence[self.game.player.click_count]:
            self.game.player.click_count += 1
            if self.game.player.click_count == len(self.game.sequence):
                self.game.player.score += 1
                self.game.player.click_count = 0
                self.next = "show"
                self.done = True
        # if player fails -> game over
        else:
            self.next = "game_over"
            self.done = True

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            for tile in self.game.tiles:
                if tile.mouse_over(pg.mouse.get_pos()):
                    tile.click(self.check_click, tile)

    def draw(self):
        for tile in self.game.tiles:
            self.game.screen.blit(tile.img_off, tile.position)


class GameOverScene(_Scene):
    def __init__(self, game):
        super().__init__(game, next_scene="main_menu")

    def draw(self):
        font = Font(30, color=(255, 0, 0))
        text = font.render("Game over")
        tw, th = text.get_size()
        self.game.screen.blit(text, (self.game.width / 2 - tw / 2, self.game.height / 2 - th / 2))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.done = True
