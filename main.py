import sys
import pygame as pg
from src.game import Game
from src import setup


def main():
    pg.mixer.init()
    pg.init()
    pg.display.set_mode(setup.SCREEN_SIZE)
    pg.display.set_caption(setup.CAPTION)
    Game().main_loop()
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    main()
