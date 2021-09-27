import pygame
from datetime import datetime, timedelta
import time
import random

# 파이게임 초기화

pygame.init()

# 게임 화면 사이즈 설정

screen_width = 600
screen_height = 600
block_size = 20


# 색 설정

red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
black = 0, 0, 0
purple = 127, 0, 127
white = 255, 255, 255

screen = pygame.display.set_mode((screen_width, screen_height))

# 점수 출력용 텍스트 설정
font = pygame.font.Font(None, 30)  # 스코어
font1 = pygame.font.Font(None, 100)  # 게임 오버
font2 = pygame.font.Font(None, 60)  # Warning
font3 = pygame.font.Font(None, 40)  # 재시작 텍스트


def draw_background(screen):
    background = pygame.Rect((0, 0), (screen_width, screen_height))
    pygame.draw.rect(screen, black, background)


def draw_block(screen, color, position):
    """position 위치에 color 색깔의 블록을 그린다."""
    block = pygame.Rect((position[1] * block_size, position[0] * block_size),
                        (block_size, block_size))
    pygame.draw.rect(screen, color, block)


block_position = [0, 0]
last_moved_time = datetime.now()

# 방향키 입력에 따라 바꿀 블록의 방향
direction_on_key = {
    pygame.K_UP: 'north',
    pygame.K_DOWN: 'south',
    pygame.K_LEFT: 'west',
    pygame.K_RIGHT: 'east'
}

block_direction = 'east'


# 뱀, 사과, 게임판 클래스 만들기

class Snake:
    """뱀 클래스"""
    color = purple

    def __init__(self):
        self.positions = [(9, 6), (9, 7), (9, 8), (9, 9)]
        self.direction = 'south'

    def draw(self, screen):
        draw_block(screen, green, self.positions[0])
        for position in self.positions[1:]:
            draw_block(screen, self.color, position)

    def crawl(self):
        """뱀이 현재 방향으로 기어간다."""
        head_positions = self.positions[0]
        y, x = head_positions

        if self.direction == 'north':
            self.positions = [(y - 1, x)] + self.positions[:-1]
        elif self.direction == 'south':
            self.positions = [(y + 1, x)] + self.positions[:-1]
        elif self.direction == 'east':
            self.positions = [(y, x + 1)] + self.positions[:-1]
        elif self.direction == 'west':
            self.positions = [(y, x - 1)] + self.positions[:-1]

    def turn(self, direction):
        """뱀의 방향을 바꾼다."""
        self.direction = direction

    def grow(self):
        new_block = self.positions[-1]
        self.positions.append(new_block)


class Apple:
    """사과 클래스"""
    color = white

    def __init__(self, position=(5, 5)):
        self.position = position

    def draw(self, screen):
        """사과를 화면에 그린다."""
        draw_block(screen, self.color, self.position)


class SnakeCollisionException(Exception):
    """뱀 충돌 예외"""
    pass


class GameBoard:
    """게임판 클래스"""

    def __init__(self):
        self.snake = Snake()
        self.apple = Apple()
        self.score = 0

    def draw(self, screen):
        self.apple.draw(screen)
        self.snake.draw(screen)

    def put_new_apple(self):
        """게임판에 새 사과를 둔다."""
        self.apple = Apple((random.randint(0, 29), random.randint(0, 29)))
        for positions in self.snake.positions:
            if self.apple.position == positions:
                self.put_new_apple()
                break

    def process_turn(self):
        """게임을 한 차례 진행한다."""
        self.snake.crawl()

        if self.snake.positions[0] == self.apple.position:
            self.snake.grow()
            self.put_new_apple()
            self.score += 1

        # 뱀의 머리가 게임판을 벗어났을 때
        if self.snake.positions[0][0] in (-1, 30) or self.snake.positions[0][1] in (-1, 30):
            self.score -= 1
            self.snake.positions.pop()
            warning = font2.render('WARNING!!', False, red)
            screen.blit(warning, (100, 100))
            pygame.display.update()
            time.sleep(0.1)

        # 뱀의 머리와 몸이 부딪혔을 때
        if self.snake.positions[0] in self.snake.positions[1:]:
            raise SnakeCollisionException()

        # 스코어가 0점 이하로 떨어졌을 때
        if self.score < 0:
            raise SnakeCollisionException()


gameboard = GameBoard()

turn_interval = timedelta(seconds=0.05)  # 게임 진행 간격을 0.08초로 설정
is_need_to_restart = False  # 게임 재시작을 위한 변


# 초기화함수 만들어보기
def init():
    global gameboard
    pygame.init()
    gameboard.snake.positions = [(9, 6), (9, 7), (9, 8), (9, 9)]
    gameboard.snake.direction = 'south'
    gameboard.score = 0

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key in direction_on_key:
                # 충돌 오류 방지를 위해 180도 방향전환 불가토록 수정 2/15
                if event.key == pygame.K_LEFT and gameboard.snake.direction == 'east':
                    pass
                elif event.key == pygame.K_RIGHT and gameboard.snake.direction == 'west':
                    pass
                elif event.key == pygame.K_UP and gameboard.snake.direction == 'south':
                    pass
                elif event.key == pygame.K_DOWN and gameboard.snake.direction == 'north':
                    pass
                else:
                    gameboard.snake.turn(direction_on_key[event.key])

    if turn_interval <= datetime.now() - last_moved_time:
        try:
            gameboard.process_turn()

        except SnakeCollisionException:
            is_need_to_restart = True
            gameover = font1.render('GAME OVER', False, red)  # 게임오버 출력 2/15
            screen.blit(gameover, (100, 220))
            restart = font3.render('Press \'r\' to restart', False, blue)
            screen.blit(restart, (100, 400))
            pygame.display.update()
            time.sleep(1.5)

        except IndexError:
            is_need_to_restart = True
            gameover = font1.render('GAME OVER', False, red)  # 게임오버 출력 2/15
            restart = font3.render('Press \'r\' to restart', False, blue)
            screen.blit(restart, (100, 400))
            screen.blit(gameover, (100, 220))
            pygame.display.update()
            time.sleep(1.5)
        last_moved_time = datetime.now()

    while is_need_to_restart:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                is_need_to_restart = False
                break

        if is_need_to_restart is False:
            init()
            break

    draw_background(screen)
    gameboard.draw(screen)
    text = font.render(f'SCORE: {gameboard.score}', False, green)  # 스코어 출력 2/15
    screen.blit(text, (490, 30))
    pygame.display.update()
