# Source code released under gpl v3 licence, see COPYING file

from pyglet import window, clock, image
from pyglet.gl import *  # pylint: disable=unused-wildcard-import
from pyglet.window import key
from random import choice, randint
from pyglet import font
from pyglet.font import Text

# Grid
class Grid:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # 0,0 is bottom left.
        self.data = [[(0, 0)]*self.width for i in range(self.height)]
        self.snakes = []
        self.bonus = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 21)

    def new_snake(self, snakeId: int, snakeType: str, keys: tuple, color: int):
        """
        Adds a new snake at a random position to the grid.
            :param self: 
            :param snakeId:int: ID of the snake.
            :param snakeType:str: Type of the snake.
            :param keys:tuple: Keys to move the snake.
            :param color:int: Color of the snake, as per the "colors" variable.
        """   
        newSnake = Snake(snakeId, snakeType, keys, color, self.random_point())
        self.snakes.append(newSnake)
        self.set_point(newSnake.x, newSnake.y, (newSnake.id, 0))

    def get_point(self, x: int, y: int) -> tuple:
        """
        Get the value associated to a coordinate into the grid.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
        """
        return self.data[y][x]

    def set_point(self, x: int, y: int, value: tuple):
        """
        Set a value to a coordinate into the grid.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
            :param value:tuple: Value to set.
        """
        self.data[y][x] = value

    def reset_point(self, x: int, y: int):
        """
        Reset the value associated to the coordinates.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
        """
        self.data[y][x] = (0, 0)

    def random_point(self):
        """
        Returns a tuple of random coordinates with nothing in it at this position.
            :param self: 
        """
        bx = randint(0, self.width - 1)
        by = randint(0, self.height - 1)
        for y in range(self.height):
            by = (by + y) % self.height
            for x in range(self.width):
                bx = (bx + x) % self.width
                if self.data[by][bx] == (0, 0):
                    return (bx, by)
        return None, None

    def show_bonus(self):
        """
        Adds (or not) a bonus on the grid.
            :param self: 
        """
        b = choice(self.bonus)
        if b != 0:
            bx, by = self.random_point()
            self.set_point(bx, by, (b, 0))

    def update_grid(self, draw_grid : bool = True):
        
        for i in range(len(self.snakes)):

            # Choosing new direction for CPUs, and moving snakes into their new position.
            snake1 = self.snakes[i]
            snake1.reset = False
            snake1.select_new_direction(grid)
            snake1.dir = snake1.new_dir
            snake1.move(grid)

            # Checking for head to head collision with previously moved snakes.
            for j in range(i):
                snake2 = self.snakes[j]
                if snake1.id != snake2.id:
                    if snake1.new_x == snake2.new_x and snake1.new_y == snake2.new_y:
                        snake1.reset = True
                        snake2.reset = True

            snake1.x = snake1.new_x
            snake1.y = snake1.new_y
            # snake1.check_collision(self)

            if snake1.reset:
                pass

            state, age = self.get_point(snake1.x, snake1.y)

            if state == 0: # If new cell is empty, the grid can easily be updated.
                self.set_point(snake1.x, snake1.y, (snake1.id, 0))

            elif state >= 1 and state <= 20: # If new cell is already occupied by another snake.
                if snake1.type == "drone":
                    self.set_point(snake1.x, snake1.y, (snake1.id, 0))
                else:
                    snake1.reset = True
                    snake1.reset_tail()
                    snake1.dead += 1
                    if state != snake1.id: # If the snake's tail wasn't ours
                        self.snakes[state-1].kill += 1
            
            elif state >= 21 and state <= 40: # Bonus
                self.set_point(snake1.x, snake1.y, (snake1.id, 0))
                snake1.edit_tail(state, True)

            elif state == 255: # Wall
                snake1.reset = True
                snake1.reset_tail()
                snake1.dead += 1
        
        global squares_verts, colors, bonus_timeout

        if draw_grid:
            verts_coord = []
            verts_color = []

        for y in range(self.height):
            for x in range(self.width):
                state, age = self.get_point(x, y)

                if draw_grid:
                    color_index = 0
                    fade = 1

                if state >= 1 and state <= 20:  # Snake
                    snake = self.snakes[state - 1]
                    if snake.reset or age > snake.tail:
                        self.reset_point(x, y)
                    else:
                        self.set_point(x, y, (state, age + 1))
                        if draw_grid:
                            color_index = snake.color
                            fade -= 0.005 * age
                            if fade < 0.4:
                                fade = 0.4

                elif state >= 21 and state <= 40:  # Bonus
                    if age > bonus_timeout:
                        self.reset_point(x, y)
                    else:
                        self.set_point(x, y, (state, age + 1))
                        if draw_grid:
                            if state == 21:  # Good bonus
                                color_index = 11
                            else:  # Mild bonus
                                color_index = 12

                elif state == 255:  # Wall
                    if draw_grid:
                        color_index = 10

                if draw_grid:
                    if color_index > 0:
                        r, g, b = colors[color_index]
                        verts_color.extend([r*fade, g*fade, b*fade]*4)
                        verts_coord.extend(squares_verts[y][x])

        if draw_grid:
            verts_coord_size = len(verts_coord)
            verts_color_size = len(verts_color)
            verts_coord_gl = (GLfloat * verts_coord_size)(*verts_coord)
            verts_color_gl = (GLfloat * verts_color_size)(*verts_color)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(3, GL_FLOAT, 0, verts_color_gl)
            glVertexPointer(2, GL_FLOAT, 0, verts_coord_gl)
            glDrawArrays(GL_QUADS, 0, verts_coord_size // 2)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

class Snake:
    def __init__(self, snakeId: int, snakeType: str, keys: tuple, color: int, coord: tuple):
        """
        Initializes a snake.
            :param self: 
            :param snakeId:int: ID of the snake. Must be unique (I guess).
            :param snakeType:str: Type of the snake. Either "drone", "human" or "cpu".
            :param keys:tuple: Tuple of four Pyglet keys associated to the movements of the snake.
            :param color:int: Index of a colour from the "colors" variable defined in the body of the code.
            :param coord:tuple: Coordinates of the head in the grid.
        """
        global grid
        self.id = snakeId
        self.type = snakeType

        if snakeType == 'drone':
            self.min_tail = 0
            self.max_tail = 0
            self.default_tail = 0
        else:
            self.min_tail = 9
            self.max_tail = 299
            self.default_tail = 29

        self.reset_tail()
        self.x, self.y = coord
        self.new_x = self.x
        self.new_y = self.y
        # 0: Up // 1: Right // 2: Down // 3: Left
        self.dir = choice((0, 1, 2, 3))
        self.new_dir = self.dir
        self.score = 0
        self.reset = False
        self.up, self.right, self.down, self.left = keys
        self.color = color
        self.dead = 0
        self.kill = 0

        self.cpu_ai = [
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 3),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0),
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 1),
            (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
             3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 2)
        ]

        self.cpu_avoid = [
            (1, 1, 1, 3),
            (2, 2, 2, 0),
            (3, 3, 3, 1),
            (0, 0, 0, 2)
        ]

    def reset_tail(self):
        """
        Resets values of snake, such as its tail's length.
            :param self: 
        """   
        self.tail = self.default_tail

    def edit_tail(self, bonusType: int, editScore: bool):
        """
        Edits the length of the tail based on the bonus eaten.
            :param self: 
            :param bonusType:int: Bonus type. May be 21 or 22.
            :param editScore:bool: Whether to edit the snake's score according to the bonus.
        """   
        if bonusType == 21:
            if editScore:
                self.score += 1
            if self.tail != self.max_tail:
                self.tail += 10
                if self.tail > self.max_tail:
                    self.tail = self.max_tail
        elif bonusType == 22:
            if editScore:
                self.score += 2
            if self.tail != self.min_tail:
                self.tail -= 5
                if self.tail < self.min_tail:
                    self.tail = self.min_tail

    def select_new_direction(self, grid: Grid):
        """
        Chooses a new direction for a CPU snake.
        It looks a few cells ahead, for the presence of a player, a wall or a bonus.
        It then changes its direction based on a probability.
            :param self: 
            :param grid:Grid: Grid object to reference to when choosing the direction.
        """
        if self.type == 'drone':
            self.new_dir = choice(self.cpu_ai[self.dir])
        elif self.type == 'cpu':
            avoid_detection = choice((2, 4, 4, 8, 8, 8))
            avoid_x = self.x
            avoid_y = self.y

            if self.dir == 0:
                avoid_y += avoid_detection
            elif self.dir == 1:
                avoid_x += avoid_detection
            elif self.dir == 2:
                avoid_y -= avoid_detection
            elif self.dir == 3:
                avoid_x -= avoid_detection

            if avoid_y > grid_height - 1:
                avoid_y -= grid_height
            if avoid_x > grid_width - 1:
                avoid_x -= grid_width
            if avoid_y < 0:
                avoid_y += grid_height
            if avoid_x < 0:
                avoid_x += grid_width

            state, age = grid.get_point( # pylint: disable=unused-variable
                avoid_x, avoid_y)

            if state == 0:
                self.new_dir = choice(self.cpu_ai[self.dir])
            elif state >= 1 and state <= 20:
                self.new_dir = choice(self.cpu_avoid[self.dir])
            elif state >= 21 and state <= 40:
                self.new_dir = self.dir
            elif state == 255:
                self.new_dir = choice(self.cpu_avoid[self.dir])

    def move(self, grid: Grid):
        """
        Moves the snake into its new position and checks if it is outside the boundaries.
            :param self: 
            :param grid:Grid: Grid to reference against.
        """
        if self.dir == 0:
            if self.y < grid.height - 1:
                self.new_y += 1
            else:
                self.new_y = 0
        elif self.dir == 1:
            if self.x < grid.width - 1:
                self.new_x += 1
            else:
                self.new_x = 0
        elif self.dir == 2:
            if self.y > 0:
                self.new_y -= 1
            else:
                self.new_y = grid.height - 1
        elif self.dir == 3:
            if self.x > 0:
                self.new_x -= 1
            else:
                self.new_x = grid.width - 1


def draw_arena():
    global arena_verts
    glBegin(GL_LINES)
    glColor3f(0.5, 0.5, 0.5)
    for i in range(4):
        glVertex2f(*arena_verts[i])
        glVertex2f(*arena_verts[i + 1])
    glEnd()


def draw_header():
    global arena_border, arena_height
    glColor3f(1, 1, 1)
    header_img.blit(arena_border, arena_border + arena_border + arena_height)


def draw_points():
    global font, points_coord
    for snake in grid.snakes:
        if snake.type != 'drone':
            text = "KILL %-3d, DEATH %-3d, BONUS %-3d" % (
                snake.kill, snake.dead, snake.score)
            x, y = points_coord[snake.id - 1]
            r, g, b = colors[snake.color]
            txt = Text(font, text, x, y, color=(r, g, b, 1))
            txt.draw()


screen_width = 740
screen_height = 550

arena_width = 720
arena_height = 480
arena_border = 10

# 2,3,4,5,6,8,10,12,15,16,20,24,30,40
square_size = 10
grid_width = int(arena_width / square_size)
grid_height = int(arena_height / square_size)
# 8 = 90 x 60 = 5400 squares
# 10 = 72 x 48 = 3456 squares

win = window.Window(width=screen_width, height=screen_height)
header_img = image.load('header.png').texture
fps_limit = 12
clock.set_fps_limit(fps_limit)
#keyboard = key.KeyStateHandler()
font = font.load('Arial', 12, bold=True, italic=False)


@win.event
def on_key_press(symbol, modifiers):
    for snake in grid.snakes:
        if snake.type == 'human':
            if symbol == snake.up and snake.dir != 2:
                snake.new_dir = 0
            elif symbol == snake.right and snake.dir != 3:
                snake.new_dir = 1
            elif symbol == snake.down and snake.dir != 0:
                snake.new_dir = 2
            elif symbol == snake.left and snake.dir != 1:
                snake.new_dir = 3
#win.on_key_press = on_key_press


arena_verts = [
    (arena_border-1, arena_border-2),
    (arena_border+arena_width+1, arena_border-2),
    (arena_border+arena_width+1, arena_border+arena_height),
    (arena_border-1, arena_border+arena_height),
    (arena_border-1, arena_border-2)
]
square_verts = [
    (0, 0),
    (square_size-1, 0),
    (square_size-1, square_size-1),
    (0, square_size-1)
]

points_coord = [
    (150, 530),
    (150, 510),
    (420, 530),
    (420, 510)
]

squares_verts = []
for y in range(grid_height):
    squares_verts.append([])
    for x in range(grid_width):
        squares_verts[y].append([])
        for vx, vy in square_verts:
            squares_verts[y][x].append(vx + arena_border + (x * square_size))
            squares_verts[y][x].append(vy + arena_border + (y * square_size))

#(id, age)
# id = 0          : empty
# id >= 1 e <=20  : snake (human, cpu, drone)
# id >=21 e <=40  : bonus
# id = 255        : wall
grid = Grid(grid_width, grid_height)

# set wall
for y in [10, 11, 48 - 12, 49 - 12]:
    for x in range(22, 67 - 18):
        grid.set_point(x, y, (255, 0))
for x in [10, 11, 78 - 18, 79 - 18]:
    for y in range(22, 37 - 12):
        grid.set_point(x, y, (255, 0))
# for y in range(10):
#  for x in range(90):
#    grid.set_point(x,y,(255,0))

colors = [
    (0, 0, 0),
    (0, 0, 1),
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1),
    (0.5, 0.5, 0),
    (0.5, 0, 0.5),
    (0, 0.5, 0.5),
    (1, 1, 1),
    (1, 1, 1),
    (1, 1, 1),
    (0, 1, 0),
    (1, 0, 0)
]

#bonusArray = []
bonus_timeout = 74

grid.new_snake(1, 'human', (key.UP, key.RIGHT, key.DOWN, key.LEFT), 1)
grid.new_snake(2, 'cpu', (key.W, key.D, key.S, key.A), 2)
grid.new_snake(3, 'cpu', (key.R, key.G, key.F, key.D), 3)
grid.new_snake(4, 'cpu', (key.U, key.K, key.J, key.H), 4)
grid.new_snake(5, 'drone', (0, 0, 0, 0), 8)
grid.new_snake(6, 'drone', (0, 0, 0, 0), 8)


#counter = 0
while not win.has_exit:
    win.dispatch_events()
    dt = clock.tick()
    # print dt
    win.set_caption('Pytron v0.5 (fps: %s)' % (round(clock.get_fps())))

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    draw_header()
    draw_arena()

#  if counter == 3:
#    counter = 0
    grid.show_bonus()
    grid.update_grid()
#  else:
#    counter += 1
    draw_points()
    win.flip()

# print "Punteggio"
# for snake in snakesArray:
#  print snake.id, ": points:", snake.points, ", dead: ", snake.dead, ", kill: ", snake.kill
