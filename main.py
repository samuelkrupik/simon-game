import sys
import pygame as pg
from src.game import Game
from src import setup, tools


def main():
    pg.init()
    pg.display.set_mode(setup.SCREEN_SIZE)
    pg.display.set_caption(setup.CAPTION)
    pg.display.set_icon(pg.image.load(tools.parse_path(setup.IMG_PATH, 'others', "icon.png")).convert_alpha())
    Game().main_loop()
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    main()
