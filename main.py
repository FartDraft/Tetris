import pygame as pg
from os import path


pg.init()

allowed_keys = (
    pg.QUIT,
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
            Является родительским классом для: SettingsList, RecordsList.

        Атрибуты:
            surface: pygame.Surface: поверхность, на которой будут отрисованы предложения.
            font_path: str: путь к шрифту.
            font_size: int: размер шрифта.
            list_sentences: tuple(tuple):
            {
                list_sentences[n][0]: str: предложение.
                list_sentences[n][1]: int: координата x начала отрисовки предложения.
                list_sentences[n][2]: int: координата y начала отрисовки предложения.
                list_sentences[n][3]: tuple: цвет шрифта предложения, формат - RGB.
            }

        Методы:
            render(): Отрисовывает предложения шрифтом(путь - font_path, размер - font_size) на поверхности surface,
             используя list_sentences.
    """
    def __init__(self, surface, font_path: str, font_size: int, list_sentences: tuple):
        self.surface = surface
        self.font = pg.font.Font(font_path, font_size)
        self.sentences = list_sentences

    def render(self):
        for name, x, y, color in self.sentences:
            self.surface.blit(self.font.render(name, True, color), (x, y))


class Menu():
    """Расширенная версия листа, с реализацией активных пунктов.
    Они подсвечиваются, выбираются, и рендерятся по-другому."""
    pass


class MainMenu(Menu):
    """Стартовое меню с настройками, выходом, рекордами, кнопкой играть"""
    pass


class SettingsList(List):
    """
    Здесь будут хоткеи, описание раундов, правила начисления очков.
    """
    HOTKEYS = {}


class RecordsList(List):
    """Последние 5 рекордов будут храниться в кеше. Этот класс должен их выводить"""
    pass


class GameOverMenu(Menu):
    """Поздравление с новым рекордом, кнопка играть еще, кнопка выхода в главное меню."""
    pass


class PauseMenu(Menu):
    """При нажимании на хоткей паузы, будет отрисовываться иконка паузы, и игра замирать."""
    pass



class Tetromino:
    """Сами фигурки, их коорднаты и рандомный выбор?"""
    pass


class Round:
    """Изменение цвета фигурок, их скорости падения и повявления, надписи раунда на экране. """
    pass


# Тест работы нового класса.
test = List(screen, path.join("Resources", "Fonts", "Coder_4F_Bold.ttf"), 50,
         (("Privet", 100, 100, (100, 100, 200)), ("Bye", 200, 200, (200, 200, 200))))
# Цикл, для тестировки работоспособности программы. Позже, будет удалён.
running = True
while running:
    screen.fill(pg.Color('magenta'))
    test.render()  #

    for i in pg.event.get():
        if i.type == pg.QUIT:
            running = False

    pg.display.flip()
    clock.tick(FPS)

pg.quit()
