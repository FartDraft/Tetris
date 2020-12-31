import pygame as pg
from os import path


pg.init()

HOTKEYS = {}

pg.display.set_caption("Tetris")
pg.display.set_icon(pg.image.load(path.join("Resources", "Images", "tetris.png")))  # path.abspath("tetris.png")
screen = pg.display.set_mode((0, 0), flags=pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF)
W, H = pg.display.get_window_size()

FPS = 60
clock = pg.time.Clock()


class Settings:
    """
    Здесь будут хоткеи, описание раундов, правила начисления очков.
    """
    pass


class Pause:
    """При нажимании на хоткей паузы, будет отрисовываться иконка паузы, и игра замирать."""
    pass


class Records:
    """Последние 5 рекордов будут храниться в кеше. Этот класс должен их выводить"""
    pass


class MainMenu:
    """Стартовое меню с настройками, выходом, рекордами, кнопкой играть"""
    pass


class GameOverMenu:
    """Поздравление с новым рекордом, кнопка играть еще, кнопка выхода в главное меню."""
    pass


class Tetromino:
    """Сами фигурки, их коорднаты и рандомный выбор?"""
    pass


class Handler:
    """Будущий обработчик событий, все хоткеи вносятся в словарь хоткеев"""
    pass


class Round:
    """Изменение цвета фигурок, их скорости падения и повявления, надписи раунда на экране. """
    pass


# Цикл, для тестировки работоспособности программы. Позже, будет удалён.
running = True
while running:
    screen.fill(pg.Color('magenta'))

    for i in pg.event.get():
        if i.type == pg.QUIT:
            running = False

    pg.display.flip()
    clock.tick(FPS)

pg.quit()
