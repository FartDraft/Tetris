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
            Является родительским классом для: Menu.

      Примечание:
            Чтобы отобразить только 1 предложение, передай кортеж предложений вот так: ((параметры предложения), ).

        Атрибуты:
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
    def __init__(self, sentences: tuple):
        self.sentences = sentences

    def render_sentences(self) -> None:
        for name, x, y, font, color in self.sentences:
            screen.blit(font.render(name, True, color), (x, y))


class Menu(List):
    """Класс Menu используется для графического отображения меню.

        Основое применение:
           Является родительским классом для: MainMenu, GameOverMenu, PauseMenu.

        Примечание:
            Чтобы отобразить только 1 предложение, передай кортеж предложения вот так: ((параметры предложения), ).
            Чтобы отобразить только 1 пункт, передай кортеж пункта вот так: ((параметры пункта), ).

        Атрибуты:
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
                Отрисовывает пункты и предложения, используя self.sentences и self.items.

            main(surface: pygame.Surface: поверхность, которая будет отрисована на экране screen):
                Входит в цикл, который создаёт меню, используя surface, self.sentences и self.items.
                Если выбрать пункт, функция которого равна 'return', то цикл завершится, вернув None.
                Если нажать ALT+F4, вся программа завершится.
    """

    def __init__(self, sentences: tuple, items: tuple):
        super(Menu, self).__init__(sentences)
        self.items = items
        # Получаю размеры, необходимые для отображения каждого пункта своим шрифтом.
        self.fonts_sizes = tuple(item[3].size(item[0]) for item in items)

    def render(self, active_item_num: int) -> None:
        # Отрисовываю пункты.
        if active_item_num is not None:
            for name, x, y, font, unselect_color, select_color, item_num, _ in self.items:
                if active_item_num == item_num:
                    screen.blit(font.render(name, True, select_color), (x, y))
                else:
                    screen.blit(font.render(name, True, unselect_color), (x, y))
        else:
            for name, x, y, font, unselect_color, _, item_num, _ in self.items:
                screen.blit(font.render(name, True, unselect_color), (x, y))
        # Отрисовываю предложения.
        self.render_sentences()

    def main(self) -> None:
        active_item_num = None  # При запуске номер активного пункта не определён.
        while True:
            mouse_x, mouse_y = pg.mouse.get_pos()
            items_not_active = True  # Все пункты не активны.
            for item, font_size in zip(self.items, self.fonts_sizes):
                name, x, y, item_num = item[0], item[1], item[2], item[6]
                size_x, size_y = font_size
                # Если мышь наведена на пункт.
                if x < mouse_x < x + size_x and y < mouse_y < y + size_y:
                    # Этот пункт становится активным.
                    items_not_active = False
                    active_item_num = item_num
                    # Если нажали левой кнопкой мыши.
                    if pg.mouse.get_pressed(3)[0]:
                        action = self.items[active_item_num][7]
                        if action == 'return':
                            return None  # Возращаемся на предыдущую сцену.
                        else:
                            action()

            # Если все пункты не активны, то номер активного пункта не определён.
            if items_not_active:
                active_item_num = None

            # Если нажали ALT+F4.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            screen.blit(background, (0, 0))  # Отрисовываю surface на мониторе.
            self.render(active_item_num)  # Отрисовываю пункты и предложения на мониторе.
            pg.display.flip()  # Обновляю монитор.


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


# Создаю фон для всей игры, учитывая разрешени экрана.
background = pg.transform.scale(pg.image.load(path.join("Resources", "Images", "background.jpg")).convert(), (W, H))
# Создаю шрифты, чтобы поменять размер шрифта - необходимо создать новый объект шрифта нужного размера.
font1 = pg.font.Font(path.join("Resources", "font.ttf"), 30)
font2 = pg.font.Font(path.join("Resources", "font.ttf"), 50)
font3 = pg.font.Font(path.join("Resources", "font.ttf"), 100)

# Создаю сцену помощи. TODO Сделать нормально.
assistance_sentences = (
    ("В разработке", W // 2, H // 2, font1, (0, 0, 0)),
)
assistance_items = (
    ("<-", 0, 0, font3, (0, 0, 0), (255, 0, 0), 0, 'return'),
)
assistance = Menu(assistance_sentences, assistance_items)

# Создаю сцену игрового меню.
main_menu_sentences = (
    ("Тетрис", W // 2 - 155, 0, font3, (255, 0, 0)),
    ("Автор: Афанасин Егор", 100, H - 100, font1, (54, 54, 54)),
)
main_menu_items = (
    ("Играть", W // 2 - 80, 100, font2, (0, 0, 0), (255, 0, 0), 0, print),
    ("Помощь", W // 2 - 80, 180, font2, (0, 0, 0), (255, 0, 0), 1, assistance.main),
    ("Рекорды", W // 2 - 80, 260, font2, (0, 0, 0), (255, 0, 0), 2, print),
    ("Выйти", W // 2 - 80, 340, font2, (0, 0, 0), (255, 0, 0), 3, sys.exit),
)
main_menu = Menu(main_menu_sentences, main_menu_items)

main_menu.main()
