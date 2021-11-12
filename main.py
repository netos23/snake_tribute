# Pygame шаблон - скелет для нового проекта Pygame
import pygame
import random

# Описание констант
X = 0
Y = 1

# Настройки поля
FIELD_WIDTH = 20
FIELD_HEIGHT = 20
START_POS = (FIELD_WIDTH // 2, 2)
CHERRY_START = (FIELD_WIDTH // 2, FIELD_HEIGHT // 2)

# описание действий
MOVE = 0
EAT = 1
DEATH = 2

# типы клеток
EMPTY = 0
CHERRY = 1
SNAKE = 2
WALL = 3

# значения направлений
UP = 0
LEFT = 1
RIGHT = 2
DOWN = 3

# настройки игры
WIDTH = 360
HEIGHT = 480
# (скорость)
FPS = 30

# Задаем цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (1, 200, 20)


class SnakePart:
	def __init__(self, cord):
		self.pos = cord
		self.next = None


class Snake:
	def __init__(self, cord):
		head = SnakePart(cord)
		self.head = head
		self.tail = head
		self.direction = RIGHT

	def move(self):
		pos = self.head.pos
		# сдвигаем голову
		self.head.pos = self.next_pos()
		# сдвигаем оставшиеся части
		next_part = self.head.next
		while next_part is not None:
			tmp = next_part.pos
			next_part.pos = pos
			pos = tmp
			next_part = next_part.next

	def eat(self):
		# запоминаем позицию хвоста
		pos = self.tail.pos
		# двигаем змейку
		self.move()
		# добавляем новый сегмент в хвост
		new_part = SnakePart(pos)
		self.tail.next = new_part
		self.tail = new_part

	def next_pos(self):
		pos = self.head.pos

		if self.direction == UP:
			next_pos = pos[X], pos[Y] - 1
		elif self.direction == DOWN:
			next_pos = pos[X], pos[Y] + 1
		elif self.direction == LEFT:
			next_pos = pos[X] - 1, pos[Y]
		else:
			next_pos = pos[X] + 1, pos[Y]

		if next_pos[X] >= FIELD_WIDTH:
			next_pos = 0, next_pos[Y]
		if next_pos[X] < 0:
			next_pos = FIELD_WIDTH - 1, next_pos[Y]
		if next_pos[Y] >= FIELD_HEIGHT:
			next_pos = next_pos[X], 0
		if next_pos[Y] < 0:
			next_pos = next_pos[X], FIELD_HEIGHT - 1
		return next_pos

	def next_action(self, field):
		pos = self.next_pos()
		cell_type = field[pos[Y]][pos[X]]
		if cell_type == EMPTY:
			return MOVE
		elif cell_type == CHERRY:
			return EAT
		else:
			return DEATH

	def set_direction(self, direction):
		if (direction + self.direction) != 3:
			self.direction = direction


class Rectangle(pygame.sprite.Sprite):
	def __init__(self, x=0, y=0, w=50, h=50, col=GREEN):
		# Описание спрайта
		pygame.sprite.Sprite.__init__(self)
		# Установка размера
		self.image = pygame.Surface((w, h))
		# Установка цвета
		self.image.fill(col)
		self.rect = self.image.get_rect()
		# Установка позиции
		self.rect.x = x
		self.rect.y = y


if __name__ == '__main__':
	# Создаем игру и окно
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Snake")
	clock = pygame.time.Clock()

	# дополнительные переменные
	cell_w = WIDTH // FIELD_WIDTH
	cell_h = HEIGHT // FIELD_HEIGHT

	# создаем спрайты
	snake_sprites = pygame.sprite.Group()
	env_sprites = pygame.sprite.Group()

	cherry = Rectangle(CHERRY_START[X] * cell_w, CHERRY_START[X] * cell_h, cell_w, cell_h, RED)
	snake_head_sprite = Rectangle(START_POS[X] * cell_w, START_POS[Y] * cell_h, cell_w, cell_h, DARK_GREEN)

	env_sprites.add(cherry)
	snake_sprites.add(snake_head_sprite)

	# Создаем игровую логику
	snake = Snake(START_POS)
	cherry_pos = CHERRY_START
	start_field = [[0 for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
	game_field = start_field.copy()

	# Цикл игры
	running = True
	pause = True
	fail = False
	while running:
		# Держим цикл на правильной скорости
		clock.tick(FPS)

		# Ввод процесса (события)
		for event in pygame.event.get():
			# check for closing window
			if event.type == pygame.QUIT:
				running = False
			# обработка нажатий пользователя
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					snake.set_direction(LEFT)
				elif event.key == pygame.K_RIGHT:
					snake.set_direction(RIGHT)
				elif event.key == pygame.K_UP:
					snake.set_direction(UP)
				elif event.key == pygame.K_DOWN:
					snake.set_direction(DOWN)

				if event.key == pygame.K_SPACE:
					pause = not pause

				# if event.key == pygame.K_r:

		if not pause and not fail:
			# Обновление логики
			action = snake.next_action(game_field)
			if action == MOVE:
				snake.move()
			elif action == EAT:
				snake.eat()

				# Выставляем новую позицию для вишенки
				tmp = random.randint(0, FIELD_HEIGHT * FIELD_HEIGHT - 1)
				cherry_pos = (tmp // FIELD_HEIGHT, tmp % FIELD_HEIGHT)
				while game_field[cherry_pos[Y]][cherry_pos[X]] != EMPTY:
					tmp = random.randint(0, FIELD_HEIGHT * FIELD_HEIGHT)
					cherry_pos = (tmp // FIELD_HEIGHT, tmp % FIELD_HEIGHT)

				snake_sprites.add(Rectangle(0, 0, cell_w, cell_h))
			else:
				print('Snake dead')
				# running = not running
				fail = True

			# Отчистка поля и его заполнение
			game_field = [[0 for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
			cur = snake.head
			while cur is not None:
				game_field[cur.pos[Y]][cur.pos[X]] = SNAKE
				cur = cur.next
			game_field[cherry_pos[Y]][cherry_pos[X]] = CHERRY

			# Обновление спрайтов
			cur = snake.head
			for snake_sprite in snake_sprites:
				snake_sprite.rect.x = cur.pos[X] * cell_w
				snake_sprite.rect.y = cur.pos[Y] * cell_h
				cur = cur.next
			cherry.rect.x = cherry_pos[X] * cell_w
			cherry.rect.y = cherry_pos[Y] * cell_h
			snake_sprites.update()
			env_sprites.update()

		# Рендеринг
		screen.fill(BLACK)
		snake_sprites.draw(screen)
		env_sprites.draw(screen)

		# После отрисовки всего, переворачиваем экран
		pygame.display.flip()

	pygame.quit()
