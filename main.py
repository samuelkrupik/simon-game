import sys

from game import Controller
import pygame as pg

CAPTION = "Simon"
SCREEN_SIZE = (560, 560)


def main():
    pg.init()
    pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption(CAPTION)
    Controller().main_loop()
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    main()
