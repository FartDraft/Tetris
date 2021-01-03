__author__ = "Afanasin Egor"
__email__ = "fartdraft@gmail.com"

import pygame as pg
from os import path
import sys
from random import choice, randrange
from copy import deepcopy  # TODO cделать документ строку ко всем функциям


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

# Фон для всей игры, учитывая разрешение экрана.
background = pg.transform.scale(pg.image.load(path.join("Resources", "Images", "background.jpg")).convert(), (W, H))

pg.event.set_blocked(None)  # Блокирую все типы событий для помещений в очередь событий.
pg.event.set_allowed(allowed_keys)  # Разрешаю только нужные мне типы событий.

WT, HT = 10, 20  # Ширина и высота прямоугольного стакана тетриса.
TILE = H // (HT + 2)  # Размер плитки стакана.
CENTER = (W - (WT * TILE)) // 2  # Смещение по оси 0x от краёв экрана до краёв стакана.
# Координаты сетки стакана.
grid = [pg.Rect(CENTER + TILE * x, TILE * (y + 1), TILE, TILE) for x in range(WT) for y in range(HT)]
# Координаты каждого квадрата тетромино, где первая координата каждого тетромино - его центр вращения.
figures_pos = [[(-1, -1), (-2, -1), (0, -1), (1, -1)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]
# Координаты квадратов фигур на сетке стакана.
figures = [[pg.Rect(x + 5, y + 1, 1, 1) for x, y in figure_pos] for figure_pos in figures_pos]
# Квадрат меньшего размера (учитывается ширина линии сетки) для отрисовки квадратов тетромино.
figure_rect = pg.Rect(0, 0, TILE - 3, TILE - 3)


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
                            return name  # Возращаемся на предыдущую сцену, передавая имя выбранного пункта.
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

            screen.blit(background, (0, 0))  # Отрисовываю background на мониторе.
            self.render(active_item_num)  # Отрисовываю пункты и предложения на мониторе.
            pg.display.flip()  # Обновляю монитор.
            clock.tick(FPS)  # Ограничиваю скорость выполнения программы до 60 кадров в секунду.


class GameOverMenu(Menu):
    """Поздравление с новым рекордом, кнопка играть еще, кнопка выхода в главное меню.
    Третичный цикл, нужен флаг menu, для правильного выхода в меню"""
    pass


class PauseMenu(Menu):
    """При нажимании на хоткей паузы, будет отрисовываться иконка паузы, и игра замирать.
    Третичный цикл, нужен флаг menu, для правильного выхода в меню"""
    pass


class Round:
    def __init__(self):  # TODO передавать номер текущего раунда
        # Двумерный массив, отображающий заполненность стакана.
        self.field = [[False for i in range(WT)] for j in range(HT)]
        # Глубокая копия, т.к. figures - двумерный массив.
        self.figure, self.next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
        # TODO сделать свой цвет для каждого раунда
        self.color = (randrange(250), randrange(250), randrange(250))
        # TODO сделать свою скорость падения для каждого раунда
        self.anim_count_y, self.anim_speed_y, self.anim_limit_y = 0, 60, 2000

    def abroad_x(self, figure):
        # Нахожу минимальную и максимальную координату по оси 0x квадратов тетромино.
        min_x = W
        max_x = 0
        for i in range(4):
            min_x = min(min_x, figure[i].x)
            max_x = max(max_x, figure[i].x)
        # Минимальный квадрат по оси 0x вышел за левую границу стакана или
        # максимальный квадрат по оси 0x вышел за правую границу стакана.
        return not (CENTER + 2 <= min_x * TILE + CENTER + 2) or \
               not (max_x * TILE + CENTER - 2 <= CENTER + (WT - 1) * TILE - 2)

    def abroad_y(self, figure):
        # Нахожу максимальную координату по оси 0y квадратов тетромино.
        max_y = 0
        for i in range(4):
            if max_y < figure[i].y:
                max_y = figure[i].y
        return not max_y * TILE < TILE * HT  # Если тетромино упало в стакан.

    def collision(self, figure):
        # Столкнулось ли активное тетромино с квадратами тетромино в стакане.
        for i in range(4):
            if self.field[figure[i].y][figure[i].x]:
                return True
        return False

    def is_square(self, figure):
        # Является ли тетромино квадратом
        return (figure[0].x == figure[3].x and figure[1].x == figure[2].x and figure[0].y == figure[1].y
                and figure[2].y == figure[3].y)

    def main(self):
        while True:
            dx, rotate = 0, False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        dx = -1
                    elif event.key == pg.K_RIGHT:
                        dx = 1
                    elif event.key == pg.K_DOWN:
                        self.anim_limit_y = 100
                    elif event.key == pg.K_UP and not self.is_square(self.figure):  # Квадрат не нужно вращать.
                        rotate = True

            # Двигаю тетромино по оси 0x.
            figure_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].x += dx
            # Если вышли за границы - оставляю координаты старой фигуры.
            if self.abroad_x(self.figure) or self.collision(self.figure):
                self.figure = figure_old

            # Двигаю тетромино по оси 0y.
            self.anim_count_y += self.anim_speed_y
            if self.anim_count_y > self.anim_limit_y:
                self.anim_count_y = 0
                figure_old = deepcopy(self.figure)
                for i in range(4):
                    self.figure[i].y += 1
                # Если вышли за дно стакана или столкнулись с другим тетромино.
                if self.abroad_y(self.figure) or self.collision(self.figure):
                    for i in range(4):
                        self.field[figure_old[i].y][figure_old[i].x] = True
                    self.figure = self.next_figure
                    self.next_figure = deepcopy(choice(figures))
                    self.anim_limit_y = 2000

            # Поворачиваю тетромино на 90 градусов.
            center = self.figure[0]
            figure_old = deepcopy(self.figure)
            if rotate:
                for i in range(4):
                    x = self.figure[i].y - center.y
                    y = self.figure[i].x - center.x
                    self.figure[i].x = center.x - x
                    self.figure[i].y = center.y + y
            # Если при повороте тетромино столкнулось с квадратами других тетромино в стакане или вышло из стакана(бывает только у палки).
            if self.abroad_x(self.figure) or self.abroad_y(self.figure) or self.collision(self.figure) or self.figure[1].y > TILE:
                self.figure = deepcopy(figure_old)

            screen.blit(background, (0, 0))  # Отрисовываю background на мониторе.

            [pg.draw.rect(screen, (0, 0, 0), rect, 2) for rect in grid]  # Отрисовываю сетку стакана с толщиной = 2.
            # Отрисовываю тетромино.
            for i in range(4):
                # Рассчитываю новые координаты для квадрата тетромино, учитывая толщину линии и смещение по оси 0x.
                figure_rect.x = CENTER + self.figure[i].x * TILE + 2
                figure_rect.y = (self.figure[i].y + 1) * TILE + 2
                # Рисую квадрат фигуры на новых координатах
                pg.draw.rect(screen, (self.color), figure_rect)
            # Отрисовываю квадраты других фигур на поле.
            for y, raw in enumerate(self.field):
                for x, flag in enumerate(raw):
                    if flag:
                        figure_rect.x, figure_rect.y = CENTER + x * TILE + 2, (y + 1) * TILE + 2
                        pg.draw.rect(screen, self.color, figure_rect)
            # Рисую следущую фигуру. TODO уравнять для всех мониторов, сделать в сетку, в окошке.
            for i in range(4):
                # Рассчитываю новые координаты для квадрата тетромино, учитывая толщину линии и смещение по оси 0x.
                figure_rect.x = CENTER + self.next_figure[i].x * TILE + 2 + 300
                figure_rect.y = (self.next_figure[i].y + 1) * TILE + 2 + 300
                # Рисую квадрат тетромино на новых координатах.
                pg.draw.rect(screen, (self.color), figure_rect)
            # Удаляю заполненные линии, если таковые есть.
            field = self.field
            for y in range(HT):
                if all(self.field[y]):
                    field = [[False for x in range(WT)]] + self.field[:y] + self.field[y + 1:]
            self.field = field
            # Конец игры.
            if any(field[0]):  # Если в первой линии есть любой квадрат.
                square = deepcopy(figure_rect)
                for j in range(HT):
                    for i in range(WT):
                        square.x = CENTER + i * TILE + 2
                        square.y = (j + 1) * TILE + 2
                        pg.draw.rect(screen, (randrange(250), randrange(250), randrange(250)), square)
                    pg.display.flip()
                pg.time.delay(1000)  # TODO Сделать нормальный конец игры, добавить возможность паузы, рекордов, шрифты.

            pg.display.flip()  # Обновляю монитор.
            clock.tick(FPS)  # Ограничиваю скорость выполнения программы до 60 кадров в секунду



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

# Создаю сцену рекордов.
# TODO Создать файл, в котором будут храниться последние 5 рекордов. Помещать их в records_sentences.
records_sentences = (
    ("В разработке", W // 2, H // 2, font1, (0, 0, 0)),
)
records_items = (
    ("<-", 0, 0, font3, (0, 0, 0), (255, 0, 0), 0, 'return'),
)
records = Menu(records_sentences, records_items)

new_round = Round()

# Создаю сцену игрового меню.
main_menu_sentences = (
    ("Тетрис", W // 2 - 155, 0, font3, (255, 0, 0)),
    ("Автор: Афанасин Егор", 100, H - 100, font1, (54, 54, 54)),
)
main_menu_items = (
    ("Играть", W // 2 - 80, 100, font2, (0, 0, 0), (255, 0, 0), 0, new_round.main),
    ("Помощь", W // 2 - 80, 180, font2, (0, 0, 0), (255, 0, 0), 1, assistance.main),
    ("Рекорды", W // 2 - 80, 260, font2, (0, 0, 0), (255, 0, 0), 2, records.main),
    ("Выйти", W // 2 - 80, 340, font2, (0, 0, 0), (255, 0, 0), 3, sys.exit),
)
main_menu = Menu(main_menu_sentences, main_menu_items)

main_menu.main()
