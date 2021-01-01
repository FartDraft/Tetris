__author__ = "Afanasin Egor"
__email__ = "fartdraft@gmail.com"

import pygame as pg
from os import path
import sys


pg.init()

allowed_keys = (
    pg.QUIT, pg.KEYDOWN, pg.KEYUP
)

pg.display.set_caption("Tetris")
pg.display.set_icon(pg.image.load(path.join("Resources", "Images", "icon.png")))  # path.abspath("icon.png")
screen = pg.display.set_mode((0, 0), flags=pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF)
W, H = pg.display.get_window_size()

FPS = 60
clock = pg.time.Clock()

pg.event.set_blocked(None)  # Блокирую все типы событий для помещений в очередь событий.
pg.event.set_allowed(allowed_keys)  # Разрешаю только нужные мне типы событий.


class List:
    """Класс List используется для графического отображения списка предложений.

        Основое применение:
            Является родительским классом для: Menu, SettingsList, RecordsList.

      Примечание:
            Должны быть больше 1 предложения.

        Атрибуты:
            surface: pygame.Surface: поверхность, на которой будут отрисованы предложения.
            sentences: tuple(tuple):
            {
                sentences[n][0]: str: предложение.
                sentences[n][1]: int: координата x начала отрисовки предложения.
                sentences[n][2]: int: координата y начала отрисовки предложения.
                sentences[n][3]: pygame.font.Font: шрифт для отрисовки предложения.
                sentences[n][4]: tuple: цвет шрифта предложения, формат - RGB.
            }

        Методы:
            render_sentences(): Отрисовывает предложения на поверхности surface, используя self.sentences.
    """
    def __init__(self, surface, sentences: tuple):
        self.surface = surface
        self.sentences = sentences

    def render_sentences(self) -> None:
        for name, x, y, font, color in self.sentences:
            self.surface.blit(font.render(name, True, color), (x, y))


class Menu(List):
    """Класс Menu используется для графического отображения пунктов меню.

        Основое применение:
           Является родительским классом для: MainMenu, GameOverMenu, PauseMenu.

        Примечание:
            Должно быть больше 1 предложения и больше 1 пункта.

        Атрибуты:
            surface: pygame.Surface: поверхность, на которой будут отрисованы предложения и пункты.
            sentences: tuple(tuple):
            {
                sentences[n][0]: str: предложение.
                sentences[n][1]: int: координата x начала отрисовки предложения.
                sentences[n][2]: int: координата y начала отрисовки предложения.
                sentences[n][3]: pygame.font.Font: шрифт для отрисовки предложения.
                sentences[n][4]: tuple: цвет шрифта предложения, формат - RGB.
            }
            items: tuple(tuple):
            {
                items[n][0]: str: пункт.
                items[n][1]: int: координата x начала отрисовки пункта.
                items[n][2]: int: координата y начала отрисовки пункта.
                items[n][3]: pygame.font.Font: шрифт для отрисовки пункта.
                items[n][4]: tuple: цвет пункта в неактивном состоянии, формат - RGB.
                items[n][5]: tuple: цвет пункта в активном состоянии, формат - RGB.
                items[n][6]: int: номер пункта меню, считая сверху вниз.
                items[n][7]: function: функция, которая срабатывает, если пункт выбрали.
            }

        Методы:
            render(active_item_num: int: номер активного пункта меню на данный момент времени):
                Отрисовывает пункты и предложения на поверхности surface, используя self.sentences и self.items.
    """

    def __init__(self, surface, sentences: tuple, items: tuple):
        super(Menu, self).__init__(surface, sentences)
        self.surface = surface
        self.items = items

    def render(self, active_item_num: int) -> None:
        # Отрисовываю пункты.
        for name, x, y, font, unselect_color, select_color, item_num, _ in self.items:
            if active_item_num == item_num:
                self.surface.blit(font.render(name, True, select_color), (x, y))
            else:
                self.surface.blit(font.render(name, True, unselect_color), (x, y))
        # Отрисовываю предложения.
        self.render_sentences()

    def main(self):
        active_item_num = 0
        max_item_index = len(self.items) - 1
        while True:
            mouse_x, mouse_y = pg.mouse.get_pos()
            for item in self.items:
                name, x, y, font, item_num = item[0], item[1], item[2], item[3], item[6]
                size_x, size_y = font.size(name)
                if x < mouse_x < x + size_x and y < mouse_y < y + size_y:
                    active_item_num = item_num
                    if pg.mouse.get_pressed(3)[0]:
                        self.items[active_item_num][7]()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP and active_item_num:
                        active_item_num -= 1
                    elif event.key == pg.K_DOWN and active_item_num < max_item_index:
                        active_item_num += 1
                    elif event.key == pg.K_RETURN:
                        self.items[active_item_num][7]()

            self.render(active_item_num)
            screen.blit(self.surface, (0, 0))
            pg.display.flip()


class MainMenu(Menu):
    """Стартовое меню с настройками, выходом, рекордами, кнопкой играть.
    Первичный цикл"""
    pass


class SettingsList(List):
    """
    Здесь будут хоткеи, описание раундов, правила начисления очков.
    Вторичный цикл"""
    HOTKEYS = {}


class RecordsList(List):
    """Последние 5 рекордов будут храниться в кеше. Этот класс должен их выводить
    Вторичный цикл"""
    pass


class GameOverMenu(Menu):
    """Поздравление с новым рекордом, кнопка играть еще, кнопка выхода в главное меню.
    Третичный цикл, нужен флаг menu, для правильного выхода в меню"""
    pass


class PauseMenu(Menu):
    """При нажимании на хоткей паузы, будет отрисовываться иконка паузы, и игра замирать.
    Третичный цикл, нужен флаг menu, для правильного выхода в меню"""
    pass


class Tetromino:
    """Сами фигурки, их коорднаты и рандомный выбор?"""
    pass


class Round:
    """Изменение цвета фигурок, их скорости падения и повявления, надписи раунда на экране.
    Вторичный цикл"""
    pass


# Тест работы.
menu_font = pg.font.Font(path.join("Resources", "Fonts", "Coder_4F_Bold.ttf"), 50)
sentences = (
    ("Author:", W // 2, 525, menu_font, pg.Color("green")),
    ("Afanasin Egor", W // 2, 600, menu_font, pg.Color("green"))
)
items = (
    ("Выйти", W // 2, 300, menu_font, (0, 0, 0), pg.Color("yellow"), 0, sys.exit),
    ("Quit", W // 2, 400, menu_font, (0, 0, 0), pg.Color("yellow"), 1, sys.exit)  # 0 - TypeError
)
test = pg.image.load(path.join("Resources", "Images", "menu.jpg")).convert()
menu = Menu(test, sentences, items)

menu.main()
