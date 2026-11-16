import sys
import ctypes
import os
import pygame

# Fix Windows DPI scaling cut-offs when spawned or run standalone
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

pygame.init()

WIDTH = 893
HEIGHT = 800
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Arcade Flashback Classics - Breakout")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
GREY = (212, 210, 212)
BLACK = (0, 0, 0)
BLUE = (0, 97, 148)

RED = (162, 8, 8)
ORANGE = (183, 119, 0)
GREEN = (0, 127, 33)
YELLOW = (197, 199, 37)

score = 0
balls = 1
velocity = 4

paddle_width = 60
paddle_height = 20
wall_width = 16

all_sprites_list = pygame.sprite.Group()

class Brick(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()

class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()

    def moveRight(self, pixels):
        self.rect.x += pixels
        if self.rect.x > WIDTH - wall_width - paddle_width:
            self.rect.x = WIDTH - wall_width - paddle_width

    def moveLeft(self, pixels):
        self.rect.x -= pixels
        if self.rect.x < wall_width:
            self.rect.x = wall_width

class Ball(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.velocity = [velocity, -velocity]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def bounce(self, axis):
        if axis == "x":
            self.velocity[0] = -self.velocity[0]
        elif axis == "y":
            self.velocity[1] = -self.velocity[1]

paddle = Paddle(BLUE, paddle_width, paddle_height)
paddle.rect.x = WIDTH // 2 - paddle_width // 2
paddle.rect.y = HEIGHT - 65

ball = Ball(WHITE, 10, 10)
ball.rect.x = WIDTH // 2 - 5
ball.rect.y = HEIGHT // 2 - 5

all_bricks = pygame.sprite.Group()

brick_width = 55
brick_height = 16
x_gap = 7
y_gap = 5
wall_width = 16


def clear_bricks():
    for brick in list(all_bricks):
        all_bricks.remove(brick)
        all_sprites_list.remove(brick)


def load_level(level_number):
    """Load a text grid; R/O/G/Y choose colors, # or X makes a white brick."""
    filename = "level.txt" if level_number == 1 else f"level{level_number}.txt"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.isfile(path):
        if level_number > 1:
            create_generated_level(level_number)
            return True
        return False

    colors = {"R": RED, "O": ORANGE, "G": GREEN, "Y": YELLOW,
              "1": RED, "2": ORANGE, "3": GREEN, "4": YELLOW,
              "#": WHITE, "X": WHITE}
    clear_bricks()
    with open(path, "r", encoding="utf-8") as level_file:
        for row, line in enumerate(level_file):
            if row >= 8:
                break
            for column, symbol in enumerate(line.rstrip("\r\n").upper()):
                if column >= 14:
                    break
                color = colors.get(symbol)
                if color is not None:
                    brick = Brick(color, brick_width, brick_height)
                    brick.rect.topleft = (
                        wall_width + column * (brick_width + x_gap),
                        215 + row * (brick_height + y_gap),
                    )
                    all_bricks.add(brick)
                    all_sprites_list.add(brick)
    return True


def create_default_bricks():
    row_colors = [RED, RED, ORANGE, ORANGE, GREEN, GREEN, YELLOW, YELLOW]
    for j, color in enumerate(row_colors):
        for i in range(14):
            brick = Brick(color, brick_width, brick_height)
            brick.rect.x = wall_width + i * (brick_width + x_gap)
            brick.rect.y = 215 + j * (y_gap + brick_height)
            all_sprites_list.add(brick)
            all_bricks.add(brick)


def create_generated_level(level_number):
    """Create a deterministic, progressively larger layout when no level file exists."""
    clear_bricks()
    rows = min(8, 4 + (level_number - 2) // 2)
    row_colors = [RED, ORANGE, GREEN, YELLOW]
    pattern = level_number % 4

    for row in range(rows):
        for column in range(14):
            if pattern == 0:
                include_brick = (column + row + level_number) % 6 != 0
            elif pattern == 1:
                include_brick = (column + row * 2 + level_number) % 4 != 0
            elif pattern == 2:
                include_brick = abs(column - 6.5) <= 2.5 + row
            else:
                include_brick = column % 4 != (row + level_number) % 4

            if include_brick:
                color = row_colors[(row + level_number - 2) % len(row_colors)]
                brick = Brick(color, brick_width, brick_height)
                brick.rect.topleft = (
                    wall_width + column * (brick_width + x_gap),
                    215 + row * (brick_height + y_gap),
                )
                all_bricks.add(brick)
                all_sprites_list.add(brick)


def bricks():
    if not load_level(1):
        create_default_bricks()
    all_sprites_list.add(paddle)
    all_sprites_list.add(ball)


def main():
    global score
    lives = 3
    level_number = 1
    game_over = False
    won = False
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pixeled.ttf")
    try:
        hud_font = pygame.font.Font(font_path, 22)
        game_over_font = pygame.font.Font(font_path, 40)
    except (OSError, pygame.error):
        hud_font = pygame.font.SysFont(None, 28)
        game_over_font = pygame.font.SysFont(None, 48)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif game_over and event.key == pygame.K_r:
                    score = 0
                    lives = 3
                    level_number = 1
                    game_over = False
                    won = False
                    if not load_level(1):
                        clear_bricks()
                        create_default_bricks()
                    ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                    ball.velocity = [velocity, -velocity]

        if game_over:
            screen.fill(BLACK)
            title = game_over_font.render("YOU WIN!" if won else "GAME OVER", True, WHITE)
            score_text = hud_font.render(f"SCORE: {score}", True, WHITE)
            prompt = hud_font.render("R: RESTART   ESC: QUIT", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.moveLeft(10)
        if keys[pygame.K_RIGHT]:
            paddle.moveRight(10)

        ball.update()

        if ball.rect.y <= 20:
            ball.velocity[1] = abs(ball.velocity[1])

        if ball.rect.x >= WIDTH - wall_width - 10:
            ball.velocity[0] = -abs(ball.velocity[0])

        if ball.rect.x <= wall_width:
            ball.velocity[0] = abs(ball.velocity[0])

        if ball.rect.colliderect(paddle.rect):
            if ball.velocity[1] > 0:
                ball.rect.y = paddle.rect.y - ball.rect.height
                ball.velocity[1] = -abs(ball.velocity[1])
                hit_pos = (ball.rect.centerx - paddle.rect.centerx) / (paddle_width / 2)
                ball.velocity[0] = int(hit_pos * 6)

        for brick in list(all_bricks):
            if ball.rect.colliderect(brick.rect):
                if abs(ball.rect.right - brick.rect.left) < 10 or abs(ball.rect.left - brick.rect.right) < 10:
                    ball.velocity[0] = -ball.velocity[0]
                else:
                    ball.velocity[1] = -ball.velocity[1]
                all_bricks.remove(brick)
                all_sprites_list.remove(brick)
                score += 1
                break

        if ball.rect.y > HEIGHT:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                ball.velocity = [velocity, -velocity]

        if not all_bricks and not game_over:
            level_number += 1
            if not load_level(level_number):
                won = True
                game_over = True
            else:
                ball.rect.center = (WIDTH // 2, HEIGHT // 2)
                ball.velocity = [velocity, -velocity]

        screen.fill(BLACK)

        pygame.draw.line(screen, GREY, [0, 19], [WIDTH, 19], 40)
        pygame.draw.line(screen, GREY, [(wall_width / 2) - 1, 0], [(wall_width / 2) - 1, HEIGHT], wall_width)
        pygame.draw.line(screen, GREY, [(WIDTH - wall_width / 2) - 1, 0], [(WIDTH - wall_width / 2) - 1, HEIGHT], wall_width)

        pygame.draw.line(screen, BLUE, [(wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2], [(wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2 + 54], wall_width)
        pygame.draw.line(screen, BLUE, [(WIDTH - wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2], [(WIDTH - wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2 + 54], wall_width)

        pygame.draw.line(screen, RED, [(wall_width / 2) - 1, 212.5], [(wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], wall_width)
        pygame.draw.line(screen, RED, [(WIDTH - wall_width / 2) - 1, 212.5], [(WIDTH - wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], wall_width)

        pygame.draw.line(screen, ORANGE, [(wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], [(wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], wall_width)
        pygame.draw.line(screen, ORANGE, [(WIDTH - wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], [(WIDTH - wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], wall_width)

        pygame.draw.line(screen, GREEN, [(wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], [(wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], wall_width)
        pygame.draw.line(screen, GREEN, [(WIDTH - wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], [(WIDTH - wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], wall_width)

        pygame.draw.line(screen, YELLOW, [(wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], [(wall_width / 2) - 1, 212.5 + 8 * brick_height + 8 * y_gap], wall_width)
        pygame.draw.line(screen, YELLOW, [(WIDTH - wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], [(WIDTH - wall_width / 2) - 1, 212.5 + 8 * brick_height + 8 * y_gap], wall_width)

        all_sprites_list.draw(screen)
        score_text = hud_font.render(f"SCORE: {score}", True, WHITE)
        lives_text = hud_font.render(f"LIVES: {lives}", True, WHITE)
        level_text = hud_font.render(f"LEVEL: {level_number}", True, WHITE)
        screen.blit(score_text, (30, 55))
        screen.blit(lives_text, lives_text.get_rect(center=(WIDTH // 2, 67)))
        screen.blit(level_text, (WIDTH - level_text.get_width() - 30, 55))
        pygame.display.flip()

    pygame.quit()


def run_game():
    main()


if __name__ == "__main__":
    bricks()
    main()