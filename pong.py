import pygame, sys, random

pygame.init()

WIDTH, HEIGHT = 1280, 720
WIN_SCORE = 11

FONT = pygame.font.Font("pixeled.ttf", int(WIDTH / 20))

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
CLOCK = pygame.time.Clock()

opponent = pygame.Rect(WIDTH - 110, HEIGHT / 2 - 50, 10, 100)
player = pygame.Rect(110, HEIGHT / 2 - 50, 10, 100)
player_score, opponent_score = 0, 0

ball = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 10, 20, 20)
x_speed, y_speed = 1, 1
game_over = False
result_text = ""


def reset_round():
    global x_speed, y_speed
    ball.center = (WIDTH / 2, HEIGHT / 2)
    x_speed, y_speed = random.choice([1, -1]), random.choice([1, -1])


def reset_game():
    global player_score, opponent_score, game_over, result_text
    player_score = 0
    opponent_score = 0
    game_over = False
    result_text = ""
    player.top = HEIGHT / 2 - 50
    opponent.top = HEIGHT / 2 - 50
    reset_round()


reset_game()

while True:
    keys_pressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    if game_over:
        if keys_pressed[pygame.K_r]:
            reset_game()

        SCREEN.fill("black")
        pygame.draw.rect(SCREEN, "white", player)
        pygame.draw.rect(SCREEN, "white", opponent)
        pygame.draw.circle(SCREEN, "white", ball.center, 10)

        player_score_text = FONT.render(str(player_score), True, "white")
        opponent_score_text = FONT.render(str(opponent_score), True, "white")
        SCREEN.blit(player_score_text, (WIDTH / 2 - 100, 20))
        SCREEN.blit(opponent_score_text, (WIDTH / 2 + 60, 20))

        end_text = FONT.render(result_text, True, "white")
        restart_text = FONT.render("Press R to restart", True, "white")
        SCREEN.blit(end_text, end_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
        SCREEN.blit(restart_text, restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))

        pygame.display.update()
        CLOCK.tick(60)
        continue

    if keys_pressed[pygame.K_UP]:
        if player.top > 0:
            player.top -= 2

    if keys_pressed[pygame.K_DOWN]:
        if player.bottom < HEIGHT:
            player.top += 2

    if ball.y >= HEIGHT - ball.height:
        y_speed = -1
    if ball.y <= 0:
        y_speed = 1

    if ball.x <= 0:
        opponent_score += 1
        if opponent_score >= WIN_SCORE:
            game_over = True
            result_text = "YOU LOSE!"
        else:
            reset_round()
    if ball.x >= WIDTH - ball.width:
        player_score += 1
        if player_score >= WIN_SCORE:
            game_over = True
            result_text = "YOU WIN!"
        else:
            reset_round()

    if player.x - ball.width <= ball.x <= player.x and player.top - ball.height <= ball.y <= player.bottom + ball.height:
        x_speed = 1

    if opponent.x <= ball.x <= opponent.x + opponent.width + ball.width and opponent.top - ball.height <= ball.y <= opponent.bottom + ball.height:
        x_speed = -1

    if opponent.centery < ball.centery:
        opponent.top += 1
    if opponent.centery > ball.centery:
        opponent.top -= 1

    if opponent.top < 0:
        opponent.top = 0
    if opponent.bottom > HEIGHT:
        opponent.bottom = HEIGHT

    if not game_over:
        ball.x += x_speed * 2
        ball.y += y_speed * 2

    SCREEN.fill("black")
    pygame.draw.rect(SCREEN, "white", player)
    pygame.draw.rect(SCREEN, "white", opponent)
    pygame.draw.circle(SCREEN, "white", ball.center, 10)

    player_score_text = FONT.render(str(player_score), True, "white")
    opponent_score_text = FONT.render(str(opponent_score), True, "white")
    SCREEN.blit(player_score_text, (WIDTH / 2 - 100, 20))
    SCREEN.blit(opponent_score_text, (WIDTH / 2 + 60, 20))

    if game_over:
        end_text = FONT.render(result_text, True, "white")
        restart_text = FONT.render("Press R to restart", True, "white")
        SCREEN.blit(end_text, end_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
        SCREEN.blit(restart_text, restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))

    pygame.display.update()
    CLOCK.tick(300)