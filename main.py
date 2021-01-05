__author__ = "Afanasin Egor"
__email__ = "fartdraft@gmail.com"

import pygame as pg
from os import path
import sys
from random import randrange, choice, shuffle
from copy import deepcopy


pg.init()

pg.display.set_caption("Tetris")
pg.display.set_icon(pg.image.load(path.join("Resources", "Images", "icon.png")))  # path.abspath("icon.png")
# pg.FULLSCREEN - полноэкранный режим, pg.HWSURFACE - аппаратное ускорение, pg.DOUBLEBUF - двойная буферизация.
# (0, 0) - созданная поверхность будет иметь тот же размер, что и текущее разрешение экрана.
screen = pg.display.set_mode((0, 0), flags=pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF)
W, H = pg.display.get_window_size()

FPS = 60
clock = pg.time.Clock()

# Фон для всей игры, учитывая разрешение экрана.
BACKGROUND = pg.transform.scale(pg.image.load(path.join("Resources", "Images", "background.jpg")).convert(), (W, H))

allowed_keys = (pg.QUIT, pg.KEYDOWN, pg.KEYUP)
pg.event.set_blocked(None)  # Блокирую все типы событий для помещений в очередь событий.
pg.event.set_allowed(allowed_keys)  # Разрешаю только нужные мне типы событий.

WT, HT = 10, 20  # Ширина и высота прямоугольного стакана тетриса.
TILE = H // (HT + 2)  # Размер плитки стакана.
CENTER = (W - (WT * TILE)) // 2  # Смещение по оси 0x от краёв экрана до краёв стакана.
# Координаты сетки стакана.
grid_glass = [pg.Rect(CENTER + TILE * x, TILE * (y + 1), TILE, TILE) for x in range(WT) for y in range(HT)]
# Координаты сетки для отображения следующей фигуры.
grid_next_figure = [pg.Rect(CENTER + TILE * (WT + 5 + x), TILE * (5 + y), TILE, TILE)
                    for x in range(4) for y in range(4)]
# Координаты каждого квадрата тетрамино, где первая координата каждого тетрамино - его центр вращения.
figures_pos = [[(-1, -1), (-2, -1), (0, -1), (1, -1)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]
# Координаты квадратов фигур на сетке стакана.
figures = [[pg.Rect(x + 5, y + 1, 1, 1) for x, y in figure_pos] for figure_pos in figures_pos]
# Квадрат меньшего размера (учитывается ширина линии сетки) для отрисовки квадратов тетрамино.
figure_rect = pg.Rect(0, 0, TILE - 3, TILE - 3)

rounds_colors = (
    (47, 79, 79),  # gray
    (255, 69, 0), (220, 20, 60), (178, 34, 34), (255, 0, 0), (139, 0, 0), (128, 0, 0),  # red
    (139, 69, 19), (165, 42, 42),  # brown
    (199, 21, 133), (148, 0, 211), (128, 0, 128), (139, 0, 139), (75, 0, 130), (72, 61, 139),  # purple
    (0, 0, 255), (0, 0, 205), (0, 0, 139), (0, 0, 128), (25, 25, 112)  # blue
)

# Создаю шрифты, чтобы поменять размер шрифта - необходимо создать новый объект шрифта нужного размера.
font_path = path.join("Resources", "font.ttf")
# Создаю шрифты, чтобы поменять размер шрифта - необходимо создать новый объект шрифта нужного размера.
font1 = pg.font.Font(font_path, TILE)
font2 = pg.font.Font(font_path, TILE * 2)
font3 = pg.font.Font(font_path, TILE * 3)


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
            render_sentences(self): Отрисовывает предложения на поверхности surface, используя self.sentences.
    """
    def __init__(self, sentences: tuple):
        self.sentences = sentences

    def render_sentences(self) -> None:
        """Метод для отрисовки предложений.

        Возвращаемое значение:
            None
        """
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
            render(self, active_item_num: int: номер активного пункта меню на данный момент времени):
                Отрисовывает пункты и предложения, используя self.sentences и self.items.

            main(self, surface: pygame.Surface: поверхность, которая будет отрисована на экране screen):
                Входит в цикл, который создаёт меню, используя surface, self.sentences и self.items.
                Если выбрать пункт, функция которого равна 'return', то цикл завершится,
                вернув имя этого пункта предыдущей сцене. Если нажать ALT+F4, вся программа завершится.
    """

    def __init__(self, sentences: tuple, items: tuple):
        super(Menu, self).__init__(sentences)
        self.items = items
        # Получаю размеры, необходимые для отображения каждого пункта своим шрифтом.
        self.fonts_sizes = tuple(item[3].size(item[0]) for item in items)

    def render(self, active_item_num: int) -> None:
        """Метод для отрисовки пунктов и предложений.

        Аргументы:
            active_item_num: int:  номер активного пункта в данный момент времени.

        Возвращаемое значение:
            None
        """
        # Если есть активный пункт - рисую его активным цветом, а все остальные пункты - неактивным.
        if active_item_num is not None:
            for name, x, y, font, unselect_color, select_color, item_num, _ in self.items:
                if active_item_num == item_num:
                    screen.blit(font.render(name, True, select_color), (x, y))
                else:
                    screen.blit(font.render(name, True, unselect_color), (x, y))
        else:  # Если нет ни одного активного пункта - рисую все пункты неактивным цветом.
            for name, x, y, font, unselect_color, _, item_num, _ in self.items:
                screen.blit(font.render(name, True, unselect_color), (x, y))
        self.render_sentences()

    def main(self) -> str:
        """Метод для создания меню.

        Возвращаемое значение:
            str: имя выбранного пункта, функция которого равна 'return'.
        """
        active_item_num = None  # В начале номер активного пункта не определён.
        while True:
            mouse_x, mouse_y = pg.mouse.get_pos()  # Координаты текущего положения курсора мыши.
            items_not_active = True  # Все пункты в начале каждой итерации цикла не активны.
            for item, font_size in zip(self.items, self.fonts_sizes):
                x, y, item_num = item[1], item[2], item[6]
                size_x, size_y = font_size
                # Если мышь наведена на пункт.
                if x < mouse_x < x + size_x and y < mouse_y < y + size_y:
                    items_not_active = False  # В этой итерации цикла есть активные пункты.
                    active_item_num = item_num  # Этот пункт становится активным.
                    # Если нажали левой кнопкой мыши.
                    if pg.mouse.get_pressed(3)[0]:
                        action = self.items[active_item_num][7]
                        if action == 'return':
                            return item[0]  # Возращаемся на предыдущую сцену, передавая имя выбранного пункта.
                        else:
                            action()

            # Если все пункты в этой итерации цикла не активны, то номер активного пункта не определён.
            if items_not_active:
                active_item_num = None

            # Если нажали ALT+F4.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            screen.blit(BACKGROUND, (0, 0))  # Отрисовываю BACKGROUND на мониторе.
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
    """Класс Round.

        Атрибуты:
            в разработке

        Статические методы:
            randomizer():
                Модифицированный алгоритм генератора случайностей 7-bag. Генерирует индексы для массива figures.

            abroad_x(tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.) -> bool:
                Проверяет, вышло ли тетрамино за левую или правую границу стакана.
                Возвращает True - если тетрамино вышло, иначе - False.

            abroad_y(tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.) -> bool:
                Проверяет, упало ли тетрамино в стакан.
                Возвращает True - если тетрамино упало, иначе - False.

            is_square(tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.) -> bool:
                Проверка тетрамино на квадратность.
                Возвращает True - если тетрамино квадратно, иначе - False.

            above(tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.) -> bool:
                Проверка тетрамино на выход за границу верха стакана.
                Возвращает True - если тетрамино вышло, иначе - False.

        Методы:
            collision(self, figure) -> bool:
                Проверяет тетрамино на столкновение с квадратами других тетрамино в стакане.
                Возвращает True - если тетрамино столкнулось, иначе - False.

    """
    def __init__(self):
        # Deepcopy - глубокая копия, т.к. figures - двумерный массив.
        self.figure, self.next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
        # Двумерный массив, отображающий заполненность стакана.
        self.field = [[False for _ in range(WT)] for _ in range(HT)]
        self.num = 1  # Номер раунда, при создании раунда равен 1.
        self.record = 0  # Рекорд при создании раунда равен 0.
        self.lines = 0  # Количество собранных линий в раунде.

        # Переменные, зависящие от номера раунда.
        self.color = rounds_colors[self.num - 1]  # -1, т.к. мне нужен индекс, а не порядковый номер.
        # Количество очков за 1, 2, 3, 4 линии.
        self.lines_points = (100 * self.num, 300 * self.num, 700 * self.num, 1500 * self.num)
        # Переменные для контролирования движения тетрамино по осям 0y и 0x.
        self.anim_count_y, self.anim_speed_y, self.anim_limit_y = 0, 40 + 20 * self.num, 2000
        self.anim_count_x, self.anim_speed_x, self.anim_limit_x = 0, 360 + 7 * self.num, 2000
        # Игровое меню.
        self.item = ("<-", 0, 0, font3, (0, 0, 0), (255, 0, 0))
        self.sentences = [
            [f"Раунд {self.num}", CENTER + TILE * (WT + 3), TILE, font2, self.color],
            ("Следующая фигура:", CENTER + TILE * (WT + 3), TILE * 4, font1, self.color),
            ("Счёт:", TILE, TILE * 4, font2, self.color),
            [str(self.record), TILE, TILE * 6, font1, (0, 0, 0)],
        ]
        # Размер, необходимый для отображения '->'. self.font_size[0] - x, self.font_size[1] - y.
        self.font_size = tuple(self.item[3].size(self.item[0]))

    @staticmethod
    def randomizer():
        """Модифицированный алгоритм генератора случайностей 7-bag.

        Список семи различных и ещё 2 случайные тетрамино помещаются в «мешок», после чего
        фигуры одна за другой случайным образом извлекаются из него, пока «мешок» не опустеет.
        Когда он опустеет, фигуры возвращаются в него и процесс повторяется.

        Yield:
            int: случайный индекс для массива figures.

        Примеры:
            generator = self.randomizer()
            tetromino = deepcopy(figures[next(generator)])

        """
        bag = [0, 1, 2, 3, 4, 5, 6] + [randrange(0, 7), randrange(0, 7)]
        shuffle(bag)
        while True:
            if bag:
                yield bag.pop()
            else:
                bag = [0, 1, 2, 3, 4, 5, 6] + [randrange(0, 7), randrange(0, 7)]
                shuffle(bag)

    @staticmethod
    def abroad_x(figure) -> bool:
        """Проверяет, вышло ли тетрамино за левую или правую границу стакана.

        Аргументы:
                figure: tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.

        Возвращаемое значение:
                bool: True - если тетрамино вышло, иначе - False.
        """
        # Нахожу минимальную и максимальную координату по оси 0x квадратов тетрамино.
        min_x = W
        max_x = 0
        for i in range(4):
            min_x = min(min_x, figure[i].x)
            max_x = max(max_x, figure[i].x)
        # Квадрат с минимальной координатой по оси 0x вышел за левую границу стакана или
        # квадрат с максимальной координатой по оси 0x вышел за правую границу стакана.
        return (not (CENTER + 2 <= min_x * TILE + CENTER + 2) or
                not (max_x * TILE + CENTER - 2 <= CENTER + (WT - 1) * TILE - 2))

    @staticmethod
    def abroad_y(figure) -> bool:
        """Проверяет, упало ли тетрамино в стакан.

        Аргументы:
                figure: tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.

        Возвращаемое значение:
                bool: True - если тетрамино упало, иначе - False.
        """
        # Нахожу максимальную координату по оси 0y квадратов тетрамино.
        max_y = 0
        for i in range(4):
            if max_y < figure[i].y:
                max_y = figure[i].y
        return not max_y * TILE < TILE * HT

    @staticmethod
    def is_square(figure) -> bool:
        """Проверка тетрамино на квадратность.

        Аргументы:
            figure: tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.

        Возвращаемое значение:
            bool: True - если тетрамино квадратно, иначе - False.
        """
        return (figure[0].x == figure[3].x and figure[1].x == figure[2].x and figure[0].y == figure[1].y
                and figure[2].y == figure[3].y)

    @staticmethod
    def above(figure) -> bool:
        """Проверка тетрамино на выход за границу верха стакана.

        Аргументы:
            figure: tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.

        Возвращаемое значение:
            bool: True - если тетрамино вышло, иначе - False.
        """
        for i in range(4):
            if figure[i].y < 0:
                return True
        return False

    def collision(self, figure) -> bool:
        """Метод для проверки тетрамино на столкновение с квадратами других тетрамино в стакане.

        Аргументы:
                figure: tuple(pygame.Rect): кортеж квадратов тетрамино. Длина - 4.

        Возвращаемое значение:
                bool: True - если тетрамино столкнулось, иначе - False.
        """
        for i in range(4):
            if self.field[figure[i].y][figure[i].x]:
                return True
        return False

    def main(self):
        stack = [None]  # Очередь действий, в начале тетрамино не нужно никуда двигать.
        generator = self.randomizer()  # Создаю генератор индексов для массива figures.
        while True:
            rotate = False  # В начале тетрамино не нужно поворачивать.
            for event in pg.event.get():
                if event.type == pg.QUIT:  # Если нажали ALT+F4.
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:  # Если клавишу нажали.
                    if event.key == pg.K_LEFT:  # Если это стрелка влево.
                        self.anim_limit_x = 0  # Позволяю сдвинуть тетромино на одну клетку влево.
                        stack.append('left')  # Добавляю действие двигаться влево из очереди действий.
                    elif event.key == pg.K_RIGHT:  # Если это стрелка вправо.
                        self.anim_limit_x = 0  # Позволяю сдвинуть тетромино на одну клетку вправо.
                        stack.append('right')  # Добавляю действие двигаться вправо из очереди действий.
                    elif event.key == pg.K_DOWN:  # Если это стрелка вниз.
                        self.anim_limit_y = 0  # Устремляю тетромино вниз стакана.
                    # Если это стрелка вверх и тетрамино не является квадратом.
                    elif event.key == pg.K_UP and not self.is_square(self.figure):
                        rotate = True  # Тетрамино необходимо повернуть.
                elif event.type == pg.KEYUP:  # Если клавишу отпустили.
                    if event.key == pg.K_LEFT:  # Если это стрелка влево.
                        stack.pop(stack.index('left'))  # Удалям действие двигаться влево из очереди действий.
                    elif event.key == pg.K_RIGHT:  # Если это стрелка вправо.
                        stack.pop(stack.index('right'))  # Удалям действие двигаться вправо из очереди действий.

            # Вектор движения равен последнему действию.
            if stack[-1] == 'left':
                dx = -1
            elif stack[-1] == 'right':
                dx = 1
            else:
                dx = 0

            # Двигаю тетрамино по оси 0x.
            self.anim_count_x += self.anim_speed_x
            if self.anim_count_x > self.anim_limit_x:
                self.anim_count_x = 0  # Обнуляю счётчик анимации x.
                self.anim_limit_x = 2000  # Обновляю значение, на случай, если были нажаты стрелки влево или вправо.
                figure_old = deepcopy(self.figure)  # Сохраняю координаты тетрамино.
                # Двигаю тетрамино по оси 0x в нужном направлении.
                for i in range(4):
                    self.figure[i].x += dx
                # Если вышли за границы - оставляю координаты старого тетрамино.
                if self.abroad_x(self.figure) or self.collision(self.figure):
                    self.figure = figure_old

            if rotate:  # Если была нажата стрелка вверх.
                center = self.figure[0]  # Центр тетрамино - всегда 0 элемент.
                figure_old = deepcopy(self.figure)  # Сохраняю координаты тетрамино.
                # Поворачиваю тетрамино на 90 градусов.
                for i in range(4):
                    x = self.figure[i].y - center.y
                    y = self.figure[i].x - center.x
                    self.figure[i].x = center.x - x
                    self.figure[i].y = center.y + y
                # Если при повороте тетрамино столкнулось с квадратами других тетрамино или вышло за границы стакана.
                if (self.abroad_x(self.figure) or self.abroad_y(self.figure) or
                        self.collision(self.figure) or self.above(self.figure)):
                    self.figure = deepcopy(figure_old)  # Оставляю координаты старого тетрамино.

            # Двигаю тетрамино по оси 0y.
            self.anim_count_y += self.anim_speed_y
            if self.anim_count_y > self.anim_limit_y:
                self.anim_count_y = 0  # Обнуляю счётчик анимации y.
                figure_old = deepcopy(self.figure)  # Сохраняю координаты тетрамино.
                # Двигаю тетрамино по оси 0y в нужном направлении.
                for i in range(4):
                    self.figure[i].y += 1
                # Если тетрамино упало на дно стакана или столкнулось с квадратами других тетрамино.
                if self.abroad_y(self.figure) or self.collision(self.figure):
                    # Заношу в массив заполненности стакана.
                    for i in range(4):
                        self.field[figure_old[i].y][figure_old[i].x] = True
                    # Обновляю значение падающего тетрамино.
                    # Не deepcopy потому что в следующей строке значение self.next_figure меняется на случайное.
                    self.figure = self.next_figure
                    # Беру следущий индекс из генератора индексов для массива figures.
                    self.next_figure = deepcopy(figures[next(generator)])
                    self.anim_limit_y = 2000  # Обновляю значение, на случай, если была нажата стрелка вниз.

            screen.blit(BACKGROUND, (0, 0))  # Отрисовываю BACKGROUND на мониторе.

            [pg.draw.rect(screen, (0, 0, 0), rect, 2) for rect in grid_glass]  # Отрисовываю сетку стакана с толщиной 2.

            # Отрисовываю падающее тетрамино.
            for i in range(4):
                # Рассчитываю новые координаты для квадрата тетрамино, учитывая толщину линии и смещение по оси 0x.
                figure_rect.x = CENTER + self.figure[i].x * TILE + 2
                figure_rect.y = (self.figure[i].y + 1) * TILE + 2
                # Рисую квадрат фигуры на новых координатах.
                pg.draw.rect(screen, self.color, figure_rect)

            # Отрисовываю квадраты других тетрамино на поле.
            for y, raw in enumerate(self.field):
                for x, flag in enumerate(raw):
                    if flag:  # Если на этой координате есть квадрат тетромино.
                        # Рассчитываю новые координаты для квадрата тетрамино,
                        # учитывая толщину линии и смещение по оси 0x.
                        figure_rect.x, figure_rect.y = CENTER + x * TILE + 2, (y + 1) * TILE + 2
                        pg.draw.rect(screen, self.color, figure_rect)  # Отрисовываю квадрат на новых координатах.

            # Отрисовываю сетку следующей фигуры с толщиной 2.
            [pg.draw.rect(screen, (0, 0, 0), rect, 2) for rect in grid_next_figure]
            # Отрисовываю следущую фигуру.
            for i in range(4):
                # Рассчитываю новые координаты для квадрата следующего тетрамино.
                figure_rect.x = CENTER + (self.next_figure[i].x + WT + 2) * TILE + 2
                figure_rect.y = (self.next_figure[i].y + 6) * TILE + 2
                # Рисую квадрат следущего тетрамино на новых координатах.
                pg.draw.rect(screen, self.color, figure_rect)

            # Удаляю заполненные линии, если таковые есть.
            field = self.field  # Копирую значение текущей заполненности стакана.
            count = 0  # Счетчик заполненных линий.
            for y in range(HT):
                if all(self.field[y]):  # Если линия заполнена.
                    # Удаляю эту линию, добавляю пустую линию в начало cтакана.
                    field = [[False for _ in range(WT)]] + self.field[:y] + self.field[y + 1:]
                    count += 1
            if count:
                # Увеличиваю рекорд на очки за количество заполненных линий.
                self.record += self.lines_points[count - 1]  # -1, т.к. мне нужен индекс, а не порядковый номер.
            self.lines += count  # Обновляю значение заполненных линий в этом раунде.
            self.field = field  # Обновляю массив заполненности стакана.
            self.sentences[3][0] = str(self.record)  # Обновляю изображение рекорда.

            # Новый раунд.
            if self.lines > 10:
                self.num += 1  # Переходим на следующий раунд.
                self.lines = 0  # Обнуляем значение собранных линий.
                self.color = rounds_colors[self.num - 1]  # -1, т.к. мне нужен индекс, а не порядковый номер.
                # Количество очков за 1, 2, 3, 4 линии обновляется.
                self.lines_points = (100 * self.num, 300 * self.num, 700 * self.num, 1500 * self.num)
                # Переменные для контролирования движения тетрамино по осям 0y и 0x.
                self.anim_count_y, self.anim_speed_y, self.anim_limit_y = 0, 40 + 20 * self.num, 2000
                self.anim_count_x, self.anim_speed_x, self.anim_limit_x = 0, 360 + 7 * self.num, 2000
                self.sentences[0][0] = f"Раунд {self.num}"  # Обновляем изображение номера раунда.

            # Отслеживание пункта '<-'.
            active = False
            mouse_x, mouse_y = pg.mouse.get_pos()  # Координаты текущего положения курсора мыши.
            x, y = self.item[1], self.item[2]
            # Если мышь наведена на '<-'.
            if x < mouse_x < x + self.font_size[0] and y < mouse_y < y + self.font_size[1]:
                active = True
                # Если нажали левой кнопкой мыши.
                if pg.mouse.get_pressed(3)[0]:
                    self.__init__()
                    return

            # Отрисовка пункта '<-'.
            name, x, y, font = self.item[0], self.item[1], self.item[2], self.item[3]
            if active:
                screen.blit(font.render(name, True, self.item[5]), (x, y))
            else:
                screen.blit(font.render(name, True, self.item[4]), (x, y))
            # Отрисовка предложений.
            for name, x, y, font, color in self.sentences:
                screen.blit(font.render(name, True, color), (x, y))

            # Конец игры.
            if any(field[0]):  # Если в первой линии есть любой квадрат.
                square = deepcopy(figure_rect)
                # Рисую красивую мозайку.
                for j in range(HT):
                    for i in range(WT):
                        square.x = CENTER + i * TILE + 2
                        square.y = (j + 1) * TILE + 2
                        pg.draw.rect(screen, (randrange(250), randrange(250), randrange(250)), square)
                pg.display.flip()
                pg.time.wait(1000)
                # Обнуляю все значения, возвращаюсь на предыдущую сцену.
                self.__init__()
                return

            pg.display.flip()  # Обновляю монитор.
            clock.tick(FPS)  # Ограничиваю скорость выполнения программы до 60 кадров в секунду.


# Создаю новый раунд.
new_round = Round()

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

# Создаю сцену игрового меню.
main_menu_sentences = (
    ("Тетрис", W // 2 - TILE * 4, 0, font3, (255, 0, 0)),
    ("Автор: Афанасин Егор", TILE * 3, H - TILE * 3, font1, (54, 54, 54)),
)
main_menu_items = (
    ("Играть", W // 2 - 80, TILE * 3, font2, (0, 0, 0), (255, 0, 0), 0, new_round.main),
    ("Помощь", W // 2 - 80, TILE * 5 + TILE // 2, font2, (0, 0, 0), (255, 0, 0), 1, assistance.main),
    ("Рекорды", W // 2 - 80, TILE * 8, font2, (0, 0, 0), (255, 0, 0), 2, records.main),
    ("Выйти", W // 2 - 80, TILE * 10 + TILE // 2, font2, (0, 0, 0), (255, 0, 0), 3, sys.exit),
)
main_menu = Menu(main_menu_sentences, main_menu_items)

main_menu.main()
